from __future__ import annotations

import re
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from .. import db
from ..services import ai, codegen

router = APIRouter(prefix="/assistant", tags=["assistant IA"])

MODEL_NAME = re.compile(r"^[A-Za-z0-9._\-/]+(:[A-Za-z0-9._\-]+)?$")


class ChatPayload(BaseModel):
    message: str = Field(min_length=1, max_length=8000)
    project_id: str | None = None
    finding_id: str | None = None
    model: str | None = None


class ModelPayload(BaseModel):
    model: str = Field(min_length=1, max_length=120)
    provider: str = Field(default="local", max_length=10)  # "local" ou "cloud" : chaque serveur a son modèle


@router.get("/status")
def status(refresh: bool = False, retry_cloud: bool = False) -> dict[str, Any]:
    """État des deux serveurs (local et en ligne) et serveur actif. ``refresh`` ignore le cache de quelques secondes,
    ``retry_cloud`` lève la pause qui suit un refus du service en ligne (clé, crédits, limite)."""
    if retry_cloud:
        ai.reset_cloud_block()
    if refresh:
        ai.invalidate_status()
    return ai.ollama_status(full=True)


@router.post("/chat")
def chat(payload: ChatPayload) -> dict[str, Any]:
    try:
        return ai.chat(payload.message, payload.project_id, payload.model, payload.finding_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/chat/stream")
def chat_stream(payload: ChatPayload) -> StreamingResponse:
    try:
        stream = ai.chat_stream(payload.message, payload.project_id, payload.model, payload.finding_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return StreamingResponse(stream, media_type="application/x-ndjson")


@router.put("/model")
def select_model(payload: ModelPayload) -> dict[str, Any]:
    key = "ollama_cloud_model" if payload.provider == "cloud" else "ollama_model"
    db.set_setting(key, payload.model.strip())
    db.audit("assistant_model_selected", {"model": payload.model, "provider": payload.provider})
    ai.invalidate_status()
    return ai.ollama_status(full=True)


class GeneratePayload(BaseModel):
    kind: str = Field(min_length=1, max_length=20)
    description: str = Field(min_length=1, max_length=codegen.MAX_DESCRIPTION)
    language: str = Field(default="", max_length=20)


@router.get("/generate/kinds")
def generate_kinds() -> dict[str, Any]:
    return {"items": codegen.kinds(), "languages": sorted(codegen.LANGUAGES)}


@router.post("/generate")
def generate(payload: GeneratePayload) -> dict[str, Any]:
    """Configuration de proxy/VPN ou code produit par le modèle « code » du serveur Ollama actif (texte à relire, rien d'appliqué)."""
    try:
        return codegen.generate(payload.kind, payload.description, payload.language)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/models/pull")
def pull_model(payload: ModelPayload) -> StreamingResponse:
    if not MODEL_NAME.match(payload.model.strip()):
        raise HTTPException(status_code=400, detail="Nom de modèle invalide.")
    return StreamingResponse(ai.pull_model(payload.model.strip()), media_type="application/x-ndjson")


@router.get("/history")
def history(limit: int = 50) -> dict[str, Any]:
    return {"items": ai.history(limit)}


@router.delete("/history")
def clear() -> dict[str, Any]:
    ai.clear_history()
    return {"ok": True}


@router.get("/search")
def search(q: str, limit: int = 5) -> dict[str, Any]:
    return {"items": ai.retrieve(q, limit)}
