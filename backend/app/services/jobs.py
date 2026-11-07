from __future__ import annotations

import threading
import traceback
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable

from .. import db
from ..utils import new_id, now_iso
from . import resources
from .base import ScanContext
from .scope import check_scan_scope

MAX_WORKERS = resources.recommended_workers("scans")  # 3 sur 4 cœurs physiques, jusqu'à 8
_executor = ThreadPoolExecutor(max_workers=MAX_WORKERS, thread_name_prefix="cybbig-scan")
_cancel_events: dict[str, threading.Event] = {}
_lock = threading.Lock()
_active: dict[str, Any] = {}


def _load_scan(scan_id: str) -> tuple[dict | None, dict | None]:
    scan = db.fetch_one("SELECT * FROM scans WHERE id=?", (scan_id,))
    if not scan:
        return None, None
    project = db.fetch_one("SELECT * FROM projects WHERE id=?", (scan["project_id"],))
    return scan, project


def create_scan(project_id: str, kind: str, target: str = "", config: dict | None = None) -> dict[str, Any]:
    scan_id = new_id("scan")
    now = now_iso()
    db.execute(
        """INSERT INTO scans(id,project_id,kind,mode,target,status,progress,message,config_json,summary_json,created_at)
           VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
        (
            scan_id, project_id, kind, "passive", target[:2000], "queued", 0,
            "En attente d'exécution", db.json_dumps(config or {}), "{}", now,
        ),
    )
    return db.fetch_one("SELECT * FROM scans WHERE id=?", (scan_id,)) or {}


def start_scan(scan_id: str) -> None:
    scan, project = _load_scan(scan_id)
    if not scan or not project:
        return
    if scan["status"] in {"running", "queued"} and scan_id in _active:
        return
    event = threading.Event()
    with _lock:
        _cancel_events[scan_id] = event
    _executor.submit(_run_scan, scan_id, event)


def _run_scan(scan_id: str, cancel_event: threading.Event) -> None:
    scan, project = _load_scan(scan_id)
    if not scan or not project:
        return
    _active[scan_id] = threading.current_thread()
    try:
        # Revalidation du périmètre au moment de l'exécution (pas seulement à la création).
        decision = check_scan_scope(project, scan["kind"], scan["target"])
        if not decision.allowed:
            db.execute(
                "UPDATE scans SET status='blocked', error=?, finished_at=?, message=? WHERE id=?",
                (decision.reason, now_iso(), "Périmètre refusé", scan_id),
            )
            return
        db.execute(
            "UPDATE scans SET status='running', started_at=?, progress=1, message=? WHERE id=?",
            (now_iso(), "Initialisation du moteur", scan_id),
        )
        config = db.json_loads(scan.get("config_json"), {}) or {}
        ctx = ScanContext(scan=scan, project=project, config=config, cancel_event=cancel_event)
        from .engines import dispatch

        dispatch(scan["kind"], ctx)
        if cancel_event.is_set():
            ctx.persist()
            db.execute(
                "UPDATE scans SET status='cancelled', finished_at=?, message=? WHERE id=?",
                (now_iso(), "Analyse annulée par l'utilisateur", scan_id),
            )
            return
        ctx.persist()
        summary = ctx.summary()
        db.execute(
            """UPDATE scans SET status='completed', progress=100, message=?,
               summary_json=?, finished_at=? WHERE id=?""",
            ("Analyse terminée", db.json_dumps(summary), now_iso(), scan_id),
        )
        from . import ai_worker  # import tardif : évite un cycle

        ai_worker.on_scan_completed(scan_id)
        if summary.get("findings"):
            db.execute(
                """INSERT INTO alerts(id,project_id,source,severity,title,message,link,created_at)
                   VALUES(?,?,?,?,?,?,?,?)""",
                (
                    new_id("alert"), project["id"], scan["kind"],
                    _top_severity(summary.get("severity", {})),
                    f"Analyse {scan['kind']} terminée : {summary['findings']} résultat(s)",
                    project.get("name", ""), f"/scans/{scan_id}", now_iso(),
                ),
            )
    except Exception as exc:  # noqa: BLE001
        detail = f"{type(exc).__name__}: {exc}"
        db.execute(
            "UPDATE scans SET status='failed', error=?, finished_at=?, message=? WHERE id=?",
            (detail[:2000], now_iso(), "Échec de l'analyse", scan_id),
        )
        db.audit("scan_failed", {"scan_id": scan_id, "error": detail, "trace": traceback.format_exc()[-3000:]})
    finally:
        _active.pop(scan_id, None)
        with _lock:
            _cancel_events.pop(scan_id, None)


def _top_severity(counts: dict[str, int]) -> str:
    for sev in ("critical", "high", "medium", "low", "info"):
        if counts.get(sev):
            return sev
    return "info"


def cancel_scan(scan_id: str) -> bool:
    with _lock:
        event = _cancel_events.get(scan_id)
    if event:
        event.set()
        db.execute("UPDATE scans SET message=? WHERE id=?", ("Annulation demandée…", scan_id))
        return True
    scan = db.fetch_one("SELECT status FROM scans WHERE id=?", (scan_id,))
    if scan and scan["status"] == "queued":
        db.execute("UPDATE scans SET status='cancelled', finished_at=? WHERE id=?", (now_iso(), scan_id))
        return True
    return False


def active_scan_ids() -> list[str]:
    with _lock:
        return list(_active.keys())


def recover_stale_scans() -> None:
    """Marque les scans interrompus par un arrêt du processus."""
    db.execute(
        """UPDATE scans SET status='failed', message='Interrompu par l''arrêt de Cybbig',
           error='process_restart', finished_at=? WHERE status IN ('queued','running')""",
        (now_iso(),),
    )
