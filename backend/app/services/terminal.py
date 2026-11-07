from __future__ import annotations

import json
import subprocess
import time
import uuid
from pathlib import Path
from typing import Any

from .. import db
from ..utils import truncate

ALLOWED_EXECUTABLES = {
    "python", "python3", "pip", "npm", "node", "pytest", "git", "ls", "dir",
    "cat", "type", "echo", "pwd", "whoami",
}
WORKING_DIRS = {"root", "backend", "frontend"}


def _root() -> Path:
    return Path(__file__).resolve().parents[3]


def _resolve_cwd(working_dir: str) -> Path:
    root = _root()
    if working_dir in {"backend", "frontend"} and (root / working_dir).is_dir():
        return root / working_dir
    # Version installée : le code source du frontend n'est pas embarqué.
    return root


def list_guardrails() -> list[dict[str, Any]]:
    rows = db.fetch_all("SELECT * FROM terminal_guardrails ORDER BY created_at DESC")
    for row in rows:
        row["command"] = db.json_loads(row.get("command"), [])
        row["enabled"] = bool(row.get("enabled"))
    return rows


def add_guardrail(name: str, command: list[str], working_dir: str = "root", description: str = "", enabled: bool = True) -> dict[str, Any]:
    name = (name or "").strip()[:120]
    if not name:
        raise ValueError("Le nom est obligatoire.")
    if not isinstance(command, list) or not command or not all(isinstance(part, str) and part.strip() for part in command):
        raise ValueError("La commande doit être une liste d'arguments non vides.")
    executable = Path(command[0]).name.lower()
    if executable not in ALLOWED_EXECUTABLES:
        raise ValueError(f"Exécutable non autorisé : {executable}. Garde-fou actif.")
    if working_dir not in WORKING_DIRS:
        raise ValueError("Répertoire de travail invalide.")
    guardrail_id = str(uuid.uuid4())
    db.execute(
        """INSERT INTO terminal_guardrails(id,name,command,working_dir,description,enabled,created_at)
           VALUES(?,?,?,?,?,?,?)""",
        (guardrail_id, name, db.json_dumps(command), working_dir, description[:500], 1 if enabled else 0, db.utcnow()),
    )
    return {"id": guardrail_id, "name": name, "command": command, "working_dir": working_dir, "description": description, "enabled": enabled}


def remove_guardrail(guardrail_id: str) -> None:
    db.execute("DELETE FROM terminal_guardrails WHERE id=?", (guardrail_id,))


def set_enabled(guardrail_id: str, enabled: bool) -> None:
    db.execute("UPDATE terminal_guardrails SET enabled=? WHERE id=?", (1 if enabled else 0, guardrail_id))


def list_runs(limit: int = 30) -> list[dict[str, Any]]:
    rows = db.fetch_all("SELECT * FROM terminal_runs ORDER BY started_at DESC LIMIT ?", (min(100, max(1, limit)),))
    for row in rows:
        row["command"] = db.json_loads(row.get("command"), [])
    return rows


def run_guardrail(guardrail_id: str) -> dict[str, Any]:
    row = db.fetch_one("SELECT * FROM terminal_guardrails WHERE id=?", (guardrail_id,))
    if not row:
        raise ValueError("Garde-fou introuvable.")
    if not row.get("enabled"):
        raise ValueError("Ce garde-fou est désactivé.")
    command = db.json_loads(row.get("command"), [])
    if not command:
        raise ValueError("Commande invalide.")
    working_dir = row.get("working_dir") or "root"
    if working_dir not in WORKING_DIRS:
        working_dir = "root"
    cwd = _resolve_cwd(working_dir)
    run_id = str(uuid.uuid4())
    started = db.utcnow()
    db.execute(
        """INSERT INTO terminal_runs(id,guardrail_id,command,working_dir,started_at,status)
           VALUES(?,?,?,?,?,?)""",
        (run_id, guardrail_id, db.json_dumps(command), working_dir, started, "running"),
    )
    try:
        completed = subprocess.run(
            command, cwd=str(cwd), capture_output=True, text=True,
            timeout=120, check=False, shell=False,
        )
        status = "completed" if completed.returncode == 0 else "failed"
        exit_code = completed.returncode
        stdout = truncate(completed.stdout or "", 20000)
        stderr = truncate(completed.stderr or "", 20000)
    except subprocess.TimeoutExpired as exc:
        status = "timeout"
        exit_code = 124
        stdout = truncate((exc.stdout or "") if isinstance(exc.stdout, str) else "", 20000)
        stderr = truncate((exc.stderr or "") if isinstance(exc.stderr, str) else "Délai dépassé (120 s).", 20000)
    except (OSError, Exception) as exc:  # noqa: BLE001
        status = "error"
        exit_code = 127
        stdout = ""
        stderr = truncate(str(exc), 20000)
    finished = db.utcnow()
    db.execute(
        """UPDATE terminal_runs SET finished_at=?, exit_code=?, stdout=?, stderr=?, status=? WHERE id=?""",
        (finished, exit_code, stdout, stderr, status, run_id),
    )
    db.audit("terminal_run", {"run_id": run_id, "guardrail_id": guardrail_id, "command": command, "status": status, "exit_code": exit_code})
    return {
        "id": run_id,
        "guardrail_id": guardrail_id,
        "command": command,
        "working_dir": working_dir,
        "started_at": started,
        "finished_at": finished,
        "exit_code": exit_code,
        "stdout": stdout,
        "stderr": stderr,
        "status": status,
    }