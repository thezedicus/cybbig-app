"""Archive locale et indexation des flux annuels NVD CVE 2.0.

Les flux JSON sont téléchargés depuis NVD, vérifiés contre leur SHA-256 officiel,
puis conservés dans le dossier de données du poste et indexés dans threat_items.
L'import est reprenable par année et les descriptions restent des données externes.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import os
import re
import shutil
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

import requests

from .. import db
from ..config import DATA_DIR, USER_AGENT
from ..utils import now_iso, truncate
from .intel import _insert_items, _iso, _known_kev, _mark_source, _nvd_cvss

NVD_FEED = "https://nvd.nist.gov/feeds/json/cve/2.0/nvdcve-2.0-{year}.json.gz"
NVD_META = "https://nvd.nist.gov/feeds/json/cve/2.0/nvdcve-2.0-{year}.meta"
ARCHIVE_DIR = DATA_DIR / "knowledge_sources" / "nvd" / "cve"
BATCH_SIZE = 200
INDEXER_VERSION = "2"
_lock = threading.Lock()
_worker: threading.Thread | None = None


def _status(**changes: Any) -> dict[str, Any]:
    prior = db.json_loads(db.get_setting("nvd_archive_status", "{}"), {}) or {}
    prior.update(changes)
    prior["updated_at"] = now_iso()
    db.set_setting("nvd_archive_status", json.dumps(prior, ensure_ascii=False))
    return prior


def get_status() -> dict[str, Any]:
    value = db.json_loads(db.get_setting("nvd_archive_status", "{}"), {}) or {}
    if _lock.locked():
        value["running"] = True
    else:
        value["running"] = False
    return value


def start_import() -> dict[str, Any]:
    global _worker
    if not _lock.acquire(blocking=False):
        return {**get_status(), "running": True}
    _lock.release()
    _worker = threading.Thread(target=_run_guarded, name="cybbig-nvd-archive", daemon=True)
    _worker.start()
    return {**get_status(), "running": True}


def _run_guarded() -> None:
    if not _lock.acquire(blocking=False):
        return
    try:
        _run_import()
    except Exception as exc:  # noqa: BLE001
        _status(phase="error", running=False, error=f"{type(exc).__name__}: {exc}")
    finally:
        _lock.release()


def _parse_meta(text: str) -> dict[str, str]:
    return {k: v for k, v in (line.split(":", 1) for line in text.splitlines() if ":" in line)
            if k in {"lastModifiedDate", "size", "gzSize", "sha256"}}


def _feed_for_year(year: int, session: requests.Session) -> tuple[Path, dict[str, str]]:
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    meta_response = session.get(NVD_META.format(year=year), timeout=(15, 45))
    meta_response.raise_for_status()
    meta = _parse_meta(meta_response.text)
    if not meta.get("sha256") or not meta.get("size"):
        raise ValueError(f"Métadonnées NVD incomplètes pour {year}.")
    target = ARCHIVE_DIR / f"nvdcve-2.0-{year}.json"
    sidecar = ARCHIVE_DIR / f"nvdcve-2.0-{year}.meta.json"
    prior = {}
    if sidecar.exists():
        try:
            prior = json.loads(sidecar.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            prior = {}
    if target.exists() and prior.get("sha256", "").lower() == meta["sha256"].lower() and target.stat().st_size == int(meta["size"]):
        return target, meta

    compressed_part = target.with_suffix(".json.gz.part")
    json_part = target.with_suffix(".json.part")
    for part in (compressed_part, json_part):
        part.unlink(missing_ok=True)
    response = session.get(NVD_FEED.format(year=year), stream=True, timeout=(20, 180))
    response.raise_for_status()
    compressed_bytes = 0
    with compressed_part.open("wb") as out:
        for chunk in response.iter_content(1024 * 1024):
            if chunk:
                out.write(chunk)
                compressed_bytes += len(chunk)
    digest = hashlib.sha256()
    uncompressed_bytes = 0
    with gzip.open(compressed_part, "rb") as src, json_part.open("wb") as dst:
        while True:
            chunk = src.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
            dst.write(chunk)
            uncompressed_bytes += len(chunk)
    if uncompressed_bytes != int(meta["size"]):
        json_part.unlink(missing_ok=True)
        compressed_part.unlink(missing_ok=True)
        raise ValueError(f"Taille NVD inattendue pour {year} ({uncompressed_bytes} octets).")
    if digest.hexdigest().lower() != meta["sha256"].lower():
        json_part.unlink(missing_ok=True)
        compressed_part.unlink(missing_ok=True)
        raise ValueError(f"SHA-256 NVD invalide pour {year}.")
    os.replace(json_part, target)
    compressed_part.unlink(missing_ok=True)
    sidecar.write_text(json.dumps({**meta, "source": NVD_FEED.format(year=year),
                                   "verified_at": now_iso(), "compressed_bytes": compressed_bytes}, indent=2), encoding="utf-8")
    return target, meta


def _iter_vulnerabilities(path: Path) -> Iterator[dict[str, Any]]:
    """Lit le tableau vulnerabilities en flux, sans charger un flux annuel de plusieurs centaines de Mo en RAM."""
    decoder = json.JSONDecoder()
    with path.open("r", encoding="utf-8") as fp:
        buf = ""
        marker = '"vulnerabilities"'
        while marker not in buf:
            chunk = fp.read(1024 * 1024)
            if not chunk:
                raise ValueError(f"Tableau vulnerabilities absent de {path.name}.")
            buf += chunk
        buf = buf[buf.index(marker) + len(marker):]
        while ":" not in buf:
            buf += fp.read(1024 * 1024)
        buf = buf[buf.index(":") + 1:]
        while "[" not in buf:
            buf += fp.read(1024 * 1024)
        buf = buf[buf.index("[") + 1:]
        while True:
            buf = buf.lstrip()
            while buf.startswith(","):
                buf = buf[1:].lstrip()
            if buf.startswith("]"):
                return
            if not buf:
                buf = fp.read(1024 * 1024)
                if not buf:
                    raise ValueError(f"Fin inattendue de {path.name}.")
                continue
            try:
                item, end = decoder.raw_decode(buf)
            except json.JSONDecodeError:
                chunk = fp.read(1024 * 1024)
                if not chunk:
                    raise
                buf += chunk
                continue
            if isinstance(item, dict):
                yield item
            buf = buf[end:]


def _products(nodes: list[dict[str, Any]]) -> str:
    found: set[str] = set()
    stack = list(nodes)
    while stack:
        node = stack.pop()
        stack.extend(node.get("nodes") or [])
        stack.extend(node.get("children") or [])
        for match in node.get("cpeMatch") or []:
            parts = (match.get("criteria") or "").split(":")
            if len(parts) > 4:
                found.add(f"{parts[3]}:{parts[4]}")
    return ", ".join(sorted(found)[:12])


def _to_item(entry: dict[str, Any]) -> dict[str, Any] | None:
    cve = entry.get("cve") or {}
    cve_id = (cve.get("id") or "").strip()
    if not cve_id:
        return None
    descriptions = cve.get("descriptions") or []
    description = next((d.get("value") for d in descriptions if d.get("lang") == "en"), None)
    description = description or next((d.get("value") for d in descriptions), "")
    score, severity = _nvd_cvss(cve)
    cwes = sorted({d.get("value") for w in cve.get("weaknesses") or []
                   for d in w.get("description") or [] if (d.get("value") or "").startswith("CWE-")})
    return {
        "external_id": cve_id,
        "title": cve_id,
        "summary": truncate(description, 4000),
        "severity": severity,
        "cvss": score,
        "published_at": _iso(cve.get("published")),
        "modified_at": _iso(cve.get("lastModified")),
        "product": _products(cve.get("configurations") or []),
        "cve": cve_id,
        "exploited": 0,
        "url": f"https://nvd.nist.gov/vuln/detail/{cve_id}",
        "tags": cwes[:20],
        "raw": {"id": cve_id, "metrics": cve.get("metrics", {}), "weaknesses": cve.get("weaknesses", []),
                "references": cve.get("references", [])},
    }


def _run_import() -> None:
    start_year = 2002
    end_year = datetime.now(timezone.utc).year
    years = list(range(start_year, end_year + 1))
    done = 0
    imported = 0
    _status(phase="starting", running=True, error="", years_total=len(years), feeds_ready=0,
            feeds_indexed=0, cves_indexed=0, current_year=None, started_at=now_iso(),
            archive_path=str(ARCHIVE_DIR), expected_uncompressed_bytes=0)
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    known_kev = _known_kev()
    total_bytes = 0
    for year in years:
        _status(phase="download", current_year=year, feeds_ready=done, cves_indexed=imported)
        path, meta = _feed_for_year(year, session)
        total_bytes += int(meta["size"])
        _status(phase="index", current_year=year, feeds_ready=done + 1,
                expected_uncompressed_bytes=total_bytes, cves_indexed=imported)
        setting_key = f"nvd_archive_indexed_{year}"
        indexed_hash = f"{INDEXER_VERSION}:{meta['sha256']}"
        if db.get_setting(setting_key) != indexed_hash:
            batch: list[dict[str, Any]] = []
            year_count = 0
            for entry in _iter_vulnerabilities(path):
                item = _to_item(entry)
                if item:
                    batch.append(item)
                    year_count += 1
                if len(batch) >= BATCH_SIZE:
                    _insert_items("nvd", batch, known_kev)
                    batch.clear()
                    imported += BATCH_SIZE
                    _status(phase="index", current_year=year, feeds_ready=done + 1,
                            cves_indexed=imported)
            if batch:
                _insert_items("nvd", batch, known_kev)
                imported += len(batch)
            db.set_setting(setting_key, indexed_hash)
            db.audit("nvd_archive_year_indexed", {"year": year, "cves": year_count, "sha256": meta["sha256"]})
        done += 1
        _status(phase="index", current_year=year, feeds_ready=done, feeds_indexed=done,
                cves_indexed=imported, expected_uncompressed_bytes=total_bytes)
    total = (db.fetch_one("SELECT COUNT(*) AS c FROM threat_items WHERE source='nvd'") or {}).get("c", 0)
    _mark_source("nvd", "ok", total)
    _status(phase="complete", running=False, current_year=None, feeds_ready=len(years),
            feeds_indexed=len(years), cves_indexed=imported, nvd_total=total,
            expected_uncompressed_bytes=total_bytes, completed_at=now_iso(), error="")
    db.audit("nvd_archive_import_completed", {"years": len(years), "indexed": imported, "total_nvd": total})
