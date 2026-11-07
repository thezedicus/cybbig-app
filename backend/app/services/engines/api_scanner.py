from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests
import yaml

from ...utils import now_iso, read_text, safe_relpath, truncate
from ..base import ScanContext
from .web_scanner import _fetch, _session

FINANCIAL = re.compile(r"(transfer|payment|paiement|refund|remboursement|order|commande|account|compte|beneficiar|transaction|wallet|payout|virement|invoice|facture)", re.I)
OBJECT_PARAM = re.compile(r"(^id$|account|order|user|customer|invoice|transaction|beneficiar|wallet|card|payment)", re.I)
MUTATING = {"post", "put", "patch", "delete"}


def _load_spec(ctx: ScanContext, target: str) -> tuple[dict, str]:
    if target.lower().startswith(("http://", "https://")):
        session = _session()
        ctx.log("Récupération de la spécification OpenAPI", 15)
        try:
            result = _fetch(session, target, max_bytes=3_000_000)
        except requests.RequestException as exc:
            raise RuntimeError(f"Spécification inaccessible : {exc}") from exc
        if result["status"] != 200:
            raise RuntimeError(f"La spécification a retourné HTTP {result['status']}.")
        text = result["text"]
        source = target
    else:
        root = Path(ctx.project.get("path") or "").resolve()
        candidate = Path(target)
        if not target:
            candidate = root / "openapi-demo.json"
            if not candidate.exists():
                for name in ("openapi.json", "swagger.json", "openapi.yaml", "swagger.yaml"):
                    if (root / name).exists():
                        candidate = root / name
                        break
        elif not candidate.is_absolute():
            candidate = root / candidate
        resolved = candidate.resolve()
        try:
            resolved.relative_to(root)
        except ValueError as exc:
            raise RuntimeError("La spécification doit rester dans le dossier du projet.") from exc
        if not resolved.exists():
            raise RuntimeError("Spécification OpenAPI introuvable. Indiquez une URL ou un fichier du projet.")
        text = read_text(resolved, 3_000_000)
        source = safe_relpath(resolved, root)
    try:
        spec = json.loads(text)
    except json.JSONDecodeError:
        try:
            spec = yaml.safe_load(text)
        except yaml.YAMLError as exc:
            raise RuntimeError("Le document n'est ni un JSON ni un YAML OpenAPI valide.") from exc
    if not isinstance(spec, dict):
        raise RuntimeError("Le document OpenAPI doit être un objet.")
    if not (spec.get("openapi") or spec.get("swagger")):
        raise RuntimeError("Le document ne contient pas de champ openapi/swagger.")
    return spec, source


def _resolve_ref(spec: dict, ref: str) -> dict:
    if not ref.startswith("#/"):
        return {}
    current: Any = spec
    for part in ref[2:].split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return {}
    return current if isinstance(current, dict) else {}


def _security_schemes(spec: dict) -> dict:
    components = spec.get("components", {}) or {}
    schemes = components.get("securitySchemes", {}) or {}
    if not schemes and isinstance(spec.get("securityDefinitions"), dict):
        schemes = spec["securityDefinitions"]
    return schemes if isinstance(schemes, dict) else {}


def run(ctx: ScanContext) -> None:
    target = (ctx.scan.get("target") or "").strip()
    spec, source = _load_spec(ctx, target)
    ctx.log("Analyse du contrat API", 35)
    info = spec.get("info", {}) or {}
    paths = spec.get("paths", {}) or {}
    schemes = _security_schemes(spec)
    global_security = spec.get("security")
    servers = spec.get("servers", []) or []
    if not servers and spec.get("host"):
        scheme = spec.get("schemes", ["https"])[0] if spec.get("schemes") else "https"
        servers = [{"url": f"{scheme}://{spec.get('host')}{spec.get('basePath','')}"}]
    operations: list[dict] = []
    for path, item in paths.items():
        if not isinstance(item, dict):
            continue
        for method, op in item.items():
            method_l = method.lower()
            if method_l not in {"get", "post", "put", "patch", "delete", "head", "options"} or not isinstance(op, dict):
                continue
            op_security = op.get("security", global_security)
            security_list = op_security if isinstance(op_security, list) else []
            auth_required = bool(security_list)
            # Une liste vide explicite signifie "pas d'authentification" ; l'absence hérite du global.
            if op.get("security") == []:
                auth_required = False
            params = (op.get("parameters") or []) + (item.get("parameters") or [])
            resolved_params = []
            for p in params:
                if isinstance(p, dict) and "$ref" in p:
                    p = _resolve_ref(spec, p["$ref"]) or p
                if isinstance(p, dict):
                    resolved_params.append(p)
            path_params = [p for p in resolved_params if p.get("in") == "path"]
            query_params = [p for p in resolved_params if p.get("in") == "query"]
            header_params = [p for p in resolved_params if p.get("in") == "header"]
            op_id = op.get("operationId") or f"{method_l}-{path}"
            operations.append({
                "method": method_l.upper(),
                "path": path,
                "operation_id": op_id,
                "summary": (op.get("summary") or "")[:300],
                "auth_required": auth_required,
                "financial": bool(FINANCIAL.search(path) or FINANCIAL.search(op.get("summary") or "")),
                "path_params": [p.get("name") for p in path_params],
                "query_params": [p.get("name") for p in query_params],
                "idempotency_header": any("idempot" in str(p.get("name", "")).lower() for p in header_params),
                "mutating": method_l in MUTATING,
            })

    financial_ops = [o for o in operations if o["financial"]]
    ctx.extra.update({
        "source": source,
        "title": info.get("title", ""),
        "version": info.get("version", ""),
        "spec_version": spec.get("openapi") or spec.get("swagger"),
        "servers": [s.get("url") for s in servers if isinstance(s, dict)][:20],
        "security_schemes": sorted(schemes.keys()),
        "global_security": bool(global_security),
        "operations": operations,
        "operation_count": len(operations),
        "financial_operations": len(financial_ops),
        "unauthenticated_operations": len([o for o in operations if not o["auth_required"]]),
        "scanned_at": now_iso(),
    })
    ctx.log(f"{len(operations)} opération(s), {len(financial_ops)} opération(s) financière(s)", 55)

    # Serveurs en HTTP.
    for server in servers:
        if not isinstance(server, dict):
            continue
        url = str(server.get("url") or "")
        if url.startswith("http://"):
            ctx.add_finding(
                engine="api", rule_id="api-server-http", title="Serveur API déclaré en HTTP",
                severity="medium", confidence="high", category="Transport API",
                description="La spécification déclare un serveur non chiffré. Les jetons et données pourraient transiter en clair.",
                evidence=f"servers: {truncate(url, 300)}", url=source,
                cwe="CWE-319", owasp="A02:2021",
                remediation="Déclarer uniquement des URL HTTPS et rediriger HTTP.",
                references=["https://owasp.org/API-Security/"],
            )
    if not schemes:
        ctx.add_finding(
            engine="api", rule_id="api-no-security-schemes", title="Aucun schéma d'authentification déclaré",
            severity="critical" if financial_ops else "high", confidence="high", category="Authentification API",
            description="Le contrat ne définit aucun mécanisme d'authentification (securitySchemes).",
            evidence=f"{len(operations)} opération(s) sans schéma d'authentification déclaré", url=source,
            cwe="CWE-306", owasp="API2:2023",
            remediation="Définir un schéma (OAuth2/OIDC, JWT signé) et l'appliquer globalement ou par opération.",
            references=["https://owasp.org/API-Security/editions/2023/en/0xa2-broken-authentication/"],
        )
    else:
        for name, scheme in schemes.items():
            if not isinstance(scheme, dict):
                continue
            stype = (scheme.get("type") or "").lower()
            if stype == "apikey" and (scheme.get("in") or "").lower() == "query":
                ctx.add_finding(
                    engine="api", rule_id="api-key-query", title=f"Clé API transmise en query string : {name}",
                    severity="medium", confidence="high", category="Authentification API",
                    description="Les clés en query string apparaissent dans les URL, proxys, historiques et journaux.",
                    evidence=f"securityScheme {name}: apiKey in query", url=source,
                    cwe="CWE-598", owasp="API2:2023",
                    remediation="Transmettre les jetons dans un en-tête Authorization et éviter les URL journalisées.",
                    references=["https://owasp.org/API-Security/"],
                )
            if stype == "http" and (scheme.get("scheme") or "").lower() == "basic":
                ctx.add_finding(
                    engine="api", rule_id="api-basic-auth", title=f"Authentification HTTP Basic : {name}",
                    severity="low", confidence="high", category="Authentification API",
                    description="HTTP Basic transmet des identifiants réutilisables ; elle doit être réservée à des contextes très contrôlés et toujours sous TLS.",
                    evidence=f"securityScheme {name}: http/basic", url=source,
                    cwe="CWE-522", owasp="API2:2023",
                    remediation="Préférer OAuth2/OIDC ou des jetons courts, avec MFA et rotation.",
                    references=["https://owasp.org/API-Security/"],
                )
    if operations and not global_security:
        ctx.add_finding(
            engine="api", rule_id="api-global-security", title="Sécurité globale absente du contrat",
            severity="high", confidence="medium", category="Authentification API",
            description="Aucune exigence de sécurité n'est déclarée au niveau global. Chaque opération devrait hériter d'une exigence explicite.",
            evidence=f"{len(operations)} opération(s) — security racine absent", url=source,
            cwe="CWE-306", owasp="API2:2023",
            remediation="Déclarer security au niveau racine et surcharger explicitement les endpoints publics.",
            references=["https://swagger.io/docs/specification/authentication/"],
        )
    no_auth = 0
    for op in operations:
        if op["auth_required"]:
            continue
        no_auth += 1
        if no_auth > 15:
            break
        sev = "critical" if op["financial"] and op["mutating"] else ("high" if op["mutating"] else "medium")
        ctx.add_finding(
            engine="api", rule_id="api-operation-no-auth", title=f"Opération sans authentification déclarée : {op['method']} {op['path']}",
            severity=sev, confidence="high" if schemes else "medium", category="Authentification API",
            description="L'opération n'exige aucun schéma de sécurité dans le contrat. Vérifier si un middleware non documenté la protège.",
            evidence=f"{op['method']} {op['path']} — security absent" + (" — endpoint financier" if op["financial"] else ""),
            url=source, cwe="CWE-306", owasp="API2:2023",
            remediation="Ajouter une exigence de sécurité, vérifier le refus anonyme et documenter les endpoints publics.",
            references=["https://owasp.org/API-Security/editions/2023/en/0xa2-broken-authentication/"],
        )
    # Revues BOLA (informatives, pas une preuve).
    bola_added = 0
    for op in operations:
        if not op["path_params"]:
            continue
        for param in op["path_params"]:
            if not param or not OBJECT_PARAM.search(param):
                continue
            if bola_added >= 10:
                break
            bola_added += 1
            ctx.add_finding(
                engine="api", rule_id="api-bola-review", title=f"Contrôle de propriété à vérifier : {op['method']} {op['path']}",
                severity="medium" if not op["auth_required"] else "info",
                confidence="low" if op["auth_required"] else "medium",
                category="Autorisation API",
                description=f"Le paramètre « {param} » identifie un objet. Vérifier côté serveur que l'utilisateur authentifié en est propriétaire. Ceci est une revue, pas une preuve de vulnérabilité.",
                evidence=f"{op['method']} {op['path']} — path param {param}",
                url=source, cwe="CWE-639", owasp="API1:2023",
                remediation="Comparer l'identité du token signé à l'identifiant du propriétaire de l'objet avant toute lecture ou modification.",
                references=["https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/"],
            )
    # Idempotence des opérations financières.
    for op in financial_ops:
        if op["method"] in {"POST", "PUT", "PATCH"} and not op["idempotency_header"]:
            ctx.add_finding(
                engine="api", rule_id="api-idempotency", title=f"Idempotence non déclarée : {op['method']} {op['path']}",
                severity="medium", confidence="medium", category="Logique financière",
                description="Aucun en-tête d'idempotence n'est déclaré sur une opération financière. Un rejeu peut créer un double débit.",
                evidence=f"{op['method']} {op['path']} — paramètre Idempotency-Key absent du contrat",
                url=source, cwe="CWE-837", owasp="API6:2023",
                remediation="Exiger une clé d'idempotence, une contrainte unique en base et des transitions d'état explicites.",
                references=["https://owasp.org/API-Security/editions/2023/en/0xa6-unrestricted-access-to-sensitive-business-flows/"],
            )
    version = str(ctx.extra.get("version") or "")
    if re.search(r"\d+\.\d+", version) and version not in {"", "1.0.0"}:
        ctx.add_finding(
            engine="api", rule_id="api-version-disclosure", title="Version d'API exposée dans le contrat",
            severity="info", confidence="high", category="Exposition d'information",
            description="La version est publique. Ce n'est pas une vulnérabilité en soi, mais elle aide le ciblage.",
            evidence=f"info.version = {version}", url=source,
            cwe="CWE-200", owasp="API8:2023",
            remediation="Documenter les versions supportées, déprécier proprement et ne pas exposer de détails internes.",
            references=["https://owasp.org/API-Security/"],
        )
    ctx.log("Consolidation de l'audit API", 95)
