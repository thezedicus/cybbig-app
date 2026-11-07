"""Moteur IA de fond : enrichit automatiquement chaque module avec le modèle Ollama local.

- Analyse terminée  → synthèse de l'analyse + triage des résultats les plus graves.
- Veille synchronisée → digest des menaces pertinentes.
- Tableau de bord   → plan de la semaine rafraîchi périodiquement.

Les tâches passent par une file à priorités. Avec le modèle local, un seul fil la traite (le modèle tourne sur
le processeur : deux générations simultanées seraient deux fois plus lentes) ; avec le modèle en ligne, jusqu'à
trois fils travaillent en parallèle, car le calcul est fait à distance. L'intensité (ai_boost) règle le volume et
la fréquence des appels. Les décisions de l'utilisateur sur les résultats (faux positif, corrigé…) sont
réinjectées dans les triages suivants de la même règle : la qualité s'améliore avec l'usage.
"""
from __future__ import annotations

import heapq
import itertools
import logging
import os
import re
import threading
import time
from datetime import datetime, timedelta, timezone
from typing import Any

from .. import db
from ..utils import now_iso
from . import ai, ai_agents, ai_tasks, resources, training

logger = logging.getLogger("cybbig.ai")

BOOST = {
    "eco": {"label": "Économe", "triage": 3, "dashboard_hours": 24, "num_predict": 500},
    "balanced": {"label": "Équilibré", "triage": 8, "dashboard_hours": 6, "num_predict": 900},
    "intense": {"label": "Intensif", "triage": 20, "dashboard_hours": 2, "num_predict": 1400},
}
SECTIONS = {
    "ai_auto_scans": "Synthèse automatique des analyses",
    "ai_auto_triage": "Triage automatique des résultats graves",
    "ai_auto_intel": "Digest automatique de la veille",
    "ai_auto_dashboard": "Plan de la semaine sur le tableau de bord",
    "ai_agents": "Agents d'amélioration continue (un par module)",
}
VERDICT_RE = re.compile(r"VERDICT\s*:\s*\**\s*(vrai positif|faux positif|incertain)", re.I)

_queue: list[tuple[int, int, dict[str, Any]]] = []
_pending: set[str] = set()
_counter = itertools.count()
_lock = threading.Lock()
_wake = threading.Event()
_stop = threading.Event()
_threads: list[threading.Thread] = []
_running: dict[int, dict[str, Any]] = {}
_state: dict[str, Any] = {"processed": 0, "failed": 0, "last_error": "", "last_done_at": None}


def _flag(key: str, default: bool = True) -> bool:
    return str(db.get_setting(key, "true" if default else "false")).lower() in {"1", "true", "yes", "on"}


def enabled() -> bool:
    return _flag("ai_auto") and os.environ.get("CYBBIG_AI_WORKER", "1") != "0"


def boost() -> dict[str, Any]:
    return BOOST.get(str(db.get_setting("ai_boost", "balanced")), BOOST["balanced"])


def enqueue(key: str, task: str, params: dict[str, Any], priority: int = 5, target: str = "cache") -> bool:
    """Ajoute une tâche ; ignorée si la même clé attend déjà. Priorité basse = traitée en premier."""
    if not enabled():
        return False
    with _lock:
        if key in _pending:
            return False
        _pending.add(key)
        heapq.heappush(_queue, (priority, next(_counter), {"key": key, "task": task, "params": params, "target": target}))
    _wake.set()
    return True


# --- Points d'accroche appelés par les modules ---------------------------------

def on_scan_completed(scan_id: str) -> None:
    if _flag("ai_auto_scans"):
        enqueue(f"scan:{scan_id}", "scan_summary", {"scan_id": scan_id}, priority=2)
    if _flag("ai_auto_triage"):
        rows = db.fetch_all(
            f"SELECT id FROM findings WHERE scan_id=? AND severity IN ('critical','high') AND COALESCE(ai_verdict,'')='' "
            f"ORDER BY {ai_tasks.SEV_ORDER}, risk_score DESC LIMIT ?",
            (scan_id, boost()["triage"]),
        )
        for row in rows:
            enqueue(f"finding:{row['id']}", "finding_triage", {"finding_id": row["id"]}, priority=3, target="finding")


def on_intel_synced() -> None:
    if _flag("ai_auto_intel"):
        enqueue("intel:digest", "intel_digest", {"days": 7}, priority=4)


def _maybe_refresh_dashboard() -> None:
    if not _flag("ai_auto_dashboard"):
        return
    row = db.fetch_one("SELECT created_at FROM ai_cache WHERE key='dashboard'")
    hours = boost()["dashboard_hours"]
    if row:
        try:
            age = datetime.now(timezone.utc) - datetime.fromisoformat(row["created_at"])
            if age < timedelta(hours=hours):
                return
        except ValueError:
            pass
    enqueue("dashboard", "dashboard_priorities", {}, priority=6)


# --- Exécution -----------------------------------------------------------------

def _store(job: dict[str, Any], text: str, model: str) -> None:
    if job["target"] == "finding":
        match = VERDICT_RE.search(text)
        verdict = match.group(1).lower() if match else "incertain"
        db.execute("UPDATE findings SET ai_verdict=?, ai_notes=?, ai_at=? WHERE id=?",
                   (verdict, text[:12000], now_iso(), job["params"]["finding_id"]))
    db.execute(
        """INSERT INTO ai_cache(key,task,params_json,content,model,created_at) VALUES(?,?,?,?,?,?)
           ON CONFLICT(key) DO UPDATE SET content=excluded.content, model=excluded.model, created_at=excluded.created_at""",
        (job["key"], job["task"], db.json_dumps(job["params"]), text[:20000], model, now_iso()),
    )


def _maybe_run_agents() -> None:
    if not _flag("ai_agents"):
        return
    # Les propositions peuvent contenir des métriques et résultats internes : l'agent reste local.
    local = ai._local_status()
    if not (local.get("available") and local.get("selected_model")):
        return
    boost_name = str(db.get_setting("ai_boost", "balanced"))
    for module in ai_agents.due_agents(boost_name):
        enqueue(f"agent:{module}", "agent", {"module": module}, priority=7, target="agent")


def _run(job: dict[str, Any]) -> None:
    if job["target"] == "agent":
        ai_agents.run_agent(job["params"]["module"], num_predict=boost()["num_predict"])
        return
    if job["target"] == "income":
        text = ai_tasks.complete_local("income_digest", job["params"], num_predict=boost()["num_predict"])
        if not text:
            raise RuntimeError("modèle IA local indisponible ou réponse vide")
        db.set_setting("income_watch_review", text[:12000])
        db.set_setting("income_watch_review_at", now_iso())
        db.audit("income_opportunities_reviewed", {"provider": "local"})
        return
    status = ai.ollama_status()
    if not (status["available"] and status["selected_model"]):
        # Sans modèle, la tâche est remise en file pour plus tard plutôt que perdue.
        raise RuntimeError("modèle indisponible")
    text = ai_tasks.complete(job["task"], job["params"], num_predict=boost()["num_predict"])
    if not text:
        raise RuntimeError("réponse vide")
    _store(job, text, status["selected_model"])


def _loop(index: int) -> None:
    """Fil de traitement ``index``. Le fil 0 travaille toujours ; les suivants seulement quand le modèle actif est en ligne."""
    last_periodic = 0.0
    while not _stop.is_set():
        if index == 0 and time.monotonic() - last_periodic > 300:
            last_periodic = time.monotonic()
            try:
                if enabled():
                    _maybe_refresh_dashboard()
                    _maybe_run_agents()
                    training.autopilot_tick()
            except Exception:  # noqa: BLE001
                logger.exception("Planification IA impossible")
        if index > 0 and ai.status_provider(ai.ollama_status()) != "cloud":
            _stop.wait(30)  # modèle local : un seul fil à la fois
            continue
        with _lock:
            item = heapq.heappop(_queue) if _queue else None
        if not item:
            _wake.wait(30)
            _wake.clear()
            continue
        priority, _, job = item
        _running[index] = {"key": job["key"], "task": job["task"], "started_at": now_iso()}
        try:
            _run(job)
            _state["processed"] += 1
            _state["last_done_at"] = now_iso()
            with _lock:
                _pending.discard(job["key"])
        except Exception as exc:  # noqa: BLE001
            _state["failed"] += 1
            _state["last_error"] = f"{job['task']} : {exc}"
            retries = job.get("retries", 0)
            with _lock:
                if retries < 3:
                    job["retries"] = retries + 1
                    heapq.heappush(_queue, (priority + 1, next(_counter), job))
                else:
                    _pending.discard(job["key"])
            _stop.wait(60)  # laisse au modèle le temps de redevenir disponible
        finally:
            _running.pop(index, None)


def _warm_up() -> None:
    resources.prime()
    try:
        ai.warm_up()
    except Exception:  # noqa: BLE001 — le préchargement est un confort, jamais une cause d'arrêt
        logger.debug("Préchargement du modèle impossible", exc_info=True)


def start() -> None:
    if not enabled() or any(t.is_alive() for t in _threads):
        return
    _stop.clear()
    _threads.clear()
    for index in range(resources.recommended_workers("ai_cloud")):
        thread = threading.Thread(target=_loop, args=(index,), name=f"cybbig-ai-worker-{index}", daemon=True)
        thread.start()
        _threads.append(thread)
    threading.Thread(target=_warm_up, name="cybbig-ai-warmup", daemon=True).start()


def stop() -> None:
    _stop.set()
    _wake.set()


def status() -> dict[str, Any]:
    with _lock:
        queued = [{"key": j["key"], "task": j["task"]} for _, _, j in sorted(_queue)[:20]]
    current_boost = str(db.get_setting("ai_boost", "balanced"))
    return {
        "enabled": enabled(),
        "running": any(t.is_alive() for t in _threads),
        "provider": ai.status_provider(ai.ollama_status()),
        "parallel": len(_running),
        "boost": current_boost if current_boost in BOOST else "balanced",
        "boosts": {k: v["label"] for k, v in BOOST.items()},
        "sections": {key: {"label": label, "enabled": _flag(key)} for key, label in SECTIONS.items()},
        "queue": queued,
        "queue_size": len(_queue),
        "current": next(iter(_running.values()), None),
        **_state,
    }


def get_cached(key: str) -> dict[str, Any] | None:
    return db.fetch_one("SELECT key,task,content,model,created_at FROM ai_cache WHERE key=?", (key,))
