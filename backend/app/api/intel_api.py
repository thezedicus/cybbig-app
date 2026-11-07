from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .. import db
from ..services import intel, nvd_archive

router = APIRouter(prefix="/intel", tags=["threat intelligence"])


class SyncPayload(BaseModel):
    sources: list[str] = Field(default_factory=list)


@router.get("/sources")
def sources() -> dict[str, Any]:
    return {"items": intel.list_sources()}


@router.post("/sync")
def sync(payload: SyncPayload | None = None) -> dict[str, Any]:
    selected = (payload.sources if payload else []) or None
    return intel.sync_all(selected)


@router.get("/archive/status")
def archive_status() -> dict[str, Any]:
    return nvd_archive.get_status()


@router.post("/archive/start")
def start_archive_import() -> dict[str, Any]:
    return nvd_archive.start_import()


@router.get("/items")
def items(
    q: str = "", source: str = "", severity: str = "", exploited: bool | None = None,
    limit: int = 100, offset: int = 0, sort: str = "recent",
) -> dict[str, Any]:
    return intel.search_items(q, source, severity, exploited, limit, offset, sort)


@router.get("/items/{item_id}")
def item(item_id: int) -> dict[str, Any]:
    row = db.fetch_one("SELECT * FROM threat_items WHERE id=?", (item_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Élément introuvable.")
    row["tags"] = db.json_loads(row.pop("tags_json", None), [])
    row["raw"] = db.json_loads(row.pop("raw_json", None), {})
    return row


@router.get("/stats")
def stats() -> dict[str, Any]:
    by_source = db.fetch_all(
        "SELECT source, COUNT(*) AS count, SUM(exploited) AS exploited FROM threat_items GROUP BY source ORDER BY count DESC"
    )
    by_severity = db.fetch_all(
        "SELECT severity, COUNT(*) AS count FROM threat_items GROUP BY severity ORDER BY count DESC"
    )
    totals = db.fetch_one(
        "SELECT COUNT(*) AS total, SUM(exploited) AS exploited, MAX(fetched_at) AS last_fetch FROM threat_items"
    ) or {}
    recent = db.fetch_all(
        "SELECT id,source,title,severity,cve,exploited,epss,published_at,url FROM threat_items "
        "ORDER BY (exploited) DESC, COALESCE(epss,0) DESC, published_at DESC LIMIT 8"
    )
    latest = db.fetch_all(
        "SELECT name,label,last_sync_at,status,items_count,error FROM threat_sources ORDER BY name"
    )
    return {"total": totals.get("total") or 0, "exploited": totals.get("exploited") or 0,
            "last_fetch": totals.get("last_fetch"), "by_source": by_source, "by_severity": by_severity,
            "recent": recent, "sources": latest}


@router.get("/search")
def search(q: str, limit: int = 20) -> dict[str, Any]:
    return intel.search_items(q=q, limit=limit)
