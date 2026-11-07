from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from .. import db
from ..services import ai_tasks
from ..utils import now_iso

router = APIRouter(prefix="/income", tags=["opportunités rémunérées"])
STATUSES = {"new", "shortlisted", "proposal_prepared", "applied", "accepted", "declined", "completed"}


class OpportunityUpdate(BaseModel):
    status: str | None = None
    note: str | None = Field(default=None, max_length=3000)
    proposal_draft: str | None = Field(default=None, max_length=12000)


@router.get("/review")
def latest_review() -> dict[str, str]:
    return {"content": str(db.get_setting("income_watch_review", "") or ""),
            "updated_at": str(db.get_setting("income_watch_review_at", "") or "")}


@router.get("/status")
def radar_status() -> dict[str, Any]:
    row = db.fetch_one(
        "SELECT a.id,a.enabled,a.interval_minutes,a.last_status,a.last_run_at,a.next_run_at,"
        "r.started_at AS run_started_at,r.finished_at AS run_finished_at,r.status AS run_status,r.log AS run_log "
        "FROM automations a LEFT JOIN automation_runs r ON r.id=(SELECT id FROM automation_runs WHERE automation_id=a.id ORDER BY started_at DESC LIMIT 1) "
        "WHERE a.kind='income_watch' ORDER BY a.created_at LIMIT 1"
    )
    if not row:
        return {"configured": False, "enabled": False}
    return {"configured": True, "enabled": bool(row.get("enabled")),
            "interval_minutes": row.get("interval_minutes"), "last_status": row.get("last_status"),
            "last_run_at": row.get("last_run_at"), "next_run_at": row.get("next_run_at"),
            "run_status": row.get("run_status"), "run_log": str(row.get("run_log") or "")[-6000:]}


@router.get("/opportunities")
def list_opportunities(status: str = Query(default="all"), limit: int = Query(default=100, ge=1, le=300)) -> dict[str, Any]:
    if status != "all" and status not in STATUSES:
        raise HTTPException(status_code=400, detail="Filtre de statut invalide.")
    where = "" if status == "all" else "WHERE status=?"
    params: tuple[Any, ...] = () if status == "all" else (status,)
    items = db.fetch_all(
        f"SELECT * FROM income_opportunities {where} ORDER BY CASE status WHEN 'new' THEN 0 WHEN 'shortlisted' THEN 1 ELSE 2 END, last_seen_at DESC LIMIT ?",
        (*params, limit),
    )
    counts = {row["status"]: row["total"] for row in db.fetch_all("SELECT status,COUNT(*) AS total FROM income_opportunities GROUP BY status")}
    return {"items": items, "counts": counts, "total": sum(counts.values())}


@router.patch("/opportunities/{opportunity_id}")
def update_opportunity(opportunity_id: str, payload: OpportunityUpdate) -> dict[str, Any]:
    if not db.fetch_one("SELECT id FROM income_opportunities WHERE id=?", (opportunity_id,)):
        raise HTTPException(status_code=404, detail="Opportunité introuvable.")
    data = payload.dict(exclude_unset=True)
    if "status" in data and data["status"] not in STATUSES:
        raise HTTPException(status_code=400, detail="Statut d’opportunité invalide.")
    fields, values = [], []
    if "status" in data:
        fields.append("status=?"); values.append(data["status"])
    if "note" in data:
        fields.append("note=?"); values.append(data["note"] or "")
    if "proposal_draft" in data:
        fields.append("proposal_draft=?"); values.append(data["proposal_draft"] or "")
    if fields:
        fields.append("updated_at=CURRENT_TIMESTAMP")
        values.append(opportunity_id)
        db.execute(f"UPDATE income_opportunities SET {', '.join(fields)} WHERE id=?", values)
        db.audit("income_opportunity_updated", {"id": opportunity_id, "fields": list(data)})
    return db.fetch_one("SELECT * FROM income_opportunities WHERE id=?", (opportunity_id,)) or {}


@router.post("/opportunities/{opportunity_id}/draft")
def prepare_response_draft(opportunity_id: str) -> dict[str, Any]:
    row = db.fetch_one("SELECT id FROM income_opportunities WHERE id=?", (opportunity_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Opportunité introuvable.")
    draft = ai_tasks.complete_local("income_proposal_draft", {"opportunity_id": opportunity_id}, num_predict=700)
    if not draft:
        raise HTTPException(status_code=503, detail="Le modèle IA local n’est pas disponible. Configurez-le dans Paramètres > IA.")
    now = now_iso()
    db.execute("UPDATE income_opportunities SET proposal_draft=?,status='proposal_prepared',updated_at=? WHERE id=?",
               (draft[:12000], now, opportunity_id))
    db.audit("income_proposal_draft_prepared", {"opportunity_id": opportunity_id, "provider": "local"})
    return db.fetch_one("SELECT * FROM income_opportunities WHERE id=?", (opportunity_id,)) or {}
