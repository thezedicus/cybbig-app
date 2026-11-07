"""Client VPN : pilote les clients officiels WireGuard / OpenVPN du poste.

Cybbig ne reproduit PAS un service VPN (Proton VPN, Hide.me…) : ces services
sont des infrastructures distantes. Ce module gère des *profils* = pointeurs
vers les fichiers de configuration que l'utilisateur a exportés depuis son
fournisseur (.conf WireGuard, .ovpn OpenVPN), affiche l'état de la connexion et
l'IP de sortie, et lance les clients officiels pour (dé)connecter.

Aucun identifiant VPN n'est stocké. Établir/fermer un tunnel exige en général
des droits administrateur : les commandes sont exécutées telles quelles et leur
sortie est remontée honnêtement.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

import requests

from .. import db
from ..config import IP_ECHO_URL, NET_CHECK_TIMEOUT, USER_AGENT
from ..utils import new_id, now_iso

_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0
_KINDS = {"wireguard", "openvpn"}

_WIREGUARD_CANDIDATES = [
    r"C:\Program Files\WireGuard\wireguard.exe",
    r"C:\Program Files\WireGuard\wg.exe",
]
_OPENVPN_CANDIDATES = [
    r"C:\Program Files\OpenVPN\bin\openvpn.exe",
    r"C:\Program Files\OpenVPN Connect\OpenVPNConnect.exe",
]


def _find(candidates: list[str], names: list[str]) -> str:
    for name in names:
        found = shutil.which(name)
        if found:
            return found
    for path in candidates:
        if Path(path).exists():
            return path
    return ""


def detect_clients() -> dict[str, Any]:
    wg = _find(_WIREGUARD_CANDIDATES, ["wireguard", "wg"])
    ovpn = _find(_OPENVPN_CANDIDATES, ["openvpn"])
    return {
        "wireguard": {"available": bool(wg), "path": wg},
        "openvpn": {"available": bool(ovpn), "path": ovpn},
    }


_PROVIDER_APPS = {
    "Proton VPN": [r"C:\Program Files\Proton\VPN\ProtonVPN.Launcher.exe"],
    "NordVPN": [r"C:\Program Files\NordVPN\NordVPN.exe"],
}


def detect_provider_apps() -> list[dict[str, Any]]:
    """Applications de fournisseurs présentes sur le poste (information seulement : Cybbig ne les pilote ni ne les modifie)."""
    return [{"name": name, "installed": any(Path(p).exists() for p in paths)} for name, paths in _PROVIDER_APPS.items()]


# --- Profils (pointeurs vers les configs de l'utilisateur) -------------------

def list_profiles() -> list[dict[str, Any]]:
    rows = db.fetch_all("SELECT * FROM vpn_profiles ORDER BY created_at DESC")
    for row in rows:
        row["config_exists"] = Path(row["config_path"]).is_file()
    return rows


def add_profile(*, config_path: str, label: str = "", provider: str = "", kind: str = "") -> dict[str, Any]:
    raw = (config_path or "").strip().strip('"')
    if not raw:
        raise ValueError("Chemin du fichier de configuration requis.")
    path = Path(raw).expanduser()
    if not path.is_file():
        raise ValueError(f"Fichier de configuration introuvable : {raw}")
    suffix = path.suffix.lower()
    if not kind:
        kind = "wireguard" if suffix == ".conf" else "openvpn" if suffix in {".ovpn", ".conf"} else ""
    kind = (kind or "").lower()
    if kind not in _KINDS:
        raise ValueError("Type inconnu : indiquez 'wireguard' (.conf) ou 'openvpn' (.ovpn).")
    pid = new_id("vpn")
    db.execute(
        """INSERT INTO vpn_profiles(id,label,provider,kind,config_path,created_at)
           VALUES(?,?,?,?,?,?)""",
        (pid, label.strip()[:120], provider.strip()[:60], kind, str(path.resolve()), now_iso()),
    )
    db.audit("vpn_profile_added", {"id": pid, "kind": kind, "provider": provider})
    return _profile(pid)


def _profile(pid: str) -> dict[str, Any]:
    row = db.fetch_one("SELECT * FROM vpn_profiles WHERE id=?", (pid,))
    if not row:
        raise KeyError("Profil VPN introuvable.")
    row["config_exists"] = Path(row["config_path"]).is_file()
    return row


def delete_profile(pid: str) -> None:
    _profile(pid)
    db.execute("DELETE FROM vpn_profiles WHERE id=?", (pid,))
    db.audit("vpn_profile_deleted", {"id": pid})


# --- État réseau -------------------------------------------------------------

def public_ip() -> dict[str, Any]:
    """IP de sortie actuelle (requête réseau explicite vers un service d'écho)."""
    try:
        resp = requests.get(IP_ECHO_URL, timeout=NET_CHECK_TIMEOUT, headers={"User-Agent": USER_AGENT})
        resp.raise_for_status()
        try:
            ip = str(resp.json().get("ip", "")).strip()
        except ValueError:
            ip = resp.text.strip()[:64]
        return {"ok": bool(ip), "ip": ip}
    except requests.exceptions.RequestException as exc:
        return {"ok": False, "ip": "", "error": str(exc)[:200]}


def _wireguard_tunnels(wg_path: str) -> list[str]:
    """Interfaces WireGuard actives (`wg show interfaces`)."""
    exe = wg_path if wg_path.lower().endswith("wg.exe") else shutil.which("wg") or ""
    if not exe:
        return []
    try:
        out = subprocess.run(
            [exe, "show", "interfaces"],
            capture_output=True, text=True, timeout=10, creationflags=_NO_WINDOW,
        )
        return [t for t in (out.stdout or "").split() if t]
    except (OSError, subprocess.SubprocessError):
        return []


def _process_running(name: str) -> bool:
    if os.name != "nt":
        return False
    try:
        out = subprocess.run(
            ["tasklist", "/FI", f"IMAGENAME eq {name}", "/NH"],
            capture_output=True, text=True, timeout=10, creationflags=_NO_WINDOW,
        )
        return name.lower() in (out.stdout or "").lower()
    except (OSError, subprocess.SubprocessError):
        return False


def status(with_ip: bool = False) -> dict[str, Any]:
    clients = detect_clients()
    wg_tunnels = _wireguard_tunnels(clients["wireguard"]["path"]) if clients["wireguard"]["available"] else []
    openvpn_running = _process_running("openvpn.exe")
    connected = bool(wg_tunnels or openvpn_running)
    result: dict[str, Any] = {
        "clients": clients,
        "connected": connected,
        "wireguard_tunnels": wg_tunnels,
        "openvpn_running": openvpn_running,
        "profiles": len(db.fetch_all("SELECT id FROM vpn_profiles")),
        "provider_apps": detect_provider_apps(),
    }
    if with_ip:
        result["public_ip"] = public_ip()
    return result


# --- (Dé)connexion via les clients officiels ---------------------------------

def _run(cmd: list[str]) -> dict[str, Any]:
    try:
        out = subprocess.run(
            cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=60, creationflags=_NO_WINDOW,
        )
        return {
            "ok": out.returncode == 0,
            "returncode": out.returncode,
            "stdout": (out.stdout or "")[-1500:],
            "stderr": (out.stderr or "")[-1500:],
        }
    except (OSError, subprocess.SubprocessError) as exc:
        return {"ok": False, "returncode": None, "stdout": "", "stderr": str(exc)[:400]}


def connect(pid: str) -> dict[str, Any]:
    prof = _profile(pid)
    if not prof["config_exists"]:
        raise RuntimeError(f"Fichier de configuration manquant : {prof['config_path']}")
    clients = detect_clients()
    if prof["kind"] == "wireguard":
        if not clients["wireguard"]["available"]:
            raise RuntimeError("WireGuard n'est pas installé sur ce poste.")
        # Installe le tunnel comme service (nécessite des droits administrateur).
        res = _run([clients["wireguard"]["path"], "/installtunnelservice", prof["config_path"]])
    else:
        if not clients["openvpn"]["available"]:
            raise RuntimeError("OpenVPN n'est pas installé sur ce poste.")
        res = _run([clients["openvpn"]["path"], "--config", prof["config_path"]])
    db.audit("vpn_connect", {"id": pid, "kind": prof["kind"], "ok": res["ok"], "rc": res["returncode"]})
    if not res["ok"]:
        res["hint"] = "Échec probable par manque de droits administrateur : lancez Cybbig en tant qu'administrateur pour gérer le tunnel."
    return res


def disconnect(pid: str = "") -> dict[str, Any]:
    clients = detect_clients()
    results = []
    # WireGuard : désinstalle chaque tunnel actif.
    if clients["wireguard"]["available"]:
        for tunnel in _wireguard_tunnels(clients["wireguard"]["path"]):
            results.append({"tunnel": tunnel, **_run([clients["wireguard"]["path"], "/uninstalltunnelservice", tunnel])})
    # OpenVPN : arrête le processus.
    if _process_running("openvpn.exe"):
        results.append({"tunnel": "openvpn", **_run(["taskkill", "/IM", "openvpn.exe", "/F"])})
    db.audit("vpn_disconnect", {"count": len(results)})
    if not results:
        return {"ok": True, "detail": "Aucun tunnel actif.", "results": []}
    return {"ok": all(r.get("ok") for r in results), "results": results}
