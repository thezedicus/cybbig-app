"""API Confidentialité & Accessibilité : synthèse vocale, proxies, client VPN.

Modules locaux du poste. Les actions à effet réseau (test de proxy, IP de sortie,
connexion VPN) exigent le consentement accepté et sont journalisées.
"""
from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from .. import db
from ..services import proxy as proxy_svc
from ..services import tts as tts_svc
from ..services import vpn as vpn_svc
from ..services import vpn_engine
from ..services.scope import require_consent

router = APIRouter(prefix="/privacy", tags=["privacy"])


def _need_consent() -> None:
    decision = require_consent()
    if not decision.allowed:
        raise HTTPException(status_code=403, detail=decision.reason)


# --- Vue d'ensemble ----------------------------------------------------------

@router.get("")
def overview() -> dict[str, Any]:
    return {
        "tts": {"available": tts_svc.available(), "speaking": tts_svc.is_speaking()},
        "proxy": proxy_svc.status(),
        "vpn": vpn_svc.status(),
    }


# --- Synthèse vocale (TTS) ---------------------------------------------------

class SpeakPayload(BaseModel):
    text: str = Field(min_length=1, max_length=40000)
    voice: str = ""
    rate: int = Field(default=0, ge=-10, le=10)


@router.get("/tts/voices")
def tts_voices() -> dict[str, Any]:
    return {"available": tts_svc.available(), "voices": tts_svc.list_voices()}


@router.post("/tts/speak")
def tts_speak(payload: SpeakPayload) -> dict[str, Any]:
    try:
        return tts_svc.speak(payload.text, payload.voice, payload.rate)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/tts/stop")
def tts_stop() -> dict[str, Any]:
    return {"stopped": tts_svc.stop()}


@router.post("/tts/wav")
def tts_wav(payload: SpeakPayload):
    out = Path(tempfile.mkdtemp(prefix="cybbig-tts-")) / "cybbig-lecture.wav"
    try:
        tts_svc.synthesize_to_wav(payload.text, out, payload.voice, payload.rate)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return FileResponse(out, media_type="audio/wav", filename="cybbig-lecture.wav")


# --- Proxies -----------------------------------------------------------------

class ProxyCreate(BaseModel):
    scheme: str = "http"
    host: str = Field(min_length=1, max_length=255)
    port: int = Field(ge=1, le=65535)
    label: str = ""
    username: str = ""
    password: str = ""
    note: str = ""


class ProxyUpdate(BaseModel):
    scheme: str | None = None
    host: str | None = None
    port: int | None = None
    label: str | None = None
    username: str | None = None
    password: str | None = None
    note: str | None = None
    enabled: bool | None = None


class RoutePayload(BaseModel):
    enabled: bool


@router.get("/proxies")
def proxies_list() -> dict[str, Any]:
    return {"items": proxy_svc.list_proxies(), "status": proxy_svc.status()}


@router.post("/proxies")
def proxies_add(payload: ProxyCreate) -> dict[str, Any]:
    try:
        return proxy_svc.add_proxy(**payload.dict())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.put("/proxies/{pid}")
def proxies_update(pid: str, payload: ProxyUpdate) -> dict[str, Any]:
    try:
        return proxy_svc.update_proxy(pid, **payload.dict(exclude_none=True))
    except KeyError:
        raise HTTPException(status_code=404, detail="Proxy introuvable.")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.delete("/proxies/{pid}")
def proxies_delete(pid: str) -> dict[str, Any]:
    try:
        proxy_svc.delete_proxy(pid)
    except KeyError:
        raise HTTPException(status_code=404, detail="Proxy introuvable.")
    return {"ok": True}


@router.post("/proxies/{pid}/activate")
def proxies_activate(pid: str) -> dict[str, Any]:
    try:
        return proxy_svc.set_active(pid)
    except KeyError:
        raise HTTPException(status_code=404, detail="Proxy introuvable.")


@router.post("/proxies/deactivate")
def proxies_deactivate() -> dict[str, Any]:
    return proxy_svc.set_active(None)


@router.post("/proxies/route")
def proxies_route(payload: RoutePayload) -> dict[str, Any]:
    proxy_svc.set_route_scans(payload.enabled)
    return proxy_svc.status()


@router.post("/proxies/route-research")
def proxies_route_research(payload: RoutePayload) -> dict[str, Any]:
    proxy_svc.set_route_research(payload.enabled)
    return proxy_svc.status()


@router.post("/proxies/{pid}/test")
def proxies_test(pid: str) -> dict[str, Any]:
    _need_consent()
    try:
        return proxy_svc.test_proxy(pid)
    except KeyError:
        raise HTTPException(status_code=404, detail="Proxy introuvable.")


# --- VPN ---------------------------------------------------------------------

class VpnProfileCreate(BaseModel):
    config_path: str = Field(min_length=1)
    label: str = ""
    provider: str = ""
    kind: str = ""


@router.get("/vpn")
def vpn_status(with_ip: bool = False) -> dict[str, Any]:
    if with_ip:
        _need_consent()
    return vpn_svc.status(with_ip=with_ip)


@router.get("/vpn/profiles")
def vpn_profiles() -> dict[str, Any]:
    return {"items": vpn_svc.list_profiles(), "clients": vpn_svc.detect_clients()}


@router.post("/vpn/profiles")
def vpn_add_profile(payload: VpnProfileCreate) -> dict[str, Any]:
    try:
        return vpn_svc.add_profile(**payload.dict())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.delete("/vpn/profiles/{pid}")
def vpn_delete_profile(pid: str) -> dict[str, Any]:
    try:
        vpn_svc.delete_profile(pid)
    except KeyError:
        raise HTTPException(status_code=404, detail="Profil VPN introuvable.")
    return {"ok": True}


@router.post("/vpn/profiles/{pid}/connect")
def vpn_connect(pid: str) -> dict[str, Any]:
    _need_consent()
    try:
        return vpn_svc.connect(pid)
    except KeyError:
        raise HTTPException(status_code=404, detail="Profil VPN introuvable.")
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/vpn/disconnect")
def vpn_disconnect() -> dict[str, Any]:
    _need_consent()
    return vpn_svc.disconnect()


# --- Cybbig Tunnel : moteur VPN interne ---------------------------------------------------------

class BundlePayload(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    endpoint_host: str = Field(min_length=1, max_length=253)
    endpoint_port: int = Field(default=51820, ge=1, le=65535)
    subnet: str = "10.66.0.0/24"
    dns: list[str] = Field(default_factory=lambda: list(vpn_engine.DEFAULT_DNS), max_items=4)
    full_tunnel: bool = True
    use_preshared_key: bool = True


class AnalyzePayload(BaseModel):
    text: str = Field(min_length=1, max_length=20000)


def _engine(call, *args, **kwargs) -> Any:
    try:
        return call(*args, **kwargs)
    except vpn_engine.VpnEngineError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/vpn/bundle")
def vpn_bundle(payload: BundlePayload) -> dict[str, Any]:
    return _engine(vpn_engine.build_bundle, name=payload.name, endpoint_host=payload.endpoint_host, endpoint_port=payload.endpoint_port,
                   subnet=payload.subnet, dns=tuple(payload.dns), full_tunnel=payload.full_tunnel, use_preshared_key=payload.use_preshared_key)


@router.post("/vpn/analyze")
def vpn_analyze_text(payload: AnalyzePayload) -> dict[str, Any]:
    return vpn_engine.analyze_config(payload.text)


@router.get("/vpn/profiles/{pid}/analysis")
def vpn_profile_analysis(pid: str) -> dict[str, Any]:
    return _engine(vpn_engine.analyze_profile, pid)


@router.post("/vpn/profiles/{pid}/harden")
def vpn_profile_harden(pid: str) -> dict[str, Any]:
    return _engine(vpn_engine.harden_profile, pid)


@router.get("/vpn/ranking")
def vpn_ranking() -> dict[str, Any]:
    _need_consent()
    return {"items": vpn_engine.rank_profiles()}


@router.post("/vpn/quick-connect")
def vpn_quick_connect() -> dict[str, Any]:
    _need_consent()
    return _engine(vpn_engine.quick_connect)


@router.get("/proxies/presets")
def proxies_presets() -> dict[str, Any]:
    return {"items": proxy_svc.list_presets()}


@router.post("/proxies/presets/{key}")
def proxies_from_preset(key: str) -> dict[str, Any]:
    try:
        return proxy_svc.add_from_preset(key)
    except KeyError:
        raise HTTPException(status_code=404, detail="Modèle de proxy inconnu.")
