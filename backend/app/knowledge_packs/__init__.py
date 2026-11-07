"""Paquets de connaissances livrés avec Cybbig, installés dans la base au démarrage.

Chaque paquet a une version (réglage ``kb_pack_<id>``). Un paquet n'est réinstallé que si sa version change, et
une fiche que l'utilisateur a modifiée (``updated_at`` différent de ``created_at``) n'est jamais écrasée.
"""
from __future__ import annotations

import re
import unicodedata
from types import ModuleType
from typing import Any

from .. import db
from ..utils import now_iso
from . import cyber_defense_fr, cyber_world, complementary_volumes, cybbig_execution, cybbig_ops, income_autonomy, language_security, network_privacy, security_sources, software_engineering, user_libraries_6_7_8

PACKS: tuple[ModuleType, ...] = (cyber_defense_fr, cyber_world, software_engineering, cybbig_ops, cybbig_execution, network_privacy, security_sources, language_security, user_libraries_6_7_8, complementary_volumes, income_autonomy)
LEVELS = {"beginner": "débutant", "intermediate": "intermédiaire", "advanced": "avancé"}
RISKS = {"informational": "informatif", "low": "faible", "medium": "moyen", "high": "élevé", "critical": "critique"}


def _slug(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "divers"


def _doc(pack: str, slug: str, title: str, category: str, content: str, tags: list[str], source: str) -> dict[str, Any]:
    return {"id": f"kb-{pack}-{slug}", "title": title, "category": category, "content": content.strip(),
            "source": source, "tags": ",".join(dict.fromkeys([*tags, f"pack-{pack}"]))}


def _articles(module: ModuleType) -> list[dict[str, Any]]:
    refs = getattr(module, "REFERENCES", {})
    out = []
    for slug, title, cat, summary, content, level, risk, tech in module.ARTICLES:
        body = f"{summary}\n\n{content}\n\nNiveau : {LEVELS.get(level, level)} · Gravité : {RISKS.get(risk, risk)}"
        if tech:
            body += f"\nTechnologies : {', '.join(tech)}"
        links = refs.get(slug, [])
        if links:
            body += "\n\nRéférences :\n" + "\n".join(f"- {label} : {url}" for label, url in links)
        out.append(_doc(module.PACK_ID, slug, title, module.CATEGORIES[cat], body, tech,
                        links[0][1] if links else "Paquet Cybbig"))
    return out


def _world_extras(module: ModuleType) -> list[dict[str, Any]]:
    out = []
    for slug, title, date, publisher, products, summary, actions, url, note in module.INCIDENTS:
        body = (f"{summary}\n\nSTATUT : À VÉRIFIER — synthèse importée telle quelle, non confirmée par Cybbig "
                f"(identifiants CVE, dates et chiffres à contrôler à la source avant toute décision).\n\n"
                f"Date : {date} · Publié par : {publisher}\nProduits concernés : {products}\n"
                f"Actions défensives : {actions}\nNote de confiance : {note}\nSource à consulter : {url}")
        out.append(_doc(module.PACK_ID, f"inc-{slug}", f"Incident — {title}", module.CATEGORIES["incidents"], body,
                        ["incident", "2026", "à-vérifier"], url))
    for slug, name, url, desc, topics, notes in module.REPOS:
        body = f"{name} — {desc}\n\nDépôt : {url}\nSujets : {topics.replace(';', ', ')}\nPrécautions d'usage : {notes}"
        out.append(_doc(module.PACK_ID, f"repo-{slug}", f"Outil — {name}", module.CATEGORIES["ressources"], body,
                        ["outil", "open-source", *topics.split(";")], url))
    by_type: dict[str, list[tuple[str, str, str]]] = {}
    for name, desc, url, kind in module.SOURCES:
        by_type.setdefault(kind, []).append((name, desc, url))
    for kind, items in by_type.items():
        body = "\n".join(f"- {name} : {desc} — {url}" for name, desc, url in items)
        out.append(_doc(module.PACK_ID, f"src-{_slug(kind)}", f"Sources de veille — {kind}", module.CATEGORIES["sources"],
                        f"Sources à consulter régulièrement ({kind}).\n\n{body}", ["veille", "sources", _slug(kind)], items[0][2]))
    out.append(_doc(module.PACK_ID, "regles-ingestion", "Règles de qualité pour alimenter la base de connaissances",
                    module.CATEGORIES["sources"], module.INGESTION_RULES, ["qualité", "ingestion", "provenance"], "Paquet Cybbig"))
    return out


def _simple(module: ModuleType) -> list[dict[str, Any]]:
    return [_doc(module.PACK_ID, slug, title, f"{module.PREFIX} · {cat}", content, [t.strip() for t in tags.split(",")], "Paquet Cybbig")
            for slug, title, cat, content, tags in module.DOCS]


def build(module: ModuleType) -> list[dict[str, Any]]:
    if hasattr(module, "ARTICLES"):
        docs = _articles(module)
        if hasattr(module, "INCIDENTS"):
            docs += _world_extras(module)
        return docs
    return _simple(module)


def all_docs() -> list[dict[str, Any]]:
    return [doc for module in PACKS for doc in build(module)]


def install() -> dict[str, dict[str, int]]:
    """Installe ou met à jour les paquets dont la version a changé. Renvoie {paquet: {added, updated}}."""
    report: dict[str, dict[str, int]] = {}
    for module in PACKS:
        key = f"kb_pack_{module.PACK_ID}"
        if db.get_setting(key) == module.VERSION:
            continue
        added = updated = 0
        now = now_iso()
        with db.db_cursor() as conn:
            for doc in build(module):
                row = conn.execute("SELECT created_at, updated_at FROM knowledge_docs WHERE id=?", (doc["id"],)).fetchone()
                if row is None:
                    conn.execute("INSERT INTO knowledge_docs(id,title,category,content,source,tags,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?)",
                                 (doc["id"], doc["title"], doc["category"], doc["content"], doc["source"], doc["tags"], now, now))
                    added += 1
                elif row["created_at"] == row["updated_at"]:  # jamais modifiée par l'utilisateur
                    conn.execute("UPDATE knowledge_docs SET title=?, category=?, content=?, source=?, tags=?, updated_at=created_at WHERE id=?",
                                 (doc["title"], doc["category"], doc["content"], doc["source"], doc["tags"], doc["id"]))
                    updated += 1
        db.set_setting(key, module.VERSION)
        db.audit("knowledge_pack_installed", {"pack": module.PACK_ID, "version": module.VERSION, "added": added, "updated": updated})
        report[module.PACK_ID] = {"added": added, "updated": updated}
    return report
