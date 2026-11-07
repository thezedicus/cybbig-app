from __future__ import annotations

import json
import re
import socket
import ssl
import time
from datetime import datetime, timezone
from http.cookies import SimpleCookie
from typing import Any
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from ...config import MAX_HTTP_BYTES, MAX_PAGES_DEFAULT, REQUEST_DELAY_SECONDS, USER_AGENT
from ...utils import now_iso, redact_text, truncate
from ..base import ScanContext
from .php_scanner import SECRET_KEY_RE as PHP_SECRET_KEY_RE, _likely_secret_value as likely_secret_value
from ..scope import check_web_scope
from . import active_checks

SECURITY_HEADERS = {
    "strict-transport-security": "HSTS",
    "content-security-policy": "CSP",
    "x-content-type-options": "X-Content-Type-Options",
    "x-frame-options": "X-Frame-Options",
    "referrer-policy": "Referrer-Policy",
    "permissions-policy": "Permissions-Policy",
}

SENSITIVE_PATHS = [
    ("/.env", "Fichier .env exposé", "critical", "env"),
    ("/.git/HEAD", "Dépôt Git exposé", "critical", "git"),
    ("/.git/config", "Configuration Git exposée", "high", "gitconfig"),
    ("/wp-config.php.bak", "Sauvegarde de configuration WordPress", "critical", "php"),
    ("/wp-config.php~", "Sauvegarde de configuration WordPress", "critical", "php"),
    ("/config.php.bak", "Sauvegarde de configuration PHP", "high", "php"),
    ("/backup.zip", "Archive de sauvegarde exposée", "high", "zip"),
    ("/backup.sql", "Export SQL exposé", "critical", "sql"),
    ("/database.sql", "Export SQL exposé", "critical", "sql"),
    ("/phpinfo.php", "phpinfo() exposé", "high", "phpinfo"),
    ("/info.php", "phpinfo() exposé", "high", "phpinfo"),
    ("/server-status", "Page de statut serveur exposée", "medium", "status"),
    ("/adminer.php", "Adminer exposé", "high", "adminer"),
    ("/.DS_Store", "Métadonnées macOS exposées", "low", "dsstore"),
    ("/composer.lock", "Verrou de dépendances exposé", "low", "composer"),
    ("/storage/logs/laravel.log", "Journal Laravel exposé", "high", "log"),
    ("/debug.log", "Journal de debug exposé", "medium", "log"),
    ("/artisan", "Fichier artisan exposé", "low", "text"),
]

CHECKOUT_HINTS = re.compile(r"(checkout|payment|paiement|panier|cart|billing|facturation|order|commande)", re.I)
CARD_FIELD_NAMES = re.compile(
    r"(card[_-]?(number|num|no)|cc[_-]?number|pan|card[_-]?cvc|cvv|cvc2|expir|cc[_-]?exp)", re.I
)
TRUSTED_SCRIPT_DOMAINS = {
    "googletagmanager.com", "www.googletagmanager.com", "google-analytics.com", "www.google-analytics.com",
    "js.stripe.com", "checkout.stripe.com", "www.paypal.com", "js.paypal.com", "www.paypalobjects.com",
    "cdn.jsdelivr.net", "cdnjs.cloudflare.com", "unpkg.com", "www.gstatic.com", "recaptcha.net",
}


def _session(user_agent: str = "") -> requests.Session:
    s = requests.Session()
    agent = (user_agent or USER_AGENT).replace("\r", "").replace("\n", "").strip()[:200] or USER_AGENT
    s.headers.update({
        "User-Agent": agent,
        "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
        "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.7",
        "Cache-Control": "no-cache",
    })
    # Route les analyses passives via le proxy actif si l'utilisateur l'a demandé.
    try:
        from ..proxy import requests_proxies

        proxies = requests_proxies()
        if proxies:
            s.proxies.update(proxies)
    except Exception:  # noqa: BLE001 — un proxy indisponible ne doit pas casser le scan
        pass
    return s


def _decode_body(content: bytes, content_type: str) -> str:
    if not content:
        return ""
    charset = ""
    m = re.search(r"charset=([A-Za-z0-9_\-]+)", content_type or "", re.I)
    if m:
        charset = m.group(1)
    for enc in [charset, "utf-8", "latin-1"]:
        if not enc:
            continue
        try:
            return content.decode(enc, errors="strict")
        except (UnicodeDecodeError, LookupError):
            continue
    return content.decode("utf-8", errors="replace")


def _fetch(session: requests.Session, url: str, max_bytes: int = MAX_HTTP_BYTES) -> dict[str, Any]:
    response = session.get(url, timeout=15, allow_redirects=False, stream=True, verify=True)
    content = b""
    try:
        for chunk in response.iter_content(65536):
            if chunk:
                content += chunk
            if len(content) >= max_bytes:
                break
    finally:
        response.close()
    headers = {k.lower(): v for k, v in response.headers.items()}
    return {
        "status": response.status_code,
        "headers": headers,
        "raw_headers": response.raw.headers,
        "content": content[:max_bytes],
        "text": _decode_body(content[:max_bytes], headers.get("content-type", "")),
        "url": url,
        "elapsed_ms": int(response.elapsed.total_seconds() * 1000),
        "reason": response.reason,
    }


def _follow(session: requests.Session, ctx: ScanContext, url: str) -> tuple[dict[str, Any] | None, list[dict[str, Any]], str]:
    chain: list[dict[str, Any]] = []
    current = url
    for _ in range(4):
        if ctx.cancelled():
            return None, chain, current
        try:
            result = _fetch(session, current)
        except requests.exceptions.SSLError as exc:
            return None, chain, f"TLS: {exc}"
        except requests.RequestException as exc:
            return None, chain, f"{type(exc).__name__}: {exc}"
        chain.append({"url": current, "status": result["status"]})
        if result["status"] in {301, 302, 303, 307, 308}:
            location = result["headers"].get("location", "")
            if not location:
                return result, chain, ""
            next_url = urljoin(current, location)
            if urlparse(next_url).scheme not in {"http", "https"}:
                return result, chain, ""
            decision = check_web_scope(ctx.project, next_url)
            if not decision.allowed:
                ctx.extra.setdefault("warnings", []).append(
                    f"Redirection vers {next_url} non suivie : {decision.reason}"
                )
                return result, chain, ""
            current = next_url
            time.sleep(REQUEST_DELAY_SECONDS)
            continue
        return result, chain, ""
    return None, chain, "Trop de redirections (max 4)."


def _tls_info(host: str, port: int) -> dict[str, Any]:
    info: dict[str, Any] = {"checked": False}
    try:
        context = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=8) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert() or {}
                info.update({
                    "checked": True,
                    "version": ssock.version(),
                    "cipher": (ssock.cipher() or ("",))[0],
                    "subject": cert.get("subject"),
                    "issuer": cert.get("issuer"),
                    "not_before": cert.get("notBefore"),
                    "not_after": cert.get("notAfter"),
                    "san": cert.get("subjectAltName", []),
                })
                if cert.get("notAfter"):
                    try:
                        expiry = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
                        info["days_to_expiry"] = (expiry - datetime.now(timezone.utc)).days
                    except ValueError:
                        pass
                return info
    except (ssl.SSLError, socket.error, ValueError) as exc:
        info["error"] = f"{type(exc).__name__}: {exc}"
        return info


def _add(ctx: ScanContext, **kwargs: Any) -> None:
    kwargs.setdefault("engine", "web")
    ctx.add_finding(**kwargs)


def _analyze_headers(ctx: ScanContext, url: str, result: dict[str, Any]) -> None:
    headers = result["headers"]
    parsed = urlparse(url)
    https = parsed.scheme == "https"
    hsts = headers.get("strict-transport-security", "")
    if https and not hsts:
        _add(
            ctx, rule_id="web-hsts-missing", title="HSTS absent", severity="medium",
            confidence="high", category="Configuration HTTP", url=url,
            description="Le site HTTPS ne demande pas au navigateur d'imposer TLS pour les prochaines visites.",
            evidence=f"Strict-Transport-Security: absent — {url}",
            cwe="CWE-319", owasp="A02:2021",
            remediation="Ajouter Strict-Transport-Security: max-age=31536000; includeSubDomains après validation de tous les sous-domaines HTTPS.",
            references=["https://developer.mozilla.org/fr/docs/Web/HTTP/Headers/Strict-Transport-Security"],
        )
    elif https and hsts:
        m = re.search(r"max-age\s*=\s*(\d+)", hsts, re.I)
        if m and int(m.group(1)) < 15_552_000:
            _add(
                ctx, rule_id="web-hsts-short", title="HSTS avec durée trop courte", severity="low",
                confidence="high", category="Configuration HTTP", url=url,
                description="La durée HSTS est inférieure à six mois.", evidence=f"Strict-Transport-Security: {hsts}",
                cwe="CWE-319", owasp="A02:2021",
                remediation="Utiliser max-age=31536000 et envisager includeSubDomains/preload.",
                references=["https://developer.mozilla.org/fr/docs/Web/HTTP/Headers/Strict-Transport-Security"],
            )
    if not https:
        _add(
            ctx, rule_id="web-http", title="Application accessible en HTTP", severity="medium",
            confidence="high", category="Transport", url=url,
            description="La page a été récupérée en clair. Les données peuvent être interceptées ou modifiées.",
            evidence=f"URL finale : {url}", cwe="CWE-319", owasp="A02:2021",
            remediation="Rediriger HTTP vers HTTPS, activer HSTS et vérifier les ressources mixtes.",
            references=["https://owasp.org/www-project-top-ten/2017/A3_2017-Sensitive_Data_Exposure"],
        )
    csp = headers.get("content-security-policy", "")
    if not csp:
        _add(
            ctx, rule_id="web-csp-missing", title="Content-Security-Policy absente", severity="high",
            confidence="high", category="Configuration HTTP", url=url,
            description="Aucune CSP n'est définie. Une injection HTML ou un script tiers malveillant dispose de moins de barrières.",
            evidence=f"Content-Security-Policy: absent — {url}",
            cwe="CWE-693", owasp="A05:2021",
            remediation="Déployer une CSP avec nonces/hashs, script-src restreint, object-src 'none', base-uri 'none' et frame-ancestors.",
            references=["https://developer.mozilla.org/fr/docs/Web/HTTP/CSP"],
        )
    else:
        lower = csp.lower()
        issues = []
        if "'unsafe-inline'" in lower:
            issues.append("unsafe-inline")
        if "'unsafe-eval'" in lower:
            issues.append("unsafe-eval")
        if re.search(r"script-src[^;]*\*", lower):
            issues.append("wildcard script-src")
        if "object-src 'none'" not in lower:
            issues.append("object-src manquant")
        if "frame-ancestors" not in lower:
            issues.append("frame-ancestors manquant")
        if "base-uri" not in lower:
            issues.append("base-uri manquant")
        if issues:
            _add(
                ctx, rule_id="web-csp-weak", title="Content-Security-Policy permissive", severity="medium",
                confidence="medium", category="Configuration HTTP", url=url,
                description="La CSP présente des directives permissives ou incomplètes.",
                evidence=f"Content-Security-Policy: {truncate(csp, 500)} — points : {', '.join(issues)}",
                cwe="CWE-693", owasp="A05:2021",
                remediation="Retirer unsafe-inline/unsafe-eval, restreindre script-src et ajouter object-src/base-uri/frame-ancestors.",
                references=["https://developer.mozilla.org/fr/docs/Web/HTTP/CSP"],
            )
    if headers.get("x-content-type-options", "").lower() != "nosniff":
        _add(
            ctx, rule_id="web-nosniff", title="X-Content-Type-Options absent", severity="low",
            confidence="high", category="Configuration HTTP", url=url,
            description="Le navigateur peut interpréter un contenu avec un type différent de celui déclaré.",
            evidence=f"X-Content-Type-Options: {headers.get('x-content-type-options', 'absent')}",
            cwe="CWE-436", owasp="A05:2021",
            remediation="Ajouter X-Content-Type-Options: nosniff sur toutes les réponses.",
            references=["https://developer.mozilla.org/fr/docs/Web/HTTP/Headers/X-Content-Type-Options"],
        )
    if not headers.get("x-frame-options") and "frame-ancestors" not in csp.lower():
        _add(
            ctx, rule_id="web-clickjacking", title="Protection anti-clickjacking absente", severity="medium",
            confidence="high", category="Configuration HTTP", url=url,
            description="La page peut être intégrée dans une iframe tierce et être victime de clickjacking.",
            evidence="X-Frame-Options absent et aucune directive frame-ancestors.",
            cwe="CWE-1021", owasp="A05:2021",
            remediation="Ajouter frame-ancestors 'none' (ou une liste blanche) et X-Frame-Options: DENY en défense en profondeur.",
            references=["https://owasp.org/www-community/attacks/Clickjacking"],
        )
    referrer = headers.get("referrer-policy", "")
    if not referrer or referrer.lower() in {"unsafe-url", "no-referrer-when-downgrade"}:
        _add(
            ctx, rule_id="web-referrer", title="Referrer-Policy absente ou permissive", severity="low",
            confidence="high", category="Configuration HTTP", url=url,
            description="Les URL internes peuvent fuiter vers des sites tiers via le referer.",
            evidence=f"Referrer-Policy: {referrer or 'absente'}", cwe="CWE-200", owasp="A05:2021",
            remediation="Utiliser strict-origin-when-cross-origin ou no-referrer selon le besoin.",
            references=["https://developer.mozilla.org/fr/docs/Web/HTTP/Headers/Referrer-Policy"],
        )
    if not headers.get("permissions-policy"):
        _add(
            ctx, rule_id="web-permissions-policy", title="Permissions-Policy absente", severity="info",
            confidence="high", category="Configuration HTTP", url=url,
            description="Les fonctionnalités navigateur (caméra, micro, géolocalisation) ne sont pas explicitement restreintes.",
            evidence="Permissions-Policy: absente", cwe="CWE-693", owasp="A05:2021",
            remediation="Déclarer Permissions-Policy avec les fonctionnalités réellement nécessaires.",
            references=["https://developer.mozilla.org/fr/docs/Web/HTTP/Headers/Permissions-Policy"],
        )
    for header in ("server", "x-powered-by", "x-aspnet-version", "x-generator"):
        value = headers.get(header, "")
        if value and re.search(r"\d+\.\d+", value):
            _add(
                ctx, rule_id="web-version-disclosure", title="Version logicielle divulguée",
                severity="low", confidence="high", category="Exposition d'information", url=url,
                description="Un en-tête révèle une version de serveur ou de framework, ce qui facilite le ciblage.",
                evidence=f"{header}: {value}", cwe="CWE-200", owasp="A05:2021",
                remediation="Masquer les versions (ServerTokens, expose_php) et limiter les en-têtes superflus.",
                references=["https://owasp.org/Top10/A05_2021-Security_Misconfiguration/"],
            )
    cors = headers.get("access-control-allow-origin", "")
    credentials = headers.get("access-control-allow-credentials", "").lower() == "true"
    if cors == "*" and credentials:
        _add(
            ctx, rule_id="web-cors-wildcard", title="CORS permissif avec credentials", severity="high",
            confidence="high", category="CORS", url=url,
            description="L'origine * combinée aux credentials est une configuration dangereuse (et normalement refusée par les navigateurs).",
            evidence="Access-Control-Allow-Origin: * + Access-Control-Allow-Credentials: true",
            cwe="CWE-942", owasp="A05:2021",
            remediation="Spécifier une origine précise et éviter les credentials sur des endpoints publics.",
            references=["https://portswigger.net/web-security/cors"],
        )
    elif cors == "*":
        _add(
            ctx, rule_id="web-cors-public", title="CORS ouvert à toutes les origines", severity="low",
            confidence="high", category="CORS", url=url,
            description="L'API/ressource est lisible par n'importe quelle origine. Vérifier qu'aucune donnée sensible n'est exposée.",
            evidence="Access-Control-Allow-Origin: *", cwe="CWE-942", owasp="A05:2021",
            remediation="Restreindre aux origines nécessaires ; ne jamais exposer de données authentifiées avec *.",
            references=["https://portswigger.net/web-security/cors"],
        )
    cookie_headers = []
    try:
        cookie_headers = result["raw_headers"].getlist("Set-Cookie")  # type: ignore[attr-defined]
    except Exception:
        if headers.get("set-cookie"):
            cookie_headers = [headers["set-cookie"]]
    for raw in cookie_headers:
        try:
            jar = SimpleCookie()
            jar.load(raw)
        except Exception:
            continue
        for name, morsel in jar.items():
            attrs = {k.lower(): v for k, v in morsel.items()}
            issues = []
            if https and not attrs.get("secure"):
                issues.append("Secure absent")
            if not attrs.get("httponly"):
                issues.append("HttpOnly absent")
            if not attrs.get("samesite"):
                issues.append("SameSite absent")
            if issues:
                _add(
                    ctx, rule_id="web-cookie-flags", title=f"Attributs de cookie insuffisants : {name}",
                    severity="medium", confidence="high", category="Cookies", url=url,
                    description="Un cookie est émis sans tous les attributs de protection recommandés.",
                    evidence=f"Set-Cookie: {name} — {', '.join(issues)}",
                    cwe="CWE-614", owasp="A07:2021",
                    remediation="Ajouter Secure, HttpOnly et SameSite=Lax/Strict selon l'usage ; limiter Path et la durée de vie.",
                    references=["https://owasp.org/www-community/controls/SecureCookieAttribute"],
                )


try:
    import trafilatura as _trafilatura
except Exception:  # pragma: no cover - optional dependency
    _trafilatura = None


def _clean_text(soup: BeautifulSoup) -> str:
    if _trafilatura is not None:
        try:
            extracted = _trafilatura.extract(str(soup), output_format="txt", include_comments=False, include_tables=True)
            if extracted:
                return re.sub(r"\s+", " ", extracted).strip()
        except Exception:
            pass
    clone = BeautifulSoup(str(soup), "html.parser")
    for tag in clone(["script", "style", "noscript", "template"]):
        tag.decompose()
    return re.sub(r"\s+", " ", clone.get_text(" ", strip=True)).strip()


def _html_to_markdown(soup: BeautifulSoup) -> str:
    if _trafilatura is not None:
        try:
            extracted = _trafilatura.extract(str(soup), output_format="markdown", include_comments=False, include_tables=True)
            if extracted:
                return extracted[:8000]
        except Exception:
            pass
    lines: list[str] = []
    for element in soup.find_all(["h1", "h2", "h3", "h4", "p", "li", "pre", "code"]):
        text = element.get_text(" ", strip=True)
        if not text:
            continue
        name = element.name
        if name in {"h1", "h2", "h3", "h4"}:
            level = int(name[1])
            lines.append(f"{'#' * level} {text}")
        elif name == "li":
            lines.append(f"- {text}")
        elif name in {"pre", "code"}:
            lines.append(f"```\n{text}\n```")
        else:
            lines.append(text)
    # Liens utiles.
    for link in soup.find_all("a", href=True)[:30]:
        label = link.get_text(" ", strip=True)
        href = (link.get("href") or "").strip()
        if label and href:
            lines.append(f"- [{label}]({href})")
    markdown = "\n\n".join(lines)
    return markdown[:8000]


def parse_html_assets(base_url: str, html: str) -> dict[str, Any]:
    soup = BeautifulSoup(html or "", "html.parser")
    scripts: list[dict[str, Any]] = []
    inline_scripts: list[str] = []
    for tag in soup.find_all("script"):
        src = (tag.get("src") or "").strip()
        if src:
            absolute = urljoin(base_url, src)
            host = (urlparse(absolute).hostname or "").lower()
            scripts.append({
                "url": absolute,
                "host": host,
                "integrity": bool(tag.get("integrity")),
                "crossorigin": bool(tag.get("crossorigin")),
                "type": (tag.get("type") or "").lower(),
                "async": bool(tag.get("async")),
                "defer": bool(tag.get("defer")),
                "inline": False,
            })
        else:
            content = tag.string or tag.get_text() or ""
            if content.strip():
                inline_scripts.append(content)
    forms: list[dict[str, Any]] = []
    for form in soup.find_all("form"):
        fields = [{
            "name": (inp.get("name") or "").strip(),
            "type": (inp.get("type") or "text").lower(),
            "autocomplete": (inp.get("autocomplete") or "").lower(),
        } for inp in form.find_all(["input", "select", "textarea"])]
        forms.append({
            "action": urljoin(base_url, form.get("action") or base_url),
            "method": (form.get("method") or "get").upper(),
            "fields": fields,
            "has_password": any(f["type"] == "password" for f in fields),
            "has_card_fields": any(CARD_FIELD_NAMES.search(f["name"]) or CARD_FIELD_NAMES.search(f["autocomplete"]) for f in fields if f["name"] or f["autocomplete"]),
            "has_csrf_token": any(
                re.search(r"(csrf|xsrf|token|nonce|authenticity)", f["name"], re.I)
                for f in fields if f["name"]
            ),
        })
    iframes = [{
        "src": urljoin(base_url, i.get("src") or ""),
        "host": (urlparse(urljoin(base_url, i.get("src") or "")).hostname or "").lower(),
    } for i in soup.find_all("iframe")]
    generator = ""
    meta = soup.find("meta", attrs={"name": re.compile("generator", re.I)})
    if meta:
        generator = (meta.get("content") or "").strip()
    title = soup.title.get_text(strip=True) if soup.title else ""
    html_tag = soup.find("html")
    meta: dict[str, str] = {}
    for tag in soup.find_all("meta"):
        key = (tag.get("name") or tag.get("property") or tag.get("http-equiv") or "").strip().lower()
        content = (tag.get("content") or "").strip()
        if key and content and key not in meta:
            meta[key] = content[:500]
    json_ld: list[Any] = []
    for script in soup.find_all("script", attrs={"type": re.compile("application/ld\\+json", re.I)}):
        try:
            payload = json.loads(script.string or script.get_text() or "")
            json_ld.append(payload)
        except (ValueError, TypeError):
            continue
        if len(json_ld) >= 5:
            break
    api_candidates = []
    seen_candidates: set[str] = set()
    for value in [urljoin(base_url, a.get("href")) for a in soup.find_all("a", href=True)] + [s["url"] for s in scripts]:
        lower = value.lower()
        if any(token in lower for token in ("openapi", "swagger", "api-doc", "api/docs", "graphql", ".json")) and value not in seen_candidates:
            seen_candidates.add(value)
            api_candidates.append(value)
        if len(api_candidates) >= 20:
            break
    headings = [h.get_text(" ", strip=True) for h in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]) if h.get_text(strip=True)]
    links = [urljoin(base_url, a.get("href")) for a in soup.find_all("a", href=True)]
    internal_links = [link for link in links if (urlparse(link).hostname or "").lower() == (urlparse(base_url).hostname or "").lower()]
    cleaned_text = _clean_text(soup)
    markdown = _html_to_markdown(soup)
    return {
        "title": title,
        "generator": generator,
        "scripts": scripts,
        "inline_scripts": inline_scripts,
        "forms": forms,
        "iframes": iframes,
        "links": links[:200],
        "images": [urljoin(base_url, i.get("src")) for i in soup.find_all("img", src=True)][:200],
        "lang": (html_tag.get("lang") if html_tag else "") or "",
        "svg_onload": bool(re.search(r"<svg[^>]*\bonload\s*=", html or "", re.I)),
        "has_card_fields": any(f["has_card_fields"] for f in forms),
        "has_password_form": any(f["has_password"] for f in forms),
        "text_excerpt": cleaned_text[:4000],
        "markdown_excerpt": markdown[:6000],
        "meta": meta,
        "json_ld": json_ld,
        "api_candidates": api_candidates,
        "headings": headings[:25],
        "internal_links": len(internal_links),
        "external_links": len(links) - len(internal_links),
        "word_count": len(cleaned_text.split()),
    }


def _analyze_html(ctx: ScanContext, url: str, html: str, assets: dict[str, Any], checkout: bool) -> None:
    parsed = urlparse(url)
    https = parsed.scheme == "https"
    base_host = (parsed.hostname or "").lower()
    trusted = set(TRUSTED_SCRIPT_DOMAINS)
    configured = ctx.config.get("trusted_script_domains") or []
    if isinstance(configured, str):
        configured = [item.strip() for item in configured.split(",")]
    trusted.update(str(item).strip().lower().lstrip(".") for item in configured if str(item).strip())
    for script in assets["scripts"]:
        host = script["host"]
        if https and script["url"].startswith("http://"):
            _add(
                ctx, rule_id="web-mixed-script", title="Script chargé en HTTP sur une page HTTPS",
                severity="high", confidence="high", category="Contenu mixte", url=url,
                description="Un script non chiffré permet une injection ou une altération par un attaquant réseau.",
                evidence=f"<script src=\"{truncate(script['url'], 300)}\">",
                cwe="CWE-319", owasp="A02:2021",
                remediation="Servir tous les scripts en HTTPS et ajouter une CSP limitant les sources.",
                references=["https://developer.mozilla.org/fr/docs/Web/Security/Mixed_content"],
            )
        if host and host != base_host and not script["integrity"] and host not in trusted:
            _add(
                ctx, rule_id="web-thirdparty-script", title=f"Script tiers sans intégrité : {host}",
                severity="medium" if checkout else "low", confidence="medium", category="Scripts tiers",
                url=url, description="Un script tiers est chargé sans Subresource Integrity. Une compromission du tiers affecte la page.",
                evidence=f"{truncate(script['url'], 300)} (integrity absent)",
                cwe="CWE-829", owasp="A08:2021",
                remediation="Inventorier et autoriser chaque script, épingler une version, utiliser SRI/crossorigin et une CSP.",
                references=["https://developer.mozilla.org/fr/docs/Web/Security/Subresource_Integrity"],
            )
        if checkout and host and host != base_host and host not in trusted:
            _add(
                ctx, rule_id="checkout-thirdparty-domain", title=f"Domaine de script non référencé sur le checkout : {host}",
                severity="medium", confidence="low", category="Intégrité checkout", url=url,
                description="Un script d'un domaine inconnu est chargé sur la page de paiement. À comparer au registre PCI DSS 6.4.3.",
                evidence=truncate(script["url"], 300), cwe="CWE-829", owasp="A08:2021",
                remediation="Vérifier le propriétaire et la finalité du script, l'ajouter au registre autorisé ou le retirer.",
                references=["https://www.pcisecuritystandards.org/"],
            )
    if https:
        for resource in assets["images"][:100]:
            if resource.startswith("http://"):
                _add(
                    ctx, rule_id="web-mixed-image", title="Ressource image chargée en HTTP sur HTTPS",
                    severity="low", confidence="high", category="Contenu mixte", url=url,
                    description="Une ressource non chiffrée est chargée dans une page HTTPS.",
                    evidence=truncate(resource, 300), cwe="CWE-319", owasp="A02:2021",
                    remediation="Utiliser HTTPS pour toutes les ressources.", references=[],
                )
                break
    for form in assets["forms"]:
        action_host = (urlparse(form["action"]).hostname or "").lower()
        if form["method"] == "GET" and form["has_password"]:
            _add(
                ctx, rule_id="web-password-get", title="Formulaire de mot de passe en GET",
                severity="high", confidence="high", category="Formulaires", url=url,
                description="Un mot de passe envoyé en GET peut apparaître dans l'URL, l'historique et les journaux.",
                evidence=f"<form method=\"get\"> — {truncate(form['action'], 200)}",
                cwe="CWE-598", owasp="A04:2021",
                remediation="Utiliser POST sur HTTPS pour toute donnée d'authentification.",
                references=["https://owasp.org/www-community/vulnerabilities/Information_exposure_through_query_strings_in_url"],
            )
        if https and form["action"].startswith("http://"):
            _add(
                ctx, rule_id="web-form-http", title="Formulaire soumis en HTTP depuis HTTPS",
                severity="high", confidence="high", category="Formulaires", url=url,
                description="Les données du formulaire seraient transmises en clair.",
                evidence=f"action=\"{truncate(form['action'], 300)}\"", cwe="CWE-319", owasp="A02:2021",
                remediation="Pointer le formulaire vers une URL HTTPS du même périmètre de confiance.",
                references=[],
            )
        if form["method"] == "POST" and not form["has_csrf_token"]:
            _add(
                ctx, rule_id="web-csrf-heuristic", title="Formulaire POST sans jeton CSRF visible",
                severity="low", confidence="low", category="CSRF", url=url,
                description="Aucun champ caché de type CSRF/token n'a été détecté. Vérifier si la protection est appliquée par un en-tête ou un middleware.",
                evidence=f"POST {truncate(form['action'], 200)} — champs : {', '.join(f['name'] for f in form['fields'] if f['name'])[:300]}",
                cwe="CWE-352", owasp="A01:2021",
                remediation="Mettre en place un jeton anti-CSRF à usage unique et des cookies SameSite adaptés.",
                references=["https://owasp.org/www-community/attacks/csrf"],
            )
        if checkout and form["has_card_fields"] and action_host and action_host != base_host:
            _add(
                ctx, rule_id="checkout-external-form", title="Champs de carte soumis vers un domaine externe",
                severity="high", confidence="medium", category="Intégrité checkout", url=url,
                description="Le formulaire contient des champs de carte et pointe vers un domaine différent. Vérifier qu'il s'agit bien du PSP autorisé et du bon usage (iframe/tokenisation).",
                evidence=f"action=\"{truncate(form['action'], 300)}\" — champs carte détectés",
                cwe="CWE-829", owasp="A08:2021",
                remediation="Préférer une iframe/tokenisation du PSP, documenter le domaine autorisé et surveiller les modifications.",
                references=["https://www.pcisecuritystandards.org/"],
            )
    for iframe in assets["iframes"]:
        if checkout and iframe["host"] and iframe["host"] != base_host and iframe["host"] not in trusted:
            _add(
                ctx, rule_id="checkout-iframe-external", title=f"Iframe externe sur le checkout : {iframe['host']}",
                severity="medium", confidence="low", category="Intégrité checkout", url=url,
                description="Une iframe externe est présente sur la page de paiement. Vérifier le prestataire et l'inventaire.",
                evidence=truncate(iframe["src"], 300), cwe="CWE-829", owasp="A08:2021",
                remediation="Documenter l'iframe, restreindre frame-src et vérifier l'intégrité du contenu.",
                references=["https://www.pcisecuritystandards.org/"],
            )
    if checkout:
        _analyze_checkout_patterns(ctx, url, html, assets["inline_scripts"], source="page")


def _analyze_checkout_patterns(ctx: ScanContext, url: str, html: str, inline_scripts: list[str], source: str) -> None:
    combined = "\n".join(inline_scripts)
    if source == "page":
        combined = (html or "") + "\n" + combined
    patterns = [
        ("checkout-svg-onload", "SVG avec gestionnaire onload", "high",
         r"<svg[^>]*\bonload\s*=", "Un SVG inline avec onload peut exécuter du code. C'est un vecteur documenté de skimmer.",
         "Supprimer le SVG suspect, vérifier l'origine du contenu et restaurer depuis une version autorisée."),
        ("checkout-atob", "Décodage base64 dynamique (atob)", "medium",
         r"\batob\s*\(", "atob() est utilisé pour décoder une chaîne. Sur une page de paiement, cela peut masquer une charge utile.",
         "Auditer le script, vérifier son hash et le registre des scripts autorisés."),
        ("checkout-new-function", "Exécution dynamique new Function()", "high",
         r"\bnew\s+Function\s*\(", "new Function() permet d'exécuter du code construit dynamiquement, parfois depuis le réseau.",
         "Supprimer l'exécution dynamique et charger un script épinglé avec SRI."),
        ("checkout-eval", "Utilisation de eval()", "high",
         r"\beval\s*\(", "eval() exécute une chaîne comme du code. Sa présence sur le checkout est à justifier.",
         "Remplacer eval par une logique statique et vérifier le script."),
        ("checkout-websocket", "Connexion WebSocket sur le checkout", "medium",
         r"\b(new\s+WebSocket|wss://)", "Une WebSocket peut recevoir des charges utiles ou exfiltrer des données en contournant certains contrôles HTTP.",
         "Inventorier la destination, vérifier le besoin métier et bloquer les domaines non autorisés."),
        ("checkout-webrtc", "WebRTC détecté sur le checkout", "medium",
         r"\bRTCPeerConnection\b", "WebRTC peut établir un canal de données hors des contrôles HTTP classiques.",
         "Vérifier l'usage légitime et restreindre les permissions/CSP."),
        ("checkout-localstorage", "Stockage local utilisé sur le checkout", "low",
         r"\b(localStorage|sessionStorage)\s*\.", "Un script utilise le stockage local. Des skimmers y stockent parfois des données avant exfiltration.",
         "Inventorier les clés et les scripts qui les utilisent ; ne jamais stocker de données de carte."),
        ("checkout-stripe-secret", "Clé Stripe secrète dans du code client", "critical",
         r"\bsk_(live|test)_[A-Za-z0-9]{12,}", "Une clé secrète Stripe exposée côté client peut permettre des opérations non autorisées sur le compte.",
         "Révoquer la clé immédiatement, la déplacer côté serveur et auditer les accès."),
        ("checkout-fake-gtm", "Conteneur GTM détecté sur le checkout", "info",
         r"googletagmanager\.com/gtm\.js\?id=(GTM-[A-Z0-9]+)", "Un conteneur GTM est chargé. Il doit figurer dans l'inventaire des scripts autorisés.",
         "Vérifier le propriétaire du conteneur, son historique et les balises qu'il déclenche."),
        ("checkout-obfuscation", "Chaîne fortement obfusquée", "medium",
         r"(?:\\x[0-9a-f]{2}){20,}|(?:[A-Za-z0-9+/]{80,}={0,2})", "Une longue chaîne encodée/obfusquée est présente. À examiner manuellement.",
         "Décoder uniquement dans un environnement isolé, comparer au hash autorisé et remplacer le script si non justifié."),
    ]
    for rule_id, title, sev, pattern, description, remediation in patterns:
        match = re.search(pattern, combined if source != "page-svg" else html, re.I | re.S)
        if match:
            snippet = combined[max(0, match.start() - 60): match.end() + 120] if combined else html[max(0, match.start() - 60): match.end() + 120]
            _add(
                ctx, engine="checkout", rule_id=rule_id, title=title, severity=sev,
                confidence="high" if rule_id in {"checkout-stripe-secret", "checkout-new-function"} else "medium",
                category="Intégrité checkout", url=url,
                description=description, evidence=redact_text(snippet, 500),
                cwe="CWE-829", owasp="A08:2021", remediation=remediation,
                references=["https://www.pcisecuritystandards.org/"],
            )


def _analyze_js_text(ctx: ScanContext, url: str, text: str, origin: str) -> None:
    if not text or not text.strip():
        return
    seen: set[str] = set()
    lines = text.splitlines()
    # Secrets dans le JavaScript.
    secret_count = 0
    for idx, line in enumerate(lines, 1):
        if ctx.cancelled():
            return
        for match in PHP_SECRET_KEY_RE.finditer(line):
            key, value = match.group(1), match.group(2)
            if not likely_secret_value(value):
                continue
            if secret_count >= 5:
                break
            secret_count += 1
            rule_key = f"web-js-secret-{key.lower()}-{idx}"
            if rule_key in seen:
                continue
            seen.add(rule_key)
            _add(
                ctx, rule_id="web-js-secret", title=f"Secret potentiel dans un script JavaScript ({key})",
                severity="high", confidence="medium", category="Secrets exposés", url=url,
                description="Une valeur ressemblant à un secret est présente en clair dans un script côté client.",
                evidence=f"{origin} — ligne {idx} : {key} = {redact_secret(value)}",
                cwe="CWE-798", owasp="A07:2021",
                remediation="Retirer le secret du code client, le révoquer et le stocker côté serveur ou dans un gestionnaire de secrets.",
                references=["https://owasp.org/www-community/vulnerabilities/Use_of_hard-coded_password"],
            )
    # Motifs dangereux dans le JavaScript.
    patterns = [
        ("web-js-eval", "Utilisation de eval() dans un script", "high",
         r"\beval\s*\(", "eval() exécute une chaîne comme du code et facilite l'injection."),
        ("web-js-new-function", "Exécution dynamique new Function()", "high",
         r"\bnew\s+Function\s*\(", "new Function() construit et exécute du code dynamiquement."),
        ("web-js-document-write", "Utilisation de document.write()", "medium",
         r"document\.write\s*\(", "document.write() peut injecter du HTML non filtré et écraser le document."),
        ("web-js-innerhtml", "Écriture directe dans innerHTML", "medium",
         r"\.innerHTML\s*=", "L'écriture dans innerHTML sans encodage expose à des XSS."),
        ("web-js-atob", "Décodage base64 dans un script", "low",
         r"\batob\s*\(", "atob() est utilisé pour décoder une charge utile ; à vérifier manuellement."),
        ("web-js-websocket", "Connexion WebSocket dans un script", "low",
         r"\bnew\s+WebSocket\s*\(|wss?://", "Une WebSocket est ouverte ; vérifier la destination et l'authentification."),
        ("web-js-localstorage", "Stockage local utilisé par un script", "info",
         r"\b(localStorage|sessionStorage)\s*\.", "Le stockage local est utilisé ; vérifier qu'aucune donnée sensible n'y est conservée."),
        ("web-js-dynamic-script", "Injection dynamique de script", "medium",
         r"createElement\s*\(\s*['\"]script['\"]", "Un script est injecté dynamiquement dans la page."),
        ("web-js-fetch", "Requête réseau depuis un script", "info",
         r"\b(fetch|XMLHttpRequest)\s*\(", "Le script effectue des requêtes réseau ; vérifier les destinations et les données envoyées."),
        ("web-js-card-field", "Champ de carte manipulé par un script", "high",
         r"(card[_-]?(number|num|pan|cvv|cvc)|payment)", "Un script manipule des données de paiement ; vérifier l'absence de skimmer."),
    ]
    for rule_id, title, severity, pattern, description in patterns:
        if rule_id in seen:
            continue
        match = re.search(pattern, text, re.I)
        if not match:
            continue
        seen.add(rule_id)
        snippet = text[max(0, match.start() - 80): match.end() + 120]
        _add(
            ctx, rule_id=rule_id, title=title, severity=severity, confidence="medium",
            category="Code source JavaScript", url=url, description=description,
            evidence=f"{origin} — {redact_text(snippet, 300)}", cwe="CWE-79", owasp="A03:2021",
            remediation="Auditer le script, vérifier son origine, son hash et son inscription au registre des scripts autorisés.",
            references=["https://owasp.org/www-community/attacks/xss/"],
        )

def _probe_paths(ctx: ScanContext, session: requests.Session, base_url: str) -> None:
    if ctx.config.get("probe_exposed_files", True) is False:
        return
    parsed = urlparse(base_url)
    origin = f"{parsed.scheme}://{parsed.netloc}"
    probes = []
    limited = SENSITIVE_PATHS[: int(ctx.config.get("max_exposed_paths", 12))]
    for path, label, severity, kind in limited:
        if ctx.cancelled():
            return
        url = origin + path
        try:
            time.sleep(REQUEST_DELAY_SECONDS)
            r = session.get(url, timeout=8, allow_redirects=False, stream=True, verify=True)
            content = b""
            try:
                for chunk in r.iter_content(64):
                    content += chunk
                    if len(content) >= 64:
                        break
            finally:
                r.close()
            ctype = (r.headers.get("content-type") or "").lower()
            head = content.decode("latin-1", errors="ignore")
            match = False
            if r.status_code == 200:
                if kind == "env":
                    match = "=" in head and "<html" not in head.lower() and "{" not in head[:1]
                elif kind == "git":
                    match = head.startswith("ref:") or "refs/" in head
                elif kind == "gitconfig":
                    match = "[core]" in head.lower()
                elif kind == "zip":
                    match = content.startswith(b"PK") or "zip" in ctype
                elif kind == "sql":
                    match = "sql" in ctype or "CREATE TABLE" in head.upper() or "INSERT INTO" in head.upper()
                elif kind == "phpinfo":
                    match = "php version" in head.lower()
                elif kind == "status":
                    match = "server status" in head.lower() or "apache" in head.lower()
                elif kind == "adminer":
                    match = "adminer" in head.lower()
                elif kind == "dsstore":
                    match = content.startswith(b"\x00\x00\x00\x01Bud1")
                elif kind == "composer":
                    match = head.lstrip().startswith("{") and "packages" in head.lower()
                elif kind == "log":
                    match = bool(re.search(r"(production|local)\.(ERROR|WARNING|INFO)", head))
                elif kind == "text":
                    match = False
                if match and not head.lstrip().startswith("<!doctype html") and not head.lstrip().startswith("<html"):
                    _add(
                        ctx, rule_id="web-exposed-file", title=label, severity=severity,
                        confidence="high", category="Fichiers exposés", url=url,
                        description="Une ressource sensible est accessible publiquement. Le contenu n'a pas été collecté ni enregistré.",
                        evidence=f"HTTP 200 — {url} — contenu non collecté (type {ctype or 'inconnu'})",
                        cwe="CWE-538", owasp="A05:2021",
                        remediation="Bloquer l'accès (règles serveur), déplacer hors racine web, révoquer les secrets éventuellement exposés et vérifier les journaux.",
                        references=["https://owasp.org/www-project-top-ten/2017/A6_2017-Security_Misconfiguration"],
                    )
                    probes.append({"path": path, "status": 200, "match": True})
                else:
                    probes.append({"path": path, "status": r.status_code, "match": False})
            else:
                probes.append({"path": path, "status": r.status_code, "match": False})
        except requests.RequestException:
            probes.append({"path": path, "status": None, "match": False})
    ctx.extra["exposed_probes"] = probes


def _fingerprint(assets: dict[str, Any], headers: dict[str, str], url: str) -> list[str]:
    tech: list[str] = []
    server = headers.get("server", "")
    powered = headers.get("x-powered-by", "")
    if server:
        tech.append(f"Serveur: {server}")
    if powered:
        tech.append(f"X-Powered-By: {powered}")
    if assets.get("generator"):
        tech.append(f"Generator: {assets['generator']}")
    html = " ".join([url] + [s["url"] for s in assets.get("scripts", [])])
    if re.search(r"/wp-(content|includes)/", html):
        tech.append("WordPress")
    if re.search(r"/media/jui/|/components/com_", html):
        tech.append("Joomla")
    if re.search(r"laravel_session|XSRF-TOKEN", html, re.I):
        tech.append("Laravel")
    if "__NEXT_DATA__" in html:
        tech.append("Next.js")
    if re.search(r"drupal", html, re.I):
        tech.append("Drupal")
    if "PHPSESSID" in html:
        tech.append("PHP")
    return sorted(set(tech))


def run_web_analysis(ctx: ScanContext) -> tuple[str, dict[str, Any], Any]:
    target = ctx.scan.get("target") or ctx.project.get("base_url") or ""
    session = _session(str(ctx.config.get("user_agent") or ""))
    active = active_checks.is_enabled()
    if active:
        # Mode actif : toute la liste des chemins sensibles est vérifiée.
        ctx.config["probe_exposed_files"] = True
        ctx.config["max_exposed_paths"] = len(SENSITIVE_PATHS)
    ctx.log("Récupération de la page cible", 8)
    result, chain, error = _follow(session, ctx, target)
    if error and (not result or result.get("status") is None):
        if error.startswith("TLS:"):
            _add(
                ctx, engine="web", rule_id="web-tls-invalid", title="Certificat TLS invalide ou connexion refusée",
                severity="critical", confidence="high", category="TLS", url=target,
                description="La connexion TLS n'a pas pu être validée. Les données peuvent être interceptées.",
                evidence=truncate(error, 500), cwe="CWE-295", owasp="A02:2021",
                remediation="Installer un certificat valide, vérifier la chaîne et le nom d'hôte, puis renouveler avant expiration.",
                references=["https://owasp.org/www-project-top-ten/2017/A3_2017-Sensitive_Data_Exposure"],
            )
        raise RuntimeError(f"Cible inaccessible : {error}")
    if not result:
        raise RuntimeError("Aucune réponse HTTP exploitable.")
    final_url = chain[-1]["url"] if chain else target
    ctx.extra["http"] = {
        "status": result["status"],
        "chain": chain,
        "headers": {k: v for k, v in result["headers"].items() if k in SECURITY_HEADERS or k in {"server", "x-powered-by", "content-type", "set-cookie"}},
        "elapsed_ms": result["elapsed_ms"],
    }
    ctx.log("Analyse des en-têtes et cookies", 22)
    _analyze_headers(ctx, final_url, result)
    parsed = urlparse(final_url)
    if parsed.scheme == "https":
        ctx.log("Inspection TLS", 28)
        tls = _tls_info(parsed.hostname or "", parsed.port or 443)
        ctx.extra["tls"] = tls
        if tls.get("checked"):
            if tls.get("version") in {"TLSv1", "TLSv1.1", "SSLv3", "SSLv2"}:
                _add(
                    ctx, rule_id="web-tls-version", title="Version TLS obsolète", severity="high",
                    confidence="high", category="TLS", url=final_url,
                    description="Le serveur négocie une version TLS obsolète.",
                    evidence=f"Version négociée : {tls.get('version')} — {tls.get('cipher','')}",
                    cwe="CWE-327", owasp="A02:2021",
                    remediation="Désactiver TLS 1.0/1.1 et SSLv3 ; imposer TLS 1.2+ (idéalement 1.3).",
                    references=["https://cheatsheetseries.owasp.org/cheatsheets/Transport_Layer_Security_Cheat_Sheet.html"],
                )
            days = tls.get("days_to_expiry")
            if isinstance(days, int) and days < 30:
                _add(
                    ctx, rule_id="web-tls-expiry", title="Certificat TLS proche de l'expiration",
                    severity="high" if days < 7 else "medium", confidence="high", category="TLS",
                    url=final_url, description="Le certificat expire bientôt et peut interrompre le service.",
                    evidence=f"Expiration : {tls.get('not_after')} ({days} jours)",
                    cwe="CWE-298", owasp="A02:2021",
                    remediation="Renouveler le certificat et automatiser le suivi de l'expiration.",
                    references=[],
                )
        elif tls.get("error"):
            _add(
                ctx, rule_id="web-tls-error", title="Inspection TLS impossible", severity="high",
                confidence="medium", category="TLS", url=final_url,
                description="La connexion TLS n'a pas pu être inspectée avec validation.",
                evidence=truncate(tls["error"], 400), cwe="CWE-295", owasp="A02:2021",
                remediation="Vérifier le certificat, la chaîne intermédiaire et la configuration TLS du serveur.",
                references=[],
            )
    ctx.log("Analyse du HTML, des formulaires et des scripts", 40)
    assets = parse_html_assets(final_url, result["text"])
    checkout = bool(CHECKOUT_HINTS.search(final_url) or assets["has_card_fields"])
    ctx.extra["html"] = {
        "title": assets["title"],
        "generator": assets["generator"],
        "lang": assets["lang"],
        "forms": len(assets["forms"]),
        "scripts": len(assets["scripts"]),
        "inline_scripts": len(assets["inline_scripts"]),
        "iframes": len(assets["iframes"]),
        "checkout_context": checkout,
    }
    ctx.extra["content"] = {
        "text_excerpt": assets.get("text_excerpt", ""),
        "markdown_excerpt": assets.get("markdown_excerpt", ""),
        "meta": assets.get("meta", {}),
        "json_ld": assets.get("json_ld", []),
        "api_candidates": assets.get("api_candidates", []),
        "headings": assets.get("headings", []),
        "internal_links": assets.get("internal_links", 0),
        "external_links": assets.get("external_links", 0),
        "word_count": assets.get("word_count", 0),
    }
    ctx.extra["scripts"] = assets["scripts"]
    ctx.extra["forms"] = [{
        "action": f["action"], "method": f["method"], "has_password": f["has_password"],
        "has_card_fields": f["has_card_fields"], "has_csrf_token": f["has_csrf_token"],
    } for f in assets["forms"]]
    ctx.extra["technology"] = _fingerprint(assets, result["headers"], final_url)
    _analyze_html(ctx, final_url, result["text"], assets, checkout)
    ctx.log("Lecture et analyse des scripts côté client", 52)
    for inline in (assets.get("inline_scripts") or [])[:20]:
        if ctx.cancelled():
            break
        _analyze_js_text(ctx, final_url, inline, "inline")
    fetched_scripts = 0
    for script in assets.get("scripts") or []:
        if ctx.cancelled() or fetched_scripts >= 6:
            break
        if not str(script.get("url", "")).lower().endswith((".js", ".mjs")):
            continue
        decision = check_web_scope(ctx.project, script["url"])
        if not decision.allowed:
            continue
        try:
            time.sleep(REQUEST_DELAY_SECONDS)
            js = _fetch(session, script["url"], max_bytes=200000)
            if js.get("status") == 200 and js.get("text"):
                fetched_scripts += 1
                _analyze_js_text(ctx, script["url"], js["text"], "externe")
        except requests.RequestException:
            continue
    if checkout:
        ctx.extra["checkout_detected"] = True
    ctx.log("Vérification des fichiers exposés", 65)
    _probe_paths(ctx, session, final_url)
    ctx.log("Recherche de security.txt", 72)
    for candidate in ("/.well-known/security.txt", "/security.txt"):
        if ctx.cancelled():
            break
        try:
            time.sleep(REQUEST_DELAY_SECONDS)
            candidate_url = urljoin(final_url, candidate)
            decision = check_web_scope(ctx.project, candidate_url)
            if not decision.allowed:
                continue
            sec = _fetch(session, candidate_url, max_bytes=20000)
            if sec.get("status") == 200 and sec.get("text"):
                text = sec["text"].strip()
                if "contact:" in text.lower() or "policy:" in text.lower() or len(text) < 4000:
                    ctx.extra["security_txt"] = {"url": candidate_url, "content": text[:4000]}
                    break
        except requests.RequestException:
            continue
    # Analyse des scripts same-origin pour le checkout.
    if checkout:
        ctx.log("Analyse des scripts du checkout", 78)
        base_host = (urlparse(final_url).hostname or "").lower()
        for script in assets["scripts"]:
            if ctx.cancelled():
                break
            if script["host"] != base_host or not script["url"].lower().endswith((".js", ".mjs")):
                continue
            decision = check_web_scope(ctx.project, script["url"])
            if not decision.allowed:
                continue
            try:
                time.sleep(REQUEST_DELAY_SECONDS)
                js = _fetch(session, script["url"], max_bytes=400_000)
                if js["status"] == 200:
                    _analyze_checkout_patterns(ctx, final_url, js["text"], [js["text"]], source="script")
            except requests.RequestException:
                continue
    if active and not ctx.cancelled():
        ctx.log("Contrôles actifs (méthodes, CORS, réflexion, redirections)", 82)
        active_checks.run(ctx, session, final_url, assets)
    ctx.log("Consolidation", 88)
    return final_url, result, session


def run(ctx: ScanContext) -> None:
    final_url, result, session = run_web_analysis(ctx)
    ctx.extra["final_url"] = final_url
    ctx.extra["scanned_at"] = now_iso()
    ctx.log("Analyse Web terminée", 96)
