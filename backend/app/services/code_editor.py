"""Éditeur de code du propriétaire : lecture et modification de tout le code du logiciel.

La racine est le dossier de l'application (sources en développement, resources\\app une fois installé).
Chaque écriture ou suppression sauvegarde d'abord l'ancienne version dans data/code-backups,
ce qui permet de revenir en arrière. Les fichiers Python sont vérifiés avant enregistrement.
"""
from __future__ import annotations

import os
import shutil
import threading
from datetime import datetime
from pathlib import Path
from typing import Any

from .. import db
from ..config import DATA_DIR, PROJECT_DIR

ROOT = PROJECT_DIR.resolve()
BACKUPS = DATA_DIR / "code-backups"
HIDDEN_DIRS = {".venv", "node_modules", "__pycache__", ".git", ".pytest_cache", "data", "python"}
MAX_EDIT_BYTES = 3_000_000
RESTART_EXIT_CODE = 75  # Electron relance le service quand il s'arrête avec ce code.


def _resolve(rel: str) -> Path:
    path = (ROOT / (rel or "").replace("\\", "/").lstrip("/")).resolve()
    if path != ROOT and ROOT not in path.parents:
        raise ValueError("Chemin hors du dossier du logiciel.")
    return path


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix() if path != ROOT else ""


def tree(rel: str = "") -> dict[str, Any]:
    base = _resolve(rel)
    if not base.is_dir():
        raise ValueError("Dossier introuvable.")
    entries = []
    for child in sorted(base.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
        if child.name in HIDDEN_DIRS and child.is_dir():
            continue
        entries.append({
            "name": child.name, "path": _rel(child), "dir": child.is_dir(),
            "size": child.stat().st_size if child.is_file() else None,
        })
    return {"root": str(ROOT), "path": _rel(base), "entries": entries}


def read(rel: str) -> dict[str, Any]:
    path = _resolve(rel)
    if not path.is_file():
        raise ValueError("Fichier introuvable.")
    size = path.stat().st_size
    if size > MAX_EDIT_BYTES:
        return {"path": rel, "size": size, "binary": True, "content": "", "reason": "Fichier trop volumineux pour l'éditeur."}
    raw = path.read_bytes()
    try:
        content = raw.decode("utf-8")
    except UnicodeDecodeError:
        return {"path": rel, "size": size, "binary": True, "content": "", "reason": "Fichier binaire."}
    return {"path": rel, "size": size, "binary": False, "content": content, "modified": path.stat().st_mtime}


def _backup(path: Path) -> str | None:
    if not path.exists():
        return None
    # Microsecondes : deux sauvegardes rapprochées ne doivent jamais partager le même dossier.
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    target = BACKUPS / stamp / _rel(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, target)
    return stamp


def _check_python(rel: str, content: str) -> None:
    if rel.endswith(".py"):
        try:
            compile(content, rel, "exec")
        except SyntaxError as exc:
            raise ValueError(f"Erreur de syntaxe Python ligne {exc.lineno} : {exc.msg}") from exc


def write(rel: str, content: str, force: bool = False, create: bool = False) -> dict[str, Any]:
    path = _resolve(rel)
    if path.is_dir():
        raise ValueError("C'est un dossier.")
    if create and path.exists():
        raise ValueError("Ce fichier existe déjà.")
    if not create and not path.exists():
        raise ValueError("Fichier introuvable.")
    if not force:
        _check_python(rel, content)
    stamp = _backup(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # newline="" : conserve les fins de ligne telles qu'envoyées par l'éditeur.
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(content)
    db.audit("code_write", {"path": rel, "bytes": len(content.encode("utf-8")), "backup": stamp, "created": create}, actor="admin")
    return {"path": rel, "backup": stamp, "needs": _needs(rel)}


def delete(rel: str) -> dict[str, Any]:
    path = _resolve(rel)
    if not path.is_file():
        raise ValueError("Seuls les fichiers peuvent être supprimés.")
    stamp = _backup(path)
    path.unlink()
    db.audit("code_delete", {"path": rel, "backup": stamp}, actor="admin")
    return {"path": rel, "backup": stamp, "needs": _needs(rel)}


def _needs(rel: str) -> str:
    """Ce qu'il faut faire pour que la modification prenne effet."""
    if rel.startswith("backend/"):
        return "restart"
    if rel.startswith("frontend/") and not rel.startswith("frontend/dist/"):
        return "rebuild"
    if rel.startswith("frontend/dist/"):
        return "reload"
    if rel.startswith("desktop/"):
        return "relaunch"
    return "none"


def backups(limit: int = 100) -> list[dict[str, Any]]:
    if not BACKUPS.exists():
        return []
    items = []
    for stamp_dir in sorted(BACKUPS.iterdir(), reverse=True):
        if not stamp_dir.is_dir():
            continue
        for file in stamp_dir.rglob("*"):
            if file.is_file():
                items.append({"backup": stamp_dir.name, "path": file.relative_to(stamp_dir).as_posix(), "size": file.stat().st_size})
        if len(items) >= limit:
            break
    return items[:limit]


def restore(stamp: str, rel: str) -> dict[str, Any]:
    source = (BACKUPS / Path(stamp).name / rel).resolve()
    if BACKUPS.resolve() not in source.parents or not source.is_file():
        raise ValueError("Sauvegarde introuvable.")
    path = _resolve(rel)
    current = _backup(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, path)
    db.audit("code_restore", {"path": rel, "from": stamp, "backup_of_current": current}, actor="admin")
    return {"path": rel, "restored_from": stamp, "needs": _needs(rel)}


def schedule_restart() -> None:
    """Arrête le service après la réponse HTTP ; Electron le relance avec le code modifié."""
    db.audit("service_restart", {}, actor="admin")
    threading.Timer(0.8, os._exit, [RESTART_EXIT_CODE]).start()
