from __future__ import annotations

import os
from pathlib import Path

APP_NAME = "Cybbig"
APP_VERSION = "0.4.0"
API_PREFIX = "/api"

BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = BACKEND_DIR.parent
DATA_DIR = Path(os.environ.get("CYBBIG_DATA_DIR", BACKEND_DIR / "data")).resolve()
REPORTS_DIR = DATA_DIR / "reports"
DB_PATH = Path(os.environ.get("CYBBIG_DB_PATH", DATA_DIR / "cybbig.db")).resolve()
SAMPLES_DIR = BACKEND_DIR / "samples"
FRONTEND_DIST = PROJECT_DIR / "frontend" / "dist"

HOST = "127.0.0.1"
PORT = int(os.environ.get("CYBBIG_PORT", "8765"))
USER_AGENT = "Cybbig-PassiveAudit/0.1 (+authorized-defensive-security)"
CONSENT_VERSION = "2026-10-31"

# Garde-fous globaux
MAX_FILE_BYTES = 2_000_000
MAX_HTTP_BYTES = 2_000_000
HTTP_TIMEOUT = 15
MAX_FILES_DEFAULT = 2500
MAX_PAGES_DEFAULT = 3
MAX_EXPOSED_PATHS = 24
REQUEST_DELAY_SECONDS = 0.35

SEVERITIES = ["critical", "high", "medium", "low", "info"]
SEVERITY_WEIGHT = {"critical": 10.0, "high": 6.5, "medium": 3.5, "low": 1.0, "info": 0.0}

SCAN_KINDS = {
    "php": "Analyse PHP",
    "web": "Analyse Web passive",
    "api": "Audit API (OpenAPI)",
    "checkout": "Intégrité checkout",
    "reverse": "Reverse engineering (Ghidra headless)",
}

# Confidentialité & accessibilité (TTS, proxy, VPN)
TTS_MAX_CHARS = int(os.environ.get("CYBBIG_TTS_MAX_CHARS", "20000"))
IP_ECHO_URL = os.environ.get("CYBBIG_IP_ECHO_URL", "https://api.ipify.org?format=json")
NET_CHECK_TIMEOUT = int(os.environ.get("CYBBIG_NET_CHECK_TIMEOUT", "12"))

# Reverse engineering — Ghidra headless (analyzeHeadless)
GHIDRA_HOME = Path(os.environ.get("CYBBIG_GHIDRA_HOME", r"C:\Tools\ghidra_12.1.4_PUBLIC"))
GHIDRA_TIMEOUT_SECONDS = int(os.environ.get("CYBBIG_GHIDRA_TIMEOUT", "600"))
GHIDRA_ANALYSIS_TIMEOUT = int(os.environ.get("CYBBIG_GHIDRA_ANALYSIS_TIMEOUT", "240"))
MAX_BINARY_BYTES = int(os.environ.get("CYBBIG_MAX_BINARY_BYTES", str(120_000_000)))

ACTIVITY_LEVELS = {
    "A": "Recherche documentaire",
    "B": "Simulation locale",
    "C": "Infrastructure contrôlée",
    "D": "Tiers autorisé",
    "E": "Impact potentiel (non implémenté)",
}


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
