"""Recherche web publique pour la veille défensive et les opportunités Cybbig.

Bing RSS et DuckDuckGo fonctionnent sans clé ; Brave Search est activable avec une clé API.
Les résultats sont des données externes non fiables. Toute ouverture de page passe
ensuite par webfetch (robots.txt, DNS public, types et tailles plafonnés).
"""
from __future__ import annotations

import logging
import re
import threading
import time
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
import ipaddress
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

import requests
from bs4 import BeautifulSoup

from .. import db
from ..config import USER_AGENT
from ..utils import truncate
from . import proxy

logger = logging.getLogger("cybbig.websearch")
TIMEOUT = 12
MAX_QUERY = 400
MAX_RESULTS = 20
_cache: dict[tuple[Any, ...], tuple[float, dict[str, Any]]] = {}
_lock = threading.Lock()


def _key() -> str:
    return str(db.get_setting("brave_search_key", "") or "").strip()


def _normalize_url(url: str) -> str:
    url = (url or "").strip()
    parsed = urlparse(url)
    if parsed.netloc.endswith("duckduckgo.com") and parsed.path == "/l/":
        url = parse_qs(parsed.query).get("uddg", [""])[0]
    url = unquote(url).strip()
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return ""
    try:
        port = parsed.port
    except ValueError:
        return ""
    if parsed.username or parsed.password or port not in {None, 80, 443, 8080, 8443}:
        return ""
    host = parsed.hostname.lower().rstrip(".")
    if host in {"localhost", "metadata.google.internal"} or host.endswith((".localhost", ".local")):
        return ""
    try:
        if not ipaddress.ip_address(host).is_global:
            return ""
    except ValueError:
        pass
    if parsed.hostname.lower() in {"html.duckduckgo.com", "duckduckgo.com", "www.duckduckgo.com"}:
        return ""
    return url.split("#", 1)[0]


def _brave(query: str, count: int, lang: str) -> list[dict[str, str]]:
    key = _key()
    if not key:
        return []
    response = requests.get(
        "https://api.search.brave.com/res/v1/web/search",
        params={"q": query, "count": count, "search_lang": lang, "safesearch": "moderate"},
        headers={"Accept": "application/json", "X-Subscription-Token": key, "User-Agent": USER_AGENT},
        timeout=TIMEOUT, proxies=proxy.requests_proxies(route="research"),
    )
    response.raise_for_status()
    results = response.json().get("web", {}).get("results", [])
    return [{"title": truncate(x.get("title"), 300), "url": _normalize_url(x.get("url", "")),
             "snippet": truncate(x.get("description"), 900), "source": "Brave"}
            for x in results if isinstance(x, dict) and _normalize_url(x.get("url", ""))]


def _duckduckgo(query: str, count: int, lang: str) -> list[dict[str, str]]:
    response = requests.get(
        "https://html.duckduckgo.com/html/",
        params={"q": query, "kl": f"{lang}-{lang.upper()}"},
        headers={"User-Agent": USER_AGENT, "Accept": "text/html", "Accept-Language": f"{lang},{lang};q=0.8,en;q=0.6"},
        timeout=TIMEOUT, proxies=proxy.requests_proxies(route="research"),
    )
    if response.status_code != 200:
        raise requests.HTTPError(f"DuckDuckGo a répondu HTTP {response.status_code}", response=response)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    if soup.select_one("form#challenge-form, #anomaly-modal, .anomaly-modal") or "select all squares" in response.text.lower():
        raise requests.HTTPError("DuckDuckGo a renvoyé une page anti-robot", response=response)
    output: list[dict[str, str]] = []
    for item in soup.select(".result"):
        anchor = item.select_one("a.result__a")
        if not anchor:
            continue
        url = _normalize_url(anchor.get("href", ""))
        if not url:
            continue
        snippet = item.select_one(".result__snippet")
        output.append({"title": truncate(anchor.get_text(" ", strip=True), 300), "url": url,
                       "snippet": truncate(snippet.get_text(" ", strip=True) if snippet else "", 900),
                       "source": "DuckDuckGo"})
        if len(output) >= count:
            break
    return output


def _bing(query: str, count: int, lang: str) -> list[dict[str, str]]:
    response = requests.get(
        "https://www.bing.com/search", params={"format": "rss", "q": query, "setlang": lang},
        headers={"User-Agent": USER_AGENT, "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.5"},
        timeout=TIMEOUT, proxies=proxy.requests_proxies(route="research"),
    )
    response.raise_for_status()
    try:
        root = ET.fromstring(response.content)
    except ET.ParseError as exc:
        raise requests.RequestException("Bing a renvoyé un flux RSS illisible") from exc
    output: list[dict[str, str]] = []
    for item in root.findall(".//item"):
        title = item.findtext("title") or ""
        url = _normalize_url(item.findtext("link") or "")
        description = item.findtext("description") or ""
        if not url:
            continue
        output.append({"title": truncate(BeautifulSoup(title, "html.parser").get_text(" ", strip=True), 300),
                       "url": url, "snippet": truncate(BeautifulSoup(description, "html.parser").get_text(" ", strip=True), 900),
                       "source": "Bing"})
        if len(output) >= count:
            break
    return output


def _domains(values: list[str] | None) -> tuple[str, ...]:
    clean: list[str] = []
    for raw in values or []:
        host = str(raw).strip().lower().rstrip(".")
        if not host:
            continue
        if "://" in host or "/" in host or "@" in host or len(host) > 253:
            raise ValueError("Indiquez un nom de domaine uniquement, sans protocole ni chemin.")
        try:
            host.encode("ascii")
        except UnicodeEncodeError:
            try:
                host = host.encode("idna").decode("ascii")
            except UnicodeError as exc:
                raise ValueError("Nom de domaine invalide.") from exc
        if not re.fullmatch(r"(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)(?:\.(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?))+", host):
            raise ValueError("Nom de domaine invalide.")
        if host not in clean:
            clean.append(host)
    if len(clean) > 8:
        raise ValueError("Limitez la recherche à huit domaines sélectionnés.")
    return tuple(clean)


def _search_query(query: str, limit: int, lang: str, provider: str) -> tuple[list[dict[str, str]], list[str]]:
    engines = []
    if provider != "duckduckgo" and _key():
        engines.append(("Brave", _brave))
    if provider == "auto" or (provider == "brave" and not _key()):
        engines.append(("Bing", _bing))
    if provider in {"auto", "duckduckgo"} or not engines:
        engines.append(("DuckDuckGo", _duckduckgo))
    by_engine: dict[str, list[dict[str, str]]] = {}
    errors: list[str] = []
    with ThreadPoolExecutor(max_workers=len(engines), thread_name_prefix="cybbig-search") as pool:
        futures = {pool.submit(func, query, limit, lang): name for name, func in engines}
        for future in as_completed(futures):
            name = futures[future]
            try:
                by_engine[name] = future.result()
            except (requests.RequestException, ValueError) as exc:
                logger.info("%s search unavailable: %s", name, type(exc).__name__)
                errors.append(f"{name} indisponible")
    rows = [row for name, _ in engines for row in by_engine.get(name, [])]
    if provider == "brave" and not _key():
        errors.append("Clé Brave absente ; DuckDuckGo utilisé")
    return rows, errors


def search(query: str, limit: int | None = 10, lang: str = "fr", provider: str = "auto", domains: list[str] | None = None) -> dict[str, Any]:
    """Recherche classée et dédupliquée, Brave prioritaire quand configuré, Bing/DDG en repli."""
    query = re.sub(r"\s+", " ", (query or "")).strip()[:MAX_QUERY]
    if len(query) < 2:
        raise ValueError("Saisissez au moins deux caractères pour rechercher.")
    if limit is None:
        limit = 20 if str(db.get_setting("web_research_mode", "false")).lower() == "true" else 10
    limit = max(1, min(MAX_RESULTS, int(limit)))
    lang = "en" if (lang or "fr").lower().startswith("en") else "fr"
    provider = provider if provider in {"auto", "brave", "duckduckgo"} else "auto"
    selected_domains = _domains(domains)
    cache_key = (query.lower(), lang, limit, provider, selected_domains, bool(_key()))
    now = time.monotonic()
    with _lock:
        hit = _cache.get(cache_key)
        if hit and hit[0] > now:
            return {**hit[1], "cached": True}

    if selected_domains:
        rows = []
        errors = []
        # Requêtes en parallèle, chaque requête étant contrainte à un domaine précis.
        by_domain: dict[str, list[dict[str, str]]] = {}
        with ThreadPoolExecutor(max_workers=min(8, len(selected_domains)), thread_name_prefix="cybbig-domain-search") as pool:
            futures = {pool.submit(_search_query, f"{query} site:{domain}", limit, lang, provider): domain for domain in selected_domains}
            for future in as_completed(futures):
                domain = futures[future]
                try:
                    found, notices = future.result()
                    errors.extend(notices)
                    by_domain[domain] = []
                    for row in found:
                        host = (urlparse(row.get("url", "")).hostname or "").lower().rstrip(".")
                        if host == domain or host.endswith("." + domain):
                            by_domain[domain].append(row)
                except (requests.RequestException, RuntimeError, ValueError) as exc:
                    logger.info("Domain search unavailable (%s): %s", domain, type(exc).__name__)
                    errors.append(f"Recherche indisponible : {domain}")
        rows = [row for domain in selected_domains for row in by_domain.get(domain, [])]
        if not _key() and provider == "brave":
            errors.append("Clé Brave absente ; DuckDuckGo utilisé")
    else:
        rows, errors = _search_query(query, limit, lang, provider)
    deduped: list[dict[str, str]] = []
    seen: set[str] = set()
    for row in rows:
        url = row["url"].rstrip("/").lower()
        if url in seen:
            continue
        seen.add(url)
        deduped.append(row)
        if len(deduped) >= limit:
            break
    if not deduped and errors:
        raise RuntimeError("Aucun moteur de recherche n’a répondu. Vérifiez la connexion et la clé Brave facultative.")
    result = {"query": query, "provider": "+".join(dict.fromkeys(r["source"] for r in deduped)) or "aucun", "domains": list(selected_domains),
              "items": deduped, "total": len(deduped), "cached": False, "warnings": list(dict.fromkeys(errors))}
    with _lock:
        _cache[cache_key] = (now + 300, result)
        if len(_cache) > 256:
            for key, value in list(_cache.items()):
                if value[0] <= now:
                    _cache.pop(key, None)
    return result
