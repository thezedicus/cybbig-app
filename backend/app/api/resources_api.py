from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .. import db
from ..services import ai, resources

router = APIRouter(prefix="/resources", tags=["ressources du poste"])


class ProfilePayload(BaseModel):
    profile: str = Field(max_length=12)
    num_thread: int | None = Field(default=None, ge=1, le=128)


@router.get("")
def status() -> dict[str, Any]:
    """Matériel détecté, charge en direct, réglages Ollama appliqués et recommandations."""
    return resources.status()


@router.put("/profile")
def set_profile(payload: ProfilePayload) -> dict[str, Any]:
    if payload.profile not in resources.PROFILES:
        raise HTTPException(status_code=400, detail="Profil inconnu.")
    db.set_setting("perf_profile", payload.profile)
    db.set_setting("perf_num_thread", "" if payload.num_thread is None else str(payload.num_thread))
    db.audit("perf_profile_changed", {"profile": payload.profile, "num_thread": payload.num_thread})
    resources.reset_cache()
    return resources.status()


@router.post("/warmup")
def warmup() -> dict[str, Any]:
    """Précharge le modèle local en mémoire (évite l'attente du premier appel)."""
    return {"warmed": ai.warm_up(force=True)}
