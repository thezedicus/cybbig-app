"""Ressources du poste (processeur, mémoire, carte graphique) et réglages de performance de l'IA.

Cybbig ne « pilote » pas le matériel : il le détecte, mesure la charge, puis règle ce qui est réellement
réglable — les options envoyées à Ollama (threads, taille de contexte, lot de tokens) et le nombre de
tâches parallèles (analyses, file IA). Ollama décharge tout seul les couches du modèle sur un GPU compatible
(NVIDIA CUDA, AMD ROCm) ; un GPU intégré Intel n'est en général pas utilisé.
"""
from __future__ import annotations

import ctypes
import json
import os
import platform
import shutil
import subprocess
import threading
import time
from typing import Any

import requests

from .. import db

PROFILES = {
    "auto": "Automatique (selon le matériel)",
    "eco": "Économe (laisse de la place aux autres applications)",
    "balanced": "Équilibré",
    "max": "Performance maximale",
}
_NO_WINDOW = 0x08000000 if os.name == "nt" else 0
_lock = threading.Lock()
_hw_cache: dict[str, Any] = {}
_opt_cache: tuple[float, dict[str, Any]] | None = None
_cpu_sample: tuple[float, int, int] | None = None


def _run(command: list[str], timeout: int = 15) -> str:
    try:
        done = subprocess.run(command, capture_output=True, text=True, timeout=timeout, creationflags=_NO_WINDOW, check=False)
        return done.stdout or ""
    except (OSError, subprocess.SubprocessError):
        return ""


def _powershell_json(script: str) -> Any:
    out = _run(["powershell", "-NoProfile", "-NonInteractive", "-Command", f"{script} | ConvertTo-Json -Compress"])
    try:
        return json.loads(out) if out.strip() else None
    except ValueError:
        return None


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


# --- Détection statique (mise en cache pour la durée du processus) ---------------------------

def _detect_gpus() -> list[dict[str, Any]]:
    gpus: list[dict[str, Any]] = []
    smi = shutil.which("nvidia-smi")
    if smi:
        out = _run([smi, "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader,nounits"], timeout=10)
        for line in out.splitlines():
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 3 and parts[0]:
                try:
                    vram = int(float(parts[1]))
                except ValueError:
                    vram = 0
                gpus.append({"name": parts[0], "vendor": "NVIDIA", "vram_mb": vram, "driver": parts[2], "dedicated": True, "ollama_usable": True})
    if os.name == "nt":
        rows = _as_list(_powershell_json("Get-CimInstance Win32_VideoController | Select-Object Name,AdapterRAM,DriverVersion"))
        known = {g["name"].lower() for g in gpus}
        for row in rows:
            name = str(row.get("Name") or "").strip()
            if not name or name.lower() in known or "basic display" in name.lower() or "remote" in name.lower():
                continue
            lower = name.lower()
            vendor = "Intel" if "intel" in lower else "NVIDIA" if ("nvidia" in lower or "geforce" in lower or "rtx" in lower) else \
                "AMD" if ("amd" in lower or "radeon" in lower) else "Autre"
            integrated = vendor == "Intel" or "vega" in lower and "radeon" in lower and "rx" not in lower
            ram = int(row.get("AdapterRAM") or 0) // (1024 * 1024)
            gpus.append({"name": name, "vendor": vendor, "vram_mb": ram, "driver": str(row.get("DriverVersion") or ""),
                         "dedicated": not integrated, "ollama_usable": vendor in {"NVIDIA", "AMD"} and not integrated})
    return gpus


def _physical_cores(logical: int) -> int:
    if os.name == "nt":
        rows = _as_list(_powershell_json("Get-CimInstance Win32_Processor | Select-Object NumberOfCores"))
        total = sum(int(r.get("NumberOfCores") or 0) for r in rows)
        if total:
            return total
    return max(1, logical // 2)


def _cpu_name() -> str:
    if os.name == "nt":
        rows = _as_list(_powershell_json("Get-CimInstance Win32_Processor | Select-Object Name"))
        if rows and rows[0].get("Name"):
            return str(rows[0]["Name"]).strip()
    return platform.processor() or platform.machine()


def hardware() -> dict[str, Any]:
    with _lock:
        if _hw_cache:
            return dict(_hw_cache)
    logical = os.cpu_count() or 1
    info = {
        "cpu_name": _cpu_name(),
        "cores_physical": _physical_cores(logical),
        "cores_logical": logical,
        "ram_total_mb": memory()["total_mb"],
        "gpus": _detect_gpus(),
        "os": f"{platform.system()} {platform.release()}",
    }
    with _lock:
        _hw_cache.update(info)
    return dict(info)


# --- Mesures en direct ------------------------------------------------------------------------

class _MemoryStatus(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong), ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong), ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong), ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong), ("sullAvailExtendedVirtual", ctypes.c_ulonglong)]


def memory() -> dict[str, int]:
    if os.name == "nt":
        status = _MemoryStatus()
        status.dwLength = ctypes.sizeof(_MemoryStatus)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):  # type: ignore[attr-defined]
            total, free = status.ullTotalPhys // (1024 * 1024), status.ullAvailPhys // (1024 * 1024)
            return {"total_mb": int(total), "free_mb": int(free), "used_percent": int(status.dwMemoryLoad)}
    try:
        pages, avail, size = os.sysconf("SC_PHYS_PAGES"), os.sysconf("SC_AVPHYS_PAGES"), os.sysconf("SC_PAGE_SIZE")
        total, free = pages * size // (1024 * 1024), avail * size // (1024 * 1024)
        return {"total_mb": int(total), "free_mb": int(free), "used_percent": int(100 - 100 * free / max(1, total))}
    except (ValueError, OSError, AttributeError):
        return {"total_mb": 0, "free_mb": 0, "used_percent": 0}


def _system_times() -> tuple[int, int] | None:
    if os.name != "nt":
        return None

    class FileTime(ctypes.Structure):
        _fields_ = [("low", ctypes.c_uint32), ("high", ctypes.c_uint32)]

    idle, kernel, user = FileTime(), FileTime(), FileTime()
    if not ctypes.windll.kernel32.GetSystemTimes(ctypes.byref(idle), ctypes.byref(kernel), ctypes.byref(user)):  # type: ignore[attr-defined]
        return None
    value = lambda t: (t.high << 32) | t.low  # noqa: E731
    return value(idle), value(kernel) + value(user)  # le temps noyau comprend le temps d'inactivité


def cpu_load() -> float | None:
    """Charge globale du processeur en %, mesurée depuis l'appel précédent (premier appel ou échantillon périmé : 200 ms d'attente)."""
    global _cpu_sample
    first = _system_times()
    if first is None:
        try:
            return round(100 * os.getloadavg()[0] / (os.cpu_count() or 1), 1)  # type: ignore[attr-defined]
        except (AttributeError, OSError):
            return None
    with _lock:
        previous = _cpu_sample
    if previous is None or time.monotonic() - previous[0] > 30:
        previous = (time.monotonic(), first[0], first[1])
        time.sleep(0.2)
        current = _system_times() or first
    else:
        current = first
    with _lock:
        _cpu_sample = (time.monotonic(), current[0], current[1])
    idle, total = current[0] - previous[1], current[1] - previous[2]
    return round(max(0.0, min(100.0, 100.0 * (1 - idle / total))), 1) if total > 0 else None


def gpu_live() -> list[dict[str, Any]]:
    smi = shutil.which("nvidia-smi")
    if not smi:
        return []
    out = _run([smi, "--query-gpu=name,utilization.gpu,memory.used,memory.total,temperature.gpu", "--format=csv,noheader,nounits"], timeout=5)
    result = []
    for line in out.splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) >= 5:
            try:
                result.append({"name": parts[0], "load_percent": float(parts[1]), "vram_used_mb": int(float(parts[2])),
                               "vram_total_mb": int(float(parts[3])), "temperature_c": float(parts[4])})
            except ValueError:
                continue
    return result


def ollama_loaded() -> dict[str, Any]:
    """Modèles chargés dans le serveur local et part de leur mémoire placée sur le GPU (/api/ps)."""
    from . import ai  # import tardif
    url = ai._ollama_url()
    if not ai.is_local_url(url):
        return {"reachable": False, "models": []}
    try:
        r = requests.get(f"{url}/api/ps", timeout=2, headers=ai._ollama_headers(url))
        r.raise_for_status()
        models = []
        for m in r.json().get("models") or []:
            size, vram = int(m.get("size") or 0), int(m.get("size_vram") or 0)
            models.append({"name": m.get("name"), "size_mb": size // (1024 * 1024), "gpu_percent": round(100 * vram / size) if size else 0,
                           "expires_at": m.get("expires_at")})
        return {"reachable": True, "models": models}
    except (requests.RequestException, ValueError):
        return {"reachable": False, "models": []}


# --- Réglages ---------------------------------------------------------------------------------

def profile() -> str:
    value = str(db.get_setting("perf_profile", "auto") or "auto")
    return value if value in PROFILES else "auto"


def _effective_profile(hw: dict[str, Any]) -> str:
    chosen = profile()
    if chosen != "auto":
        return chosen
    if any(g["ollama_usable"] for g in hw["gpus"]):
        return "max"
    return "balanced" if hw["ram_total_mb"] >= 8000 else "eco"


def ollama_options() -> dict[str, Any]:
    """Options Ollama dérivées du matériel et du profil (mises en cache 30 s : appelées à chaque requête IA)."""
    global _opt_cache
    now = time.monotonic()
    if _opt_cache and _opt_cache[0] > now:
        return dict(_opt_cache[1])
    hw = hardware()
    effective = _effective_profile(hw)
    physical = hw["cores_physical"]
    if effective == "eco":
        options = {"num_thread": max(1, physical // 2), "num_ctx": 2048, "num_batch": 128}
    elif effective == "max":
        options = {"num_thread": max(1, physical), "num_ctx": 8192, "num_batch": 512}
    else:
        options = {"num_thread": max(1, physical), "num_ctx": 4096, "num_batch": 256}
    # Options STABLES (matériel + profil seulement) : changer num_ctx d'une requête à l'autre force Ollama à recharger le modèle.
    if hw["ram_total_mb"] and hw["ram_total_mb"] < 8000:
        options["num_ctx"] = min(options["num_ctx"], 2048)
    manual = str(db.get_setting("perf_num_thread", "") or "").strip()
    if manual.isdigit() and 1 <= int(manual) <= max(64, hw["cores_logical"]):
        options["num_thread"] = int(manual)
    _opt_cache = (now + 30, options)
    return dict(options)


def reset_cache() -> None:
    global _opt_cache
    _opt_cache = None


def recommended_workers(kind: str = "scans") -> int:
    """Nombre de tâches parallèles. Appelé à l'import : estimation rapide (cœurs logiques / 2), sans interroger WMI."""
    if kind == "ai_cloud":
        return 3  # le calcul est fait en ligne : seul le réseau limite
    physical = max(1, (os.cpu_count() or 2) // 2)
    return max(2, min(8, physical // 2 + 1))


def prime() -> None:
    """Détecte le matériel en arrière-plan au démarrage (quelques appels WMI, 1 à 3 s) pour que la première requête IA n'attende pas."""
    threading.Thread(target=hardware, name="cybbig-hw-detect", daemon=True).start()


def recommendations(hw: dict[str, Any], loaded: dict[str, Any]) -> list[str]:
    tips: list[str] = []
    usable = [g for g in hw["gpus"] if g["ollama_usable"]]
    if not usable:
        names = ", ".join(g["name"] for g in hw["gpus"]) or "aucune carte détectée"
        tips.append(f"Aucun GPU exploitable par Ollama ({names}) : l'IA locale tourne sur le processeur. "
                    "L'IA en ligne est la voie la plus rapide ; en local, préférez un modèle de 3 milliards de paramètres ou moins "
                    "(qwen2.5:3b, llama3.2:3b) aux modèles de 7 milliards.")
        if any(g["vendor"] == "Intel" for g in hw["gpus"]):
            tips.append("Un GPU intégré Intel n'est pas utilisé par défaut. Ollama propose un support Vulkan expérimental "
                        "(variable d'environnement OLLAMA_VULKAN=1, puis redémarrage d'Ollama) : le gain n'est pas garanti, à tester.")
    else:
        tips.append(f"GPU détecté : {usable[0]['name']}. Ollama y place automatiquement les couches du modèle ; "
                    "vérifiez la colonne « GPU % » ci-dessous une fois un modèle chargé.")
    if hw["ram_total_mb"] and hw["ram_total_mb"] < 12000:
        tips.append("Moins de 12 Go de mémoire vive : évitez les modèles de plus de 7 milliards de paramètres.")
    for model in loaded.get("models", []):
        if usable and model["gpu_percent"] < 50:
            tips.append(f"Le modèle {model['name']} n'est que partiellement sur le GPU ({model['gpu_percent']} %) : "
                        "un modèle plus petit ou une quantification plus légère accélérerait les réponses.")
    return tips


def status() -> dict[str, Any]:
    hw = hardware()
    loaded = ollama_loaded()
    effective = _effective_profile(hw)
    return {
        "hardware": hw,
        "live": {"cpu_percent": cpu_load(), "memory": memory(), "gpus": gpu_live()},
        "ollama": loaded,
        "profile": profile(),
        "profile_effective": effective,
        "profiles": PROFILES,
        "options": ollama_options(),
        "workers": {"scans": recommended_workers("scans"), "ai_cloud": recommended_workers("ai_cloud"), "ai_local": 1},
        "recommendations": recommendations(hw, loaded),
    }
