from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from ..services import webfetch, websearch
from ..services.scope import require_consent

router = APIRouter(prefix="/web", tags=["visite de sites web"])


@router.get("/search")
def search(q: str = Query(min_length=2, max_length=400), limit: int | None = Query(default=None, ge=1, le=20), lang: str = "fr", provider: str = "auto", domains: list[str] | None = Query(default=None, max_length=8)) -> dict[str, Any]:
    """Recherche sur le Web public ; les pages ne sont pas ouvertes automatiquement."""
    try:
        return websearch.search(q, limit, lang, provider, domains)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


def _need_consent() -> None:
    decision = require_consent()
    if not decision.allowed:
        raise HTTPException(status_code=403, detail=decision.reason)


class VisitPayload(BaseModel):
    url: str = Field(min_length=3, max_length=2000)
    selector: str = Field(default="", max_length=200)
    save: bool = False
    category: str = Field(default="Web", max_length=100)
    tags: str = Field(default="", max_length=300)


class CrawlPayload(BaseModel):
    url: str = Field(min_length=3, max_length=2000)
    max_pages: int = Field(default=10, ge=1, le=webfetch.MAX_CRAWL_PAGES)
    depth: int = Field(default=1, ge=0, le=webfetch.MAX_CRAWL_DEPTH)
    selector: str = Field(default="", max_length=200)
    category: str = Field(default="Web", max_length=100)
    tags: str = Field(default="", max_length=300)


@router.post("/visit")
def visit(payload: VisitPayload) -> dict[str, Any]:
    """Lit une page publique (aperçu) et, si ``save``, l'ajoute à la base de connaissances."""
    _need_consent()
    try:
        return webfetch.visit(payload.url, payload.selector, payload.save, payload.category.strip() or "Web", payload.tags)
    except webfetch.FetchError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/crawl")
def crawl(payload: CrawlPayload) -> dict[str, Any]:
    """Explore plusieurs pages du même site en tâche de fond et les ajoute à la base de connaissances."""
    _need_consent()
    try:
        return webfetch.start_crawl(payload.url, payload.max_pages, payload.depth, payload.category.strip() or "Web", payload.tags, payload.selector)
    except webfetch.FetchError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/jobs")
def jobs() -> dict[str, Any]:
    return {"items": webfetch.list_jobs()}


@router.get("/jobs/{job_id}")
def job(job_id: str) -> dict[str, Any]:
    found = webfetch.get_job(job_id)
    if not found:
        raise HTTPException(status_code=404, detail="Tâche introuvable.")
    return found


@router.post("/jobs/{job_id}/cancel")
def cancel(job_id: str) -> dict[str, Any]:
    return {"cancelled": webfetch.cancel_job(job_id)}
