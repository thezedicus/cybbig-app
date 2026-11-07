from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from typing import Any

import requests

from .. import db
from ..config import USER_AGENT
from ..utils import new_id, now_iso, severity_from_cvss, truncate

CISA_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
NVD_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
CERT_URL = "https://www.cert.ssi.gouv.fr/feed/"
PHP_URL = "https://www.php.net/releases/index.php?json&version=8&max=6"


def _iso(value: str | None) -> str:
    if not value:
        return now_iso()
    value = value.strip()
    try:
        dt = parsedate_to_datetime(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).isoformat(timespec="seconds")
    except (TypeError, ValueError):
        pass
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d", "%d %b %Y"):
        try:
            return datetime.strptime(value[:26] if "." in value else value, fmt).replace(tzinfo=timezone.utc).isoformat(timespec="seconds")
        except ValueError:
            continue
    return now_iso()


def _norm_severity(value: str | None) -> str:
    v = (value or "").lower()
    return v if v in {"critical", "high", "medium", "low", "info", "unknown"} else "unknown"


def _insert_items(source: str, items: list[dict[str, Any]], known_kev: set[str]) -> int:
    if not items:
        return 0
    with db.db_cursor() as conn:
        before = conn.execute("SELECT COUNT(*) FROM threat_items WHERE source=?", (source,)).fetchone()[0]
        for item in items:
            cve = (item.get("cve") or "").upper()
            exploited = 1 if cve and cve in known_kev else int(item.get("exploited") or 0)
            conn.execute(
                """INSERT INTO threat_items(
                    source,external_id,title,summary,severity,cvss,published_at,modified_at,
                    product,cve,exploited,url,tags_json,raw_json,fetched_at
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(source, external_id) DO UPDATE SET
                    title=excluded.title,
                    summary=excluded.summary,
                    severity=excluded.severity,
                    cvss=excluded.cvss,
                    published_at=excluded.published_at,
                    modified_at=excluded.modified_at,
                    product=excluded.product,
                    cve=excluded.cve,
                    exploited=MAX(threat_items.exploited, excluded.exploited),
                    url=excluded.url,
                    tags_json=excluded.tags_json,
                    raw_json=excluded.raw_json,
                    fetched_at=excluded.fetched_at""",
                (
                    source, item["external_id"], item["title"][:500], truncate(item.get("summary"), 5000),
                    _norm_severity(item.get("severity")), item.get("cvss"),
                    item.get("published_at"), item.get("modified_at"),
                    item.get("product", "")[:300], cve, exploited,
                    item.get("url", "")[:2000], json.dumps(item.get("tags", []), ensure_ascii=False),
                    truncate(json.dumps(item.get("raw", {}), ensure_ascii=False), 50_000), now_iso(),
                ),
            )
        after = conn.execute("SELECT COUNT(*) FROM threat_items WHERE source=?", (source,)).fetchone()[0]
        return max(0, after - before)


def _mark_source(name: str, status: str, count: int, error: str = "") -> None:
    db.execute(
        "UPDATE threat_sources SET status=?, last_sync_at=?, items_count=?, error=? WHERE name=?",
        (status, now_iso(), count, truncate(error, 1000), name),
    )


def _known_kev() -> set[str]:
    rows = db.fetch_all("SELECT cve FROM threat_items WHERE source='cisa_kev' AND cve != ''")
    return {r["cve"].upper() for r in rows}


def sync_cisa() -> dict[str, Any]:
    r = requests.get(CISA_URL, headers={"User-Agent": USER_AGENT}, timeout=45)
    r.raise_for_status()
    data = r.json()
    items = []
    for v in (data.get("vulnerabilities") or [])[:3000]:
        cve = v.get("cveID", "")
        items.append({
            "external_id": cve or f"kev-{len(items)}",
            "title": v.get("vulnerabilityName") or cve,
            "summary": " | ".join(filter(None, [
                v.get("shortDescription"), f"Action : {v.get('requiredAction')}" if v.get("requiredAction") else "",
                f"Échéance : {v.get('dueDate')}" if v.get("dueDate") else "",
                f"Ransomware connu : {v.get('knownRansomwareCampaignUse')}" if v.get("knownRansomwareCampaignUse") else "",
            ])),
            "severity": "high",
            "cvss": None,
            "published_at": _iso(v.get("dateAdded")),
            "modified_at": _iso(v.get("dateAdded")),
            "product": " ".join(filter(None, [v.get("vendorProject"), v.get("product")])),
            "cve": cve,
            "exploited": 1,
            "url": f"https://nvd.nist.gov/vuln/detail/{cve}" if cve else "https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
            "tags": ["KEV", "exploited"] + (v.get("cwes") or []),
            "raw": v,
        })
    new = _insert_items("cisa_kev", items, set())
    total = db.fetch_one("SELECT COUNT(*) AS c FROM threat_items WHERE source='cisa_kev'")["c"]  # type: ignore[index]
    _mark_source("cisa_kev", "ok", total)
    if new:
        _alert("cisa_kev", "high", f"{new} nouvelle(s) vulnérabilité(s) exploitée(s) dans KEV",
               "Le catalogue CISA des vulnérabilités exploitées a été actualisé.", "/intel?source=cisa_kev")
    return {"source": "cisa_kev", "status": "ok", "new": new, "total": total}


def _nvd_cvss(cve: dict) -> tuple[float | None, str]:
    metrics = cve.get("metrics", {}) or {}
    for key in ("cvssMetricV40", "cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
        arr = metrics.get(key) or []
        if not arr:
            continue
        first = arr[0]
        data = first.get("cvssData", {}) or {}
        score = data.get("baseScore")
        sev = data.get("baseSeverity") or first.get("baseSeverity")
        if score is not None:
            return float(score), _norm_severity(sev) if sev else severity_from_cvss(float(score))
    return None, "unknown"


def sync_nvd(days: int = 14, max_items: int = 150, api_key: str = "") -> dict[str, Any]:
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=max(1, days))
    params = {
        "pubStartDate": start.strftime("%Y-%m-%dT%H:%M:%S.000"),
        "pubEndDate": end.strftime("%Y-%m-%dT%H:%M:%S.000"),
        "resultsPerPage": min(2000, max(1, max_items)),
    }
    headers = {"User-Agent": USER_AGENT}
    if api_key:
        headers["apiKey"] = api_key
    r = requests.get(NVD_URL, params=params, headers=headers, timeout=60)
    if r.status_code == 403:
        raise RuntimeError("NVD a refusé la requête (403). Ajoutez une clé API dans les paramètres ou réessayez plus tard.")
    r.raise_for_status()
    data = r.json()
    vulnerabilities = data.get("vulnerabilities") or []
    known = _known_kev()
    items = []
    for entry in vulnerabilities[:max_items]:
        cve = entry.get("cve", {}) or {}
        cve_id = cve.get("id", "")
        descriptions = cve.get("descriptions", []) or []
        desc = next((d.get("value") for d in descriptions if d.get("lang") == "en"), None) or next((d.get("value") for d in descriptions), "")
        score, sev = _nvd_cvss(cve)
        cwes = []
        for w in cve.get("weaknesses", []) or []:
            for d in w.get("description", []) or []:
                if d.get("value", "").startswith("CWE-"):
                    cwes.append(d["value"])
        products = []
        for cfg in cve.get("configurations", []) or []:
            for node in cfg.get("nodes", []) or []:
                for match in node.get("cpeMatch", []) or []:
                    criteria = match.get("criteria", "")
                    parts = criteria.split(":")
                    if len(parts) > 4:
                        products.append(f"{parts[3]}:{parts[4]}")
        items.append({
            "external_id": cve_id,
            "title": cve_id or "CVE sans identifiant",
            "summary": truncate(desc, 4000),
            "severity": sev,
            "cvss": score,
            "published_at": _iso(cve.get("published")),
            "modified_at": _iso(cve.get("lastModified")),
            "product": ", ".join(sorted(set(products))[:8]),
            "cve": cve_id,
            "exploited": 0,
            "url": f"https://nvd.nist.gov/vuln/detail/{cve_id}" if cve_id else "",
            "tags": sorted(set(cwes))[:12],
            "raw": {"id": cve_id, "descriptions": descriptions, "metrics": cve.get("metrics", {}), "weaknesses": cve.get("weaknesses", [])},
        })
    new = _insert_items("nvd", items, known)
    total = db.fetch_one("SELECT COUNT(*) AS c FROM threat_items WHERE source='nvd'")["c"]  # type: ignore[index]
    _mark_source("nvd", "ok", total)
    if new:
        _alert("nvd", "medium", f"{new} nouvelle(s) CVE indexée(s) par NVD",
               f"Fenêtre analysée : {days} jour(s).", "/intel?source=nvd")
    return {"source": "nvd", "status": "ok", "new": new, "total": total}


def _rss_text(node: ET.Element, names: tuple[str, ...]) -> str:
    for child in node:
        name = child.tag.split("}")[-1].lower()
        if name in names and (child.text or "").strip():
            return (child.text or "").strip()
        if name == "link" and child.get("href"):
            return child.get("href", "")
    return ""


def sync_cert_fr() -> dict[str, Any]:
    r = requests.get(CERT_URL, headers={"User-Agent": USER_AGENT}, timeout=40)
    r.raise_for_status()
    root = ET.fromstring(r.content)
    items = []
    for node in root.iter():
        tag = node.tag.split("}")[-1].lower()
        if tag not in {"item", "entry"}:
            continue
        title = _rss_text(node, ("title",)) or "Avis CERT-FR"
        link = _rss_text(node, ("link", "id", "guid"))
        desc = _rss_text(node, ("description", "summary", "content"))
        date = _rss_text(node, ("pubdate", "published", "updated"))
        guid = _rss_text(node, ("guid", "id")) or link or title
        cves = sorted(set(re.findall(r"CVE-\d{4}-\d{4,7}", title + " " + desc)))
        sev = "high" if re.search(r"alerte|critique|critical", title, re.I) else "medium"
        items.append({
            "external_id": guid[-400:],
            "title": title[:500],
            "summary": truncate(re.sub(r"<[^>]+>", " ", desc), 3000),
            "severity": sev,
            "cvss": None,
            "published_at": _iso(date),
            "modified_at": _iso(date),
            "product": "",
            "cve": cves[0] if cves else "",
            "exploited": 0,
            "url": link,
            "tags": cves + ["CERT-FR"],
            "raw": {"title": title, "link": link, "description": desc, "date": date},
        })
    new = _insert_items("cert_fr", items, _known_kev())
    total = db.fetch_one("SELECT COUNT(*) AS c FROM threat_items WHERE source='cert_fr'")["c"]  # type: ignore[index]
    _mark_source("cert_fr", "ok", total)
    if new:
        _alert("cert_fr", "high", f"{new} nouvelle(s) publication(s) CERT-FR",
               "Le flux d'alertes et d'avis a été actualisé.", "/intel?source=cert_fr")
    return {"source": "cert_fr", "status": "ok", "new": new, "total": total}


def sync_php() -> dict[str, Any]:
    r = requests.get(PHP_URL, headers={"User-Agent": USER_AGENT}, timeout=30)
    r.raise_for_status()
    data = r.json()
    items = []
    for version, info in data.items():
        if not isinstance(info, dict):
            continue
        tags = info.get("tags", []) or []
        items.append({
            "external_id": f"php-{version}",
            "title": f"PHP {version}",
            "summary": "Version publiée" + (" avec correctifs de sécurité" if "security" in tags else "") + f" le {info.get('date','')}.",
            "severity": "medium" if "security" in tags else "info",
            "cvss": None,
            "published_at": _iso(info.get("date")),
            "modified_at": _iso(info.get("date")),
            "product": "PHP",
            "cve": "",
            "exploited": 0,
            "url": f"https://www.php.net/ChangeLog-{version.split('.')[0]}.php",
            "tags": tags + ["PHP"],
            "raw": {"version": version, "date": info.get("date"), "tags": tags},
        })
    new = _insert_items("php_releases", items, set())
    total = db.fetch_one("SELECT COUNT(*) AS c FROM threat_items WHERE source='php_releases'")["c"]  # type: ignore[index]
    _mark_source("php_releases", "ok", total)
    if new:
        _alert("php_releases", "medium", f"{new} version(s) PHP indexée(s)",
               "Vérifiez les versions corrigées et l'inventaire de vos serveurs.", "/intel?source=php_releases")
    return {"source": "php_releases", "status": "ok", "new": new, "total": total}


def _alert(source: str, severity: str, title: str, message: str, link: str) -> None:
    db.execute(
        "INSERT INTO alerts(id,project_id,source,severity,title,message,link,created_at) VALUES(?,?,?,?,?,?,?,?)",
        (new_id("alert"), None, source, severity, title[:300], message[:1000], link, now_iso()),
    )


EPSS_URL = "https://api.first.org/data/v1/epss"


def enrich_epss(limit: int = 600) -> dict[str, Any]:
    """Ajoute le score EPSS (probabilité d'exploitation sous 30 jours, FIRST.org) aux CVE qui n'en ont pas."""
    cves = [r["cve"] for r in db.fetch_all(
        "SELECT DISTINCT cve FROM threat_items WHERE cve != '' AND epss IS NULL ORDER BY fetched_at DESC LIMIT ?", (limit,))]
    updated = 0
    for start in range(0, len(cves), 100):
        batch = cves[start:start + 100]
        r = requests.get(EPSS_URL, params={"cve": ",".join(batch)}, timeout=20, headers={"User-Agent": USER_AGENT})
        r.raise_for_status()
        scores = {row["cve"].upper(): row for row in r.json().get("data", [])}
        with db.db_cursor() as conn:
            for cve in batch:
                row = scores.get(cve.upper())
                # 0 = CVE inconnue d'EPSS : évite de la redemander à chaque synchronisation.
                epss = float(row["epss"]) if row else 0.0
                pct = float(row["percentile"]) if row else 0.0
                conn.execute("UPDATE threat_items SET epss=?, epss_percentile=? WHERE cve=?", (epss, pct, cve))
                updated += 1 if row else 0
    return {"source": "epss", "status": "ok", "new": updated, "total": len(cves)}


def _watchlist_alerts(min_id: int) -> int:
    """Alerte sur les nouveaux éléments qui citent une technologie de la liste de surveillance."""
    words = [w.strip() for w in str(db.get_setting("intel_watchlist", "") or "").split(",") if len(w.strip()) >= 2]
    if not words:
        return 0
    rows = db.fetch_all("SELECT id,source,title,summary,product,cve,severity,exploited FROM threat_items WHERE id > ?", (min_id,))
    count = 0
    for row in rows:
        haystack = f"{row['title']} {row['summary']} {row['product']}".lower()
        hit = next((w for w in words if re.search(rf"(?<![a-z0-9]){re.escape(w.lower())}(?![a-z0-9])", haystack)), None)
        if not hit:
            continue
        severity = "critical" if row["exploited"] else (row["severity"] if row["severity"] in {"critical", "high", "medium", "low"} else "medium")
        _alert("watchlist", severity, f"Veille « {hit} » : {row['cve'] or row['title']}"[:300],
               truncate(row["title"], 900), f"/intel?q={row['cve'] or hit}")
        count += 1
        if count >= 25:
            break
    return count


def sync_all(sources: list[str] | None = None) -> dict[str, Any]:
    selected = sources or ["cisa_kev", "cert_fr", "php_releases", "nvd"]
    results = []
    max_before = (db.fetch_one("SELECT COALESCE(MAX(id),0) AS m FROM threat_items") or {}).get("m", 0)
    for name in selected:
        try:
            if name == "cisa_kev":
                results.append(sync_cisa())
            elif name == "nvd":
                days = int(db.get_setting("intel_nvd_days", "14") or 14)
                max_items = int(db.get_setting("intel_max_items", "150") or 150)
                api_key = str(db.get_setting("nvd_api_key", "") or "")
                results.append(sync_nvd(days, max_items, api_key))
            elif name == "cert_fr":
                results.append(sync_cert_fr())
            elif name == "php_releases":
                results.append(sync_php())
            else:
                results.append({"source": name, "status": "skipped", "reason": "source non prise en charge"})
        except Exception as exc:  # noqa: BLE001
            _mark_source(name, "error", 0, f"{type(exc).__name__}: {exc}")
            results.append({"source": name, "status": "error", "error": f"{type(exc).__name__}: {exc}"})
    db.audit("intel_sync", {"results": results})
    # Marquage des CVE exploitées après mise à jour de toutes les sources.
    known = _known_kev()
    with db.db_cursor() as conn:
        for cve in known:
            conn.execute("UPDATE threat_items SET exploited=1 WHERE cve=?", (cve,))
    try:
        results.append(enrich_epss())
    except (requests.RequestException, ValueError, KeyError) as exc:
        results.append({"source": "epss", "status": "error", "error": f"{type(exc).__name__}: {exc}"})
    watch = _watchlist_alerts(int(max_before or 0))
    if watch:
        results.append({"source": "watchlist", "status": "ok", "new": watch, "total": watch})
    from . import ai_worker  # import tardif : évite un cycle

    ai_worker.on_intel_synced()
    return {"results": results, "synced_at": now_iso()}


def list_sources() -> list[dict[str, Any]]:
    return db.fetch_all("SELECT * FROM threat_sources ORDER BY name")


SORTS = {
    "recent": "exploited DESC, published_at DESC",
    "epss": "COALESCE(epss, 0) DESC, exploited DESC",
    "cvss": "COALESCE(cvss, 0) DESC, exploited DESC",
}


def search_items(
    q: str = "", source: str = "", severity: str = "", exploited: bool | None = None,
    limit: int = 100, offset: int = 0, sort: str = "recent",
) -> dict[str, Any]:
    where = []
    params: list[Any] = []
    if q:
        where.append("(title LIKE ? OR summary LIKE ? OR cve LIKE ? OR product LIKE ?)")
        like = f"%{q}%"
        params += [like, like, like, like]
    if source:
        where.append("source=?")
        params.append(source)
    if severity:
        where.append("severity=?")
        params.append(severity)
    if exploited is not None:
        where.append("exploited=?")
        params.append(1 if exploited else 0)
    clause = (" WHERE " + " AND ".join(where)) if where else ""
    total = db.fetch_one(f"SELECT COUNT(*) AS c FROM threat_items{clause}", params)["c"]  # type: ignore[index]
    rows = db.fetch_all(
        f"SELECT id,source,external_id,title,summary,severity,cvss,epss,epss_percentile,published_at,modified_at,product,cve,exploited,url,tags_json,fetched_at "
        f"FROM threat_items{clause} ORDER BY {SORTS.get(sort, SORTS['recent'])} LIMIT ? OFFSET ?",
        params + [min(500, max(1, limit)), max(0, offset)],
    )
    for row in rows:
        row["tags"] = db.json_loads(row.pop("tags_json"), [])
    return {"items": rows, "total": total, "limit": limit, "offset": offset}
