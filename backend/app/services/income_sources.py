"""Flux d'offres publiques utilisés par le radar d'opportunités.

Les réponses sont mises en cache dans les paramètres locaux afin de limiter les
appels externes, y compris lors des redémarrages de Cybbig.
"""
from __future__ import annotations

import html
import json
import re
import threading
import time
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from .. import db
from ..config import USER_AGENT
from ..utils import truncate
from . import proxy, websearch

TTL_SECONDS = 6 * 60 * 60
WEB_TTL_SECONDS = 30 * 60
TIMEOUT = 15
_lock = threading.Lock()


def _plain(value: Any, limit: int = 1200) -> str:
    return truncate(BeautifulSoup(html.unescape(str(value or "")), "html.parser").get_text(" ", strip=True), limit)


def _wrong_region(item: dict[str, str], location: str) -> bool:
    """Écarte quelques restrictions géographiques évidentes; l'annonce reste à vérifier."""
    wanted = (location or "").lower()
    if not wanted or wanted in {"remote", "worldwide", "monde", "international"}:
        return False
    text = f"{item.get('title', '')} {item.get('snippet', '')}".lower()
    if any(term in wanted for term in ("france", "europe", "paris", "lyon", "marseille")):
        restricted = ("latam", "latin america", "united states only", "us only", "u.s. only", "canada only",
                      "australia only", "india only", "based in singapore", "uk only", "united kingdom only")
        return any(term in text for term in restricted)
    return False


def _read_cache(source: str) -> tuple[list[dict[str, str]], float]:
    try:
        cached = json.loads(str(db.get_setting(f"income_feed_{source}", "{}")))
        rows = cached.get("items", [])
        stamp = float(cached.get("fetched_at", 0))
        if isinstance(rows, list):
            return [row for row in rows if isinstance(row, dict)], stamp
    except (TypeError, ValueError):
        pass
    return [], 0.0


def _save_cache(source: str, rows: list[dict[str, str]]) -> None:
    db.set_setting(f"income_feed_{source}", json.dumps({"fetched_at": time.time(), "items": rows[:120]}, ensure_ascii=False))


def _remoteok() -> list[dict[str, str]]:
    response = requests.get("https://remoteok.com/api", headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
                            timeout=TIMEOUT, proxies=proxy.requests_proxies(route="research"))
    response.raise_for_status()
    payload = response.json()
    rows = []
    for job in payload if isinstance(payload, list) else []:
        if not isinstance(job, dict) or not job.get("position") or not job.get("url"):
            continue
        url = str(job["url"])
        if urlparse(url).hostname not in {"remoteok.com", "www.remoteok.com"}:
            continue
        tags = job.get("tags") if isinstance(job.get("tags"), list) else []
        description = _plain(job.get("description"), 1200)
        salary_values = "–".join(str(job.get(k)) for k in ("salary_min", "salary_max") if job.get(k))
        salary = f"Rémunération indiquée {salary_values} (devise à vérifier)" if salary_values else ""
        rows.append({"title": truncate(job.get("position"), 300), "url": url, "source": "Remote OK",
                     "snippet": truncate(" · ".join(x for x in [str(job.get("company") or ""), str(job.get("location") or "Télétravail"), ", ".join(map(str, tags)), salary, description] if x), 1200)})
    return rows[:120]


def _remotive() -> list[dict[str, str]]:
    response = requests.get("https://remotive.com/api/remote-jobs", params={"limit": 100},
                            headers={"User-Agent": USER_AGENT, "Accept": "application/json"}, timeout=TIMEOUT,
                            proxies=proxy.requests_proxies(route="research"))
    response.raise_for_status()
    payload = response.json()
    rows = []
    for job in payload.get("jobs", []) if isinstance(payload, dict) else []:
        if not isinstance(job, dict) or not job.get("title") or not job.get("url"):
            continue
        url = str(job["url"])
        if urlparse(url).hostname not in {"remotive.com", "www.remotive.com"}:
            continue
        description = _plain(job.get("description"), 1200)
        details = " · ".join(str(job.get(k)) for k in ("company_name", "category", "job_type", "candidate_required_location", "salary") if job.get(k))
        rows.append({"title": truncate(job.get("title"), 300), "url": url, "source": "Remotive",
                     "snippet": truncate(" · ".join(x for x in (details, description) if x), 1200)})
    return rows[:120]


def _eu_funding_calls(skills: str, location: str) -> list[dict[str, str]]:
    # API publique officielle SEDIA : publication de pistes uniquement, la candidature
    # et l'éligibilité demeurent dans le portail européen.
    query = {"bool": {"must": [{"terms": {"type": ["1", "2", "8"]}},
                                {"terms": {"status": ["31094501", "31094502"]}}]}}
    response = requests.post(
        "https://api.tech.ec.europa.eu/search-api/prod/rest/search",
        params={"apiKey": "SEDIA", "text": " ".join((skills or "digital innovation") .split()[:10]),
                "pageSize": "50", "pageNumber": "1", "language": "en"},
        files={"query": (None, json.dumps(query), "application/json")},
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"}, timeout=TIMEOUT,
        proxies=proxy.requests_proxies(route="research"),
    )
    response.raise_for_status()
    payload = response.json()
    today = datetime.now(timezone.utc).date()
    rows: list[dict[str, str]] = []
    seen: set[str] = set()
    for result in payload.get("results", []) if isinstance(payload, dict) else []:
        if not isinstance(result, dict):
            continue
        meta = result.get("metadata") if isinstance(result.get("metadata"), dict) else {}
        deadline = str((meta.get("deadlineDate") or [""])[0])
        status = str((meta.get("status") or [""])[0])
        if status not in {"31094501", "31094502"}:
            continue
        if deadline:
            try:
                if datetime.fromisoformat(deadline.replace("Z", "+00:00")).date() < today:
                    continue
            except ValueError:
                continue
        title = str((meta.get("title") or meta.get("callTitle") or [""])[0])
        identifier = str((meta.get("identifier") or [""])[0])
        url = f"https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/opportunities/topic-details/{identifier}" if identifier else str(result.get("url") or "")
        if not title or not identifier or not url.startswith("https://ec.europa.eu/"):
            continue
        if url in seen:
            continue
        seen.add(url)
        text = _plain(result.get("content") or result.get("summary") or "", 900)
        extra = ["Échéance : " + (deadline[:10] if deadline else "non précisée"),
                 "Statut déclaré ouvert/futur" if status == "31094502" else "Statut à revérifier"]
        rows.append({"title": truncate(title, 300), "url": url, "source": "UE Funding & Tenders",
                     "snippet": truncate(" · ".join([*extra, text]), 1200)})
    return rows[:120]


FETCHERS = {"Remote OK": _remoteok, "Remotive": _remotive}


def search_remote_roles(skills: str, location: str, limit: int = 5) -> tuple[list[dict[str, str]], list[str]]:
    """Recherche dans deux flux publics; cache six heures et repli sur les données locales."""
    terms = [re.sub(r"[^\w+#.-]", "", term.lower()) for term in re.split(r"[,;|]", skills) if len(term.strip()) > 1]
    loc_terms = [term.lower() for term in re.split(r"[,;|]", location) if len(term.strip()) > 2]
    combined: list[dict[str, str]] = []
    warnings: list[str] = []
    for source, fetch in FETCHERS.items():
        with _lock:
            cached, fetched_at = _read_cache(source)
            if fetched_at <= 0 or time.time() - fetched_at >= TTL_SECONDS:
                try:
                    fresh = fetch()
                    _save_cache(source, fresh)
                    cached = fresh
                except (requests.RequestException, ValueError, TypeError) as exc:
                    warnings.append(f"{source} indisponible ({type(exc).__name__})" + ("; cache local utilisé" if cached else ""))
        combined.extend(cached)

    scored: list[tuple[int, dict[str, str]]] = []
    seen: set[str] = set()
    for item in combined:
        if item["url"] in seen:
            continue
        seen.add(item["url"])
        corpus = f"{item['title']} {item['snippet']}".lower()
        skill_hits = sum(1 for term in terms if term in corpus)
        location_hits = sum(1 for term in loc_terms if term in corpus)
        # Une recherche pertinente ne doit pas masquer les offres distantes non localisées.
        score = skill_hits * 4 + location_hits
        if (not terms or skill_hits) and not _wrong_region(item, location):
            scored.append((score, item))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [item for _, item in scored[:max(1, min(10, limit))]], warnings


def search_funding_calls(skills: str, location: str, limit: int = 5) -> tuple[list[dict[str, str]], list[str]]:
    """Flux européen officiel des appels à projets et marchés, avec cache persistant six heures."""
    source = "eu_funding"
    with _lock:
        cached, fetched_at = _read_cache(source)
        if fetched_at <= 0 or time.time() - fetched_at >= TTL_SECONDS:
            try:
                cached = _eu_funding_calls(skills, location)
                _save_cache(source, cached)
            except (requests.RequestException, ValueError, TypeError) as exc:
                warning = f"Portail UE indisponible ({type(exc).__name__})" + ("; cache local utilisé" if cached else "")
                return cached[:max(1, min(10, limit))], [warning]
    terms = [term.lower() for term in re.split(r"[,;|\s]+", skills) if len(term) > 2]
    location_terms = [term.lower() for term in re.split(r"[,;|\s]+", location) if len(term) > 3]
    ranked = []
    seen: set[str] = set()
    for item in cached:
        if item.get("url") in seen:
            continue
        seen.add(item.get("url", ""))
        text = f"{item.get('title', '')} {item.get('snippet', '')}".lower()
        score = sum(3 for term in terms if term in text) + sum(2 for term in location_terms if term in text)
        if not terms or score:
            ranked.append((score, item))
    ranked.sort(key=lambda pair: pair[0], reverse=True)
    return [item for _, item in ranked[:max(1, min(10, limit))]], []


def search_web_opportunities(method: str, query: str, domains: list[str], limit: int = 5) -> tuple[list[dict[str, str]], list[str]]:
    """Recherche web multi-moteur sur l'ensemble du Web et cache persistant entre cycles rapides."""
    # Versionne le cache pour éliminer les anciens résultats qui n'appliquaient
    # pas strictement les domaines sélectionnés.
    cache_key = f"income_web_v2_{method}"
    domains = [domain.lower().strip().rstrip(".") for domain in domains if domain]
    source_hints = " ".join(domain.split(".")[0].replace("-", " ") for domain in domains[:5])
    scoped_query = (query + " " + source_hints).strip()
    with _lock:
        try:
            state = json.loads(str(db.get_setting(cache_key, "{}")))
        except (TypeError, ValueError):
            state = {}
        cached = state.get("items") if isinstance(state.get("items"), list) else []
        fetched_at = float(state.get("fetched_at") or 0)
        if state.get("query") == scoped_query and fetched_at and time.time() - fetched_at < WEB_TTL_SECONDS:
            return cached[:limit], list(state.get("warnings") or [])
    try:
        result = websearch.search(scoped_query, limit=min(20, max(limit * 2, limit)), lang="en", provider="auto", domains=domains)
        rows = []
        for item in result.get("items", []):
            rows.append({"title": truncate(item.get("title"), 300), "url": item.get("url", ""),
                         "source": truncate(item.get("source"), 40), "snippet": truncate(item.get("snippet"), 1200)})
        warnings = list(result.get("warnings") or [])
        db.set_setting(cache_key, json.dumps({"query": scoped_query, "fetched_at": time.time(), "items": rows[:30], "warnings": warnings}, ensure_ascii=False))
        return rows[:limit], warnings
    except (requests.RequestException, RuntimeError, ValueError) as exc:
        warning = f"Recherche Web indisponible ({type(exc).__name__})"
        if cached and time.time() - fetched_at < 24 * 60 * 60:
            return cached[:limit], list(state.get("warnings") or []) + [warning, "cache précédent utilisé"]
        return [], [warning]
