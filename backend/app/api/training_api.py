from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from ..services import training
from ..services.scope import require_consent

router = APIRouter(prefix="/training", tags=["entraînement IA"])


def _need_consent() -> None:
    decision = require_consent()
    if not decision.allowed:
        raise HTTPException(status_code=403, detail=decision.reason)


class EnrichPayload(BaseModel):
    limit: int = Field(default=10, ge=1, le=60)
    teacher: str = Field(default="auto", max_length=10)


class QaPayload(BaseModel):
    limit: int = Field(default=12, ge=1, le=60)
    per_doc: int = Field(default=3, ge=1, le=5)
    teacher: str = Field(default="auto", max_length=10)


class BuildPayload(BaseModel):
    name: str = Field(default=training.MODEL_NAME, max_length=40)
    base: str = Field(default="", max_length=120)
    max_examples: int = Field(default=12, ge=0, le=30)
    activate: bool = True


class ExamplePatch(BaseModel):
    question: str | None = Field(default=None, max_length=300)
    answer: str | None = Field(default=None, max_length=3000)
    status: str | None = Field(default=None, max_length=12)


class BulkPayload(BaseModel):
    from_status: str = Field(default="pending", max_length=12)
    to_status: str = Field(default="approved", max_length=12)


def _run(kind: str, params: dict[str, Any]) -> dict[str, Any]:
    _need_consent()
    try:
        return training.start_job(kind, params)
    except training.TrainingError as exc:
        raise HTTPException(status_code=409 if "déjà en cours" in str(exc) else 400, detail=str(exc)) from exc


@router.get("")
def overview() -> dict[str, Any]:
    return training.overview()


@router.get("/curriculum")
def curriculum() -> dict[str, Any]:
    missing = {t[0] for t in training.missing_topics()}
    return {"items": [{"slug": s, "title": t, "category": c, "hint": h, "generated": s not in missing} for s, t, c, h in training.CURRICULUM]}


@router.post("/enrich")
def enrich(payload: EnrichPayload) -> dict[str, Any]:
    return _run("enrich", payload.dict())


@router.post("/qa")
def generate_qa(payload: QaPayload) -> dict[str, Any]:
    return _run("qa", payload.dict())


@router.post("/auto-run")
def auto_run() -> dict[str, Any]:
    """Lance tout de suite un cycle du pilote automatique (en ligne uniquement)."""
    _need_consent()
    try:
        return training.start_job("auto", {"approve": training.auto_config()["approve"]})
    except training.TrainingError as exc:
        raise HTTPException(status_code=409 if "déjà en cours" in str(exc) else 400, detail=str(exc)) from exc


@router.post("/model")
def build_model(payload: BuildPayload) -> dict[str, Any]:
    return _run("build_model", payload.dict())


@router.delete("/model")
def delete_model() -> dict[str, Any]:
    _need_consent()
    try:
        return {"deleted": training.delete_model()}
    except training.TrainingError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/jobs/{job_id}")
def job(job_id: str) -> dict[str, Any]:
    found = training.get_job(job_id)
    if not found:
        raise HTTPException(status_code=404, detail="Tâche introuvable.")
    return found


@router.post("/jobs/{job_id}/cancel")
def cancel(job_id: str) -> dict[str, Any]:
    return {"cancelled": training.cancel_job(job_id)}


@router.get("/examples")
def examples(status: str = "", limit: int = 50, offset: int = 0) -> dict[str, Any]:
    return training.list_examples(status, limit, offset)


@router.patch("/examples/{example_id}")
def patch_example(example_id: str, payload: ExamplePatch) -> dict[str, Any]:
    try:
        found = training.update_example(example_id, payload.question, payload.answer) if (payload.question or payload.answer) else True
        if found and payload.status:
            found = training.set_example_status(example_id, payload.status)
    except training.TrainingError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not found:
        raise HTTPException(status_code=404, detail="Exemple introuvable.")
    return {"ok": True}


@router.post("/examples/bulk")
def bulk(payload: BulkPayload) -> dict[str, Any]:
    try:
        return {"updated": training.bulk_status(payload.from_status, payload.to_status)}
    except training.TrainingError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/export")
def export(include_pending: bool = False) -> StreamingResponse:
    return StreamingResponse(training.export_jsonl(include_pending), media_type="application/x-ndjson",
                             headers={"Content-Disposition": 'attachment; filename="cybbig-training.jsonl"'})
