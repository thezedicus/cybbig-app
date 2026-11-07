from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, HTTPException

from .. import db
from ..services import ai, scheduler
from ..config import SEVERITIES
from ..utils import now_iso, risk_score_from_counts

router = APIRouter(tags=["tableau de bord"])
alerts_router = APIRouter(prefix="/alerts", tags=["alertes"])


@router.get("/dashboard")
def dashboard() -> dict[str, Any]:
    projects = db.fetch_all("SELECT id,name,client,base_url,path,activity_level,updated_at FROM projects ORDER BY updated_at DESC")
    severity = {name: 0 for name in SEVERITIES}
    project_counts: dict[str, dict[str, int]] = {}
    open_count = total_findings = 0
    for row in db.fetch_all(
        "SELECT project_id,severity,COUNT(*) AS total_count, "
        "SUM(CASE WHEN status NOT IN ('fixed','false_positive') THEN 1 ELSE 0 END) AS open_count "
        "FROM findings GROUP BY project_id,severity"
    ):
        total_findings += row["total_count"]
        count = row["open_count"] or 0
        if count:
            severity[row["severity"]] = severity.get(row["severity"], 0) + count
            open_count += count
            project_counts.setdefault(row["project_id"], {})[row["severity"]] = count
    scans = db.fetch_all(
        "SELECT s.id,s.kind,s.status,s.progress,s.target,s.created_at,s.finished_at,s.summary_json,p.name AS project_name "
        "FROM scans s LEFT JOIN projects p ON p.id=s.project_id ORDER BY s.created_at DESC LIMIT 8"
    )
    for scan in scans:
        scan["summary"] = db.json_loads(scan.pop("summary_json"), {})
    today = datetime.now(timezone.utc).date()
    first_day = today - timedelta(days=13)
    trend_rows = db.fetch_all(
        "SELECT date(created_at) AS day,severity,COUNT(*) AS count FROM findings "
        "WHERE created_at >= ? GROUP BY date(created_at),severity",
        (first_day.isoformat(),),
    )
    by_day: dict[str, dict[str, int]] = {}
    for row in trend_rows:
        by_day.setdefault(row["day"], {})[row["severity"]] = row["count"]
    trend = []
    for offset in range(14):
        day = first_day + timedelta(days=offset)
        counts = by_day.get(day.isoformat(), {})
        trend.append({"date": day.isoformat(), "total": sum(counts.values()),
                      "critical": counts.get("critical", 0), "high": counts.get("high", 0)})
    by_engine = db.fetch_all(
        "SELECT engine, COUNT(*) AS count FROM findings WHERE status NOT IN ('fixed','false_positive') GROUP BY engine ORDER BY count DESC"
    )
    by_project = []
    for p in projects[:8]:
        counts = project_counts.get(p["id"], {})
        by_project.append({**p, "risk_score": risk_score_from_counts(counts), "findings": sum(counts.values())})
    unread = db.fetch_one("SELECT COUNT(*) AS c FROM alerts WHERE read=0")["c"]  # type: ignore[index]
    latest_alerts = db.fetch_all(
        "SELECT id,severity,title,message,link,read,created_at FROM alerts ORDER BY created_at DESC LIMIT 8"
    )
    intel = db.fetch_one(
        "SELECT COUNT(*) AS total, SUM(exploited) AS exploited, MAX(fetched_at) AS last_fetch FROM threat_items"
    ) or {}
    return {
        "counts": {
            "projects": len(projects),
            "scans": db.fetch_one("SELECT COUNT(*) AS c FROM scans")["c"],  # type: ignore[index]
            "findings": open_count,
            "findings_total": total_findings,
            "alerts_unread": unread,
            "critical": severity.get("critical", 0),
            "high": severity.get("high", 0),
        },
        "risk_score": risk_score_from_counts(severity),
        "severity": severity,
        "trend": trend,
        "by_engine": by_engine,
        "projects": by_project,
        "recent_scans": scans,
        "alerts": latest_alerts,
        "intel": {
            "items": intel.get("total") or 0,
            "exploited": intel.get("exploited") or 0,
            "last_fetch": intel.get("last_fetch"),
        },
        "scheduler": scheduler.status(),
        "ai": ai.ollama_status(),
        "top_findings": db.fetch_all(
            "SELECT f.id,f.title,f.severity,f.engine,f.file_path,f.url,f.project_id,p.name AS project_name "
            "FROM findings f LEFT JOIN projects p ON p.id=f.project_id "
            "WHERE f.status NOT IN ('fixed','false_positive') "
            "ORDER BY CASE f.severity WHEN 'critical' THEN 0 WHEN 'high' THEN 1 WHEN 'medium' THEN 2 "
            "WHEN 'low' THEN 3 ELSE 4 END, f.created_at DESC LIMIT 8"
        ),
        "generated_at": now_iso(),
    }


@alerts_router.get("")
def list_alerts(unread_only: bool = False, limit: int = 100) -> dict[str, Any]:
    clause = " WHERE read=0" if unread_only else ""
    rows = db.fetch_all(
        f"SELECT * FROM alerts{clause} ORDER BY created_at DESC LIMIT ?", (min(500, max(1, limit)),)
    )
    return {"items": rows}


@alerts_router.patch("/{alert_id}/read")
def mark_read(alert_id: str) -> dict[str, Any]:
    if not db.fetch_one("SELECT id FROM alerts WHERE id=?", (alert_id,)):
        raise HTTPException(status_code=404, detail="Alerte introuvable.")
    db.execute("UPDATE alerts SET read=1 WHERE id=?", (alert_id,))
    return {"ok": True}


@alerts_router.post("/read-all")
def mark_all_read() -> dict[str, Any]:
    db.execute("UPDATE alerts SET read=1 WHERE read=0")
    return {"ok": True}


@alerts_router.delete("/{alert_id}")
def delete_alert(alert_id: str) -> dict[str, Any]:
    db.execute("DELETE FROM alerts WHERE id=?", (alert_id,))
    return {"ok": True}
