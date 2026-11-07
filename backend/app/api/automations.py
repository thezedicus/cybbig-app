from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .. import db
from ..services import scheduler

router = APIRouter(prefix="/automations", tags=["automatisations"])


class AutomationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    kind: str
    project_id: str | None = None
    interval_minutes: int = Field(default=1440, ge=5, le=525600)
    config: dict[str, Any] = Field(default_factory=dict)
    enabled: bool = True


class AutomationUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    interval_minutes: int | None = Field(default=None, ge=5, le=525600)
    config: dict[str, Any] | None = None
    enabled: bool | None = None


@router.get("")
def list_automations() -> dict[str, Any]:
    return {"items": scheduler.list_automations(), "status": scheduler.status()}


@router.post("")
def create(payload: AutomationCreate) -> dict[str, Any]:
    try:
        row = scheduler.create_automation(payload.dict())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return row


@router.patch("/{automation_id}")
def update(automation_id: str, payload: AutomationUpdate) -> dict[str, Any]:
    try:
        row = scheduler.update_automation(automation_id, payload.dict(exclude_unset=True))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return row


@router.delete("/{automation_id}")
def delete(automation_id: str) -> dict[str, Any]:
    if not db.fetch_one("SELECT id FROM automations WHERE id=?", (automation_id,)):
        raise HTTPException(status_code=404, detail="Automatisation introuvable.")
    scheduler.delete_automation(automation_id)
    return {"ok": True}


@router.post("/{automation_id}/run")
def run(automation_id: str) -> dict[str, Any]:
    try:
        return scheduler.run_now(automation_id, manual=True)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{automation_id}/runs")
def runs(automation_id: str, limit: int = 20) -> dict[str, Any]:
    if not db.fetch_one("SELECT id FROM automations WHERE id=?", (automation_id,)):
        raise HTTPException(status_code=404, detail="Automatisation introuvable.")
    rows = db.fetch_all(
        "SELECT * FROM automation_runs WHERE automation_id=? ORDER BY started_at DESC LIMIT ?",
        (automation_id, min(100, max(1, limit))),
    )
    return {"items": rows}
