from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..services import lab

router = APIRouter(prefix="/lab", tags=["laboratoire"])


class ValidatePayload(BaseModel):
    code: str = Field(min_length=1, max_length=100_000)
    language: str = Field(default="php", max_length=30)


@router.get("/scenarios")
def scenarios(category: str = "") -> dict[str, Any]:
    items = lab.list_scenarios(category)
    categories = sorted({s["category"] for s in items})
    return {"items": items, "categories": categories}


@router.get("/scenarios/{identifier}")
def scenario(identifier: str) -> dict[str, Any]:
    row = lab.get_scenario(identifier)
    if not row:
        raise HTTPException(status_code=404, detail="Scénario introuvable.")
    return row


@router.post("/validate")
def validate(payload: ValidatePayload) -> dict[str, Any]:
    return lab.validate_code(payload.code, payload.language)
