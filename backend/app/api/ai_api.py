from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from ..services import ai_agents, ai_tasks, ai_worker
from ..services.engines import active_checks

router = APIRouter(tags=["IA et mode"])


class TaskPayload(BaseModel):
    task: str = Field(min_length=1, max_length=60)
    params: dict[str, Any] = Field(default_factory=dict)


@router.post("/ai/run")
def run_task(payload: TaskPayload) -> StreamingResponse:
    try:
        stream = ai_tasks.stream(payload.task, payload.params)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return StreamingResponse(stream, media_type="application/x-ndjson")


@router.get("/ai/status")
def ai_status() -> dict[str, Any]:
    return ai_worker.status()


@router.get("/ai/cache/{key:path}")
def ai_cache(key: str) -> dict[str, Any]:
    return {"item": ai_worker.get_cached(key)}


@router.post("/ai/refresh/{section}")
def ai_refresh(section: str) -> dict[str, Any]:
    """Relance tout de suite une tâche de fond (le résultat arrive dans le cache)."""
    jobs = {
        "dashboard": ("dashboard", "dashboard_priorities", {}),
        "intel": ("intel:digest", "intel_digest", {"days": 7}),
    }
    if section not in jobs:
        raise HTTPException(status_code=400, detail="Section inconnue.")
    key, task, params = jobs[section]
    return {"queued": ai_worker.enqueue(key, task, params, priority=1)}


@router.get("/ai/agents")
def ai_agents_overview() -> dict[str, Any]:
    return {"items": ai_agents.overview()}


@router.get("/ai/suggestions")
def ai_suggestions(module: str = "", status: str = "") -> dict[str, Any]:
    return {"items": ai_agents.list_suggestions(module, status)}


@router.post("/ai/agents/{module}/run")
def ai_agent_run(module: str) -> dict[str, Any]:
    if module not in ai_agents.AGENTS:
        raise HTTPException(status_code=404, detail="Agent inconnu.")
    return {"queued": ai_worker.enqueue(f"agent:{module}", "agent", {"module": module}, priority=1, target="agent")}


@router.get("/mode")
def mode() -> dict[str, Any]:
    return {"active": active_checks.is_enabled()}
