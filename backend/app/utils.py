from __future__ import annotations

import hashlib
import html
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from .config import SEVERITY_WEIGHT, SEVERITIES


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def new_id(prefix: str = "") -> str:
    value = str(uuid4())
    return f"{prefix}-{value}" if prefix else value


def fingerprint(*parts: Any) -> str:
    raw = "|".join("" if p is None else str(p) for p in parts)
    return hashlib.sha256(raw.encode("utf-8", errors="replace")).hexdigest()[:32]


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def severity_from_cvss(score: float | None) -> str:
    if score is None:
        return "unknown"
    if score >= 9.0:
        return "critical"
    if score >= 7.0:
        return "high"
    if score >= 4.0:
        return "medium"
    if score > 0:
        return "low"
    return "info"


def risk_score(findings: list[dict[str, Any]]) -> float:
    """Score 0-100 simple, plafonné, pondéré par la sévérité."""
    if not findings:
        return 0.0
    counts: dict[str, int] = {}
    for finding in findings:
        severity = finding.get("severity", "info")
        counts[severity] = counts.get(severity, 0) + 1
    return risk_score_from_counts(counts)


def risk_score_from_counts(counts: dict[str, int]) -> float:
    """Même score de risque, calculé sans matérialiser chaque résultat en mémoire."""
    if not counts or not any(counts.values()):
        return 0.0
    raw = sum(SEVERITY_WEIGHT.get(severity, 0) * count for severity, count in counts.items())
    # Une seule faille critique reste visible, sans prétendre à une précision scientifique.
    return round(clamp(100.0 * (1.0 - math.exp(-raw / 28.0)), 0, 100), 1)


def severity_counts(findings: list[dict[str, Any]]) -> dict[str, int]:
    counts = {s: 0 for s in SEVERITIES}
    for finding in findings:
        sev = finding.get("severity", "info")
        counts[sev] = counts.get(sev, 0) + 1
    return counts


def truncate(text: str | None, length: int = 5000) -> str:
    if not text:
        return ""
    text = str(text)
    return text if len(text) <= length else text[:length] + "…"


def redact_secret(value: str, keep: int = 4) -> str:
    if not value:
        return ""
    value = value.strip()
    if len(value) <= keep + 2:
        return "*" * len(value)
    return value[:keep] + "*" * min(24, max(6, len(value) - keep - 2)) + value[-2:]


SECRET_VALUE_RE = re.compile(
    r"""(?ix)
    (?P<key>[A-Za-z0-9_.\-]*(?:api[_-]?key|secret|passw(?:or)?d|token|private[_-]?key|access[_-]?key)[A-Za-z0-9_.\-]*)
    \s*[:=]\s*
    (?P<quote>['"]?)
    (?P<value>[^\s'";,]{6,})
    (?P=quote)
    """
)


def redact_text(text: str, max_len: int = 1200) -> str:
    """Masque les valeurs qui ressemblent à des secrets dans une preuve."""
    if not text:
        return ""

    def repl(match: re.Match[str]) -> str:
        value = match.group("value")
        return f"{match.group('key')} = {redact_secret(value)}"

    result = SECRET_VALUE_RE.sub(repl, text)
    return truncate(result, max_len)


def safe_json(value: Any, default: Any = None) -> Any:
    if value is None:
        return default
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(value)
    except (TypeError, ValueError):
        return default


def html_escape(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def read_text(path: Path, max_bytes: int = 2_000_000) -> str:
    try:
        data = path.read_bytes()
    except OSError:
        return ""
    if len(data) > max_bytes:
        data = data[:max_bytes]
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def safe_relpath(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve())).replace("\\", "/")
    except (ValueError, OSError):
        return path.name


def strip_html(value: str, limit: int = 500) -> str:
    text = re.sub(r"<script.*?</script>", " ", value, flags=re.I | re.S)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", html.unescape(text)).strip()
    return truncate(text, limit)


def finding_dict(
    *,
    project_id: str,
    scan_id: str,
    engine: str,
    rule_id: str,
    title: str,
    severity: str,
    description: str = "",
    evidence: str = "",
    category: str = "",
    confidence: str = "medium",
    file_path: str = "",
    line_start: int | None = None,
    line_end: int | None = None,
    url: str = "",
    cwe: str = "",
    owasp: str = "",
    remediation: str = "",
    references: list[str] | None = None,
    risk: float | None = None,
) -> dict[str, Any]:
    sev = severity if severity in SEVERITIES else "info"
    return {
        "id": new_id("find"),
        "project_id": project_id,
        "scan_id": scan_id,
        "engine": engine,
        "rule_id": rule_id,
        "category": category,
        "title": title,
        "severity": sev,
        "confidence": confidence,
        "description": truncate(description, 8000),
        "evidence": truncate(evidence, 4000),
        "file_path": file_path,
        "line_start": line_start,
        "line_end": line_end,
        "url": url,
        "cwe": cwe,
        "owasp": owasp,
        "remediation": truncate(remediation, 8000),
        "references_json": json.dumps(references or [], ensure_ascii=False),
        "fingerprint": fingerprint(engine, rule_id, file_path or url, line_start, title),
        "status": "open",
        "risk_score": risk if risk is not None else SEVERITY_WEIGHT.get(sev, 0),
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }
