from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field

from ..services import admin, ai_agents, ai_tasks, code_assistant, code_editor, owner

router = APIRouter(prefix="/admin", tags=["administration"])


def require_admin(x_admin_token: str | None = Header(default=None)) -> str:
    if not admin.check_session(x_admin_token):
        raise HTTPException(status_code=401, detail="Session administrateur requise ou expirée.")
    return x_admin_token or ""


class LoginPayload(BaseModel):
    identifier: str = Field(min_length=1, max_length=200)
    password: str = Field(min_length=1, max_length=200)


class OwnerActivatePayload(BaseModel):
    challenge: str = Field(min_length=1, max_length=200)
    signature: str = Field(min_length=1, max_length=200)
    identifier: str = Field(min_length=1, max_length=200)
    password: str = Field(min_length=1, max_length=200)


class CredentialsPayload(BaseModel):
    current_password: str = Field(min_length=1, max_length=200)
    new_identifier: str = Field(min_length=1, max_length=200)
    new_password: str = Field(min_length=1, max_length=200)


class SettingsPayload(BaseModel):
    values: dict[str, Any]


class ExecPayload(BaseModel):
    code: str = Field(min_length=1, max_length=20000)
    shell: str = Field(default="powershell", max_length=20)
    cwd: str = Field(default="root", max_length=500)
    timeout: int = Field(default=120, ge=5, le=900)
    stdin: str = Field(default="", max_length=20000)


class SqlPayload(BaseModel):
    sql: str = Field(min_length=1, max_length=20000)


@router.get("/status")
def status() -> dict[str, Any]:
    return {"configured": admin.is_configured()}


@router.post("/owner/challenge")
def owner_challenge() -> dict[str, Any]:
    return owner.new_challenge()


@router.post("/owner/activate")
def owner_activate(payload: OwnerActivatePayload) -> dict[str, Any]:
    try:
        admin.owner_activate(payload.challenge, payload.signature, payload.identifier, payload.password)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"ok": True}


@router.post("/login")
def login(payload: LoginPayload) -> dict[str, Any]:
    try:
        return admin.login(payload.identifier, payload.password)
    except PermissionError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


@router.get("/session")
def session(token: str = Depends(require_admin)) -> dict[str, Any]:
    return {"ok": True, "must_change": admin.must_change()}


@router.post("/logout")
def logout(token: str = Depends(require_admin)) -> dict[str, Any]:
    admin.logout(token)
    return {"ok": True}


@router.post("/credentials")
def change_credentials(payload: CredentialsPayload, token: str = Depends(require_admin)) -> dict[str, Any]:
    try:
        admin.change_credentials(payload.current_password, payload.new_identifier, payload.new_password)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"ok": True}


@router.get("/overview")
def overview(token: str = Depends(require_admin)) -> dict[str, Any]:
    return admin.overview()


@router.get("/settings")
def get_settings(token: str = Depends(require_admin)) -> dict[str, Any]:
    return {"values": admin.list_settings()}


@router.put("/settings")
def put_settings(payload: SettingsPayload, token: str = Depends(require_admin)) -> dict[str, Any]:
    return {"ok": True, "changed": admin.update_settings(payload.values)}


@router.delete("/settings/{key}")
def delete_setting(key: str, token: str = Depends(require_admin)) -> dict[str, Any]:
    try:
        admin.delete_setting(key)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"ok": True}


@router.post("/exec")
def execute(payload: ExecPayload, token: str = Depends(require_admin)) -> dict[str, Any]:
    try:
        return admin.execute(payload.code, payload.shell, payload.cwd, payload.timeout, payload.stdin)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/exec/history")
def exec_history(limit: int = 50, token: str = Depends(require_admin)) -> dict[str, Any]:
    return {"items": admin.exec_history(limit)}


class CodeWritePayload(BaseModel):
    path: str = Field(min_length=1, max_length=500)
    content: str = Field(default="", max_length=3_000_000)
    force: bool = False
    create: bool = False


class CodeRestorePayload(BaseModel):
    backup: str = Field(min_length=1, max_length=60)
    path: str = Field(min_length=1, max_length=500)


def _code_call(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/code/tree")
def code_tree(path: str = "", token: str = Depends(require_admin)) -> dict[str, Any]:
    return _code_call(code_editor.tree, path)


@router.get("/code/file")
def code_read(path: str, token: str = Depends(require_admin)) -> dict[str, Any]:
    return _code_call(code_editor.read, path)


@router.put("/code/file")
def code_write(payload: CodeWritePayload, token: str = Depends(require_admin)) -> dict[str, Any]:
    return _code_call(code_editor.write, payload.path, payload.content, payload.force, payload.create)


@router.delete("/code/file")
def code_delete(path: str, token: str = Depends(require_admin)) -> dict[str, Any]:
    return _code_call(code_editor.delete, path)


@router.get("/code/backups")
def code_backups(token: str = Depends(require_admin)) -> dict[str, Any]:
    return {"items": code_editor.backups()}


@router.post("/code/restore")
def code_restore(payload: CodeRestorePayload, token: str = Depends(require_admin)) -> dict[str, Any]:
    return _code_call(code_editor.restore, payload.backup, payload.path)


@router.post("/ai/suggestions/{suggestion_id}/{action}")
def decide_suggestion(suggestion_id: str, action: str, token: str = Depends(require_admin)) -> dict[str, Any]:
    return _code_call(ai_agents.decide, suggestion_id, action)


@router.post("/restart")
def restart_service(token: str = Depends(require_admin)) -> dict[str, Any]:
    code_editor.schedule_restart()
    return {"ok": True, "message": "Redémarrage du service local…"}


class ActiveModePayload(BaseModel):
    enabled: bool


@router.put("/active-mode")
def set_active_mode(payload: ActiveModePayload, token: str = Depends(require_admin)) -> dict[str, Any]:
    admin.update_settings({"active_mode": "true" if payload.enabled else "false"})
    return {"active": payload.enabled}


@router.put("/web-research-mode")
def set_web_research_mode(payload: ActiveModePayload, token: str = Depends(require_admin)) -> dict[str, Any]:
    """Le propriétaire peut activer des recherches publiques plus larges, sans désactiver les contrôles réseau."""
    admin.update_settings({"web_research_mode": "true" if payload.enabled else "false"})
    return {"enabled": payload.enabled}


@router.get("/web-research-mode")
def get_web_research_mode(token: str = Depends(require_admin)) -> dict[str, Any]:
    from .. import db
    return {"enabled": str(db.get_setting("web_research_mode", "false")).lower() == "true"}


@router.post("/ai/run")
def run_ai_task(payload: dict[str, Any], token: str = Depends(require_admin)) -> StreamingResponse:
    try:
        stream = ai_tasks.stream(str(payload.get("task") or ""), payload.get("params") or {}, admin=True)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return StreamingResponse(stream, media_type="application/x-ndjson")


@router.post("/sql")
def run_sql(payload: SqlPayload, token: str = Depends(require_admin)) -> dict[str, Any]:
    try:
        return admin.run_sql(payload.sql)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/backups")
def list_backups(token: str = Depends(require_admin)) -> dict[str, Any]:
    return {"items": admin.list_backups()}


@router.post("/backups")
def create_backup(token: str = Depends(require_admin)) -> dict[str, Any]:
    return admin.create_backup()


@router.delete("/backups/{name}")
def delete_backup(name: str, token: str = Depends(require_admin)) -> dict[str, Any]:
    try:
        admin.delete_backup(name)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"ok": True}


@router.get("/backups/{name}/download")
def download_backup(name: str, token: str = Depends(require_admin)) -> FileResponse:
    try:
        path = admin.backup_path(name)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return FileResponse(path, filename=path.name, media_type="application/octet-stream")


# --- Atelier IA : un modèle propose des modifications de code, le propriétaire valide ---------------

class CodeAskPayload(BaseModel):
    instruction: str = Field(min_length=1, max_length=6000)
    paths: list[str] = Field(default_factory=list, max_items=code_assistant.MAX_FILES)
    history: list[dict[str, str]] = Field(default_factory=list, max_items=12)
    model: str | None = Field(default=None, max_length=120)


class CodeEdit(BaseModel):
    path: str = Field(max_length=500)
    search: str = Field(default="", max_length=200_000)
    replace: str = Field(default="", max_length=200_000)


class CodeApplyPayload(BaseModel):
    edits: list[CodeEdit] = Field(min_items=1, max_items=40)


@router.get("/code/search")
def code_search(q: str = "", token: str = Depends(require_admin)) -> dict[str, Any]:
    return {"items": code_assistant.search_files(q)}


@router.post("/code/assist")
def code_assist(payload: CodeAskPayload, token: str = Depends(require_admin)) -> StreamingResponse:
    try:
        stream = code_assistant.stream(payload.instruction, payload.paths, payload.history, payload.model)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return StreamingResponse(stream, media_type="application/x-ndjson")


@router.post("/code/assist/preview")
def code_assist_preview(payload: CodeApplyPayload, token: str = Depends(require_admin)) -> dict[str, Any]:
    return {"edits": _code_call(code_assistant.preview, [e.dict() for e in payload.edits])}


@router.post("/code/assist/apply")
def code_assist_apply(payload: CodeApplyPayload, token: str = Depends(require_admin)) -> dict[str, Any]:
    return _code_call(code_assistant.apply, [e.dict() for e in payload.edits])
