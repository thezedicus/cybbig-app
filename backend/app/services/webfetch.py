"""Visite de sites web : lecture contrôlée de pages publiques pour alimenter la base de connaissances.

Garde-fous (la page lue est une donnée NON FIABLE, et une consigne cachée dans une page pourrait pousser
l'IA à viser le réseau interne) :
- http/https uniquement, ports 80/443/8080/8443, pas d'identifiants dans l'URL ;
- le nom d'hôte doit résoudre vers des adresses publiques (pas de loopback, réseau privé, link-local,
  métadonnées cloud) ; chaque redirection est revalidée ;
- robots.txt respecté par défaut ; délai entre deux pages d'une exploration ; taille et durée plafonnées ;
- le texte récupéré n'est jamais exécuté ni interprété comme une instruction.

Extraction : trafilatura (texte principal) puis Scrapling (sélecteurs CSS, liens, métadonnées).
Limite connue : la résolution DNS est contrôlée avant la requête ; une réponse DNS qui change entre le contrôle et la
connexion (DNS rebinding) n'est pas bloquée au niveau du socket.
"""
from __future__ import annotations

import hashlib
import ipaddress
import logging
import re
import socket
import threading
import time
import urllib.robotparser
from typing import Any
from urllib.parse import urldefrag, urljoin, urlparse

import requests

from .. import db
from ..utils import new_id, now_iso, truncate

logger = logging.getLogger("cybbig.web")

READER_AGENT = "CybbigReader/0.3 (+lecture publique; respecte robots.txt)"
MAX_BYTES = 2_000_000
TIMEOUT = 12
MAX_REDIRECTS = 5
MAX_CRAWL_PAGES = 25
MAX_CRAWL_DEPTH = 2
CRAWL_DELAY = 0.7
ALLOWED_PORTS = {80, 443, 8080, 8443}
ALLOWED_TYPES = ("text/html", "application/xhtml+xml", "text/plain", "text/markdown", "application/json", "application/xml", "text/xml")
URL_RE = re.compile(r"https?://[^\s<>\"')\]]+", re.I)


class FetchError(Exception):
    """Erreur lisible par l'utilisateur (URL refusée, page trop grande, robots.txt…)."""


def _flag(key: str, default: bool = True) -> bool:
    return str(db.get_setting(key, "true" if default else "false")).lower() in {"1", "true", "yes", "on"}


# --- Contrôle des destinations -----------------------------------------------------------------

def _check_address(raw: str) -> None:
    address = ipaddress.ip_address(raw.split("%")[0])
    if isinstance(address, ipaddress.IPv6Address) and address.ipv4_mapped:
        address = address.ipv4_mapped
    if not address.is_global or address.is_multicast:
        raise FetchError(f"Adresse non publique refusée ({address}).")


def check_url(url: str) -> str:
    """Valide l'URL et renvoie sa forme normalisée (sans fragment). Lève FetchError si elle n'est pas publique."""
    url = (url or "").strip()
    if not url or len(url) > 2000:
        raise FetchError("URL vide ou trop longue.")
    if "://" not in url:
        url = "https://" + url
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise FetchError("Seuls les schémas http et https sont acceptés.")
    if parsed.username or parsed.password:
        raise FetchError("Les identifiants dans l'URL sont refusés.")
    host = parsed.hostname or ""
    if not host:
        raise FetchError("Nom d'hôte manquant.")
    try:
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
    except ValueError as exc:
        raise FetchError("Port invalide.") from exc
    if port not in ALLOWED_PORTS:
        raise FetchError(f"Port {port} refusé (autorisés : {', '.join(str(p) for p in sorted(ALLOWED_PORTS))}).")
    try:
        _check_address(host)  # l'hôte est déjà une adresse IP
    except ValueError:
        try:
            infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
        except socket.gaierror as exc:
            raise FetchError(f"Nom d'hôte introuvable : {host}.") from exc
        for info in infos:
            _check_address(info[4][0])
    return urldefrag(url)[0]


# --- robots.txt ---------------------------------------------------------------------------------

_robots_cache: dict[str, tuple[float, urllib.robotparser.RobotFileParser | None]] = {}
_robots_lock = threading.Lock()


def _proxies() -> dict[str, str]:
    from . import proxy  # import tardif
    return proxy.requests_proxies(route="research")


def _get_once(url: str, timeout: float, max_bytes: int) -> tuple[requests.Response, bytes]:
    response = requests.get(url, headers={"User-Agent": READER_AGENT, "Accept": ", ".join(ALLOWED_TYPES) + ";q=0.9,*/*;q=0.1",
                                          "Accept-Language": "fr,en;q=0.7"},
                            timeout=timeout, stream=True, allow_redirects=False, proxies=_proxies())
    chunks, size = [], 0
    try:
        for chunk in response.iter_content(65536):
            size += len(chunk)
            if size > max_bytes:
                raise FetchError(f"Page trop volumineuse (plus de {max_bytes // 1000} Ko).")
            chunks.append(chunk)
    finally:
        response.close()
    return response, b"".join(chunks)


def _robots_allows(url: str) -> bool:
    if not _flag("web_respect_robots"):
        return True
    parsed = urlparse(url)
    origin = f"{parsed.scheme}://{parsed.netloc}"
    now = time.monotonic()
    with _robots_lock:
        hit = _robots_cache.get(origin)
    if hit and hit[0] > now:
        parser = hit[1]
    else:
        parser = None
        try:
            robots_url = check_url(origin + "/robots.txt")
            response, body = _get_once(robots_url, 6, 300_000)
            if response.status_code == 200:
                parser = urllib.robotparser.RobotFileParser()
                parser.parse(body.decode("utf-8", "replace").splitlines())
        except (FetchError, requests.RequestException):
            parser = None  # robots.txt injoignable : lecture permise (l'utilisateur a demandé cette page)
        with _robots_lock:
            _robots_cache[origin] = (now + 3600, parser)
    return True if parser is None else parser.can_fetch(READER_AGENT, url)


# --- Récupération et extraction ----------------------------------------------------------------

_CHARSET_RE = re.compile(r"charset=[\"']?([\w\-]+)", re.I)
_META_CHARSET_RE = re.compile(rb"<meta[^>]+charset=[\"']?([\w\-]+)", re.I)


def _decode(body: bytes, content_type: str) -> str:
    """Décode une page. requests suppose du latin-1 quand l'en-tête ne donne pas d'encodage : on ne s'y fie pas."""
    declared = _CHARSET_RE.search(content_type)
    candidates = [declared.group(1)] if declared else []
    if not declared:
        meta = _META_CHARSET_RE.search(body[:4096])
        if meta:
            candidates.append(meta.group(1).decode("ascii", "ignore"))
        candidates.append("utf-8")
    for name in candidates:
        try:
            return body.decode(name)
        except (LookupError, UnicodeDecodeError):
            continue
    return body.decode("cp1252", "replace")


def fetch(url: str, timeout: float = TIMEOUT) -> dict[str, Any]:
    current = check_url(url)
    for _ in range(MAX_REDIRECTS + 1):
        if not _robots_allows(current):
            raise FetchError("Le fichier robots.txt du site interdit cette page (réglage « Respecter robots.txt »).")
        try:
            response, body = _get_once(current, timeout, MAX_BYTES)
        except requests.RequestException as exc:
            raise FetchError(f"Connexion impossible : {type(exc).__name__}.") from exc
        if response.status_code in {301, 302, 303, 307, 308} and response.headers.get("Location"):
            current = check_url(urljoin(current, response.headers["Location"]))  # chaque saut est revalidé
            continue
        if response.status_code >= 400:
            raise FetchError(f"Le site a répondu {response.status_code}.")
        ctype = (response.headers.get("Content-Type") or "text/html").split(";")[0].strip().lower()
        if not ctype.startswith(ALLOWED_TYPES):
            raise FetchError(f"Type de contenu non pris en charge : {ctype}.")
        text = _decode(body, response.headers.get("Content-Type") or "")
        return {"url": current, "status": response.status_code, "content_type": ctype, "text": text, "bytes": len(body)}
    raise FetchError("Trop de redirections.")


def _collapse(text: str) -> str:
    text = re.sub(r"[ \t\r\f\v]+", " ", text or "")
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def extract(raw: dict[str, Any], selector: str = "") -> dict[str, Any]:
    """Titre, description, texte principal et liens d'une page déjà récupérée."""
    from scrapling.parser import Selector  # Scrapling : analyse HTML rapide, sélecteurs CSS/XPath

    url, content = raw["url"], raw["text"]
    if raw["content_type"] not in {"text/html", "application/xhtml+xml"}:
        return {"url": url, "title": url, "description": "", "text": _collapse(content)[:200_000], "links": [],
                "bytes": raw["bytes"], "hash": hashlib.sha256(content.encode("utf-8", "replace")).hexdigest()[:24]}
    page = Selector(content, url=url)
    title = _collapse(page.css("title::text").get() or "") or _collapse(page.css("h1::text").get() or "") or url
    description = _collapse(page.css('meta[name="description"]::attr(content)').get() or "")
    selector = (selector or "").strip()
    if selector:
        if len(selector) > 200:
            raise FetchError("Sélecteur CSS trop long.")
        try:
            elements = page.css(selector)
        except Exception as exc:  # noqa: BLE001 — SelectorSyntaxError et erreurs lxml
            raise FetchError(f"Sélecteur CSS invalide : {exc}") from exc
        parts = [_collapse(el.get_all_text(separator=" ", strip=True)) for el in elements]
        text = "\n\n".join(p for p in parts if p)
        if not text:
            raise FetchError("Le sélecteur CSS ne correspond à aucun contenu.")
    else:
        text = ""
        try:
            import trafilatura
            text = trafilatura.extract(content, include_tables=True, include_comments=False, favor_recall=True, url=url) or ""
        except Exception:  # noqa: BLE001 — trafilatura peut échouer sur du HTML très abîmé : repli ci-dessous
            logger.debug("trafilatura a échoué pour %s", url, exc_info=True)
        if len(text) < 200:  # page atypique : texte du corps via Scrapling
            body = page.css("body")
            fallback = _collapse(body[0].get_all_text(separator=" ", strip=True)) if len(body) else ""
            text = fallback if len(fallback) > len(text) else text
    links: list[str] = []
    seen: set[str] = set()
    for href in page.css("a::attr(href)").getall():
        absolute = urldefrag(urljoin(url, href.strip()))[0]
        if absolute.startswith(("http://", "https://")) and absolute not in seen:
            seen.add(absolute)
            links.append(absolute)
    text = _collapse(text)[:200_000]
    return {"url": url, "title": truncate(title, 300), "description": truncate(description, 500), "text": text,
            "links": links[:400], "bytes": raw["bytes"], "hash": hashlib.sha256(text.encode("utf-8", "replace")).hexdigest()[:24]}


def read_page(url: str, selector: str = "") -> dict[str, Any]:
    page = extract(fetch(url), selector)
    if not page["text"]:
        raise FetchError("Aucun texte exploitable sur cette page (page vide ou rendue par JavaScript).")
    page["fetched_at"] = now_iso()
    return page


# --- Enregistrement dans la base de connaissances -----------------------------------------------

def save_page(page: dict[str, Any], category: str = "Web", tags: str = "") -> dict[str, Any]:
    """Crée ou met à jour la fiche de cette URL. ``status`` : created, updated ou unchanged."""
    content = (f"{page['title']}\n\nSource : {page['url']}\nCollecté le {page.get('fetched_at') or now_iso()} "
               f"(contenu externe, non vérifié)\n\n{page['text']}")[:200_000]
    tag_list = ",".join(dict.fromkeys(t.strip() for t in ("web-import," + tags).split(",") if t.strip()))
    existing = db.fetch_one("SELECT id,content FROM knowledge_docs WHERE source=? ORDER BY updated_at DESC LIMIT 1", (page["url"],))
    now = now_iso()
    if existing:
        if existing["content"] == content:
            return {"id": existing["id"], "status": "unchanged"}
        db.execute("UPDATE knowledge_docs SET title=?, category=?, content=?, tags=?, updated_at=? WHERE id=?",
                   (page["title"][:300], category[:100], content, tag_list[:500], now, existing["id"]))
        return {"id": existing["id"], "status": "updated"}
    doc_id = new_id("kb")
    db.execute("INSERT INTO knowledge_docs(id,title,category,content,source,tags,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?)",
               (doc_id, page["title"][:300], category[:100], content, page["url"][:500], tag_list[:500], now, now))
    return {"id": doc_id, "status": "created"}


def visit(url: str, selector: str = "", save: bool = False, category: str = "Web", tags: str = "") -> dict[str, Any]:
    page = read_page(url, selector)
    db.audit("web_visit", {"url": page["url"], "bytes": page["bytes"], "saved": save})
    result = {k: page[k] for k in ("url", "title", "description", "bytes", "fetched_at")}
    result["text"] = truncate(page["text"], 20_000)
    result["chars"] = len(page["text"])
    result["links"] = page["links"][:50]
    if save:
        result["saved"] = save_page(page, category or "Web", tags)
    return result


# --- Pages citées dans une question de l'assistant -----------------------------------------------

_page_cache: dict[str, tuple[float, dict[str, Any] | None]] = {}
_page_lock = threading.Lock()


def pages_for_message(message: str, limit: int = 2) -> list[dict[str, Any]]:
    found = list(dict.fromkeys(m.rstrip(".,;:!?") for m in URL_RE.findall(message or "")))[:limit]
    if found and not _flag("ai_browse"):
        return []
    if not found and not _flag("ai_search", False):
        return []
    pages: list[dict[str, Any]] = []
    # Sans lien explicite, effectue une recherche Web pour apporter des références récentes.
    # Les blocs de code, secrets évidents et URL sont exclus de la requête transmise au moteur.
    if not found:
        query = re.sub(r"```.*?```|`[^`]*`", " ", message or "", flags=re.S)
        query = re.sub(r"https?://\S+|\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b", " ", query)
        query = re.sub(r"(?i)\b(?:bearer\s+\S+|(?:api[_-]?key|token|password|secret)\s*[:=]\s*\S+)", "[masqué]", query)
        query = re.sub(r"\b(?:sk-[A-Za-z0-9_-]{12,}|gh[pousr]_[A-Za-z0-9]{16,}|github_pat_[A-Za-z0-9_]{16,}|xox[abprs]-[A-Za-z0-9-]{12,}|(?:AKIA|ASIA)[0-9A-Z]{16})\b", "[masqué]", query)
        query = re.sub(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", "[clé privée masquée]", query, flags=re.S)
        query = re.sub(r"\bAIza[0-9A-Za-z_-]{30,}\b|\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b", "[jeton masqué]", query)
        query = _collapse(query)[:280]
        if len(query) >= 3:
            try:
                from . import websearch
                deep = _flag("web_research_mode", False)
                result = websearch.search(query, limit=20 if deep else 8)
                selected = result.get("items", [])[: (3 if deep else 2)]
                selected_urls = {item["url"] for item in selected}
                pages.extend({"url": item["url"], "title": item["title"], "text": item.get("snippet", ""),
                              "search_source": item.get("source", "Web"), "search_result": True}
                             for item in result.get("items", [])[: (10 if deep else 5)] if item["url"] not in selected_urls)
                found = [item["url"] for item in selected]
            except (ValueError, RuntimeError, requests.RequestException) as exc:
                logger.info("Recherche Web de l’assistant indisponible : %s", type(exc).__name__)
    now = time.monotonic()
    for url in found:
        with _page_lock:
            hit = _page_cache.get(url)
        if hit and hit[0] > now:
            page = hit[1]
        else:
            try:
                page = read_page(url)
                db.audit("web_visit", {"url": page["url"], "bytes": page["bytes"], "via": "assistant"})
            except FetchError as exc:
                logger.info("Page ignorée (%s) : %s", url, exc)
                page = None
            with _page_lock:
                _page_cache[url] = (now + 900, page)
        if page:
            pages.append(page)
    return pages


# --- Exploration (plusieurs pages d'un même site) -----------------------------------------------

_cancel: dict[str, threading.Event] = {}


def _job_update(job_id: str, **fields: Any) -> None:
    sets = ", ".join(f"{k}=?" for k in fields)
    db.execute(f"UPDATE web_jobs SET {sets} WHERE id=?", (*fields.values(), job_id))


def get_job(job_id: str) -> dict[str, Any] | None:
    row = db.fetch_one("SELECT * FROM web_jobs WHERE id=?", (job_id,))
    if row:
        row["progress"] = db.json_loads(row.pop("progress_json"), {})
        row["result"] = db.json_loads(row.pop("result_json"), {})
    return row


def list_jobs(limit: int = 20) -> list[dict[str, Any]]:
    ids = db.fetch_all("SELECT id FROM web_jobs ORDER BY created_at DESC LIMIT ?", (limit,))
    return [j for j in (get_job(r["id"]) for r in ids) if j]


def start_crawl(url: str, max_pages: int = 10, depth: int = 1, category: str = "Web", tags: str = "", selector: str = "") -> dict[str, Any]:
    start = check_url(url)
    max_pages = max(1, min(MAX_CRAWL_PAGES, int(max_pages)))
    depth = max(0, min(MAX_CRAWL_DEPTH, int(depth)))
    if db.fetch_one("SELECT id FROM web_jobs WHERE status IN ('queued','running') LIMIT 1"):
        raise FetchError("Une exploration est déjà en cours.")
    job_id = new_id("web")
    db.execute("INSERT INTO web_jobs(id,kind,url,status,progress_json,result_json,created_at) VALUES(?,?,?,?,?,?,?)",
               (job_id, "crawl", start, "queued", db.json_dumps({"pages": 0, "max_pages": max_pages}), "{}", now_iso()))
    db.audit("web_crawl_started", {"url": start, "max_pages": max_pages, "depth": depth})
    event = threading.Event()
    _cancel[job_id] = event
    threading.Thread(target=_crawl, args=(job_id, start, max_pages, depth, category, tags, selector, event),
                     name="cybbig-crawl", daemon=True).start()
    return get_job(job_id) or {}


def cancel_job(job_id: str) -> bool:
    event = _cancel.get(job_id)
    if event:
        event.set()
        return True
    return False


def _crawl(job_id: str, start: str, max_pages: int, depth: int, category: str, tags: str, selector: str, cancel: threading.Event) -> None:
    host = urlparse(start).netloc.lower()
    queue: list[tuple[str, int]] = [(start, 0)]
    seen = {start}
    counts = {"created": 0, "updated": 0, "unchanged": 0, "failed": 0}
    errors: list[str] = []
    visited = 0
    _job_update(job_id, status="running")
    try:
        while queue and visited < max_pages and not cancel.is_set():
            current, level = queue.pop(0)
            try:
                page = read_page(current, selector)
                saved = save_page(page, category or "Web", tags)
                counts[saved["status"]] += 1
                if level < depth:
                    for link in page["links"]:
                        if link not in seen and urlparse(link).netloc.lower() == host:  # même site uniquement
                            seen.add(link)
                            queue.append((link, level + 1))
            except FetchError as exc:
                counts["failed"] += 1
                errors.append(f"{current} : {exc}")
            visited += 1
            _job_update(job_id, progress_json=db.json_dumps({"pages": visited, "max_pages": max_pages, "queued": len(queue), "current": current}))
            if queue and not cancel.is_set():
                time.sleep(CRAWL_DELAY)
        final = "cancelled" if cancel.is_set() else "completed"
        _job_update(job_id, status=final, finished_at=now_iso(), result_json=db.json_dumps({**counts, "errors": errors[:10]}))
        db.audit("web_crawl_finished", {"url": start, **counts})
    except Exception as exc:  # noqa: BLE001 — le fil ne doit jamais mourir sans marquer la tâche
        logger.exception("Exploration interrompue")
        _job_update(job_id, status="failed", finished_at=now_iso(), result_json=db.json_dumps({**counts, "errors": [f"{type(exc).__name__}: {exc}"]}))
    finally:
        _cancel.pop(job_id, None)


def recover_stale_jobs() -> None:
    db.execute("UPDATE web_jobs SET status='failed', finished_at=? WHERE status IN ('queued','running')", (now_iso(),))
