from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .. import db
from ..config import ACTIVITY_LEVELS
from ..services import scope
from ..utils import new_id, now_iso, risk_score, severity_counts

router = APIRouter(prefix="/projects", tags=["projets"])


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    client: str = Field(default="", max_length=200)
    description: str = Field(default="", max_length=2000)
    path: str = Field(default="", max_length=1000)
    base_url: str = Field(default="", max_length=2000)
    environment: str = Field(default="laboratory", max_length=40)
    authorization_ref: str = Field(default="", max_length=300)
    authorized_by: str = Field(default="", max_length=200)
    authorization_confirmed: bool = False
    scope_domains: list[str] = Field(default_factory=list)
    scope_paths: list[str] = Field(default_factory=list)
    activity_level: str = "B"


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    client: str | None = Field(default=None, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    path: str | None = Field(default=None, max_length=1000)
    base_url: str | None = Field(default=None, max_length=2000)
    environment: str | None = Field(default=None, max_length=40)
    authorization_ref: str | None = Field(default=None, max_length=300)
    authorized_by: str | None = Field(default=None, max_length=200)
    authorization_confirmed: bool | None = None
    scope_domains: list[str] | None = None
    scope_paths: list[str] | None = None
    activity_level: str | None = None


class ScopeCheck(BaseModel):
    kind: str
    target: str = ""


def _domains(values: list[str]) -> list[str]:
    result = []
    for raw in values[:100]:
        value = str(raw).strip().lower()
        if not value:
            continue
        if "://" in value:
            value = urlparse(value).hostname or ""
        value = value.strip().strip("/")
        if value.startswith("*."):
            value = value[2:]
        if value and len(value) <= 253 and " " not in value:
            result.append(value)
    return sorted(set(result))


def _base_url(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return ""
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise HTTPException(status_code=400, detail="L'URL de base doit commencer par http:// ou https://.")
    if parsed.username or parsed.password:
        raise HTTPException(status_code=400, detail="Les identifiants dans l'URL ne sont pas acceptés.")
    return value.rstrip("/")


def _serialize(row: dict[str, Any], detailed: bool = False) -> dict[str, Any]:
    project = dict(row)
    project["scope_domains"] = db.json_loads(project.get("scope_domains"), [])
    project["scope_paths"] = db.json_loads(project.get("scope_paths"), [])
    project["authorization_confirmed"] = bool(project.get("authorization_confirmed"))
    findings = db.fetch_all(
        "SELECT severity,status,risk_score FROM findings WHERE project_id=?", (project["id"],)
    )
    counts = severity_counts(findings)
    open_findings = [f for f in findings if f["status"] not in {"fixed", "false_positive"}]
    project["severity"] = counts
    project["findings_count"] = len(findings)
    project["open_findings"] = len(open_findings)
    project["risk_score"] = risk_score(open_findings)
    project["scans_count"] = db.fetch_one("SELECT COUNT(*) AS c FROM scans WHERE project_id=?", (project["id"],))["c"]  # type: ignore[index]
    last = db.fetch_one("SELECT id,kind,status,created_at,finished_at FROM scans WHERE project_id=? ORDER BY created_at DESC LIMIT 1", (project["id"],))
    project["last_scan"] = last
    project["path_exists"] = bool(project.get("path")) and Path(project["path"]).is_dir()
    if detailed:
        project["recent_scans"] = db.fetch_all(
            "SELECT id,kind,status,progress,target,summary_json,created_at,finished_at FROM scans WHERE project_id=? ORDER BY created_at DESC LIMIT 10",
            (project["id"],),
        )
        for scan in project["recent_scans"]:
            scan["summary"] = db.json_loads(scan.pop("summary_json"), {})
        project["top_findings"] = db.fetch_all(
            "SELECT id,title,severity,engine,rule_id,file_path,url,status,created_at FROM findings "
            "WHERE project_id=? AND status NOT IN ('fixed','false_positive') "
            "ORDER BY CASE severity WHEN 'critical' THEN 0 WHEN 'high' THEN 1 WHEN 'medium' THEN 2 WHEN 'low' THEN 3 ELSE 4 END, created_at DESC LIMIT 12",
            (project["id"],),
        )
        project["activity_label"] = ACTIVITY_LEVELS.get(project.get("activity_level", "B"), "")
    return project


@router.get("")
def list_projects() -> dict[str, Any]:
    rows = db.fetch_all("SELECT * FROM projects ORDER BY updated_at DESC")
    return {"items": [_serialize(r) for r in rows]}


@router.post("")
def create_project(payload: ProjectCreate) -> dict[str, Any]:
    if payload.activity_level not in ACTIVITY_LEVELS:
        raise HTTPException(status_code=400, detail="Niveau d'activité invalide (A–E).")
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Le nom du projet est requis.")
    base = _base_url(payload.base_url)
    path = payload.path.strip()
    if path:
        try:
            path = str(Path(path).expanduser().resolve())
        except OSError:
            pass
    project_id = new_id("proj")
    now = now_iso()
    confirmed = bool(payload.authorization_confirmed)
    db.execute(
        """INSERT INTO projects(id,name,client,description,path,base_url,environment,
           authorization_ref,authorized_by,authorized_at,authorization_confirmed,
           scope_domains,scope_paths,activity_level,created_at,updated_at)
           VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            project_id, name, payload.client.strip(), payload.description.strip(), path, base,
            payload.environment.strip() or "laboratory", payload.authorization_ref.strip(),
            payload.authorized_by.strip(), now if confirmed else None, 1 if confirmed else 0,
            db.json_dumps(_domains(payload.scope_domains)), db.json_dumps(payload.scope_paths[:50]),
            payload.activity_level, now, now,
        ),
    )
    db.audit("project_created", {"project_id": project_id, "name": name, "activity_level": payload.activity_level})
    row = db.fetch_one("SELECT * FROM projects WHERE id=?", (project_id,))
    return _serialize(row or {}, detailed=True)


@router.get("/{project_id}")
def get_project(project_id: str) -> dict[str, Any]:
    row = db.fetch_one("SELECT * FROM projects WHERE id=?", (project_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Projet introuvable.")
    return _serialize(row, detailed=True)


@router.put("/{project_id}")
def update_project(project_id: str, payload: ProjectUpdate) -> dict[str, Any]:
    row = db.fetch_one("SELECT * FROM projects WHERE id=?", (project_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Projet introuvable.")
    data = payload.dict(exclude_unset=True)
    if "activity_level" in data and data["activity_level"] not in ACTIVITY_LEVELS:
        raise HTTPException(status_code=400, detail="Niveau d'activité invalide (A–E).")
    fields: list[str] = []
    params: list[Any] = []
    if "base_url" in data:
        data["base_url"] = _base_url(data["base_url"] or "")
    if "path" in data:
        raw = (data["path"] or "").strip()
        data["path"] = str(Path(raw).expanduser().resolve()) if raw else ""
    for key in ("name", "client", "description", "path", "base_url", "environment", "authorization_ref", "authorized_by", "activity_level"):
        if key in data:
            fields.append(f"{key}=?")
            params.append((data[key] or "").strip() if isinstance(data[key], str) else data[key])
    if "authorization_confirmed" in data:
        fields.append("authorization_confirmed=?")
        params.append(1 if data["authorization_confirmed"] else 0)
        if data["authorization_confirmed"]:
            fields.append("authorized_at=?")
            params.append(now_iso())
    if "scope_domains" in data:
        fields.append("scope_domains=?")
        params.append(db.json_dumps(_domains(data["scope_domains"] or [])))
    if "scope_paths" in data:
        fields.append("scope_paths=?")
        params.append(db.json_dumps((data["scope_paths"] or [])[:50]))
    fields.append("updated_at=?")
    params.append(now_iso())
    params.append(project_id)
    db.execute(f"UPDATE projects SET {', '.join(fields)} WHERE id=?", params)
    db.audit("project_updated", {"project_id": project_id, "fields": list(data.keys())})
    return _serialize(db.fetch_one("SELECT * FROM projects WHERE id=?", (project_id,)) or {}, detailed=True)


@router.delete("/{project_id}")
def delete_project(project_id: str) -> dict[str, Any]:
    row = db.fetch_one("SELECT name FROM projects WHERE id=?", (project_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Projet introuvable.")
    db.execute("DELETE FROM projects WHERE id=?", (project_id,))
    db.audit("project_deleted", {"project_id": project_id, "name": row["name"]})
    return {"ok": True}


@router.post("/{project_id}/scope/check")
def check_scope(project_id: str, payload: ScopeCheck) -> dict[str, Any]:
    row = db.fetch_one("SELECT * FROM projects WHERE id=?", (project_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Projet introuvable.")
    project = _serialize(row)
    target = payload.target or (project.get("path") if payload.kind == "php" else project.get("base_url"))
    decision = scope.check_scan_scope(project, payload.kind, target or "")
    return decision.as_dict()
