from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets
import sqlite3
import subprocess
import threading
import time
import uuid
from pathlib import Path
from typing import Any

from .. import db
from ..config import DATA_DIR, DB_PATH, PROJECT_DIR
from ..utils import truncate
from . import owner

# Aucun identifiant administrateur n'est livré : l'administration est activée par le
# propriétaire seul, via une signature Ed25519 (voir services/owner.py et docs/ADMIN.md).
MIN_IDENTIFIER_LENGTH = 4
MIN_PASSWORD_LENGTH = 10

PBKDF2_ITERATIONS = 240_000
SESSION_TTL_SECONDS = 30 * 60
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_SECONDS = 5 * 60
EXEC_TIMEOUT_SECONDS = 120
OUTPUT_LIMIT = 40_000
BACKUPS_DIR = DATA_DIR / "backups"

SECRET_KEYS = {"admin_identifier_hash", "admin_password_hash", "install_id"}
CWD_MARKER = "__CYBBIG_CWD__"

SHELLS = {
    # -EncodedCommand (UTF-16LE en base64) : scripts multilignes, guillemets et accents transmis intacts.
    "powershell": lambda code: ["powershell", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-EncodedCommand",
                                base64.b64encode(("[Console]::OutputEncoding = [Text.Encoding]::UTF8\n" + code).encode("utf-16-le")).decode()],
    "cmd": lambda code: ["cmd", "/d", "/v:on", "/s", "/c", code],
    "python": lambda code: [os.environ.get("CYBBIG_PYTHON") or _python(), "-c", code],
}

_sessions: dict[str, float] = {}
_failures = {"count": 0, "locked_until": 0.0}
_lock = threading.Lock()


def _python() -> str:
    import sys

    return sys.executable


def _decode_captured(value: str | bytes | None) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value or ""


def _hash(value: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", value.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt.hex()}${digest.hex()}"


def _verify(value: str, stored: str | None) -> bool:
    try:
        _, iterations, salt_hex, digest_hex = (stored or "").split("$")
        digest = hashlib.pbkdf2_hmac("sha256", value.encode("utf-8"), bytes.fromhex(salt_hex), int(iterations))
        return hmac.compare_digest(digest.hex(), digest_hex)
    except (ValueError, TypeError):
        return False


def ensure_credentials() -> None:
    """Prépare l'identifiant d'installation ; ne crée JAMAIS d'identifiants par défaut."""
    owner.install_id()


def is_configured() -> bool:
    return bool(db.get_setting("admin_password_hash")) and bool(db.get_setting("admin_identifier_hash"))


def _validate(identifier: str, password: str) -> str:
    identifier = identifier.strip()
    if len(identifier) < MIN_IDENTIFIER_LENGTH:
        raise ValueError(f"L'identifiant doit contenir au moins {MIN_IDENTIFIER_LENGTH} caractères.")
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"Le mot de passe doit contenir au moins {MIN_PASSWORD_LENGTH} caractères.")
    return identifier


def owner_activate(challenge: str, signature: str, identifier: str, password: str) -> None:
    """Crée (ou réinitialise) les identifiants : exige la signature du propriétaire."""
    with _lock:
        now = time.time()
        if _failures["locked_until"] > now:
            raise PermissionError(f"Trop de tentatives. Réessayez dans {int(_failures['locked_until'] - now)} s.")
    identifier = _validate(identifier, password)
    if not owner.consume(challenge, signature):
        with _lock:
            _failures["count"] += 1
            if _failures["count"] >= MAX_FAILED_ATTEMPTS:
                _failures["locked_until"] = time.time() + LOCKOUT_SECONDS
                _failures["count"] = 0
        db.audit("admin_owner_activation_failed", {}, actor="admin")
        raise PermissionError("Signature propriétaire invalide ou défi expiré. Générez un nouveau défi.")
    db.set_setting("admin_identifier_hash", _hash(identifier))
    db.set_setting("admin_password_hash", _hash(password))
    db.set_setting("admin_must_change", "false")
    with _lock:
        _failures["count"] = 0
        _sessions.clear()
    db.audit("admin_owner_activated", {}, actor="admin")


def must_change() -> bool:
    return str(db.get_setting("admin_must_change", "false")).lower() == "true"


# --- Sessions -----------------------------------------------------------------

def login(identifier: str, password: str) -> dict[str, Any]:
    if not is_configured():
        raise PermissionError("Administration non activée sur ce poste : activation propriétaire requise.")
    with _lock:
        now = time.time()
        if _failures["locked_until"] > now:
            wait = int(_failures["locked_until"] - now)
            raise PermissionError(f"Trop de tentatives. Réessayez dans {wait} s.")
        ok_id = _verify(identifier, db.get_setting("admin_identifier_hash"))
        ok_pw = _verify(password, db.get_setting("admin_password_hash"))
        if not (ok_id and ok_pw):
            _failures["count"] += 1
            if _failures["count"] >= MAX_FAILED_ATTEMPTS:
                _failures["locked_until"] = now + LOCKOUT_SECONDS
                _failures["count"] = 0
            db.audit("admin_login_failed", {}, actor="admin")
            raise PermissionError("Identifiant ou mot de passe incorrect.")
        _failures["count"] = 0
        token = secrets.token_urlsafe(32)
        _sessions[token] = now + SESSION_TTL_SECONDS
    db.audit("admin_login", {}, actor="admin")
    return {"token": token, "expires_in": SESSION_TTL_SECONDS, "must_change": must_change()}


def check_session(token: str | None) -> bool:
    if not token:
        return False
    with _lock:
        expires = _sessions.get(token)
        now = time.time()
        if not expires or expires < now:
            _sessions.pop(token, None)
            return False
        _sessions[token] = now + SESSION_TTL_SECONDS
        return True


def logout(token: str | None) -> None:
    with _lock:
        _sessions.pop(token or "", None)
    db.audit("admin_logout", {}, actor="admin")


def change_credentials(current_password: str, new_identifier: str, new_password: str) -> None:
    if not _verify(current_password, db.get_setting("admin_password_hash")):
        raise PermissionError("Mot de passe actuel incorrect.")
    new_identifier = _validate(new_identifier, new_password)
    db.set_setting("admin_identifier_hash", _hash(new_identifier))
    db.set_setting("admin_password_hash", _hash(new_password))
    db.set_setting("admin_must_change", "false")
    with _lock:
        _sessions.clear()
    db.audit("admin_credentials_changed", {}, actor="admin")


# --- Configuration ------------------------------------------------------------

def list_settings() -> dict[str, str]:
    rows = db.fetch_all("SELECT key,value FROM settings ORDER BY key")
    return {r["key"]: r["value"] for r in rows if r["key"] not in SECRET_KEYS}


def update_settings(values: dict[str, Any]) -> list[str]:
    changed = []
    for key, value in values.items():
        key = str(key).strip()[:120]
        if not key or key in SECRET_KEYS:
            continue
        db.set_setting(key, str(value))
        changed.append(key)
    db.audit("admin_settings_updated", {"keys": changed}, actor="admin")
    return changed


def delete_setting(key: str) -> None:
    if key in SECRET_KEYS or key == "admin_must_change":
        raise ValueError("Cette clé est protégée.")
    db.execute("DELETE FROM settings WHERE key=?", (key,))
    db.audit("admin_setting_deleted", {"key": key}, actor="admin")


# --- Vue d'ensemble -----------------------------------------------------------

def _dir_size(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())


def overview() -> dict[str, Any]:
    tables = db.fetch_all("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name NOT LIKE '%_fts%' ORDER BY name")
    counts = {}
    for table in tables:
        name = table["name"]
        row = db.fetch_one(f'SELECT COUNT(*) AS c FROM "{name}"')
        counts[name] = row["c"] if row else 0
    return {
        "tables": counts,
        "database_bytes": DB_PATH.stat().st_size if DB_PATH.exists() else 0,
        "data_bytes": _dir_size(DATA_DIR),
        "data_dir": str(DATA_DIR),
        "project_dir": str(PROJECT_DIR),
        "sessions": len(_sessions),
        "must_change": must_change(),
    }


# --- Terminal libre -----------------------------------------------------------

def _resolve_cwd(cwd: str) -> Path:
    if cwd in {"", "root"}:
        return PROJECT_DIR
    if cwd in {"backend", "frontend"}:
        return PROJECT_DIR / cwd
    path = Path(cwd).expanduser()
    if not path.is_absolute():
        path = PROJECT_DIR / path
    if not path.is_dir():
        raise ValueError(f"Répertoire introuvable : {path}")
    return path.resolve()


def execute(code: str, shell: str = "powershell", cwd: str = "root", timeout: int = EXEC_TIMEOUT_SECONDS, stdin: str = "") -> dict[str, Any]:
    if shell not in SHELLS:
        raise ValueError("Interpréteur inconnu (powershell, cmd, python).")
    if not code.strip():
        raise ValueError("Commande vide.")
    workdir = _resolve_cwd(cwd)
    run_id = str(uuid.uuid4())
    started = db.utcnow()
    clock = time.monotonic()
    # Le répertoire final est renvoyé pour que « cd » persiste entre deux commandes.
    wrapped = code
    # Le statut de la commande utilisateur est conservé avant d'afficher le répertoire.
    if shell == "powershell":
        wrapped = (
            f"$global:LASTEXITCODE = 0\n{code}\n$__ok = $?; $__rc = $global:LASTEXITCODE\n"
            f"Write-Output ('{CWD_MARKER}' + (Get-Location).Path)\n"
            "if ($__rc) { exit $__rc } elseif (-not $__ok) { exit 1 }"
        )
    elif shell == "cmd":
        wrapped = f'chcp 65001>nul & {code} & set "__RC=!ERRORLEVEL!" & echo {CWD_MARKER}!CD! & exit /b !__RC!'
    elif shell == "python":
        # L'exécution en bloc garde le mode script tout en renvoyant le répertoire final,
        # y compris si le code lève une exception ou appelle sys.exit().
        wrapped = (
            "import os as __cybbig_os\n"
            "try:\n"
            f"    exec(compile({code!r}, '<cybbig-terminal>', 'exec'), globals())\n"
            "finally:\n"
            f"    print({(CWD_MARKER)!r} + __cybbig_os.getcwd())\n"
        )
    try:
        completed = subprocess.run(
            SHELLS[shell](wrapped), cwd=str(workdir), capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=timeout, check=False,
            input=stdin,
            env={**os.environ, "PYTHONUTF8": "1"} if shell == "python" else None,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        exit_code = completed.returncode
        status = "completed" if exit_code == 0 else "failed"
        stdout, stderr = completed.stdout or "", completed.stderr or ""
    except subprocess.TimeoutExpired as exc:
        exit_code, status = 124, "timeout"
        stdout = _decode_captured(exc.stdout)
        stderr = _decode_captured(exc.stderr)
        stderr = (stderr + "\n" if stderr else "") + f"Délai dépassé ({timeout} s)."
    except OSError as exc:
        exit_code, status, stdout, stderr = 127, "error", "", str(exc)
    cwd_after = str(workdir)
    if CWD_MARKER in stdout:
        head, _, tail = stdout.rpartition(CWD_MARKER)
        candidate = tail.strip().splitlines()[0] if tail.strip() else ""
        if candidate and Path(candidate).is_dir():
            cwd_after = candidate
        stdout = head.rstrip("\r\n") + ("\n" if head.strip() else "")
    stdout, stderr = truncate(stdout, OUTPUT_LIMIT), truncate(stderr, OUTPUT_LIMIT)
    finished = db.utcnow()
    db.execute(
        """INSERT INTO terminal_runs(id,guardrail_id,command,working_dir,started_at,finished_at,exit_code,stdout,stderr,status)
           VALUES(?,?,?,?,?,?,?,?,?,?)""",
        (run_id, f"admin:{shell}", db.json_dumps([code]), str(workdir), started, finished, exit_code, stdout, stderr, status),
    )
    db.audit("admin_exec", {"run_id": run_id, "shell": shell, "cwd": str(workdir), "code": truncate(code, 500), "exit_code": exit_code}, actor="admin")
    return {
        "id": run_id, "shell": shell, "cwd": str(workdir), "cwd_after": cwd_after, "code": code, "exit_code": exit_code,
        "status": status, "stdout": stdout, "stderr": stderr,
        "duration_ms": int((time.monotonic() - clock) * 1000), "started_at": started,
    }


def exec_history(limit: int = 50) -> list[dict[str, Any]]:
    rows = db.fetch_all(
        "SELECT * FROM terminal_runs WHERE guardrail_id LIKE 'admin:%' ORDER BY started_at DESC LIMIT ?",
        (min(200, max(1, limit)),),
    )
    for row in rows:
        row["code"] = (db.json_loads(row.pop("command"), [""]) or [""])[0]
        row["shell"] = row.pop("guardrail_id", "admin:").split(":", 1)[1]
    return rows


# --- Base de données ----------------------------------------------------------

def run_sql(sql: str, limit: int = 500) -> dict[str, Any]:
    sql = sql.strip()
    if not sql:
        raise ValueError("Requête vide.")
    with db.db_cursor() as conn:
        try:
            cur = conn.execute(sql)
        except sqlite3.Error as exc:
            raise ValueError(f"Erreur SQL : {exc}") from exc
        if cur.description:
            columns = [d[0] for d in cur.description]
            rows = [list(r) for r in cur.fetchmany(limit + 1)]
            result = {"columns": columns, "rows": rows[:limit], "truncated": len(rows) > limit, "rowcount": len(rows[:limit])}
        else:
            result = {"columns": [], "rows": [], "truncated": False, "rowcount": cur.rowcount}
    db.audit("admin_sql", {"sql": truncate(sql, 500)}, actor="admin")
    return result


def create_backup() -> dict[str, Any]:
    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    target = BACKUPS_DIR / f"cybbig-{time.strftime('%Y%m%d-%H%M%S')}.db"
    with db.db_cursor() as conn:
        dest = sqlite3.connect(target)
        try:
            conn.backup(dest)
        finally:
            dest.close()
    db.audit("admin_backup", {"file": target.name}, actor="admin")
    return {"name": target.name, "bytes": target.stat().st_size}


def list_backups() -> list[dict[str, Any]]:
    if not BACKUPS_DIR.exists():
        return []
    files = sorted(BACKUPS_DIR.glob("cybbig-*.db"), reverse=True)
    return [{"name": f.name, "bytes": f.stat().st_size, "modified": f.stat().st_mtime} for f in files]


def delete_backup(name: str) -> None:
    target = (BACKUPS_DIR / Path(name).name)
    if not target.exists() or target.suffix != ".db":
        raise ValueError("Sauvegarde introuvable.")
    target.unlink()
    db.audit("admin_backup_deleted", {"file": target.name}, actor="admin")


def backup_path(name: str) -> Path:
    target = BACKUPS_DIR / Path(name).name
    if not target.exists():
        raise ValueError("Sauvegarde introuvable.")
    return target
