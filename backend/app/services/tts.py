"""Synthèse vocale locale (équivalent Balabolka) via l'API System.Speech de Windows.

100 % local, aucune requête réseau. Sert à lire à voix haute les rapports et
findings de Cybbig, ou à exporter un fichier WAV. S'appuie sur les voix SAPI
installées sur le poste (PowerShell + System.Speech).
"""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
import threading
from pathlib import Path
from typing import Any

from ..config import TTS_MAX_CHARS

_lock = threading.Lock()
_current: subprocess.Popen | None = None

_PS = ["powershell", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass"]
_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0


def available() -> bool:
    return os.name == "nt"


def _clean(text: str) -> str:
    text = (text or "").replace("\x00", " ").strip()
    if not text:
        raise RuntimeError("Aucun texte à lire.")
    return text[:TTS_MAX_CHARS]


def list_voices() -> list[dict[str, Any]]:
    if not available():
        return []
    script = (
        "Add-Type -AssemblyName System.Speech;"
        "$s=New-Object System.Speech.Synthesis.SpeechSynthesizer;"
        "$s.GetInstalledVoices() | Where-Object {$_.Enabled} | ForEach-Object {"
        "  $i=$_.VoiceInfo;"
        "  [PSCustomObject]@{name=$i.Name;culture=$i.Culture.Name;gender=$i.Gender.ToString();age=$i.Age.ToString()}"
        "} | ConvertTo-Json -Compress"
    )
    try:
        out = subprocess.run(
            _PS + ["-Command", script],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=30, creationflags=_NO_WINDOW,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise RuntimeError(f"Énumération des voix impossible : {exc}") from exc
    data = (out.stdout or "").strip()
    if not data:
        return []
    try:
        parsed = json.loads(data)
    except json.JSONDecodeError:
        return []
    if isinstance(parsed, dict):
        parsed = [parsed]
    return parsed if isinstance(parsed, list) else []


def _build_script(text_file: Path, *, voice: str, rate: int, wav: Path | None) -> str:
    lines = [
        "Add-Type -AssemblyName System.Speech;",
        "$s=New-Object System.Speech.Synthesis.SpeechSynthesizer;",
        f"$s.Rate={max(-10, min(10, int(rate)))};",
    ]
    if voice:
        safe = voice.replace("'", "''")
        lines.append(f"try{{$s.SelectVoice('{safe}')}}catch{{}};")
    tf = str(text_file).replace("'", "''")
    lines.append(f"$t=Get-Content -Raw -Encoding UTF8 -LiteralPath '{tf}';")
    if wav is not None:
        wf = str(wav).replace("'", "''")
        lines.append(f"$s.SetOutputToWaveFile('{wf}');")
    lines.append("$s.Speak($t);$s.Dispose();")
    return "".join(lines)


def speak(text: str, voice: str = "", rate: int = 0) -> dict[str, Any]:
    """Lit le texte sur les haut-parleurs. Non bloquant ; une seule lecture à la fois."""
    if not available():
        raise RuntimeError("La synthèse vocale n'est disponible que sous Windows.")
    text = _clean(text)
    stop()  # une lecture à la fois
    tmp = Path(tempfile.mkdtemp(prefix="cybbig-tts-"))
    text_file = tmp / "speak.txt"
    text_file.write_text(text, encoding="utf-8")
    script = _build_script(text_file, voice=voice, rate=rate, wav=None)
    global _current
    with _lock:
        _current = subprocess.Popen(
            _PS + ["-Command", script],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            creationflags=_NO_WINDOW,
        )
    return {"speaking": True, "chars": len(text), "voice": voice or "défaut"}


def stop() -> bool:
    global _current
    with _lock:
        proc = _current
        _current = None
    if proc and proc.poll() is None:
        try:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
        except OSError:
            pass
        return True
    return False


def is_speaking() -> bool:
    with _lock:
        return bool(_current and _current.poll() is None)


def synthesize_to_wav(text: str, out_path: Path, voice: str = "", rate: int = 0) -> Path:
    """Génère un fichier WAV (lecture différée, intégration aux rapports)."""
    if not available():
        raise RuntimeError("La synthèse vocale n'est disponible que sous Windows.")
    text = _clean(text)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="cybbig-tts-"))
    text_file = tmp / "speak.txt"
    text_file.write_text(text, encoding="utf-8")
    script = _build_script(text_file, voice=voice, rate=rate, wav=out_path)
    try:
        res = subprocess.run(
            _PS + ["-Command", script],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=180, creationflags=_NO_WINDOW,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise RuntimeError(f"Synthèse WAV impossible : {exc}") from exc
    if not out_path.exists() or out_path.stat().st_size == 0:
        raise RuntimeError(f"La synthèse n'a produit aucun fichier. {res.stderr[:300]}")
    return out_path
