from __future__ import annotations

import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from typing import Any

from .. import db
from ..utils import new_id, now_iso
from . import admin, ai_tasks, ai_worker, income_sources, intel, jobs, reports, websearch

_stop = threading.Event()
_thread: threading.Thread | None = None
_running: set[str] = set()
_queued: set[str] = set()
_lock = threading.Lock()
_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="cybbig-automation")


KINDS = {"intel_sync", "web_watch", "income_watch", "php", "web", "api", "checkout", "reverse", "project_suite", "improvement_review", "backup", "report"}
GLOBAL_KINDS = {"intel_sync", "web_watch", "income_watch", "improvement_review", "backup"}
INCOME_METHODS = {"freelance", "remote_contracts", "bug_bounty", "grants"}
INCOME_SEARCHES = {
    "freelance": ("Missions freelance rémunérées {skills} {location}", ["malt.fr", "codeur.com", "upwork.com", "freelancer.com", "comeup.com", "fiverr.com", "peopleperhour.com", "free-work.com"]),
    "remote_contracts": ("Offres de missions ou contrats rémunérés {skills} télétravail {location}", ["hellowork.com", "welcometothejungle.com", "indeed.com", "free-work.com", "weworkremotely.com", "remoteok.com", "remotive.com", "remote.co"]),
    "bug_bounty": ("Programmes officiels bug bounty avec récompenses {skills}", ["yeswehack.com", "hackerone.com", "bugcrowd.com", "intigriti.com"]),
    "grants": ("Appels à projets aides et subventions innovation numérique {skills} {location}", ["les-aides.fr", "bpifrance-creation.fr", "europe-en-france.gouv.fr", "service-public.fr"]),
}


def _interval(value: Any, minimum: int = 5) -> int:
    minutes = int(value or 1440)
    if minutes < minimum or minutes > 525600:
        raise ValueError(f"L’intervalle doit être compris entre {minimum} minutes et un an.")
    return minutes


def _parse(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _next(interval_minutes: int) -> str:
    return (datetime.now(timezone.utc) + timedelta(minutes=max(1, int(interval_minutes)))).isoformat(timespec="seconds")


def list_automations() -> list[dict[str, Any]]:
    rows = db.fetch_all(
        "SELECT a.*, p.name AS project_name FROM automations a "
        "LEFT JOIN projects p ON p.id=a.project_id ORDER BY a.created_at DESC"
    )
    for row in rows:
        row["config"] = db.json_loads(row.get("config_json"), {})
        row["enabled"] = bool(row.get("enabled"))
        row["runs"] = db.fetch_all(
            "SELECT id,started_at,finished_at,status,log FROM automation_runs WHERE automation_id=? ORDER BY started_at DESC LIMIT 5",
            (row["id"],),
        )
    return rows


def create_automation(payload: dict[str, Any]) -> dict[str, Any]:
    kind = payload.get("kind")
    if kind not in KINDS:
        raise ValueError("Type d'automatisation invalide.")
    project_id = payload.get("project_id") or None
    if kind not in GLOBAL_KINDS and not project_id:
        raise ValueError("Un projet est requis pour une analyse planifiée.")
    if project_id and not db.fetch_one("SELECT id FROM projects WHERE id=?", (project_id,)):
        raise ValueError("Projet introuvable.")
    config = payload.get("config") or {}
    if kind == "web_watch":
        query = str(config.get("query", "")).strip()
        if len(query) < 2 or len(query) > 400:
            raise ValueError("Une requête de veille d'au moins deux caractères est requise.")
        domains = config.get("domains") or []
        if not isinstance(domains, list) or any(not isinstance(domain, str) for domain in domains):
            raise ValueError("La liste des domaines de veille est invalide.")
        if len(domains) > 8:
            raise ValueError("Limitez la veille à huit domaines.")
        config = {**config, "query": query, "domains": domains,
                  "limit": min(20, max(5, int(config.get("limit", 10)))),
                  "lang": config.get("lang") if config.get("lang") in {"fr", "en"} else "fr",
                  "provider": config.get("provider") if config.get("provider") in {"auto", "brave", "ddg"} else "auto"}
    if kind == "project_suite":
        selected = config.get("scans") or ["php", "web", "api", "checkout"]
        if not isinstance(selected, list) or not selected or any(item not in {"php", "web", "api", "checkout"} for item in selected):
            raise ValueError("Sélection d’analyses combinées invalide.")
        config = {"scans": list(dict.fromkeys(selected))}
    if kind == "income_watch":
        methods = config.get("methods") or ["freelance", "remote_contracts", "bug_bounty", "grants"]
        if not isinstance(methods, list) or not methods or any(method not in INCOME_METHODS for method in methods):
            raise ValueError("Sélectionnez au moins une méthode de recherche parmi les options proposées.")
        location = str(config.get("location") or "France").strip()[:100]
        skills = str(config.get("skills") or "développement web, Python, cybersécurité").strip()[:180]
        config = {"methods": list(dict.fromkeys(methods)), "location": location or "France", "skills": skills or "développement informatique", "limit": min(10, max(3, int(config.get("limit", 5))))}
    interval = _interval(payload.get("interval_minutes"), 2 if kind == "income_watch" else 5)
    now = datetime.now(timezone.utc)
    automation_id = new_id("auto")
    db.execute(
        """INSERT INTO automations(id,project_id,name,kind,interval_minutes,config_json,enabled,
           next_run_at,last_status,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
        (
            automation_id, project_id, (payload.get("name") or "Automatisation")[:200], kind,
            interval, json.dumps(config, ensure_ascii=False),
            1 if payload.get("enabled", True) else 0,
            (now + timedelta(minutes=interval)).isoformat(timespec="seconds"),
            "never", now.isoformat(timespec="seconds"), now.isoformat(timespec="seconds"),
        ),
    )
    db.audit("automation_created", {"id": automation_id, "kind": kind})
    return db.fetch_one("SELECT * FROM automations WHERE id=?", (automation_id,)) or {}


def update_automation(automation_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    row = db.fetch_one("SELECT * FROM automations WHERE id=?", (automation_id,))
    if not row:
        raise ValueError("Automatisation introuvable.")
    fields = []
    params: list[Any] = []
    for key in ("name", "interval_minutes", "enabled"):
        if key in payload:
            value = payload[key]
            if key == "enabled":
                value = 1 if value else 0
            if key == "interval_minutes":
                value = _interval(value, 2 if row["kind"] == "income_watch" else 5)
            fields.append(f"{key}=?")
            params.append(value)
    if "config" in payload:
        fields.append("config_json=?")
        params.append(json.dumps(payload["config"] or {}, ensure_ascii=False))
    if "enabled" in payload and payload["enabled"]:
        fields.append("next_run_at=?")
        params.append(_next(int(payload.get("interval_minutes", row["interval_minutes"]))))
    if not fields:
        return row
    fields.append("updated_at=?")
    params.append(now_iso())
    params.append(automation_id)
    db.execute(f"UPDATE automations SET {', '.join(fields)} WHERE id=?", params)
    return db.fetch_one("SELECT * FROM automations WHERE id=?", (automation_id,)) or {}


def delete_automation(automation_id: str) -> None:
    db.execute("DELETE FROM automations WHERE id=?", (automation_id,))
    db.audit("automation_deleted", {"id": automation_id})


def _project_target(project: dict[str, Any], kind: str, config: dict[str, Any]) -> str:
    if config.get("target"):
        return str(config["target"])
    if kind == "php":
        return project.get("path") or ""
    if kind == "checkout":
        return project.get("base_url") or ""
    if kind == "reverse":
        return str(config.get("target") or "")
    if kind == "api":
        base = (project.get("base_url") or "").rstrip("/")
        return base + "/openapi.json" if base else ""
    return project.get("base_url") or ""


def run_now(automation_id: str, manual: bool = True) -> dict[str, Any]:
    row = db.fetch_one("SELECT * FROM automations WHERE id=?", (automation_id,))
    if not row:
        raise ValueError("Automatisation introuvable.")
    with _lock:
        if automation_id in _running:
            raise ValueError("Cette automatisation est déjà en cours.")
        _running.add(automation_id)
    run_id = new_id("run")
    db.execute(
        "INSERT INTO automation_runs(id,automation_id,started_at,status,log) VALUES(?,?,?,?,?)",
        (run_id, automation_id, now_iso(), "running", "Démarrage\n"),
    )
    try:
        config = db.json_loads(row.get("config_json"), {})
        kind = row["kind"]
        log = ""
        if kind == "intel_sync":
            sources = config.get("sources") or None
            result = intel.sync_all(sources)
            log = json.dumps(result, ensure_ascii=False, indent=2)[:8000]
            status = "completed"
        elif kind == "web_watch":
            result = websearch.search(str(config.get("query", "")), limit=config.get("limit", 10), lang=config.get("lang", "fr"), provider=config.get("provider", "auto"), domains=config.get("domains") or None)
            log = f"Veille web : {result['total']} résultat(s)\n" + "\n".join(
                f"- {item.get('title', '')} — {item.get('url', '')}" for item in result.get("items", [])
            )
            if result.get("warnings"):
                log += "\nAvertissements : " + ", ".join(dict.fromkeys(result["warnings"]))
            status = "completed"
        elif kind == "income_watch":
            methods = config.get("methods") or ["freelance", "remote_contracts", "bug_bounty", "grants"]
            location = str(config.get("location") or "France")[:100]
            skills = str(config.get("skills") or "développement informatique")[:180]
            limit = min(10, max(3, int(config.get("limit", 5))))

            def find_method(method: str) -> tuple[str, dict[str, Any] | None, str]:
                template, domains = INCOME_SEARCHES[method]
                query = template.format(skills=skills, location=location)
                direct_rows: list[dict[str, str]] = []
                notices: list[str] = []
                if method == "remote_contracts":
                    direct_rows, notices = income_sources.search_remote_roles(skills, location, limit)
                elif method == "grants":
                    direct_rows, notices = income_sources.search_funding_calls(skills, location, limit)
                if len(direct_rows) >= limit:
                    return method, {"items": direct_rows[:limit], "warnings": notices}, ""
                search_result: dict[str, Any] = {"items": [], "warnings": []}
                search_error = ""
                try:
                    web_rows, web_warnings = income_sources.search_web_opportunities(method, query, domains, limit)
                    search_result = {"items": web_rows, "warnings": web_warnings}
                except Exception as exc:  # noqa: BLE001
                    search_error = f"{type(exc).__name__}: {exc}"
                if direct_rows:
                    known = {item.get("url") for item in direct_rows}
                    direct_rows.extend(item for item in search_result.get("items", []) if item.get("url") not in known)
                    search_result = {**search_result, "items": direct_rows[:limit],
                                     "warnings": list(search_result.get("warnings", [])) + notices}
                if not search_result.get("items") and search_error:
                    return method, search_result, search_error
                return method, search_result, ""

            found: list[tuple[str, dict[str, Any] | None, str]] = []
            with ThreadPoolExecutor(max_workers=min(4, len(methods)), thread_name_prefix="cybbig-income-search") as pool:
                futures = [pool.submit(find_method, method) for method in methods]
                for future in as_completed(futures):
                    found.append(future.result())
            lines = ["Radar d’opportunités rémunérées — résultats publics à vérifier manuellement.",
                     f"Profil de recherche : {skills} · zone : {location}",
                     "Les annonces, rémunérations, conditions et périmètres de bug bounty n’ont pas été vérifiés ni garantis."]
            unique_urls: set[str] = set()
            changed_items = 0
            for method, result, error in sorted(found, key=lambda item: methods.index(item[0])):
                lines.append(f"\n[{method}]")
                if error:
                    lines.append(f"Recherche indisponible : {error[:300]}")
                    if not (result or {}).get("items"):
                        continue
                items = (result or {}).get("items", [])
                if (result or {}).get("warnings"):
                    lines.append("Sources : " + "; ".join(dict.fromkeys(result["warnings"])))
                if not items:
                    lines.append("Aucun résultat pour ce cycle.")
                for item in items:
                    url = item.get("url", "")
                    if not url or url in unique_urls:
                        continue
                    unique_urls.add(url)
                    seen_at = now_iso()
                    prior = db.fetch_one("SELECT title,snippet FROM income_opportunities WHERE url=? AND method=?", (url[:2000], method))
                    if not prior or prior.get("title") != str(item.get("title") or "Résultat sans titre")[:300] or prior.get("snippet") != str(item.get("snippet") or "")[:1200]:
                        changed_items += 1
                    db.execute(
                        "INSERT INTO income_opportunities(id,method,title,url,source,snippet,status,note,first_seen_at,last_seen_at,updated_at) "
                        "VALUES(?,?,?,?,?,?,'new','',?,?,?) ON CONFLICT(url,method) DO UPDATE SET "
                        "title=excluded.title,source=excluded.source,snippet=excluded.snippet,last_seen_at=excluded.last_seen_at,updated_at=excluded.updated_at",
                        (new_id("opp"), method, str(item.get("title") or "Résultat sans titre")[:300], url[:2000],
                         str(item.get("source") or "")[:40], str(item.get("snippet") or "")[:1200], seen_at, seen_at, seen_at),
                    )
                    lines.append(f"- {item.get('title', 'Résultat sans titre')} — {url}\n  {str(item.get('snippet') or '')[:350]}")
            review_at = _parse(db.get_setting("income_watch_ai_review_enqueued_at"))
            due_for_review = review_at is None or datetime.now(timezone.utc) - review_at >= timedelta(minutes=15)
            if changed_items or due_for_review:
                queued = ai_worker.enqueue("income:digest", "income_digest", {"skills": skills, "location": location}, priority=4, target="income")
                if queued:
                    db.set_setting("income_watch_ai_review_enqueued_at", now_iso())
                lines.append("\nAnalyse du modèle local " + ("mise en file; elle apparaîtra sur la page Opportunités." if queued else "non lancée (automatisations IA désactivées ou analyse déjà en attente)."))
            else:
                lines.append(f"\nAnalyse IA conservée; aucune piste nouvelle/modifiée parmi les résultats et revue relancée dans au plus 15 min (changements : {changed_items}).")
            log = "\n".join(lines)[:12000]
            status = "completed"
        elif kind == "backup":
            backup = admin.create_backup()
            log = f"Sauvegarde {backup['name']} ({backup['bytes']} octets)\n"
            status = "completed"
        elif kind == "report":
            summary = ai_tasks.complete("report_summary", {"project_id": row["project_id"]}) if config.get("ai_summary") else ""
            report_id, path = reports.render_html(row["project_id"], None, config.get("title") or None, summary)
            log = f"Rapport {report_id} généré{' avec synthèse IA' if summary else ''} : {path}\n"
            status = "completed"
        elif kind == "improvement_review":
            review = ai_tasks.complete("dashboard_priorities", {})
            recent_scans = db.fetch_all(
                "SELECT kind,status,COUNT(*) AS total FROM scans WHERE created_at>=? GROUP BY kind,status ORDER BY kind,status",
                ((datetime.now(timezone.utc) - timedelta(days=14)).isoformat(timespec="seconds"),),
            )
            recent_failures = db.fetch_all(
                "SELECT a.name,r.started_at,r.log FROM automation_runs r JOIN automations a ON a.id=r.automation_id "
                "WHERE r.status='failed' ORDER BY r.started_at DESC LIMIT 10"
            )
            evidence = "Activité des scans sur 14 jours : " + (json.dumps(recent_scans, ensure_ascii=False) if recent_scans else "aucun scan")
            evidence += "\nÉchecs récents d’automatisation : " + ("\n".join(f"- {r['name']} ({r['started_at']}): {str(r['log'])[:300]}" for r in recent_failures) if recent_failures else "aucun")
            existing = db.fetch_one("SELECT id,content FROM knowledge_docs WHERE id='kb-auto-improvement-cycle'")
            cycle = (f"Cycle du {now_iso()} — indicateurs locaux (14 jours)\n{evidence}\n"
                     + ("Recommandations IA (à vérifier avant tout changement) :\n" + review[:7000] if review
                        else "Modèle IA indisponible : seuls les indicateurs sont conservés. Configurez-le dans Paramètres > IA."))
            content = ((str(existing["content"]) + "\n\n---\n\n") if existing else "") + cycle
            content = content[-18000:]  # journal compact des cycles, afin de limiter l’index et le contexte IA
            now = now_iso()
            if existing:
                db.execute("UPDATE knowledge_docs SET title=?,category=?,content=?,source=?,tags=?,updated_at=? WHERE id=?",
                           ("Cycle d’amélioration continue", "Amélioration logicielle", content, "cybbig://automation/improvement_review", "automatique,amélioration,à-vérifier", now, existing["id"]))
            else:
                db.execute("INSERT INTO knowledge_docs(id,title,category,content,source,tags,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?)",
                           ("kb-auto-improvement-cycle", "Cycle d’amélioration continue", "Amélioration logicielle", content, "cybbig://automation/improvement_review", "automatique,amélioration,à-vérifier", now, now))
            db.audit("improvement_cycle_completed", {"scans_14d": len(recent_scans), "recent_failures": len(recent_failures), "ai_review": bool(review)})
            log = "Cycle consigné dans la base de connaissances pour enrichir les prochains contextes IA.\n\n" + cycle
            status = "completed"
        elif kind == "project_suite":
            project = db.fetch_one("SELECT * FROM projects WHERE id=?", (row["project_id"],))
            if not project:
                raise RuntimeError("Projet associé introuvable.")
            launched = []
            for scan_kind in config.get("scans", ["php", "web", "api", "checkout"]):
                target = _project_target(project, scan_kind, {})
                if not target:
                    continue
                scan = jobs.create_scan(project["id"], scan_kind, target, {})
                jobs.start_scan(scan["id"])
                launched.append(f"{scan_kind}: {scan['id']}")
            if not launched:
                raise RuntimeError("Aucune cible configurée pour les analyses sélectionnées.")
            log = "Analyses du projet lancées dans son périmètre configuré :\n" + "\n".join(launched)
            status = "submitted"
        else:
            project = db.fetch_one("SELECT * FROM projects WHERE id=?", (row["project_id"],))
            if not project:
                raise RuntimeError("Projet associé introuvable.")
            target = _project_target(project, kind, config)
            scan = jobs.create_scan(project["id"], kind, target, config)
            jobs.start_scan(scan["id"])
            log = f"Scan {scan['id']} démarré ({kind}) sur {target or project.get('path')}\n"
            status = "submitted"
        db.execute(
            "UPDATE automation_runs SET status=?, finished_at=?, log=? WHERE id=?",
            (status, now_iso(), log, run_id),
        )
        db.execute(
            "UPDATE automations SET last_run_at=?, next_run_at=?, last_status=?, updated_at=? WHERE id=?",
            (now_iso(), _next(row["interval_minutes"]), status, now_iso(), automation_id),
        )
        db.audit("automation_run", {"id": automation_id, "run_id": run_id, "status": status, "manual": manual})
        if kind == "income_watch":
            db.execute("DELETE FROM automation_runs WHERE automation_id=? AND id NOT IN (SELECT id FROM automation_runs WHERE automation_id=? ORDER BY started_at DESC LIMIT 1000)",
                       (automation_id, automation_id))
            db.set_setting("income_opportunity_initial_search_done", "1")
        return {"run_id": run_id, "status": status, "log": log}
    except Exception as exc:  # noqa: BLE001
        message = f"{type(exc).__name__}: {exc}"
        db.execute(
            "UPDATE automation_runs SET status='failed', finished_at=?, log=? WHERE id=?",
            (now_iso(), message, run_id),
        )
        db.execute(
            "UPDATE automations SET last_run_at=?, next_run_at=?, last_status='failed', updated_at=? WHERE id=?",
            (now_iso(), _next(row["interval_minutes"]), now_iso(), automation_id),
        )
        db.audit("automation_failed", {"id": automation_id, "error": message})
        return {"run_id": run_id, "status": "failed", "error": message}
    finally:
        with _lock:
            _running.discard(automation_id)


def _loop() -> None:
    time.sleep(5)
    while not _stop.is_set():
        try:
            rows = db.fetch_all("SELECT * FROM automations WHERE enabled=1")
            now = datetime.now(timezone.utc)
            for row in rows:
                with _lock:
                    if row["id"] in _running or row["id"] in _queued:
                        continue
                due = _parse(row.get("next_run_at"))
                if due is None or due <= now:
                    with _lock:
                        if row["id"] in _running or row["id"] in _queued:
                            continue
                        _queued.add(row["id"])
                    try:
                        _executor.submit(_run_scheduled, row["id"])
                    except RuntimeError:
                        with _lock:
                            _queued.discard(row["id"])
        except Exception:
            pass
        _stop.wait(30)


def _run_scheduled(automation_id: str) -> None:
    try:
        run_now(automation_id, manual=False)
    except Exception:
        pass
    finally:
        with _lock:
            _queued.discard(automation_id)


def start() -> None:
    global _thread
    if _thread and _thread.is_alive():
        return
    _stop.clear()
    _thread = threading.Thread(target=_loop, name="cybbig-scheduler", daemon=True)
    _thread.start()


def ensure_improvement_cycle() -> None:
    """Installe une seule fois le bilan quotidien demandé; l’utilisateur peut ensuite le désactiver ou le supprimer."""
    marker = "auto_improvement_cycle_initialized"
    if db.get_setting(marker) == "1":
        return
    existing = db.fetch_one("SELECT id FROM automations WHERE kind='improvement_review' LIMIT 1")
    if not existing:
        now = datetime.now(timezone.utc)
        db.execute(
            "INSERT INTO automations(id,project_id,name,kind,interval_minutes,config_json,enabled,next_run_at,last_status,created_at,updated_at) "
            "VALUES(?,?,?,?,?,?,?,?,?,?,?)",
            ("auto-system-improvement", None, "Cycle quotidien d’amélioration IA", "improvement_review", 1440,
             "{}", 1, (now + timedelta(days=1)).isoformat(timespec="seconds"), "never",
             now.isoformat(timespec="seconds"), now.isoformat(timespec="seconds")),
        )
        db.audit("improvement_cycle_enabled", {"interval_minutes": 1440})
    db.set_setting(marker, "1")


def ensure_income_watch() -> None:
    """Active une veille d'opportunités toutes les deux minutes, désactivable par le propriétaire."""
    marker = "income_opportunity_watch_initialized"
    cadence_marker = "income_watch_two_minute_cadence_migrated"
    if db.get_setting(cadence_marker) != "1":
        radars = db.fetch_all("SELECT id,interval_minutes FROM automations WHERE kind='income_watch' AND interval_minutes>2")
        for radar in radars:
            name_update = ",name='Radar autonome d’opportunités rémunérées'" if radar["id"] == "auto-income-opportunities" else ""
            db.execute(f"UPDATE automations SET interval_minutes=2,next_run_at=?,updated_at=?{name_update} WHERE id=?",
                       (now_iso(), now_iso(), radar["id"]))
        if radars:
            db.audit("income_watch_cadence_updated", {"count": len(radars), "interval_minutes": 2})
        db.set_setting(cadence_marker, "1")
    if db.get_setting(marker) == "1":
        # Si une ancienne version a créé le radar sans terminer son premier cycle, relancer au prochain démarrage.
        if db.get_setting("income_opportunity_initial_search_done") != "1":
            row = db.fetch_one("SELECT id,last_status,enabled FROM automations WHERE kind='income_watch' ORDER BY created_at LIMIT 1")
            if row and row.get("enabled") and row.get("last_status") != "running":
                db.execute("UPDATE automations SET next_run_at=?,updated_at=? WHERE id=?", (now_iso(), now_iso(), row["id"]))
        # Récupère une fois les anciennes installations qui ont déclaré le premier cycle
        # réussi alors que la base restait vide (ex. moteur Web bloqué/erreur d'écriture).
        if db.get_setting("income_watch_empty_recovery_attempted") != "1" and not db.fetch_one("SELECT id FROM income_opportunities LIMIT 1"):
            row = db.fetch_one("SELECT id,enabled,last_status FROM automations WHERE kind='income_watch' ORDER BY created_at LIMIT 1")
            if row and row.get("enabled") and row.get("last_status") != "running":
                db.execute("UPDATE automations SET next_run_at=?,updated_at=? WHERE id=?", (now_iso(), now_iso(), row["id"]))
                db.set_setting("income_watch_empty_recovery_attempted", "1")
        return
    existing = db.fetch_one("SELECT id FROM automations WHERE kind='income_watch' LIMIT 1")
    if not existing:
        now = datetime.now(timezone.utc)
        config = {"methods": ["freelance", "remote_contracts", "bug_bounty", "grants"],
                  "location": "France", "skills": "développement web, Python, cybersécurité", "limit": 5}
        db.execute(
            "INSERT INTO automations(id,project_id,name,kind,interval_minutes,config_json,enabled,next_run_at,last_status,created_at,updated_at) "
            "VALUES(?,?,?,?,?,?,?,?,?,?,?)",
            ("auto-income-opportunities", None, "Radar autonome d’opportunités rémunérées", "income_watch", 2,
             json.dumps(config, ensure_ascii=False), 1, now.isoformat(timespec="seconds"), "never",
             now.isoformat(timespec="seconds"), now.isoformat(timespec="seconds")),
        )
        db.audit("income_watch_enabled", {"methods": config["methods"], "interval_minutes": 2})
    db.set_setting(marker, "1")


def recover_stale_runs() -> int:
    """Clôt les exécutions interrompues par la fermeture du logiciel."""
    rows = db.fetch_all("SELECT id,automation_id FROM automation_runs WHERE status='running'")
    now = now_iso()
    for row in rows:
        db.execute("UPDATE automation_runs SET status='failed',finished_at=?,log='Exécution interrompue par le redémarrage de Cybbig.' WHERE id=?",
                   (now, row["id"]))
        db.execute("UPDATE automations SET last_status='failed',updated_at=? WHERE id=?", (now, row["automation_id"]))
    if rows:
        db.audit("automation_runs_recovered", {"count": len(rows)})
    return len(rows)


def stop() -> None:
    _stop.set()
    if _thread:
        _thread.join(timeout=3)


def status() -> dict[str, Any]:
    rows = db.fetch_all("SELECT COUNT(*) AS total, SUM(enabled) AS enabled FROM automations")
    row = rows[0] if rows else {"total": 0, "enabled": 0}
    return {
        "running": bool(_thread and _thread.is_alive()),
        "executing": len(_running),
        "queued": len(_queued),
        "total": row.get("total") or 0,
        "enabled": row.get("enabled") or 0,
        "next_runs": db.fetch_all(
            "SELECT id,name,next_run_at FROM automations WHERE enabled=1 ORDER BY next_run_at LIMIT 5"
        ),
    }
