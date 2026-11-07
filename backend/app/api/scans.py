from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .. import db
from ..config import SCAN_KINDS
from ..services import jobs, scope
from ..utils import severity_counts

router = APIRouter(prefix="/scans", tags=["scans"])


class ScanCreate(BaseModel):
    project_id: str
    kind: str
    target: str = Field(default="", max_length=2000)
    config: dict[str, Any] = Field(default_factory=dict)


def _resolve_target(project: dict[str, Any], kind: str, target: str) -> str:
    target = (target or "").strip()
    if kind == "php":
        return project.get("path") or target
    if kind == "web":
        return target or project.get("base_url") or ""
    if kind == "checkout":
        return target or project.get("base_url") or ""
    if kind == "api":
        if target:
            return target
        base = (project.get("base_url") or "").rstrip("/")
        return base + "/openapi.json" if base else ""
    if kind == "reverse":
        return target
    return target


def _scan(row: dict[str, Any], detailed: bool = False) -> dict[str, Any]:
    scan = dict(row)
    scan["config"] = db.json_loads(scan.pop("config_json", None), {})
    scan["summary"] = db.json_loads(scan.pop("summary_json", None), {})
    project = db.fetch_one("SELECT id,name,client,base_url,path,activity_level FROM projects WHERE id=?", (scan["project_id"],))
    scan["project"] = project
    if detailed:
        scan["findings"] = db.fetch_all(
            "SELECT id,engine,rule_id,title,severity,confidence,category,file_path,line_start,url,status,risk_score "
            "FROM findings WHERE scan_id=? ORDER BY CASE severity WHEN 'critical' THEN 0 WHEN 'high' THEN 1 "
            "WHEN 'medium' THEN 2 WHEN 'low' THEN 3 ELSE 4 END, created_at",
            (scan["id"],),
        )
        scan["severity"] = severity_counts(scan["findings"])
        scan["dependencies"] = db.fetch_all(
            "SELECT * FROM dependencies WHERE scan_id=? ORDER BY vulnerable DESC, package", (scan["id"],)
        )
    return scan


@router.post("")
def start_scan(payload: ScanCreate) -> dict[str, Any]:
    if payload.kind not in SCAN_KINDS:
        raise HTTPException(status_code=400, detail="Type de scan invalide.")
    project = db.fetch_one("SELECT * FROM projects WHERE id=?", (payload.project_id,))
    if not project:
        raise HTTPException(status_code=404, detail="Projet introuvable.")
    target = _resolve_target(project, payload.kind, payload.target)
    if payload.kind == "php" and not target:
        raise HTTPException(status_code=400, detail="Aucun dossier de projet n'est configuré.")
    if payload.kind in {"web", "api"} and not target:
        raise HTTPException(status_code=400, detail="Aucune cible ou URL de base n'est configurée.")
    if payload.kind == "reverse" and not target:
        raise HTTPException(status_code=400, detail="Indiquez le binaire à analyser (chemin dans le dossier du projet).")
    decision = scope.check_scan_scope(project, payload.kind, target)
    if not decision.allowed:
        detail = decision.reason
        if decision.warnings:
            detail += " " + " ".join(decision.warnings)
        raise HTTPException(status_code=403, detail=detail)
    config = payload.config or {}
    # Garde-fous de configuration.
    config["max_files"] = min(10000, max(1, int(config.get("max_files", db.get_setting("max_files", "2500")) or 2500)))
    config["max_pages"] = min(10, max(1, int(config.get("max_pages", db.get_setting("max_pages", "3")) or 3)))
    config["max_exposed_paths"] = min(24, max(0, int(config.get("max_exposed_paths", 12) or 12)))
    if "trusted_script_domains" not in config:
        configured = str(db.get_setting("trusted_script_domains", "") or "")
        config["trusted_script_domains"] = [item.strip() for item in configured.split(",") if item.strip()]
    if "probe_exposed_files" not in config:
        config["probe_exposed_files"] = str(db.get_setting("probe_exposed_files", "true")).lower() in {"1", "true", "yes", "on"}
    if not config.get("user_agent"):
        config["user_agent"] = str(db.get_setting("user_agent", "") or "")[:200]
    scan = jobs.create_scan(project["id"], payload.kind, target, config)
    jobs.start_scan(scan["id"])
    db.audit("scan_started", {
        "scan_id": scan["id"], "project_id": project["id"], "kind": payload.kind,
        "target": target, "scope": decision.as_dict(),
    })
    return _scan(db.fetch_one("SELECT * FROM scans WHERE id=?", (scan["id"],)) or {}, detailed=True)


@router.get("")
def list_scans(project_id: str = "", kind: str = "", status: str = "", limit: int = 50) -> dict[str, Any]:
    where = []
    params: list[Any] = []
    if project_id:
        where.append("project_id=?")
        params.append(project_id)
    if kind:
        where.append("kind=?")
        params.append(kind)
    if status:
        where.append("status=?")
        params.append(status)
    clause = (" WHERE " + " AND ".join(where)) if where else ""
    rows = db.fetch_all(
        f"SELECT * FROM scans{clause} ORDER BY created_at DESC LIMIT ?",
        params + [min(200, max(1, limit))],
    )
    return {"items": [_scan(r) for r in rows]}


@router.get("/{scan_id}")
def get_scan(scan_id: str) -> dict[str, Any]:
    row = db.fetch_one("SELECT * FROM scans WHERE id=?", (scan_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Scan introuvable.")
    return _scan(row, detailed=True)


@router.get("/{scan_id}/findings")
def scan_findings(scan_id: str) -> dict[str, Any]:
    if not db.fetch_one("SELECT id FROM scans WHERE id=?", (scan_id,)):
        raise HTTPException(status_code=404, detail="Scan introuvable.")
    rows = db.fetch_all(
        "SELECT * FROM findings WHERE scan_id=? ORDER BY CASE severity WHEN 'critical' THEN 0 "
        "WHEN 'high' THEN 1 WHEN 'medium' THEN 2 WHEN 'low' THEN 3 ELSE 4 END, created_at",
        (scan_id,),
    )
    for row in rows:
        row["references"] = db.json_loads(row.pop("references_json", None), [])
    return {"items": rows, "severity": severity_counts(rows)}


@router.post("/{scan_id}/cancel")
def cancel_scan(scan_id: str) -> dict[str, Any]:
    row = db.fetch_one("SELECT status FROM scans WHERE id=?", (scan_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Scan introuvable.")
    ok = jobs.cancel_scan(scan_id)
    return {"ok": ok, "status": row["status"]}


@router.post("/{scan_id}/rerun")
def rerun_scan(scan_id: str) -> dict[str, Any]:
    row = db.fetch_one("SELECT * FROM scans WHERE id=?", (scan_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Scan introuvable.")
    project = db.fetch_one("SELECT * FROM projects WHERE id=?", (row["project_id"],))
    if not project:
        raise HTTPException(status_code=404, detail="Projet introuvable.")
    decision = scope.check_scan_scope(project, row["kind"], row["target"])
    if not decision.allowed:
        raise HTTPException(status_code=403, detail=decision.reason)
    config = db.json_loads(row.get("config_json"), {})
    scan = jobs.create_scan(project["id"], row["kind"], row["target"], config)
    jobs.start_scan(scan["id"])
    db.audit("scan_rerun", {"source_scan": scan_id, "scan_id": scan["id"]})
    return _scan(db.fetch_one("SELECT * FROM scans WHERE id=?", (scan["id"],)) or {}, detailed=True)


@router.delete("/{scan_id}")
def delete_scan(scan_id: str) -> dict[str, Any]:
    row = db.fetch_one("SELECT id FROM scans WHERE id=?", (scan_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Scan introuvable.")
    db.execute("DELETE FROM scans WHERE id=?", (scan_id,))
    db.audit("scan_deleted", {"scan_id": scan_id})
    return {"ok": True}
