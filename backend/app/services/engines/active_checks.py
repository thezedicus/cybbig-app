"""Contrôles Web actifs, non destructifs, activables par le propriétaire (réglage active_mode).

Chaque requête reste dans le périmètre autorisé du projet (check_web_scope), est espacée et plafonnée.
Les valeurs envoyées sont des marqueurs inoffensifs : aucune charge d'exploitation, aucun contournement
d'authentification, aucune écriture (seules des requêtes GET/OPTIONS/TRACE sont émises).
"""
from __future__ import annotations

import secrets
import time
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

import requests

from ... import db
from ...config import REQUEST_DELAY_SECONDS
from ..base import ScanContext
from ..scope import check_web_scope

MAX_ACTIVE_REQUESTS = 40
MAX_TARGETS = 6
MAX_PARAMS_PER_TARGET = 4
REDIRECT_PARAM_NAMES = {"redirect", "redirect_uri", "redirect_url", "url", "next", "return", "return_url", "returnto", "goto", "dest", "destination", "continue", "target"}
CORS_PROBE_ORIGIN = "https://cybbig-cors-check.invalid"
REDIRECT_PROBE = "https://cybbig-redirect-check.invalid/"


def is_enabled() -> bool:
    return str(db.get_setting("active_mode", "false")).lower() in {"1", "true", "yes", "on"}


class _Budget:
    def __init__(self, ctx: ScanContext, session: requests.Session):
        self.ctx, self.session, self.used = ctx, session, 0

    def request(self, method: str, url: str, **kwargs: Any) -> requests.Response | None:
        if self.used >= MAX_ACTIVE_REQUESTS or self.ctx.cancelled():
            return None
        if not check_web_scope(self.ctx.project, url).allowed:
            return None
        self.used += 1
        time.sleep(REQUEST_DELAY_SECONDS)
        try:
            response = self.session.request(method, url, timeout=10, allow_redirects=False, stream=True, **kwargs)
            try:
                response._content = response.raw.read(200_000, decode_content=True)  # lecture bornée
            finally:
                response.close()
            return response
        except requests.RequestException:
            return None


def _add(ctx: ScanContext, **kwargs: Any) -> None:
    kwargs.setdefault("engine", "web")
    kwargs.setdefault("references", [])
    ctx.add_finding(**kwargs)


def _with_param(url: str, name: str, value: str) -> str:
    parts = urlparse(url)
    query = [(k, value if k == name else v) for k, v in parse_qsl(parts.query, keep_blank_values=True)]
    if name not in {k for k, _ in query}:
        query.append((name, value))
    return urlunparse(parts._replace(query=urlencode(query)))


def _targets(base_url: str, assets: dict[str, Any]) -> list[tuple[str, list[str]]]:
    """URL GET (liens à paramètres et formulaires GET) du même hôte, avec leurs noms de paramètres."""
    host = (urlparse(base_url).hostname or "").lower()
    out: dict[str, list[str]] = {}
    for link in assets.get("links") or []:
        parts = urlparse(link)
        if (parts.hostname or "").lower() != host or not parts.query:
            continue
        key = urlunparse(parts._replace(query="", fragment=""))
        names = [k for k, _ in parse_qsl(parts.query, keep_blank_values=True)]
        out.setdefault(key, [])
        out[key] = list(dict.fromkeys(out[key] + names))
    for form in assets.get("forms") or []:
        if form.get("method") != "GET" or (urlparse(form["action"]).hostname or "").lower() != host:
            continue
        names = [f["name"] for f in form.get("fields") or [] if f.get("name") and f.get("type") not in {"password", "hidden", "submit", "file"}]
        if names:
            out.setdefault(form["action"], [])
            out[form["action"]] = list(dict.fromkeys(out[form["action"]] + names))
    return [(url, names[:MAX_PARAMS_PER_TARGET]) for url, names in list(out.items())[:MAX_TARGETS]]


def _check_methods(ctx: ScanContext, budget: _Budget, url: str) -> None:
    response = budget.request("OPTIONS", url)
    if response is not None:
        allowed = {m.strip().upper() for m in (response.headers.get("allow") or "").split(",") if m.strip()}
        risky = sorted(allowed & {"PUT", "DELETE", "PATCH", "TRACE", "CONNECT"})
        if risky:
            _add(ctx, rule_id="web-active-methods", title="Méthodes HTTP sensibles annoncées", severity="low",
                 confidence="medium", category="Configuration HTTP", url=url,
                 description="Le serveur annonce des méthodes HTTP rarement nécessaires sur une page publique.",
                 evidence=f"OPTIONS {url} → Allow: {', '.join(sorted(allowed))}", cwe="CWE-650", owasp="A05:2021",
                 remediation="Limiter les méthodes acceptées (GET, POST, HEAD) au niveau du serveur ou du proxy.")
    marker = f"cybbig-trace-{secrets.token_hex(4)}"
    response = budget.request("TRACE", url, headers={"X-Cybbig-Trace": marker})
    if response is not None and response.status_code == 200 and marker in response.text:
        _add(ctx, rule_id="web-active-trace", title="Méthode TRACE activée", severity="medium", confidence="high",
             category="Configuration HTTP", url=url,
             description="La requête TRACE est renvoyée telle quelle, ce qui peut exposer des en-têtes (Cross-Site Tracing).",
             evidence=f"TRACE {url} → HTTP 200, en-tête témoin renvoyé", cwe="CWE-693", owasp="A05:2021",
             remediation="Désactiver TRACE (Apache : TraceEnable off ; Nginx : refuser la méthode).")


def _check_cors(ctx: ScanContext, budget: _Budget, url: str) -> None:
    response = budget.request("GET", url, headers={"Origin": CORS_PROBE_ORIGIN})
    if response is None:
        return
    acao = response.headers.get("access-control-allow-origin", "")
    credentials = response.headers.get("access-control-allow-credentials", "").lower() == "true"
    if acao == CORS_PROBE_ORIGIN or (acao == "null" and credentials):
        _add(ctx, rule_id="web-active-cors", title="CORS : origine arbitraire acceptée",
             severity="high" if credentials else "medium", confidence="high", category="CORS", url=url,
             description="Le serveur renvoie l'origine fournie par le client dans Access-Control-Allow-Origin"
                         + (" avec les identifiants autorisés : un site tiers peut lire des réponses authentifiées." if credentials else "."),
             evidence=f"Origin: {CORS_PROBE_ORIGIN} → ACAO: {acao} · credentials: {credentials}", cwe="CWE-942", owasp="A05:2021",
             remediation="N'autoriser qu'une liste fixe d'origines de confiance ; ne jamais refléter l'en-tête Origin.")


def _check_reflection(ctx: ScanContext, budget: _Budget, url: str, names: list[str]) -> None:
    for name in names:
        token = secrets.token_hex(4)
        # Marqueur inoffensif : des caractères spéciaux HTML entourant un jeton, sans script.
        canary = f"cyb{token}<\"'>"
        response = budget.request("GET", _with_param(url, name, canary))
        if response is None:
            return
        body = response.text
        ctype = (response.headers.get("content-type") or "").lower()
        if canary in body and "html" in ctype:
            _add(ctx, rule_id="web-active-reflection", title="Paramètre reflété sans encodage (XSS potentiel)",
                 severity="medium", confidence="medium", category="XSS", url=url,
                 description=f"La valeur du paramètre « {name} » est renvoyée dans la page HTML sans encodage des caractères < \" ' >.",
                 evidence=f"GET {url} ?{name}=<marqueur> → marqueur renvoyé brut (HTTP {response.status_code})",
                 cwe="CWE-79", owasp="A03:2021",
                 remediation="Encoder toute donnée renvoyée selon son contexte (htmlspecialchars en PHP) et ajouter une CSP stricte.")
            return
        if name.lower() in REDIRECT_PARAM_NAMES:
            response = budget.request("GET", _with_param(url, name, REDIRECT_PROBE))
            location = response.headers.get("location", "") if response is not None else ""
            if location.startswith(REDIRECT_PROBE.rstrip("/")):
                _add(ctx, rule_id="web-active-open-redirect", title="Redirection ouverte", severity="medium",
                     confidence="high", category="Redirection", url=url,
                     description=f"Le paramètre « {name} » redirige vers n'importe quel domaine externe (hameçonnage facilité).",
                     evidence=f"GET {url} ?{name}={REDIRECT_PROBE} → Location: {location}", cwe="CWE-601", owasp="A01:2021",
                     remediation="N'accepter que des chemins relatifs ou une liste blanche de destinations.")


def run(ctx: ScanContext, session: requests.Session, base_url: str, assets: dict[str, Any]) -> None:
    db.execute("UPDATE scans SET mode='active' WHERE id=?", (ctx.scan_id,))
    budget = _Budget(ctx, session)
    _check_methods(ctx, budget, base_url)
    _check_cors(ctx, budget, base_url)
    targets = _targets(base_url, assets)
    for url, names in targets:
        if ctx.cancelled():
            break
        _check_reflection(ctx, budget, url, names)
    ctx.extra["active_checks"] = {"requests": budget.used, "targets": len(targets)}
