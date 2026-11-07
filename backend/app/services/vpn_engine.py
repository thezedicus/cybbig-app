"""Cybbig Tunnel : moteur VPN interne, bâti sur WireGuard.

Ce que Proton VPN et NordVPN apportent à côté du protocole sont des fonctions de *client* que Cybbig reproduit
ici, avec des protocoles publics (WireGuard, RFC 7748 pour X25519) et sans toucher à leur code ni à leurs services :

- génération des clés, du couple serveur/client et du profil (un VPN que l'utilisateur héberge lui-même) ;
- analyse d'un profil (fuite DNS, tunnel partiel, clé partagée absente, keepalive) ;
- durcissement : tunnel complet IPv4 + IPv6 (c'est ce qui active le coupe-circuit natif de WireGuard pour Windows,
  sans règle de pare-feu à poser) et DNS imposé ;
- classement des profils par latence et connexion rapide.

Le transport reste celui des clients officiels (voir ``vpn.py``). Aucune règle de pare-feu n'est modifiée ici.
"""
from __future__ import annotations

import base64
import ipaddress
import os
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from .. import db
from ..config import DATA_DIR
from ..utils import now_iso
from . import vpn

_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0
VPN_DIR = DATA_DIR / "vpn"
HOST_RE = re.compile(r"^(?=.{1,253}$)([A-Za-z0-9]([A-Za-z0-9\-]{0,61}[A-Za-z0-9])?)(\.[A-Za-z0-9]([A-Za-z0-9\-]{0,61}[A-Za-z0-9])?)*$")
DEFAULT_DNS = ("1.1.1.1", "9.9.9.9")
FULL_TUNNEL = "0.0.0.0/0, ::/0"


class VpnEngineError(ValueError):
    """Erreur lisible par l'utilisateur (paramètre invalide, profil introuvable)."""


# --- X25519 (RFC 7748) : clés WireGuard sans dépendance externe ----------------------------------

_P = 2 ** 255 - 19
_A24 = 121665


def x25519(scalar: bytes, u_coordinate: bytes) -> bytes:
    if len(scalar) != 32 or len(u_coordinate) != 32:
        raise VpnEngineError("X25519 attend des valeurs de 32 octets.")
    k = bytearray(scalar)
    k[0] &= 248
    k[31] &= 127
    k[31] |= 64
    k_int = int.from_bytes(k, "little")
    x1 = (int.from_bytes(u_coordinate, "little") & ((1 << 255) - 1)) % _P
    x2, z2, x3, z3, swap = 1, 0, x1, 1, 0
    for t in range(254, -1, -1):
        bit = (k_int >> t) & 1
        swap ^= bit
        if swap:
            x2, x3, z2, z3 = x3, x2, z3, z2
        swap = bit
        a, b = (x2 + z2) % _P, (x2 - z2) % _P
        aa, bb = a * a % _P, b * b % _P
        e = (aa - bb) % _P
        c, d = (x3 + z3) % _P, (x3 - z3) % _P
        da, cb = d * a % _P, c * b % _P
        x3 = pow(da + cb, 2, _P)
        z3 = x1 * pow(da - cb, 2, _P) % _P
        x2 = aa * bb % _P
        z2 = e * (aa + _A24 * e) % _P
    if swap:
        x2, x3, z2, z3 = x3, x2, z3, z2
    return (x2 * pow(z2, _P - 2, _P) % _P).to_bytes(32, "little")


def _b64(raw: bytes) -> str:
    return base64.b64encode(raw).decode("ascii")


def _unb64(value: str) -> bytes:
    try:
        raw = base64.b64decode(value.strip(), validate=True)
    except ValueError as exc:
        raise VpnEngineError("Clé WireGuard invalide (base64 attendu).") from exc
    if len(raw) != 32:
        raise VpnEngineError("Clé WireGuard invalide (32 octets attendus).")
    return raw


def generate_keypair() -> dict[str, str]:
    private = bytearray(os.urandom(32))
    private[0] &= 248
    private[31] &= 127
    private[31] |= 64
    return {"private": _b64(bytes(private)), "public": _b64(x25519(bytes(private), b"\x09" + b"\x00" * 31))}


def public_key(private_b64: str) -> str:
    return _b64(x25519(_unb64(private_b64), b"\x09" + b"\x00" * 31))


def generate_preshared_key() -> str:
    return _b64(os.urandom(32))


# --- Lecture et analyse d'un profil -------------------------------------------------------------

def parse_config(text: str) -> list[tuple[str, dict[str, str]]]:
    """Sections ``[Interface]`` / ``[Peer]`` d'un fichier WireGuard, dans l'ordre. Clés en minuscules."""
    sections: list[tuple[str, dict[str, str]]] = []
    for raw in (text or "").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            sections.append((line[1:-1].strip().lower(), {}))
        elif "=" in line and sections:
            key, value = line.split("=", 1)
            sections[-1][1][key.strip().lower()] = value.strip()
    return sections


def _section(sections: list[tuple[str, dict[str, str]]], name: str) -> dict[str, str]:
    return next((body for title, body in sections if title == name), {})


def split_endpoint(endpoint: str) -> tuple[str, int]:
    endpoint = (endpoint or "").strip()
    match = re.match(r"^\[(?P<host>[^\]]+)\]:(?P<port>\d+)$", endpoint) or re.match(r"^(?P<host>[^:]+):(?P<port>\d+)$", endpoint)
    if not match:
        return endpoint, 0
    return match.group("host"), int(match.group("port"))


def analyze_config(text: str) -> dict[str, Any]:
    sections = parse_config(text)
    interface, peer = _section(sections, "interface"), _section(sections, "peer")
    issues: list[dict[str, str]] = []

    def note(level: str, message: str) -> None:
        issues.append({"level": level, "message": message})

    if not interface or not peer:
        note("error", "Profil incomplet : sections [Interface] et [Peer] requises.")
    allowed = [a.strip() for a in peer.get("allowedips", "").split(",") if a.strip()]
    v4_full, v6_full = "0.0.0.0/0" in allowed, "::/0" in allowed
    dns = [d.strip() for d in interface.get("dns", "").split(",") if d.strip()]
    host, port = split_endpoint(peer.get("endpoint", ""))
    if not (v4_full or v6_full):
        note("warning", "Tunnel partiel : seuls certains réseaux passent par le VPN, le reste du trafic sort en clair.")
    elif v4_full != v6_full:
        note("warning", "Une seule famille d'adresses est routée : l'autre peut fuir hors du VPN (ajoutez 0.0.0.0/0 et ::/0).")
    if (v4_full or v6_full) and not dns:
        note("warning", "Aucun DNS imposé : les requêtes DNS peuvent partir vers le résolveur du fournisseur d'accès (fuite DNS).")
    if not peer.get("presharedkey"):
        note("info", "Pas de clé pré-partagée : ajoutez-en une pour une protection post-quantique supplémentaire.")
    if not peer.get("persistentkeepalive"):
        note("info", "Pas de PersistentKeepalive : derrière un NAT, le tunnel peut cesser de répondre.")
    if peer.get("endpoint") and not port:
        note("warning", "Endpoint sans port : format attendu hôte:port.")
    return {
        "valid": bool(interface and peer) and not any(i["level"] == "error" for i in issues),
        "endpoint": peer.get("endpoint", ""), "endpoint_host": host, "endpoint_port": port,
        "dns": dns, "allowed_ips": allowed, "full_tunnel": v4_full and v6_full,
        "has_preshared_key": bool(peer.get("presharedkey")), "keepalive": peer.get("persistentkeepalive", ""),
        "issues": issues,
    }


def harden_config(text: str, dns: tuple[str, ...] = DEFAULT_DNS) -> str:
    """Tunnel complet IPv4 + IPv6, DNS imposé, keepalive. WireGuard pour Windows en déduit le coupe-circuit natif."""
    for server in dns:
        try:
            ipaddress.ip_address(server)
        except ValueError as exc:
            raise VpnEngineError(f"Adresse DNS invalide : {server}") from exc
    sections = parse_config(text)
    if not _section(sections, "interface") or not _section(sections, "peer"):
        raise VpnEngineError("Profil incomplet : sections [Interface] et [Peer] requises.")
    out: list[str] = []
    current = ""
    seen: set[str] = set()
    forced = {("interface", "dns"): ", ".join(dns), ("peer", "allowedips"): FULL_TUNNEL, ("peer", "persistentkeepalive"): "25"}
    canonical = {"dns": "DNS", "allowedips": "AllowedIPs", "persistentkeepalive": "PersistentKeepalive"}

    def flush_missing(section: str) -> None:
        for (name, key), value in forced.items():
            if name == section and (name, key) not in seen:
                out.append(f"{canonical[key]} = {value}")

    for raw in text.splitlines():
        stripped = raw.split("#", 1)[0].strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            if current:
                flush_missing(current)
            current = stripped[1:-1].strip().lower()
            out.append(raw)
            continue
        if "=" in stripped:
            key = stripped.split("=", 1)[0].strip().lower()
            if (current, key) in forced:
                seen.add((current, key))
                out.append(f"{raw.split('=', 1)[0].rstrip()} = {forced[(current, key)]}")
                continue
        out.append(raw)
    if current:
        flush_missing(current)
    return "\n".join(out).rstrip() + "\n"


# --- Création d'un VPN personnel (serveur + client) ---------------------------------------------

def _slug(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", (name or "").lower()).strip("-")
    return slug[:40] or "cybbig"


def build_bundle(
    *, name: str, endpoint_host: str, endpoint_port: int = 51820, subnet: str = "10.66.0.0/24",
    dns: tuple[str, ...] = DEFAULT_DNS, full_tunnel: bool = True, use_preshared_key: bool = True,
) -> dict[str, Any]:
    """Un VPN auto-hébergé : configuration du serveur (à déployer sur la machine de l'utilisateur) et profil client enregistré."""
    host = (endpoint_host or "").strip()
    if not host or not (HOST_RE.match(host) or _is_ip(host)):
        raise VpnEngineError("Adresse du serveur invalide (nom de domaine ou IP).")
    if not 1 <= int(endpoint_port) <= 65535:
        raise VpnEngineError("Port invalide.")
    try:
        network = ipaddress.ip_network(subnet, strict=False)
    except ValueError as exc:
        raise VpnEngineError("Sous-réseau invalide (ex. 10.66.0.0/24).") from exc
    if network.version != 4 or network.num_addresses < 4 or not network.is_private:
        raise VpnEngineError("Sous-réseau IPv4 privé d'au moins 4 adresses requis.")
    for server in dns:
        try:
            ipaddress.ip_address(server)
        except ValueError as exc:
            raise VpnEngineError(f"Adresse DNS invalide : {server}") from exc
    hosts = network.hosts()
    server_ip, client_ip = next(hosts), next(hosts)
    server_keys, client_keys = generate_keypair(), generate_keypair()
    psk = generate_preshared_key() if use_preshared_key else ""
    prefix = network.prefixlen
    psk_line = f"PresharedKey = {psk}\n" if psk else ""
    server_conf = (
        "[Interface]\n"
        f"Address = {server_ip}/{prefix}\n"
        f"ListenPort = {int(endpoint_port)}\n"
        f"PrivateKey = {server_keys['private']}\n"
        "# Passerelle Linux : remplacez eth0 par l'interface publique du serveur.\n"
        "PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE\n"
        "PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE\n\n"
        "[Peer]\n"
        f"PublicKey = {client_keys['public']}\n"
        f"{psk_line}"
        f"AllowedIPs = {client_ip}/32\n"
    )
    client_conf = (
        "[Interface]\n"
        f"PrivateKey = {client_keys['private']}\n"
        f"Address = {client_ip}/{prefix}\n"
        f"DNS = {', '.join(dns)}\n\n"
        "[Peer]\n"
        f"PublicKey = {server_keys['public']}\n"
        f"{psk_line}"
        f"Endpoint = {host if not _is_ipv6(host) else f'[{host}]'}:{int(endpoint_port)}\n"
        f"AllowedIPs = {FULL_TUNNEL if full_tunnel else f'{network.with_prefixlen}'}\n"
        "PersistentKeepalive = 25\n"
    )
    VPN_DIR.mkdir(parents=True, exist_ok=True)
    stem = _slug(name)
    path = VPN_DIR / f"{stem}.conf"
    counter = 1
    while path.exists():
        counter += 1
        path = VPN_DIR / f"{stem}-{counter}.conf"
    path.write_text(client_conf, encoding="utf-8")
    profile = vpn.add_profile(config_path=str(path), label=name.strip()[:120] or "Cybbig Tunnel", provider="Cybbig Tunnel", kind="wireguard")
    db.audit("vpn_bundle_created", {"profile": profile["id"], "endpoint": f"{host}:{int(endpoint_port)}", "full_tunnel": full_tunnel})
    return {"profile": profile, "server_config": server_conf, "client_path": str(path), "server_public_key": server_keys["public"],
            "notes": [
                "La configuration du serveur contient sa clé privée et n'est pas conservée par Cybbig : copiez-la maintenant sur votre serveur (wg-quick up).",
                "Ouvrez le port UDP choisi sur le pare-feu du serveur et activez le routage IP (net.ipv4.ip_forward=1).",
                "Le profil client est enregistré ici ; sa clé privée reste dans ce fichier, sous votre dossier de données.",
            ]}


def _is_ip(value: str) -> bool:
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return False


def _is_ipv6(value: str) -> bool:
    try:
        return ipaddress.ip_address(value).version == 6
    except ValueError:
        return False


# --- Profils : analyse, durcissement, classement -------------------------------------------------

def _profile_text(pid: str) -> tuple[dict[str, Any], str]:
    try:
        profile = vpn._profile(pid)
    except KeyError as exc:
        raise VpnEngineError("Profil VPN introuvable.") from exc
    if profile["kind"] != "wireguard":
        raise VpnEngineError("Cette fonction concerne les profils WireGuard.")
    if not profile["config_exists"]:
        raise VpnEngineError(f"Fichier de configuration manquant : {profile['config_path']}")
    return profile, Path(profile["config_path"]).read_text(encoding="utf-8", errors="replace")


def analyze_profile(pid: str) -> dict[str, Any]:
    profile, text = _profile_text(pid)
    return {"profile_id": pid, "label": profile["label"], **analyze_config(text)}


def harden_profile(pid: str) -> dict[str, Any]:
    """Crée une copie durcie du profil (l'original n'est jamais modifié) et l'enregistre comme nouveau profil."""
    profile, text = _profile_text(pid)
    hardened = harden_config(text)
    VPN_DIR.mkdir(parents=True, exist_ok=True)
    path = VPN_DIR / f"{_slug(profile['label'] or Path(profile['config_path']).stem)}-durci.conf"
    counter = 1
    while path.exists():
        counter += 1
        path = VPN_DIR / f"{path.stem.split('-durci')[0]}-durci-{counter}.conf"
    path.write_text(hardened, encoding="utf-8")
    created = vpn.add_profile(config_path=str(path), label=f"{profile['label'] or 'Profil'} (durci)", provider=profile["provider"], kind="wireguard")
    db.audit("vpn_profile_hardened", {"source": pid, "profile": created["id"]})
    return {"profile": created, "analysis": analyze_config(hardened)}


_PING_MS = re.compile(r"[=<]\s*(\d+(?:[.,]\d+)?)\s*ms", re.I)


def ping_ms(host: str, timeout_s: float = 2.0) -> float | None:
    """Latence ICMP (None si l'hôte filtre le ping : la mesure ne prouve alors rien sur le tunnel)."""
    if not host or not (HOST_RE.match(host) or _is_ip(host)):
        return None
    cmd = ["ping", "-n", "1", "-w", str(int(timeout_s * 1000)), host] if os.name == "nt" else ["ping", "-c", "1", "-W", str(int(timeout_s)), host]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                             timeout=timeout_s + 3, creationflags=_NO_WINDOW)
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    match = _PING_MS.search(out.stdout or "")
    return float(match.group(1).replace(",", ".")) if match else (0.5 if "<" in (out.stdout or "") else None)


def rank_profiles() -> list[dict[str, Any]]:
    """Profils WireGuard utilisables, du plus rapide au plus lent (les profils sans réponse ICMP en dernier)."""
    entries: list[dict[str, Any]] = []
    for profile in vpn.list_profiles():
        if profile["kind"] != "wireguard" or not profile["config_exists"]:
            continue
        info = analyze_config(Path(profile["config_path"]).read_text(encoding="utf-8", errors="replace"))
        entries.append({"id": profile["id"], "label": profile["label"] or profile["provider"] or profile["id"],
                        "provider": profile["provider"], "host": info["endpoint_host"], "ms": None})
    with ThreadPoolExecutor(max_workers=8) as pool:
        for entry, ms in zip(entries, pool.map(lambda e: ping_ms(e["host"]), entries)):
            entry["ms"] = ms
    return sorted(entries, key=lambda e: (e["ms"] is None, e["ms"] if e["ms"] is not None else 0.0))


def quick_connect() -> dict[str, Any]:
    ranked = rank_profiles()
    if not ranked:
        raise VpnEngineError("Aucun profil WireGuard utilisable : ajoutez ou créez un profil.")
    best = next((e for e in ranked if e["ms"] is not None), ranked[0])
    result = vpn.connect(best["id"])
    db.audit("vpn_quick_connect", {"profile": best["id"], "ms": best["ms"], "ok": result.get("ok")})
    return {"chosen": best, "ranked": ranked, "result": result, "at": now_iso()}
