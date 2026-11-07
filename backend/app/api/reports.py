from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

from .. import db
from ..config import REPORTS_DIR
from ..services import ai_tasks, reports
from ..utils import now_iso

router = APIRouter(prefix="/reports", tags=["rapports"])


class ReportCreate(BaseModel):
    project_id: str
    scan_id: str | None = None
    title: str | None = Field(default=None, max_length=300)
    ai_summary: bool = False


@router.post("")
def create_report(payload: ReportCreate) -> dict[str, Any]:
    try:
        # Synthèse exécutive rédigée par le modèle local (peut prendre une à deux minutes sans GPU).
        summary = ai_tasks.complete("report_summary", {"project_id": payload.project_id, "scan_id": payload.scan_id}) if payload.ai_summary else ""
        report_id, path = reports.render_html(payload.project_id, payload.scan_id, payload.title, summary)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {
        "id": report_id, "path": path, "created_at": now_iso(), "ai_summary": bool(summary),
        "download_url": f"/api/reports/{report_id}/download",
        "json_url": f"/api/reports/{report_id}/json",
    }


@router.get("")
def list_reports(project_id: str = "", limit: int = 100) -> dict[str, Any]:
    if project_id:
        rows = db.fetch_all(
            "SELECT * FROM reports WHERE project_id=? ORDER BY created_at DESC LIMIT ?",
            (project_id, min(200, max(1, limit))),
        )
    else:
        rows = db.fetch_all("SELECT * FROM reports ORDER BY created_at DESC LIMIT ?", (min(200, max(1, limit)),))
    for row in rows:
        row["meta"] = db.json_loads(row.pop("meta_json", None), {})
        row["download_url"] = f"/api/reports/{row['id']}/download"
        row["json_url"] = f"/api/reports/{row['id']}/json"
    return {"items": rows}


@router.get("/{report_id}")
def get_report(report_id: str) -> dict[str, Any]:
    row = db.fetch_one("SELECT * FROM reports WHERE id=?", (report_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Rapport introuvable.")
    row["meta"] = db.json_loads(row.pop("meta_json", None), {})
    return row


@router.get("/{report_id}/download")
def download(report_id: str) -> FileResponse:
    path = reports.report_path(report_id)
    if not path:
        raise HTTPException(status_code=404, detail="Fichier de rapport introuvable.")
    return FileResponse(path, media_type="text/html; charset=utf-8", filename=path.name)


@router.get("/{report_id}/json")
def report_json(report_id: str) -> JSONResponse:
    row = db.fetch_one("SELECT project_id,scan_id FROM reports WHERE id=?", (report_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Rapport introuvable.")
    data = reports.build_data(row["project_id"], row["scan_id"])
    # Les références sont déjà désérialisées par build_data.
    return JSONResponse(content=data, headers={"Content-Disposition": f'attachment; filename="cybbig-{report_id}.json"'})


@router.delete("/{report_id}")
def delete_report(report_id: str) -> dict[str, Any]:
    row = db.fetch_one("SELECT path FROM reports WHERE id=?", (report_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Rapport introuvable.")
    path = Path(row["path"]).resolve()
    try:
        path.relative_to(REPORTS_DIR.resolve())
        if path.exists():
            path.unlink()
    except (ValueError, OSError):
        pass
    db.execute("DELETE FROM reports WHERE id=?", (report_id,))
    db.audit("report_deleted", {"report_id": report_id})
    return {"ok": True}
