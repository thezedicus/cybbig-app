"""Gestionnaire de proxies (équivalent ProxySwitcher).

Stocke, teste et active des proxies fournis par l'utilisateur. Le proxy actif
peut router les analyses **passives** de Cybbig (option explicite), afin
d'auditer un périmètre autorisé depuis différents points de sortie.
"""
from __future__ import annotations

import time
from typing import Any
from urllib.parse import quote

import requests

from .. import db
from ..config import IP_ECHO_URL, NET_CHECK_TIMEOUT, USER_AGENT
from ..utils import new_id, now_iso

_SCHEMES = {"http", "https", "socks5", "socks5h", "socks4"}
_ACTIVE_KEY = "active_proxy_id"
_ROUTE_KEY = "route_scans_through_proxy"
_RESEARCH_ROUTE_KEY = "route_research_through_proxy"


# Modèles de proxy courants : points d'accès locaux (aucun hôte public n'est supposé).
PRESETS: dict[str, dict[str, Any]] = {
    "tor": {"label": "Tor (service local)", "scheme": "socks5h", "host": "127.0.0.1", "port": 9050,
            "note": "Service Tor installé sur ce poste. socks5h : la résolution DNS passe aussi par le proxy."},
    "tor-browser": {"label": "Tor Browser", "scheme": "socks5h", "host": "127.0.0.1", "port": 9150,
                    "note": "Tor Browser doit être ouvert."},
    "ssh-dynamic": {"label": "Tunnel SSH (ssh -D)", "scheme": "socks5h", "host": "127.0.0.1", "port": 1080,
                    "note": "Lancez d'abord : ssh -D 1080 -N utilisateur@votre-serveur"},
    "mitmproxy": {"label": "mitmproxy (inspection locale)", "scheme": "http", "host": "127.0.0.1", "port": 8080,
                  "note": "Pour inspecter le trafic de vos propres applications."},
    "zap": {"label": "OWASP ZAP", "scheme": "http", "host": "127.0.0.1", "port": 8090,
            "note": "Proxy d'écoute de ZAP pour un périmètre autorisé."},
    "squid": {"label": "Squid local", "scheme": "http", "host": "127.0.0.1", "port": 3128, "note": "Squid installé sur ce poste ou un conteneur local."},
}


def list_presets() -> list[dict[str, Any]]:
    return [{"id": key, **value} for key, value in PRESETS.items()]


def add_from_preset(key: str, **overrides: Any) -> dict[str, Any]:
    preset = PRESETS.get(key)
    if not preset:
        raise KeyError("Modèle de proxy inconnu.")
    fields = {**preset, **{k: v for k, v in overrides.items() if v not in (None, "")}}
    return add_proxy(scheme=fields["scheme"], host=fields["host"], port=fields["port"], label=fields["label"], note=fields.get("note", ""),
                     username=fields.get("username", ""), password=fields.get("password", ""))


def _redact(row: dict[str, Any]) -> dict[str, Any]:
    row = dict(row)
    pwd = row.get("password") or ""
    row["password"] = bool(pwd)  # ne jamais renvoyer le mot de passe
    row["has_password"] = bool(pwd)
    row["active"] = row["id"] == db.get_setting(_ACTIVE_KEY, "")
    row["url"] = _display_url(row)
    return row


def _display_url(row: dict[str, Any]) -> str:
    auth = ""
    if row.get("username"):
        auth = row["username"] + (":••••" if row.get("password") else "") + "@"
    return f"{row['scheme']}://{auth}{row['host']}:{row['port']}"


def _proxy_url(row: dict[str, Any]) -> str:
    auth = ""
    if row.get("username"):
        auth = quote(str(row["username"]), safe="")
        if row.get("password"):
            auth += ":" + quote(str(row["password"]), safe="")
        auth += "@"
    return f"{row['scheme']}://{auth}{row['host']}:{row['port']}"


def list_proxies() -> list[dict[str, Any]]:
    rows = db.fetch_all("SELECT * FROM proxies ORDER BY created_at DESC")
    return [_redact(r) for r in rows]


def add_proxy(
    *, scheme: str, host: str, port: int, label: str = "",
    username: str = "", password: str = "", note: str = "",
) -> dict[str, Any]:
    scheme = (scheme or "http").lower().strip()
    if scheme not in _SCHEMES:
        raise ValueError(f"Schéma de proxy non supporté : {scheme}")
    host = (host or "").strip()
    if not host:
        raise ValueError("Hôte du proxy requis.")
    port = int(port)
    if not (0 < port < 65536):
        raise ValueError("Port de proxy invalide.")
    pid = new_id("proxy")
    db.execute(
        """INSERT INTO proxies(id,label,scheme,host,port,username,password,enabled,note,created_at)
           VALUES(?,?,?,?,?,?,?,1,?,?)""",
        (pid, label.strip()[:120], scheme, host, port, username.strip(), password, note.strip()[:300], now_iso()),
    )
    db.audit("proxy_added", {"id": pid, "endpoint": f"{scheme}://{host}:{port}"})
    return get_proxy(pid)


def get_proxy(pid: str) -> dict[str, Any]:
    row = db.fetch_one("SELECT * FROM proxies WHERE id=?", (pid,))
    if not row:
        raise KeyError("Proxy introuvable.")
    return _redact(row)


def _raw(pid: str) -> dict[str, Any]:
    row = db.fetch_one("SELECT * FROM proxies WHERE id=?", (pid,))
    if not row:
        raise KeyError("Proxy introuvable.")
    return row


def update_proxy(pid: str, **fields: Any) -> dict[str, Any]:
    row = _raw(pid)
    allowed = {"label", "scheme", "host", "port", "username", "password", "enabled", "note"}
    sets, params = [], []
    for key, value in fields.items():
        if key not in allowed or value is None:
            continue
        if key == "scheme":
            value = str(value).lower()
            if value not in _SCHEMES:
                raise ValueError(f"Schéma non supporté : {value}")
        if key == "port":
            value = int(value)
            if not (0 < value < 65536):
                raise ValueError("Port invalide.")
        if key == "enabled":
            value = 1 if value else 0
        sets.append(f"{key}=?")
        params.append(value)
    if sets:
        params.append(pid)
        db.execute(f"UPDATE proxies SET {', '.join(sets)} WHERE id=?", params)
        db.audit("proxy_updated", {"id": pid, "fields": list(fields.keys())})
    return get_proxy(pid)


def delete_proxy(pid: str) -> None:
    _raw(pid)
    db.execute("DELETE FROM proxies WHERE id=?", (pid,))
    if db.get_setting(_ACTIVE_KEY, "") == pid:
        db.set_setting(_ACTIVE_KEY, "")
    db.audit("proxy_deleted", {"id": pid})


def set_active(pid: str | None) -> dict[str, Any]:
    if pid:
        _raw(pid)  # valide l'existence
        db.set_setting(_ACTIVE_KEY, pid)
        db.audit("proxy_activated", {"id": pid})
    else:
        db.set_setting(_ACTIVE_KEY, "")
        db.audit("proxy_deactivated", {})
    return status()


def set_route_scans(enabled: bool) -> None:
    db.set_setting(_ROUTE_KEY, "true" if enabled else "false")
    db.audit("proxy_route_scans", {"enabled": bool(enabled)})


def set_route_research(enabled: bool) -> None:
    db.set_setting(_RESEARCH_ROUTE_KEY, "true" if enabled else "false")
    db.audit("proxy_route_research", {"enabled": bool(enabled)})


def route_scans_enabled() -> bool:
    return str(db.get_setting(_ROUTE_KEY, "false")).lower() in {"1", "true", "yes", "on"}


def route_research_enabled() -> bool:
    return str(db.get_setting(_RESEARCH_ROUTE_KEY, "false")).lower() in {"1", "true", "yes", "on"}


def active_proxy() -> dict[str, Any] | None:
    pid = db.get_setting(_ACTIVE_KEY, "")
    if not pid:
        return None
    row = db.fetch_one("SELECT * FROM proxies WHERE id=? AND enabled=1", (pid,))
    return row or None


def requests_proxies(force: bool = False, route: str = "scans") -> dict[str, str]:
    """Dict proxies style requests pour le proxy actif.

    N'est appliqué aux scanners que si l'utilisateur a activé le routage
    (``route_scans_through_proxy``), sauf si ``force`` (test manuel).
    """
    enabled = route_research_enabled() if route == "research" else route_scans_enabled()
    if not force and not enabled:
        return {}
    row = active_proxy()
    if not row:
        return {}
    url = _proxy_url(row)
    return {"http": url, "https": url}


def test_proxy(pid: str) -> dict[str, Any]:
    """Teste le proxy par une requête vers un service d'écho d'IP (sortie réseau explicite)."""
    row = _raw(pid)
    proxies = {"http": _proxy_url(row), "https": _proxy_url(row)}
    started = time.monotonic()
    result: dict[str, Any] = {"ok": False, "ip": "", "ms": None, "error": ""}
    try:
        resp = requests.get(
            IP_ECHO_URL, proxies=proxies, timeout=NET_CHECK_TIMEOUT,
            headers={"User-Agent": USER_AGENT},
        )
        result["ms"] = int((time.monotonic() - started) * 1000)
        resp.raise_for_status()
        try:
            result["ip"] = str(resp.json().get("ip", "")).strip()
        except ValueError:
            result["ip"] = resp.text.strip()[:64]
        result["ok"] = bool(result["ip"])
    except requests.exceptions.ProxyError as exc:
        result["error"] = f"Proxy injoignable : {str(exc)[:200]}"
    except requests.exceptions.RequestException as exc:
        result["error"] = str(exc)[:200]
    db.execute(
        "UPDATE proxies SET last_test_at=?, last_test_ok=?, last_test_ip=?, last_test_ms=? WHERE id=?",
        (now_iso(), 1 if result["ok"] else 0, result["ip"], result["ms"], pid),
    )
    db.audit("proxy_tested", {"id": pid, "ok": result["ok"], "ip": result["ip"]})
    return result


def status() -> dict[str, Any]:
    active = active_proxy()
    return {
        "active": _redact(active) if active else None,
        "route_scans": route_scans_enabled(),
        "route_research": route_research_enabled(),
        "count": len(db.fetch_all("SELECT id FROM proxies")),
    }
