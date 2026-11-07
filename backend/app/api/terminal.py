from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..services import terminal

router = APIRouter(prefix="/terminal", tags=["terminal"])


class GuardrailPayload(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    command: list[str] = Field(min_items=1, max_items=40)
    working_dir: str = Field(default="root", max_length=20)
    description: str = Field(default="", max_length=500)
    enabled: bool = True


class RunPayload(BaseModel):
    guardrail_id: str = Field(min_length=1, max_length=100)


@router.get("/guardrails")
def list_guardrails() -> dict[str, Any]:
    return {"items": terminal.list_guardrails()}


@router.post("/guardrails")
def create_guardrail(payload: GuardrailPayload) -> dict[str, Any]:
    try:
        return terminal.add_guardrail(
            payload.name, payload.command, payload.working_dir, payload.description, payload.enabled
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete("/guardrails/{guardrail_id}")
def delete_guardrail(guardrail_id: str) -> dict[str, Any]:
    terminal.remove_guardrail(guardrail_id)
    return {"ok": True}


@router.patch("/guardrails/{guardrail_id}")
def toggle_guardrail(guardrail_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    if "enabled" in payload:
        terminal.set_enabled(guardrail_id, bool(payload["enabled"]))
    return {"ok": True}


@router.post("/run")
def run(payload: RunPayload) -> dict[str, Any]:
    try:
        return terminal.run_guardrail(payload.guardrail_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/runs")
def list_runs(limit: int = 30) -> dict[str, Any]:
    return {"items": terminal.list_runs(limit)}