from __future__ import annotations

import re
from typing import Any

from .. import db
from ..utils import redact_text, truncate
from .engines.php_scanner import RULES, SECRET_KEY_RE, _likely_secret_value


def list_scenarios(category: str = "") -> list[dict[str, Any]]:
    if category:
        rows = db.fetch_all("SELECT * FROM lab_scenarios WHERE category=? ORDER BY title", (category,))
    else:
        rows = db.fetch_all("SELECT * FROM lab_scenarios ORDER BY category, title")
    for row in rows:
        row["references"] = db.json_loads(row.get("references_json"), [])
    return rows


def get_scenario(identifier: str) -> dict[str, Any] | None:
    row = db.fetch_one("SELECT * FROM lab_scenarios WHERE id=? OR slug=?", (identifier, identifier))
    if row:
        row["references"] = db.json_loads(row.get("references_json"), [])
    return row


def validate_code(code: str, language: str = "php") -> dict[str, Any]:
    """Analyse pédagogique de motifs, sans exécution du code fourni."""
    code = (code or "")[:100_000]
    hits: list[dict[str, Any]] = []
    if language.lower() in {"php", "phtml"}:
        for idx, line in enumerate(code.splitlines(), 1):
            for rule in RULES:
                if rule.rule_id == "php-xss-echo":
                    if re.search(r"\b(echo|print)\b", line, re.I) and not re.search(
                        r"htmlspecialchars|htmlentities|e\(", line, re.I
                    ) and re.search(r"\$_(GET|POST|REQUEST|COOKIE)|\$[A-Za-z_][A-Za-z0-9_]*", line):
                        hits.append({
                            "line": idx, "rule_id": rule.rule_id, "title": rule.title,
                            "severity": rule.severity, "evidence": redact_text(line.strip(), 300),
                        })
                    continue
                if rule.pattern.search(line) and not line.strip().startswith(("//", "#", "*")):
                    hits.append({
                        "line": idx, "rule_id": rule.rule_id, "title": rule.title,
                        "severity": rule.severity, "evidence": redact_text(line.strip(), 300),
                    })
            for m in SECRET_KEY_RE.finditer(line):
                if _likely_secret_value(m.group(2)):
                    hits.append({
                        "line": idx, "rule_id": "php-hardcoded-secret",
                        "title": f"Secret potentiel ({m.group(1)})",
                        "severity": "high", "evidence": redact_text(line.strip(), 300),
                    })
    elif language.lower() in {"javascript", "js", "typescript", "ts"}:
        js_rules = [
            ("js-eval", "Exécution dynamique eval/new Function", r"\b(eval|new\s+Function)\s*\(", "high"),
            ("js-svg-onload", "SVG avec onload", r"<svg[^>]*onload\s*=", "high"),
            ("js-atob", "Décodage base64", r"\batob\s*\(", "medium"),
            ("js-websocket", "WebSocket", r"new\s+WebSocket|wss://", "low"),
            ("js-innerhtml", "Écriture innerHTML", r"\.innerHTML\s*=", "medium"),
            ("js-document-write", "document.write", r"document\.write\s*\(", "medium"),
        ]
        for idx, line in enumerate(code.splitlines(), 1):
            for rule_id, title, pattern, sev in js_rules:
                if re.search(pattern, line, re.I):
                    hits.append({"line": idx, "rule_id": rule_id, "title": title, "severity": sev, "evidence": redact_text(line.strip(), 300)})
    else:
        for idx, line in enumerate(code.splitlines(), 1):
            if re.search(r"(password|secret|token|api[_-]?key)\s*=\s*['\"][^'\"]{8,}", line, re.I):
                hits.append({
                    "line": idx, "rule_id": "generic-secret",
                    "title": "Secret potentiel en clair", "severity": "high",
                    "evidence": redact_text(line.strip(), 300),
                })
    return {
        "hits": hits,
        "count": len(hits),
        "note": "Validation par motifs uniquement. Aucune exécution, aucun exploit. Les résultats doivent être confirmés par une revue manuelle.",
    }
