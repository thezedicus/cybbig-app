from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Any

from .. import db
from ..utils import finding_dict, now_iso, severity_counts, risk_score


@dataclass
class ScanContext:
    scan: dict[str, Any]
    project: dict[str, Any]
    config: dict[str, Any]
    cancel_event: threading.Event = field(default_factory=threading.Event)
    findings: list[dict[str, Any]] = field(default_factory=list)
    dependencies: list[dict[str, Any]] = field(default_factory=list)
    _seen: set[str] = field(default_factory=set)
    extra: dict[str, Any] = field(default_factory=dict)

    @property
    def scan_id(self) -> str:
        return self.scan["id"]

    @property
    def project_id(self) -> str:
        return self.project["id"]

    def cancelled(self) -> bool:
        return self.cancel_event.is_set()

    def log(self, message: str, progress: int | None = None) -> None:
        if self.cancelled():
            return
        if progress is None:
            db.execute("UPDATE scans SET message=? WHERE id=?", (message[:500], self.scan_id))
        else:
            db.execute(
                "UPDATE scans SET message=?, progress=? WHERE id=?",
                (message[:500], max(0, min(99, int(progress))), self.scan_id),
            )

    def add_finding(self, **kwargs: Any) -> None:
        finding = finding_dict(project_id=self.project_id, scan_id=self.scan_id, **kwargs)
        key = "|".join(
            str(finding.get(k) or "")
            for k in ("engine", "rule_id", "file_path", "url", "line_start", "title")
        )
        if key in self._seen:
            return
        self._seen.add(key)
        self.findings.append(finding)

    def add_dependency(self, **kwargs: Any) -> None:
        dep = {
            "id": f"dep-{len(self.dependencies)}-{self.scan_id[:8]}",
            "project_id": self.project_id,
            "scan_id": self.scan_id,
            "ecosystem": kwargs.get("ecosystem", "Packagist"),
            "package": kwargs.get("package", ""),
            "version": kwargs.get("version", ""),
            "vulnerable": 1 if kwargs.get("vulnerable") else 0,
            "vuln_id": kwargs.get("vuln_id", ""),
            "severity": kwargs.get("severity", ""),
            "summary": kwargs.get("summary", ""),
            "fixed_version": kwargs.get("fixed_version", ""),
            "source": kwargs.get("source", ""),
            "created_at": now_iso(),
        }
        self.dependencies.append(dep)

    def summary(self) -> dict[str, Any]:
        counts = severity_counts(self.findings)
        return {
            "findings": len(self.findings),
            "severity": counts,
            "risk_score": risk_score(self.findings),
            "dependencies": len(self.dependencies),
            "vulnerable_dependencies": sum(1 for d in self.dependencies if d["vulnerable"]),
            "extra": self.extra,
        }

    def persist(self) -> None:
        if not self.findings and not self.dependencies:
            return
        with db.db_cursor() as conn:
            for f in self.findings:
                conn.execute(
                    """INSERT INTO findings(
                        id,project_id,scan_id,engine,rule_id,category,title,severity,
                        confidence,description,evidence,file_path,line_start,line_end,
                        url,cwe,owasp,remediation,references_json,fingerprint,status,
                        risk_score,created_at,updated_at
                    ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    ON CONFLICT(scan_id, fingerprint) DO UPDATE SET
                        severity=excluded.severity,
                        description=excluded.description,
                        evidence=excluded.evidence,
                        remediation=excluded.remediation,
                        updated_at=excluded.updated_at""",
                    (
                        f["id"], f["project_id"], f["scan_id"], f["engine"], f["rule_id"],
                        f["category"], f["title"], f["severity"], f["confidence"],
                        f["description"], f["evidence"], f["file_path"], f["line_start"],
                        f["line_end"], f["url"], f["cwe"], f["owasp"], f["remediation"],
                        f["references_json"], f["fingerprint"], f["status"],
                        f["risk_score"], f["created_at"], f["updated_at"],
                    ),
                )
            for d in self.dependencies:
                conn.execute(
                    """INSERT OR REPLACE INTO dependencies(
                        id,project_id,scan_id,ecosystem,package,version,vulnerable,
                        vuln_id,severity,summary,fixed_version,source,created_at
                    ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        d["id"], d["project_id"], d["scan_id"], d["ecosystem"],
                        d["package"], d["version"], d["vulnerable"], d["vuln_id"],
                        d["severity"], d["summary"], d["fixed_version"], d["source"],
                        d["created_at"],
                    ),
                )
