from __future__ import annotations

import time
from pathlib import Path
from urllib.parse import urlparse

import requests

from ...config import REQUEST_DELAY_SECONDS
from ...utils import now_iso, read_text, safe_relpath, truncate
from ..base import ScanContext
from .web_scanner import (
    _analyze_checkout_patterns,
    _analyze_headers,
    _fetch,
    _follow,
    _session,
    parse_html_assets,
)


def _local_checkout_file(ctx: ScanContext, target: str) -> Path:
    root = Path(ctx.project.get("path") or "").resolve()
    if target and not target.lower().startswith(("http://", "https://")):
        candidate = Path(target)
        if not candidate.is_absolute():
            candidate = root / candidate
        resolved = candidate.resolve()
        try:
            resolved.relative_to(root)
        except ValueError as exc:
            raise RuntimeError("Le fichier checkout doit rester dans le dossier du projet.") from exc
        return resolved
    default = root / "checkout-demo.html"
    if default.exists():
        return default
    for candidate in sorted(root.rglob("*.html")):
        lower = candidate.name.lower()
        if "checkout" in lower or "payment" in lower or "panier" in lower:
            return candidate
    raise RuntimeError("Aucun fichier HTML de checkout trouvé. Indiquez une URL ou un fichier du projet.")


def _analyze_local(ctx: ScanContext, path: Path) -> None:
    root = Path(ctx.project.get("path") or "").resolve()
    rel = safe_relpath(path, root)
    html = read_text(path, 2_000_000)
    base = ctx.project.get("base_url") or "http://local.invalid/"
    assets = parse_html_assets(base, html)
    ctx.extra.update({
        "mode": "offline",
        "file": rel,
        "title": assets["title"],
        "scripts": assets["scripts"],
        "forms": [{
            "action": f["action"], "method": f["method"], "has_card_fields": f["has_card_fields"],
            "has_csrf_token": f["has_csrf_token"],
        } for f in assets["forms"]],
        "has_card_fields": assets["has_card_fields"],
        "checkout_context": True,
        "scanned_at": now_iso(),
    })
    _analyze_checkout_patterns(ctx, f"file:///{rel}", html, assets["inline_scripts"], source="page")
    if assets["svg_onload"]:
        ctx.add_finding(
            engine="checkout", rule_id="checkout-svg-onload-file",
            title="SVG inline avec onload dans le fichier checkout",
            severity="high", confidence="high", category="Intégrité checkout",
            description="Un SVG inline utilise onload. Ce motif est associé à des skimmers de checkout.",
            evidence=f"{rel} — gestionnaire onload détecté, contenu non exécuté",
            file_path=rel, cwe="CWE-829", owasp="A08:2021",
            remediation="Retirer le SVG, vérifier son origine et restaurer la version autorisée de la page.",
            references=["https://www.pcisecuritystandards.org/"],
        )
    # Scripts locaux référencés.
    for script in assets["scripts"][:10]:
        src = script["url"]
        if not src.lower().split("?")[0].endswith((".js", ".mjs")):
            continue
        candidate = (path.parent / src.lstrip("/")).resolve()
        try:
            candidate.relative_to(root)
        except ValueError:
            continue
        if candidate.exists() and candidate.is_file():
            js = read_text(candidate, 400_000)
            _analyze_checkout_patterns(ctx, f"file:///{safe_relpath(candidate, root)}", "", [js], source="script")
    # Formulaire carte pointant vers un domaine externe.
    base_host = (urlparse(base).hostname or "").lower()
    for form in assets["forms"]:
        action_host = (urlparse(form["action"]).hostname or "").lower()
        if form["has_card_fields"] and action_host and action_host != base_host:
            ctx.add_finding(
                engine="checkout", rule_id="checkout-external-form-file",
                title="Formulaire de carte vers un domaine externe",
                severity="high", confidence="medium", category="Intégrité checkout",
                description="Le formulaire contient des champs de carte et pointe vers un domaine différent du site.",
                evidence=f"{rel} — action {truncate(form['action'], 300)}",
                file_path=rel, cwe="CWE-829", owasp="A08:2021",
                remediation="Vérifier le PSP, privilégier une iframe/tokenisation et documenter le domaine autorisé.",
                references=["https://www.pcisecuritystandards.org/"],
            )
    if not assets["has_card_fields"]:
        ctx.add_finding(
            engine="checkout", rule_id="checkout-no-card-fields",
            title="Aucun champ carte détecté dans le fichier",
            severity="info", confidence="medium", category="Intégrité checkout",
            description="Le fichier analysé ne contient pas de champ de carte visible. Il peut s'agir d'une iframe ou d'un formulaire tokenisé.",
            evidence=rel, file_path=rel, remediation="Vérifier manuellement le parcours de paiement et l'iframe du PSP.",
        )


def run(ctx: ScanContext) -> None:
    target = (ctx.scan.get("target") or "").strip()
    if target.lower().startswith(("http://", "https://")):
        session = _session()
        ctx.log("Récupération de la page de paiement", 10)
        result, chain, error = _follow(session, ctx, target)
        if error or not result:
            raise RuntimeError(f"Checkout inaccessible : {error}")
        final_url = chain[-1]["url"] if chain else target
        _analyze_headers(ctx, final_url, result)
        assets = parse_html_assets(final_url, result["text"])
        ctx.log("Inventaire des scripts et des formulaires", 40)
        ctx.extra.update({
            "mode": "online",
            "final_url": final_url,
            "status": result["status"],
            "title": assets["title"],
            "scripts": assets["scripts"],
            "forms": [{
                "action": f["action"], "method": f["method"], "has_card_fields": f["has_card_fields"],
                "has_csrf_token": f["has_csrf_token"], "has_password": f["has_password"],
            } for f in assets["forms"]],
            "iframes": assets["iframes"],
            "has_card_fields": assets["has_card_fields"],
            "checkout_context": True,
            "http_chain": chain,
            "scanned_at": now_iso(),
        })
        _analyze_checkout_patterns(ctx, final_url, result["text"], assets["inline_scripts"], source="page")
        base_host = (urlparse(final_url).hostname or "").lower()
        for script in assets["scripts"][:8]:
            if ctx.cancelled():
                break
            if script["host"] != base_host or not script["url"].lower().split("?")[0].endswith((".js", ".mjs")):
                continue
            try:
                time.sleep(REQUEST_DELAY_SECONDS)
                js = _fetch(session, script["url"], max_bytes=400_000)
                if js["status"] == 200:
                    _analyze_checkout_patterns(ctx, final_url, "", [js["text"]], source="script")
            except requests.RequestException:
                continue
        # Les scripts tiers sont inventoriés mais ne sont pas récupérés.
        third_party = [s for s in assets["scripts"] if s["host"] and s["host"] != base_host]
        ctx.extra["third_party_scripts"] = [
            {"host": s["host"], "url": truncate(s["url"], 500), "integrity": s["integrity"]}
            for s in third_party
        ]
        for s in third_party:
            if not s["integrity"]:
                ctx.add_finding(
                    engine="checkout", rule_id="checkout-thirdparty-no-sri",
                    title=f"Script tiers sans SRI : {s['host']}",
                    severity="medium", confidence="medium", category="Intégrité checkout",
                    description="Un script tiers est chargé sur le checkout sans intégrité vérifiable.",
                    evidence=f"{s['host']} — {truncate(s['url'], 300)}",
                    url=final_url, cwe="CWE-829", owasp="A08:2021",
                    remediation="Épingler la version, utiliser SRI/crossorigin et tenir un registre des scripts autorisés (PCI DSS 6.4.3).",
                    references=["https://www.pcisecuritystandards.org/"],
                )
    else:
        ctx.log("Lecture du fichier checkout local", 20)
        path = _local_checkout_file(ctx, target)
        _analyze_local(ctx, path)
    ctx.log("Analyse d'intégrité checkout terminée", 95)
