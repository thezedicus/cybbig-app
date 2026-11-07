from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .. import db
from ..config import APP_NAME, APP_VERSION, CONSENT_VERSION
from ..services import ai, resources, scheduler, scope
from ..utils import now_iso

router = APIRouter(tags=["système"])

LEGAL_TEXT = """CADRE D'UTILISATION DE CYBBIG

Cybbig est un outil de cybersécurité défensive destiné à la recherche, à l'audit et à la validation de protections sur des systèmes que vous possédez ou pour lesquels vous disposez d'une autorisation écrite.

1. Autorisation. Vous devez obtenir l'autorisation de la personne ou de l'organisation compétente avant tout test sur un système tiers. Le présent consentement n'est pas une autorisation juridique et ne couvre aucune cible tierce.
2. Portée. Les analyses Web de Cybbig sont passives : aucune charge d'exploitation, aucun contournement d'authentification, aucune extraction de données privées. Les analyses PHP sont statiques : le code n'est jamais exécuté.
3. Données. Les résultats restent sur votre machine. Les secrets détectés sont masqués. Vous êtes responsable de la conservation et de la protection des rapports.
4. Cadre légal. En France, les atteintes aux systèmes de traitement automatisé de données sont notamment réprimées par les articles 323-1 et suivants du Code pénal. D'autres juridictions appliquent leurs propres règles.
5. Laboratoire. Les scénarios fournis sont pédagogiques et doivent être exécutés dans un environnement isolé, avec des données fictives. Ne déployez jamais les exemples vulnérables.
6. Limites. Une analyse ne prouve pas l'absence de vulnérabilité. Les résultats doivent être revus et validés. Cybbig n'est ni une certification, ni un conseil juridique.
7. Utilisation interdite. Toute atteinte à un système sans autorisation, extraction de données personnelles, perturbation de service ou contournement de protection est interdite.

En acceptant, vous confirmez avoir lu ces conditions et utiliser Cybbig de manière légale, éthique et autorisée.
"""


class ConsentPayload(BaseModel):
    accepted: bool
    user_name: str = Field(default="", max_length=200)
    organization: str = Field(default="", max_length=200)
    purpose: str = Field(default="", max_length=1000)


class SettingsPayload(BaseModel):
    values: dict[str, Any]


@router.get("/health")
def health() -> dict[str, Any]:
    db_health = db.health_db()
    return {
        "app": APP_NAME,
        "version": APP_VERSION,
        "status": "ok",
        "time": now_iso(),
        "database": db_health,
        "consent": scope.consent_status()["accepted"],
        "scheduler": scheduler.status(),
        "engines": ["php", "web", "api", "checkout", "intel", "lab", "assistant"],
    }


@router.get("/consent")
def get_consent() -> dict[str, Any]:
    status = scope.consent_status()
    return {
        **status,
        "text": LEGAL_TEXT,
        "text_hash": hashlib.sha256(LEGAL_TEXT.encode("utf-8")).hexdigest(),
        "version": CONSENT_VERSION,
    }


@router.post("/consent")
def accept_consent(payload: ConsentPayload) -> dict[str, Any]:
    if not payload.accepted:
        raise HTTPException(status_code=400, detail="Le consentement doit être accepté pour utiliser Cybbig.")
    digest = hashlib.sha256(LEGAL_TEXT.encode("utf-8")).hexdigest()
    db.execute(
        """INSERT INTO consent(id,version,accepted_at,user_name,organization,purpose,text_hash)
           VALUES(1,?,?,?,?,?,?)
           ON CONFLICT(id) DO UPDATE SET version=excluded.version, accepted_at=excluded.accepted_at,
             user_name=excluded.user_name, organization=excluded.organization, purpose=excluded.purpose,
             text_hash=excluded.text_hash""",
        (CONSENT_VERSION, now_iso(), payload.user_name[:200], payload.organization[:200], payload.purpose[:1000], digest),
    )
    db.audit("consent_accepted", {"version": CONSENT_VERSION, "organization": payload.organization})
    return {"ok": True, "version": CONSENT_VERSION, "accepted_at": now_iso()}


UI_VALIDATORS = {
    "ui_accent": lambda v: re.fullmatch(r"#[0-9a-fA-F]{6}", v) is not None,
    "ui_font_size": lambda v: v.isdigit() and 12 <= int(v) <= 20,
    "ui_radius": lambda v: v.isdigit() and 2 <= int(v) <= 24,
    "ui_hidden_nav": lambda v: len(v) <= 400 and re.fullmatch(r"[a-z/,\-]*", v) is not None,
    "training_auto_hours": lambda v: v.isdigit() and 1 <= int(v) <= 720,
    "ai_provider": lambda v: v in {"auto", "local", "cloud", "training"},
    "ui_custom_css": lambda v: len(v) <= 20000 and "</style" not in v.lower() and "@import" not in v.lower(),
}
SECRET_SETTINGS = {"nvd_api_key", "ollama_api_key", "ollama_cloud_key", "brave_search_key"}
SETTINGS_WHITELIST = {
    "language", "theme", "intel_nvd_days", "intel_max_items", "ollama_url", "ollama_model",
    "max_files", "max_pages", "allow_private_targets", "data_retention_days", "user_agent",
    "nvd_api_key", "ollama_api_key", "brave_search_key", "trusted_script_domains", "probe_exposed_files",
    "enable_external_tools", "max_exposed_paths", "intel_watchlist", "ai_report_summary", "ai_auto", "ai_boost",
    "ai_provider", "ai_allow_cloud", "ollama_cloud_url", "ollama_cloud_key", "ollama_cloud_model", "ai_warmup", "ai_browse", "ai_search",
    "perf_profile", "perf_num_thread", "web_respect_robots", "ai_model_code", "ai_model_code_local", "ai_auto_route", "ai_model_chat", "ai_model_reason",
    "ui_accent", "ui_font_size", "ui_radius", "ui_hidden_nav", "ui_custom_css", "training_auto", "training_auto_hours", "training_auto_approve", "ai_auto_scans", "ai_auto_triage", "ai_auto_intel", "ai_auto_dashboard", "ai_agents", "osv_online",
}


@router.get("/settings")
def get_settings() -> dict[str, Any]:
    rows = db.fetch_all("SELECT key,value FROM settings ORDER BY key")
    values = {r["key"]: r["value"] for r in rows if not r["key"].startswith("admin_")}
    if values.get("nvd_api_key"):
        values["nvd_api_key"] = "********"
    for secret in SECRET_SETTINGS:
        if values.get(secret):
            values[secret] = "********"
    return {"values": values, "editable": sorted(SETTINGS_WHITELIST)}


@router.put("/settings")
def update_settings(payload: SettingsPayload) -> dict[str, Any]:
    # Les clés hors liste blanche se modifient depuis l'onglet Administration (session requise).
    changed = {}
    # Une clé API n'est jamais envoyée vers une adresse que l'utilisateur n'a pas validée avec elle :
    # changer l'adresse d'un serveur sans ressaisir sa clé efface la clé enregistrée.
    for url_key, secret_key, default_url in (("ollama_cloud_url", "ollama_cloud_key", ai.CLOUD_DEFAULT_URL),
                                              ("ollama_url", "ollama_api_key", "http://127.0.0.1:11434")):
        current_url = str(db.get_setting(url_key, default_url) or default_url).rstrip("/")
        if url_key in payload.values and (str(payload.values[url_key]).strip().rstrip("/") or default_url) != current_url:
            if str(payload.values.get(secret_key, "********")) == "********":
                db.set_setting(secret_key, "")
                changed[secret_key] = "effacée (adresse modifiée)"
    for key, value in payload.values.items():
        if key not in SETTINGS_WHITELIST:
            continue
        if key in SECRET_SETTINGS and str(value) == "********":
            continue
        string = str(value).strip()
        if key in UI_VALIDATORS and not UI_VALIDATORS[key](string):
            continue  # valeur d'apparence invalide : ignorée plutôt que d'abîmer l'interface
        db.set_setting(key, string)
        changed[key] = "********" if key in SECRET_SETTINGS else string
    db.audit("settings_updated", {"keys": list(changed.keys())})
    ai.invalidate_status()  # nouveau serveur, nouvelle clé ou nouveau mode : l'état en cache n'est plus valable
    resources.reset_cache()
    return {"ok": True, "changed": changed}


@router.get("/audit")
def list_audit(limit: int = 100) -> dict[str, Any]:
    rows = db.fetch_all("SELECT * FROM audit_log ORDER BY id DESC LIMIT ?", (min(500, max(1, limit)),))
    return {"items": rows}


@router.get("/ollama/detect")
def detect_ollama() -> dict[str, Any]:
    candidates = [
        Path.home() / "AppData" / "Local" / "Programs" / "Ollama" / "ollama.exe",
        Path("C:/Program Files/Ollama/ollama.exe"),
    ]
    found = [str(p) for p in candidates if p.exists()]
    return {"installed": bool(found), "paths": found}

@router.post("/ollama/install")
def install_ollama() -> dict[str, Any]:
    script = Path(__file__).resolve().parents[3] / "scripts" / "install-ollama.ps1"
    if not script.exists():
        raise HTTPException(status_code=404, detail="Script d'installation introuvable.")
    try:
        subprocess.Popen(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script)],
            creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0),
        )
    except OSError as exc:
        raise HTTPException(status_code=500, detail=f"Impossible de lancer l'installateur : {exc}") from exc
    return {"started": True, "message": "Installateur Ollama lancé dans une fenêtre PowerShell."}
@router.get("/engines")
def engines() -> dict[str, Any]:
    return {
        "engines": [
            {"id": "php", "name": "Scanner PHP", "mode": "statique", "status": "ready",
             "capabilities": ["règles", "taint heuristique", "secrets", "configuration", "Composer/OSV"]},
            {"id": "web", "name": "Analyse Web", "mode": "passive", "status": "ready",
             "capabilities": ["en-têtes", "TLS", "cookies", "formulaires", "scripts", "fichiers exposés"]},
            {"id": "api", "name": "Audit API", "mode": "spécification", "status": "ready",
             "capabilities": ["OpenAPI", "authentification", "BOLA (revue)", "idempotence"]},
            {"id": "checkout", "name": "Intégrité checkout", "mode": "passif", "status": "ready",
             "capabilities": ["scripts", "SRI", "SVG", "WebSocket", "indicateurs skimmer"]},
            {"id": "intel", "name": "Threat Intelligence", "mode": "collecte", "status": "ready",
             "capabilities": ["CISA KEV", "NVD", "CERT-FR", "PHP", "OSV à la demande"]},
        ],
        "limitations": [
            "Aucun exploit, fuzzing ou contournement d'authentification.",
            "Aucune exécution du code analysé.",
            "Les résultats sont heuristiques et nécessitent une validation.",
        ],
    }
