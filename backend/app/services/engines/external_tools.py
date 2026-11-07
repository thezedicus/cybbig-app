from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from ... import db
from ...utils import truncate
from ..base import ScanContext


PSALM_MAP = {
    "TaintedSql": ("injection.sql", "CWE-89", "critical"),
    "TaintedShell": ("injection.command", "CWE-78", "critical"),
    "TaintedEval": ("injection.code", "CWE-95", "critical"),
    "TaintedUnserialize": ("injection.deserialization", "CWE-502", "critical"),
    "TaintedInclude": ("injection.file", "CWE-98", "high"),
    "TaintedHtml": ("injection.xss", "CWE-79", "high"),
    "TaintedFile": ("file.path_traversal", "CWE-22", "high"),
    "TaintedSSRF": ("network.ssrf", "CWE-918", "high"),
    "TaintedLdap": ("injection.ldap", "CWE-90", "high"),
    "TaintedHeader": ("injection.header", "CWE-113", "medium"),
    "TaintedCookie": ("session.cookie_taint", "CWE-565", "medium"),
    "TaintedCallable": ("injection.callable", "CWE-470", "high"),
    "TaintedUserSecret": ("exposure.secret_user", "CWE-200", "medium"),
    "TaintedSystemSecret": ("exposure.secret_system", "CWE-200", "high"),
}


def _run(command: list[str], cwd: Path, timeout: int = 300) -> tuple[int, str, str]:
    try:
        completed = subprocess.run(
            command, cwd=str(cwd), capture_output=True, text=True,
            timeout=timeout, check=False,
        )
        return completed.returncode, completed.stdout or "", completed.stderr or ""
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 127, "", str(exc)


def _semgrep_available() -> bool:
    return shutil.which("semgrep") is not None


def run_semgrep(ctx: ScanContext, root: Path) -> None:
    if not _semgrep_available():
        return
    if str(db.get_setting("enable_external_tools", "true")).lower() not in {"1", "true", "yes", "on"}:
        return
    ctx.log("Semgrep (analyse statique externe)", 90)
    code, stdout, stderr = _run(
        ["semgrep", "scan", "--config", "p/php", "--config", "p/security-audit",
         "--json", "--quiet", str(root)],
        cwd=root, timeout=600,
    )
    if code not in {0, 1}:
        ctx.extra.setdefault("external_tools", {}).setdefault("semgrep", {"status": "error", "stderr": truncate(stderr, 500)})
        return
    try:
        data = json.loads(stdout or "{}")
    except json.JSONDecodeError:
        ctx.extra.setdefault("external_tools", {}).setdefault("semgrep", {"status": "parse_error"})
        return
    count = 0
    for result in data.get("results", []) or []:
        if ctx.cancelled():
            return
        path = result.get("path") or ""
        try:
            rel = str(Path(path).relative_to(root)) if Path(path).is_absolute() else path
        except ValueError:
            rel = path
        start = result.get("start") or {}
        line = int(start.get("line") or 0) or None
        extra = result.get("extra") or {}
        severity = str(extra.get("severity") or "medium").lower()
        if severity not in {"critical", "high", "medium", "low", "info"}:
            severity = "medium"
        ctx.add_finding(
            engine="php", rule_id=f"semgrep:{result.get('check_id', 'rule')}",
            title=f"Semgrep — {result.get('check_id', 'règle')}",
            severity=severity, confidence="high", category="Analyse externe (Semgrep)",
            description=extra.get("message") or "Résultat Semgrep.",
            evidence=f"{rel}:{line or '?'} — {truncate(extra.get('message') or '', 300)}",
            file_path=rel, line_start=line, url="",
            cwe="", owasp="", remediation="Corriger selon la règle Semgrep et la documentation associée.",
            references=[],
        )
        count += 1
        if count >= 200:
            break
    ctx.extra.setdefault("external_tools", {})["semgrep"] = {"status": "ok", "findings": count}


def _php_available() -> bool:
    return shutil.which("php") is not None


def run_psalm(ctx: ScanContext, root: Path) -> None:
    if not _php_available():
        return
    psalm = root / "vendor" / "bin" / "psalm"
    if not psalm.exists():
        psalm = Path(shutil.which("psalm") or "")
    if not psalm or not psalm.exists():
        return
    if str(db.get_setting("enable_external_tools", "true")).lower() not in {"1", "true", "yes", "on"}:
        return
    ctx.log("Psalm (taint analysis externe)", 93)
    code, stdout, stderr = _run(
        [shutil.which("php"), str(psalm), "--output-format=json", "--no-cache",
         "--no-progress", "--show-info=false", "--threads=4", "--taint-analysis"],
        cwd=root, timeout=600,
    )
    if code == 2:
        ctx.extra.setdefault("external_tools", {}).setdefault("psalm", {"status": "config_error", "stderr": truncate(stderr, 500)})
        return
    try:
        data = json.loads(stdout or "[]")
    except json.JSONDecodeError:
        ctx.extra.setdefault("external_tools", {}).setdefault("psalm", {"status": "parse_error", "stderr": truncate(stderr, 500)})
        return
    issues = data if isinstance(data, list) else (data.get("issues") if isinstance(data, dict) else [])
    count = 0
    for issue in issues or []:
        if ctx.cancelled():
            return
        issue_type = str(issue.get("type") or issue.get("check_id") or "PsalmIssue")
        if issue_type == "TaintedCustom":
            category = f"custom.{str(issue.get('custom_taint') or issue_type).lower()}"
            severity = "medium"
            cwe = ""
        elif issue_type == "TaintedSleep":
            category = "availability.dos"
            severity = "low"
            cwe = ""
        else:
            category, cwe, severity = PSALM_MAP.get(issue_type, (f"custom.{issue_type.lower()}", "", "medium"))
        rel = str(issue.get("file_path") or issue.get("file") or "")
        try:
            if Path(rel).is_absolute():
                rel = str(Path(rel).relative_to(root))
        except ValueError:
            pass
        line = issue.get("line_from") or issue.get("line") or issue.get("lineStart")
        try:
            line = int(line) if line is not None else None
        except (TypeError, ValueError):
            line = None
        confidence = "confirmed" if issue.get("trace") else "suspected"
        ctx.add_finding(
            engine="php", rule_id=f"psalm:{issue_type}",
            title=f"Psalm — {issue_type}",
            severity=severity, confidence=confidence, category=category,
            description=issue.get("message") or "Résultat Psalm.",
            evidence=f"{rel}:{line or '?'} — {truncate(issue.get('message') or issue.get('snippet') or '', 300)}",
            file_path=rel, line_start=line, url="",
            cwe=cwe, owasp="",
            remediation="Corriger selon le diagnostic Psalm et les bonnes pratiques PHP.",
            references=[],
        )
        count += 1
        if count >= 300:
            break
    ctx.extra.setdefault("external_tools", {})["psalm"] = {"status": "ok", "findings": count}


def run_phpstan(ctx: ScanContext, root: Path) -> None:
    if not _php_available():
        return
    phpstan = root / "vendor" / "bin" / "phpstan"
    if not phpstan.exists():
        phpstan = Path(shutil.which("phpstan") or "")
    if not phpstan or not phpstan.exists():
        return
    if str(db.get_setting("enable_external_tools", "true")).lower() not in {"1", "true", "yes", "on"}:
        return
    ctx.log("PHPStan (qualité externe)", 94)
    code, stdout, stderr = _run(
        [shutil.which("php"), str(phpstan), "analyse", "--error-format=json",
         "--no-progress", "--memory-limit=1G", "--level=6", str(root)],
        cwd=root, timeout=600,
    )
    try:
        data = json.loads(stdout or "{}")
    except json.JSONDecodeError:
        ctx.extra.setdefault("external_tools", {}).setdefault("phpstan", {"status": "parse_error", "stderr": truncate(stderr, 500)})
        return
    count = 0
    files = data.get("files") if isinstance(data, dict) else None
    if isinstance(files, dict):
        for file_path, info in files.items():
            rel = file_path
            try:
                if Path(rel).is_absolute():
                    rel = str(Path(rel).relative_to(root))
            except ValueError:
                pass
            for msg in (info.get("messages") or []):
                if ctx.cancelled():
                    return
                message = msg.get("message") if isinstance(msg, dict) else str(msg)
                line = msg.get("line") if isinstance(msg, dict) else None
                try:
                    line = int(line) if line is not None else None
                except (TypeError, ValueError):
                    line = None
                ctx.add_finding(
                    engine="php", rule_id="phpstan:quality",
                    title="PHPStan — incohérence de code",
                    severity="low", confidence="medium", category="Qualité (PHPStan)",
                    description=message or "Résultat PHPStan.",
                    evidence=f"{rel}:{line or '?'} — {truncate(message or '', 300)}",
                    file_path=rel, line_start=line, url="",
                    cwe="", owasp="A04:2021",
                    remediation="Corriger l'incohérence signalée par PHPStan.",
                    references=[],
                )
                count += 1
                if count >= 300:
                    break
    ctx.extra.setdefault("external_tools", {})["phpstan"] = {"status": "ok", "findings": count}


def _composer_available() -> bool:
    return shutil.which("composer") is not None


def run_composer_audit(ctx: ScanContext, root: Path) -> None:
    if not _composer_available():
        return
    if not (root / "composer.lock").exists():
        return
    if str(db.get_setting("enable_external_tools", "true")).lower() not in {"1", "true", "yes", "on"}:
        return
    ctx.log("Composer audit (dépendances)", 92)
    code, stdout, stderr = _run(["composer", "audit", "--format=json", "--no-interaction"], cwd=root, timeout=300)
    try:
        data = json.loads(stdout or "{}")
    except json.JSONDecodeError:
        ctx.extra.setdefault("external_tools", {}).setdefault("composer_audit", {"status": "parse_error", "stderr": truncate(stderr, 500)})
        return
    count = 0
    advisories = data.get("advisories") or {}
    if isinstance(advisories, dict):
        for package, items in advisories.items():
            for advisory in items or []:
                if ctx.cancelled():
                    return
                sev = str(advisory.get("severity") or "medium").lower()
                if sev not in {"critical", "high", "medium", "low", "info"}:
                    sev = "medium"
                ctx.add_finding(
                    engine="php", rule_id=f"composer:{advisory.get('advisoryId') or advisory.get('cve') or 'advisory'}",
                    title=f"Dépendance vulnérable : {package}",
                    severity=sev, confidence="high", category="Dépendances (Composer audit)",
                    description=advisory.get("title") or "Vulnérabilité connue dans une dépendance Composer.",
                    evidence=f"{package} — {advisory.get('advisoryId') or advisory.get('cve') or ''}",
                    file_path="composer.lock", line_start=None, url=advisory.get("link") or "",
                    cwe="", owasp="A06:2021",
                    remediation=f"Mettre à jour {package} vers une version corrigée. {advisory.get('affectedVersions') or ''}".strip(),
                    references=[advisory.get("link")] if advisory.get("link") else [],
                )
                count += 1
                if count >= 200:
                    break
    ctx.extra.setdefault("external_tools", {})["composer_audit"] = {"status": "ok", "findings": count}


def run_all(ctx: ScanContext, root: Path) -> None:
    run_semgrep(ctx, root)
    run_psalm(ctx, root)
    run_phpstan(ctx, root)
    run_composer_audit(ctx, root)