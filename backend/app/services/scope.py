from __future__ import annotations

import ipaddress
import os
import socket
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse

from .. import db
from ..config import CONSENT_VERSION


@dataclass
class ScopeDecision:
    allowed: bool
    reason: str
    local: bool = False
    host: str = ""
    warnings: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "allowed": self.allowed,
            "reason": self.reason,
            "local": self.local,
            "host": self.host,
            "warnings": self.warnings,
        }


def consent_status() -> dict:
    row = db.fetch_one("SELECT * FROM consent WHERE id=1")
    accepted = bool(row and row.get("version") == CONSENT_VERSION)
    return {
        "accepted": accepted,
        "version": CONSENT_VERSION,
        "record": row,
        "current_version": CONSENT_VERSION,
    }


def require_consent() -> ScopeDecision:
    status = consent_status()
    if not status["accepted"]:
        return ScopeDecision(False, "Le consentement et le cadre d'utilisation doivent être acceptés.")
    return ScopeDecision(True, "Consentement accepté.")


def _is_local_host(host: str) -> bool:
    host = host.lower().strip("[]")
    if host in {"localhost", "127.0.0.1", "::1"}:
        return True
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return False
    return ip.is_loopback or ip.is_private or ip.is_link_local


def _is_public_ip(host: str) -> bool:
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return False
    return not (ip.is_loopback or ip.is_private or ip.is_link_local or ip.is_reserved or ip.is_multicast)


def _domain_matches(host: str, allowed: list[str]) -> bool:
    host = host.lower().rstrip(".")
    for entry in allowed:
        entry = str(entry).lower().strip().rstrip(".")
        if not entry:
            continue
        if host == entry:
            return True
        if host.endswith("." + entry):
            return True
    return False


def check_web_scope(project: dict, url: str) -> ScopeDecision:
    consent = require_consent()
    if not consent.allowed:
        return consent
    if not project:
        return ScopeDecision(False, "Projet introuvable.")
    if not project.get("authorization_confirmed"):
        return ScopeDecision(False, "L'autorisation du périmètre n'a pas été confirmée pour ce projet.")

    try:
        parsed = urlparse(url)
    except ValueError:
        return ScopeDecision(False, "URL invalide.")
    if parsed.scheme not in {"http", "https"}:
        return ScopeDecision(False, "Seuls HTTP et HTTPS sont autorisés.")
    host = (parsed.hostname or "").lower()
    if not host:
        return ScopeDecision(False, "Hôte absent de l'URL.")
    if parsed.username or parsed.password:
        return ScopeDecision(False, "Les identifiants dans l'URL ne sont pas acceptés.")

    local = _is_local_host(host)
    allowed_domains = db.json_loads(project.get("scope_domains"), []) or []
    level = project.get("activity_level", "B")
    warnings: list[str] = []
    if local:
        warnings.append("Cible locale : vérifiez qu'elle ne pointe pas vers un service sensible non prévu.")
        return ScopeDecision(True, "Cible locale autorisée dans le périmètre de laboratoire.", True, host, warnings)

    if not _domain_matches(host, allowed_domains):
        return ScopeDecision(
            False,
            f"L'hôte « {host} » n'est pas dans les domaines autorisés du projet.",
            False, host,
        )
    if not project.get("authorization_ref"):
        return ScopeDecision(False, "Une référence d'autorisation écrite est obligatoire pour une cible distante.", False, host)
    if level not in {"D", "E"}:
        return ScopeDecision(
            False,
            "Le projet doit être au niveau d'activité D (tiers autorisé) pour une cible distante.",
            False, host,
        )
    if _is_public_ip(host):
        warnings.append("La cible est une adresse IP publique : confirmez l'autorisation et l'exposition.")
    warnings.append("Scan passif uniquement. Aucune charge d'exploitation ne sera envoyée.")
    return ScopeDecision(True, "Cible distante autorisée par le périmètre du projet.", False, host, warnings)


def check_path_scope(project: dict) -> ScopeDecision:
    consent = require_consent()
    if not consent.allowed:
        return consent
    if not project:
        return ScopeDecision(False, "Projet introuvable.")
    if not project.get("authorization_confirmed"):
        return ScopeDecision(False, "L'autorisation du périmètre n'a pas été confirmée pour ce projet.")
    raw = (project.get("path") or "").strip()
    if not raw:
        return ScopeDecision(False, "Aucun chemin de projet n'est configuré.")
    path = Path(raw).expanduser()
    try:
        resolved = path.resolve(strict=True)
    except (OSError, RuntimeError):
        return ScopeDecision(False, f"Le chemin n'existe pas : {raw}")
    if not resolved.is_dir():
        return ScopeDecision(False, "Le chemin doit être un dossier.")
    parts = {p.lower() for p in resolved.parts}
    if "windows" in parts or "system32" in parts or "program files" in parts or "program files (x86)" in parts:
        return ScopeDecision(False, "Les dossiers système Windows sont exclus du périmètre.")
    if resolved.parent == resolved:
        return ScopeDecision(False, "La racine d'un disque ne peut pas être analysée.")
    # Refuser un dossier personnel entier pour éviter une collecte involontaire excessive.
    home = Path.home().resolve()
    if resolved == home:
        return ScopeDecision(False, "Le dossier personnel entier est trop large ; choisissez un sous-dossier de projet.")
    warnings = []
    if resolved.drive.upper() != str(Path.home().drive).upper():
        warnings.append("Le projet se trouve sur un autre volume que le profil utilisateur.")
    return ScopeDecision(True, "Dossier de projet autorisé.", _is_local_host("127.0.0.1"), "", warnings)


def check_scan_scope(project: dict, kind: str, target: str) -> ScopeDecision:
    if kind == "php":
        return check_path_scope(project)
    if kind in {"web", "api"}:
        if target.lower().startswith(("http://", "https://")):
            return check_web_scope(project, target)
        return check_path_scope(project)
    if kind == "checkout":
        if target.lower().startswith(("http://", "https://")):
            return check_web_scope(project, target)
        return check_path_scope(project)
    if kind == "reverse":
        return check_binary_scope(project, target)
    return ScopeDecision(False, f"Type de scan inconnu : {kind}")


def check_binary_scope(project: dict, target: str) -> ScopeDecision:
    """Un binaire à rétro-analyser doit exister et rester dans le dossier du projet."""
    base = check_path_scope(project)
    if not base.allowed:
        return base
    raw = (target or "").strip().strip('"')
    if not raw:
        return ScopeDecision(False, "Indiquez le chemin du binaire à analyser.")
    root = Path((project.get("path") or "")).expanduser().resolve()
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = root / candidate
    try:
        resolved = candidate.resolve(strict=True)
    except (OSError, RuntimeError):
        return ScopeDecision(False, f"Binaire introuvable : {raw}")
    try:
        resolved.relative_to(root)
    except ValueError:
        return ScopeDecision(False, "Le binaire doit se trouver dans le dossier du projet.")
    if not resolved.is_file():
        return ScopeDecision(False, "La cible doit être un fichier.")
    warnings = ["Analyse statique uniquement : le binaire n'est jamais exécuté."]
    return ScopeDecision(True, "Binaire autorisé dans le périmètre du projet.", True, "", warnings)


def resolve_public_host(host: str) -> list[str]:
    """Résolution informative, sans requête réseau sortante."""
    try:
        infos = socket.getaddrinfo(host, None)
        return sorted({info[4][0] for info in infos})
    except OSError:
        return []


def command_line() -> str:
    return " ".join(os.environ.get("COMSPEC", "cmd.exe").split())
