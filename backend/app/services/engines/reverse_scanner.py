"""Moteur de reverse engineering : pilote Ghidra en mode headless (analyzeHeadless).

Le backend Cybbig (orchestrateur de scans) importe un binaire local dans un projet
Ghidra temporaire, lance l'analyse automatique, puis exécute le post-script
``ReaHeadlessReport.java`` qui exporte un rapport JSON. Le moteur transforme ce
rapport en findings de triage (imports sensibles, indicateurs réseau/persistance).

Passif par conception : le binaire est analysé statiquement, jamais exécuté.
"""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
import threading
import time
from pathlib import Path
from typing import Any

from ...config import (
    GHIDRA_ANALYSIS_TIMEOUT,
    GHIDRA_HOME,
    GHIDRA_TIMEOUT_SECONDS,
    MAX_BINARY_BYTES,
)
from ...utils import truncate
from ..base import ScanContext

_SCRIPT_DIR = Path(__file__).resolve().parent / "ghidra_scripts"
_POST_SCRIPT = "ReaHeadlessReport.java"

# Imports natifs à surveiller lors d'un triage de reverse engineering.
# (indicateur -> (sévérité, catégorie courte, explication défensive))
_SUSPICIOUS_IMPORTS: dict[str, tuple[str, str, str]] = {
    # Injection / exécution de code
    "virtualalloc": ("medium", "Exécution mémoire", "Allocation mémoire exécutable (shellcode/unpacking possible)."),
    "virtualallocex": ("high", "Injection", "Allocation mémoire dans un autre processus (injection)."),
    "virtualprotect": ("medium", "Exécution mémoire", "Changement de protection mémoire (RWX, déchiffrement de code)."),
    "writeprocessmemory": ("high", "Injection", "Écriture dans la mémoire d'un autre processus (injection)."),
    "createremotethread": ("high", "Injection", "Création d'un thread distant (technique d'injection classique)."),
    "ntunmapviewofsection": ("high", "Injection", "Process hollowing possible."),
    "queueuserapc": ("high", "Injection", "Injection via APC."),
    "setthreadcontext": ("high", "Injection", "Détournement de contexte de thread (hollowing)."),
    "winexec": ("medium", "Exécution", "Exécution d'un programme externe."),
    "shellexecute": ("medium", "Exécution", "Exécution d'un programme/commande externe."),
    "shellexecutew": ("medium", "Exécution", "Exécution d'un programme/commande externe."),
    "createprocess": ("low", "Exécution", "Lancement de processus."),
    "createprocessw": ("low", "Exécution", "Lancement de processus."),
    "system": ("medium", "Exécution", "Exécution d'une commande shell."),
    # Réseau
    "urldownloadtofile": ("high", "Réseau", "Téléchargement de fichier distant (dropper/stager)."),
    "internetopenurl": ("medium", "Réseau", "Requête HTTP sortante."),
    "internetreadfile": ("medium", "Réseau", "Lecture de données distantes."),
    "wininethttpopenrequest": ("low", "Réseau", "Requête HTTP via WinINet."),
    "wsastartup": ("low", "Réseau", "Initialisation sockets."),
    "connect": ("low", "Réseau", "Connexion socket sortante."),
    "send": ("info", "Réseau", "Envoi de données réseau."),
    "recv": ("info", "Réseau", "Réception de données réseau."),
    # Persistance / registre / services
    "regsetvalueex": ("medium", "Persistance", "Écriture dans le registre (persistance possible)."),
    "regcreatekeyex": ("low", "Persistance", "Création de clé de registre."),
    "createservice": ("medium", "Persistance", "Installation d'un service (persistance)."),
    "startservice": ("low", "Persistance", "Démarrage d'un service."),
    # Anti-analyse
    "isdebuggerpresent": ("low", "Anti-analyse", "Détection de débogueur."),
    "checkremotedebuggerpresent": ("low", "Anti-analyse", "Détection de débogueur distant."),
    "ntqueryinformationprocess": ("low", "Anti-analyse", "Peut servir à détecter un débogueur."),
    "outputdebugstring": ("info", "Anti-analyse", "Peut servir au timing anti-débogueur."),
    "gettickcount": ("info", "Anti-analyse", "Peut servir au timing anti-sandbox."),
    # Crypto / credentials
    "cryptencrypt": ("medium", "Crypto", "Chiffrement (ransomware/obfuscation à vérifier)."),
    "cryptacquirecontext": ("low", "Crypto", "Usage de l'API de cryptographie."),
    "bcryptencrypt": ("medium", "Crypto", "Chiffrement (CNG)."),
    "crypthashdata": ("low", "Crypto", "Hachage de données."),
    # Hooking / keylogging
    "setwindowshookex": ("high", "Surveillance", "Hook global (keylogger possible)."),
    "getasynckeystate": ("medium", "Surveillance", "Lecture clavier (keylogger possible)."),
    "getkeyboardstate": ("medium", "Surveillance", "Lecture clavier (keylogger possible)."),
}


def _resolve_binary(ctx: ScanContext, target: str) -> Path:
    """Résout le binaire cible et vérifie qu'il reste dans le dossier du projet."""
    root = Path(ctx.project.get("path") or "").resolve()
    if not root or not root.is_dir():
        raise RuntimeError("Aucun dossier de projet valide n'est configuré.")
    raw = (target or "").strip().strip('"')
    if not raw:
        raise RuntimeError("Indiquez le chemin du binaire à analyser (dans le dossier du projet).")
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = root / candidate
    resolved = candidate.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise RuntimeError("Le binaire doit se trouver dans le dossier du projet.") from exc
    if not resolved.exists() or not resolved.is_file():
        raise RuntimeError(f"Binaire introuvable : {raw}")
    size = resolved.stat().st_size
    if size == 0:
        raise RuntimeError("Le fichier est vide.")
    if size > MAX_BINARY_BYTES:
        raise RuntimeError(
            f"Binaire trop volumineux ({size} octets > {MAX_BINARY_BYTES}). "
            "Augmentez CYBBIG_MAX_BINARY_BYTES si c'est intentionnel."
        )
    return resolved


def _analyze_headless_path() -> Path:
    home = Path(GHIDRA_HOME)
    name = "analyzeHeadless.bat" if os.name == "nt" else "analyzeHeadless"
    bat = home / "support" / name
    if not bat.exists():
        raise RuntimeError(
            f"analyzeHeadless introuvable sous {home}. "
            "Définissez CYBBIG_GHIDRA_HOME vers l'installation Ghidra."
        )
    return bat


def _run_ghidra(ctx: ScanContext, binary: Path, out_json: Path, project_dir: Path) -> str:
    bat = _analyze_headless_path()
    project_name = f"cybbig_{ctx.scan_id[:8]}"
    comspec = os.environ.get("COMSPEC", "cmd.exe") if os.name == "nt" else ""
    base = [comspec, "/c", str(bat)] if os.name == "nt" else [str(bat)]
    cmd = base + [
        str(project_dir),
        project_name,
        "-import", str(binary),
        "-scriptPath", str(_SCRIPT_DIR),
        "-postScript", _POST_SCRIPT, str(out_json),
        "-analysisTimeoutPerFile", str(GHIDRA_ANALYSIS_TIMEOUT),
        "-deleteProject",
    ]
    ctx.log(f"Lancement de Ghidra headless sur {binary.name}", 20)
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0,
    )
    deadline = time.time() + GHIDRA_TIMEOUT_SECONDS
    out_lines: list[str] = []
    try:
        while True:
            if proc.poll() is not None:
                break
            if ctx.cancelled():
                _terminate(proc)
                raise RuntimeError("Analyse annulée.")
            if time.time() > deadline:
                _terminate(proc)
                raise RuntimeError(f"Ghidra a dépassé le délai de {GHIDRA_TIMEOUT_SECONDS}s.")
            time.sleep(0.5)
        # Récupère le reste de la sortie.
        remaining = proc.stdout.read() if proc.stdout else ""
        if remaining:
            out_lines.append(remaining)
    finally:
        if proc.stdout:
            proc.stdout.close()
    log = "".join(out_lines)
    if proc.returncode not in (0, None):
        tail = "\n".join(log.strip().splitlines()[-12:])
        raise RuntimeError(f"Ghidra a échoué (code {proc.returncode}).\n{tail}")
    return log


def _terminate(proc: subprocess.Popen) -> None:
    try:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
    except Exception:  # noqa: BLE001
        pass


def _emit_findings(ctx: ScanContext, report: dict[str, Any], binary_name: str) -> None:
    imports = report.get("imports") or []
    seen: dict[str, dict[str, Any]] = {}
    for imp in imports:
        name = str(imp.get("name") or "")
        key = name.lower().lstrip("_").rstrip("aw")  # CreateProcessW/A, _system, ...
        info = _SUSPICIOUS_IMPORTS.get(name.lower()) or _SUSPICIOUS_IMPORTS.get(key)
        if not info:
            continue
        severity, category, explanation = info
        bucket = seen.setdefault(name.lower(), {
            "name": name, "library": imp.get("library", ""),
            "severity": severity, "category": category, "explanation": explanation,
        })
        bucket["library"] = bucket["library"] or imp.get("library", "")

    for data in seen.values():
        ctx.add_finding(
            engine="reverse",
            rule_id=f"ghidra-import-{data['name'].lower()}",
            title=f"Import sensible : {data['name']}",
            severity=data["severity"],
            confidence="low",
            category=f"Reverse · {data['category']}",
            description=(
                f"Le binaire importe {data['name']} "
                f"({data['library'] or 'bibliothèque inconnue'}). {data['explanation']} "
                "Indicateur de triage statique : à corréler avec le contexte, ce n'est pas une preuve de malveillance."
            ),
            evidence=f"{binary_name} → import {data['name']} ({data['library']})",
            file_path=binary_name,
            remediation="Confirmer l'origine du binaire et analyser l'usage réel de cette API dans le flux de code.",
            references=["https://attack.mitre.org/"],
        )

    # Indicateurs réseau dans les chaînes (URLs / IP).
    strings = report.get("strings") or []
    url_hits = [s.get("value", "") for s in strings if "://" in str(s.get("value", ""))][:15]
    if url_hits:
        ctx.add_finding(
            engine="reverse", rule_id="ghidra-embedded-urls",
            title=f"{len(url_hits)} URL(s) intégrée(s) dans le binaire",
            severity="info", confidence="medium", category="Reverse · Réseau",
            description="Des URL sont présentes dans les chaînes du binaire. Utile pour identifier des points de contact réseau.",
            evidence=truncate("\n".join(url_hits), 1500),
            file_path=binary_name,
            remediation="Vérifier les domaines contactés et leur légitimité.",
        )


def run(ctx: ScanContext) -> None:
    target = (ctx.scan.get("target") or "").strip()
    binary = _resolve_binary(ctx, target)
    ctx.log(f"Préparation de l'analyse de {binary.name}", 10)

    tmp_dir = Path(tempfile.mkdtemp(prefix="cybbig-ghidra-"))
    out_json = tmp_dir / "rea_report.json"
    try:
        log = _run_ghidra(ctx, binary, out_json, tmp_dir)
        if ctx.cancelled():
            return
        if not out_json.exists():
            tail = "\n".join(log.strip().splitlines()[-12:])
            raise RuntimeError(f"Ghidra n'a pas produit de rapport.\n{tail}")
        ctx.log("Lecture du rapport Ghidra", 80)
        report = json.loads(out_json.read_text(encoding="utf-8", errors="replace"))
    finally:
        _cleanup(tmp_dir)

    program = report.get("program", {}) or {}
    ctx.extra.update({
        "engine": "reverse",
        "mode": "ghidra-headless",
        "binary": binary.name,
        "program": program,
        "function_count": report.get("function_count", 0),
        "decompiled_count": report.get("decompiled_count", 0),
        "import_count": report.get("import_count", 0),
        "export_count": report.get("export_count", 0),
        "string_count": report.get("string_count", 0),
        "functions_sample": (report.get("functions") or [])[:50],
        "decompiled_functions": (report.get("decompiled_functions") or [])[:12],
        "imports_sample": (report.get("imports") or [])[:100],
        "exports_sample": (report.get("exports") or [])[:50],
        "strings_sample": (report.get("strings") or [])[:100],
    })

    # Finding récapitulatif (toujours présent, même sans indicateur sensible).
    ctx.add_finding(
        engine="reverse", rule_id="ghidra-summary",
        title=f"Analyse Ghidra : {binary.name}",
        severity="info", confidence="high", category="Reverse · Synthèse",
        description=(
            f"Format {program.get('format', '?')}, architecture {program.get('language', '?')}. "
            f"{report.get('function_count', 0)} fonctions, {report.get('import_count', 0)} imports, "
            f"{report.get('export_count', 0)} exports, {report.get('string_count', 0)} chaînes définies, "
            f"{report.get('decompiled_count', 0)} fonction(s) décompilée(s) pour le triage. "
            f"SHA-256 {program.get('sha256', '')}."
        ),
        evidence=f"{binary.name} — image base {program.get('image_base', '')}",
        file_path=binary.name,
        remediation="Relire les extraits décompilés et les recouper avec les appels et les références du binaire.",
    )

    _emit_findings(ctx, report, binary.name)
    ctx.log("Analyse de reverse engineering terminée", 95)


def _cleanup(path: Path) -> None:
    import shutil

    for _ in range(3):
        try:
            shutil.rmtree(path, ignore_errors=False)
            return
        except OSError:
            time.sleep(0.5)
    shutil.rmtree(path, ignore_errors=True)
