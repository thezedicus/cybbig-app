from __future__ import annotations

import csv
import io
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from .. import db
from ..services import ai_worker
from ..utils import now_iso, severity_counts

router = APIRouter(prefix="/findings", tags=["résultats"])

ALLOWED_STATUS = {"open", "acknowledged", "fixed", "accepted_risk", "false_positive"}


class FindingUpdate(BaseModel):
    status: str


@router.get("")
def list_findings(
    project_id: str = "", scan_id: str = "", severity: str = "", status: str = "",
    engine: str = "", q: str = "", limit: int = 100, offset: int = 0,
) -> dict[str, Any]:
    where = []
    params: list[Any] = []
    for field, value in (("project_id", project_id), ("scan_id", scan_id), ("severity", severity), ("status", status), ("engine", engine)):
        if value:
            where.append(f"f.{field}=?")
            params.append(value)
    if q:
        where.append("(f.title LIKE ? OR f.description LIKE ? OR f.file_path LIKE ? OR f.url LIKE ? OR f.rule_id LIKE ?)")
        like = f"%{q}%"
        params += [like, like, like, like, like]
    clause = (" WHERE " + " AND ".join(where)) if where else ""
    total = db.fetch_one(f"SELECT COUNT(*) AS c FROM findings f{clause}", params)["c"]  # type: ignore[index]
    rows = db.fetch_all(
        f"""SELECT f.*, p.name AS project_name FROM findings f
            LEFT JOIN projects p ON p.id=f.project_id{clause}
            ORDER BY CASE f.severity WHEN 'critical' THEN 0 WHEN 'high' THEN 1 WHEN 'medium' THEN 2
            WHEN 'low' THEN 3 ELSE 4 END, f.created_at DESC LIMIT ? OFFSET ?""",
        params + [min(500, max(1, limit)), max(0, offset)],
    )
    for row in rows:
        row["references"] = db.json_loads(row.pop("references_json", None), [])
    all_for_counts = db.fetch_all(f"SELECT f.severity FROM findings f{clause}", params)
    return {
        "items": rows, "total": total, "limit": limit, "offset": offset,
        "severity": severity_counts(all_for_counts),
    }


@router.get("/export.csv")
def export_csv(project_id: str = "", severity: str = "", status: str = "") -> StreamingResponse:
    where = []
    params: list[Any] = []
    for field, value in (("project_id", project_id), ("severity", severity), ("status", status)):
        if value:
            where.append(f"{field}=?")
            params.append(value)
    clause = (" WHERE " + " AND ".join(where)) if where else ""
    rows = db.fetch_all(
        f"SELECT title,severity,confidence,engine,rule_id,category,file_path,line_start,url,status,description,remediation,created_at "
        f"FROM findings{clause} ORDER BY created_at DESC LIMIT 5000", params,
    )
    buffer = io.StringIO()
    buffer.write("\ufeff")
    writer = csv.DictWriter(
        buffer, fieldnames=["title", "severity", "confidence", "engine", "rule_id", "category",
                            "file_path", "line_start", "url", "status", "description", "remediation", "created_at"],
        delimiter=";",
    )
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    content = buffer.getvalue()
    return StreamingResponse(
        iter([content]), media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=cybbig-findings.csv"},
    )


@router.get("/{finding_id}")
def get_finding(finding_id: str) -> dict[str, Any]:
    row = db.fetch_one(
        "SELECT f.*, p.name AS project_name FROM findings f LEFT JOIN projects p ON p.id=f.project_id WHERE f.id=?",
        (finding_id,),
    )
    if not row:
        raise HTTPException(status_code=404, detail="Résultat introuvable.")
    row["references"] = db.json_loads(row.pop("references_json", None), [])
    row["scan"] = db.fetch_one("SELECT id,kind,status,target,created_at FROM scans WHERE id=?", (row.get("scan_id"),))
    return row


@router.patch("/{finding_id}")
def update_finding(finding_id: str, payload: FindingUpdate) -> dict[str, Any]:
    if payload.status not in ALLOWED_STATUS:
        raise HTTPException(status_code=400, detail="Statut invalide.")
    if not db.fetch_one("SELECT id FROM findings WHERE id=?", (finding_id,)):
        raise HTTPException(status_code=404, detail="Résultat introuvable.")
    db.execute("UPDATE findings SET status=?, updated_at=? WHERE id=?", (payload.status, now_iso(), finding_id))
    db.audit("finding_status", {"finding_id": finding_id, "status": payload.status})
    row = db.fetch_one("SELECT * FROM findings WHERE id=?", (finding_id,))
    if row:
        row["references"] = db.json_loads(row.pop("references_json", None), [])
        if payload.status in {"false_positive", "fixed", "accepted_risk"}:
            # Apprentissage : les résultats ouverts de la même règle sont réévalués avec cette décision.
            for other in db.fetch_all(
                "SELECT id FROM findings WHERE rule_id=? AND id!=? AND status='open' ORDER BY created_at DESC LIMIT 5",
                (row["rule_id"], finding_id),
            ):
                ai_worker.enqueue(f"finding:{other['id']}:retriage", "finding_triage", {"finding_id": other["id"]}, priority=4, target="finding")
    return row or {}


@router.get("/{finding_id}/history")
def finding_history(finding_id: str) -> dict[str, Any]:
    if not db.fetch_one("SELECT id FROM findings WHERE id=?", (finding_id,)):
        raise HTTPException(status_code=404, detail="Résultat introuvable.")
    rows = db.fetch_all(
        "SELECT * FROM audit_log WHERE details LIKE ? ORDER BY id DESC LIMIT 50", (f"%{finding_id}%",)
    )
    return {"items": rows}
