from __future__ import annotations

import html
import json
import re
from pathlib import Path
from typing import Any

from .. import db
from ..config import REPORTS_DIR
from ..utils import new_id, now_iso, risk_score, severity_counts

SEV_LABELS = {
    "critical": "Critique", "high": "Élevé", "medium": "Moyen",
    "low": "Faible", "info": "Information", "unknown": "Inconnu",
}
SEV_COLORS = {
    "critical": "#b91c1c", "high": "#dc2626", "medium": "#d97706",
    "low": "#2563eb", "info": "#64748b", "unknown": "#64748b",
}


def _e(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def _findings(project_id: str, scan_id: str | None = None) -> list[dict[str, Any]]:
    if scan_id:
        rows = db.fetch_all(
            "SELECT * FROM findings WHERE project_id=? AND scan_id=? ORDER BY "
            "CASE severity WHEN 'critical' THEN 0 WHEN 'high' THEN 1 WHEN 'medium' THEN 2 "
            "WHEN 'low' THEN 3 ELSE 4 END, created_at DESC",
            (project_id, scan_id),
        )
    else:
        rows = db.fetch_all(
            "SELECT * FROM findings WHERE project_id=? ORDER BY "
            "CASE severity WHEN 'critical' THEN 0 WHEN 'high' THEN 1 WHEN 'medium' THEN 2 "
            "WHEN 'low' THEN 3 ELSE 4 END, created_at DESC LIMIT 1000",
            (project_id,),
        )
    for row in rows:
        row["references"] = db.json_loads(row.get("references_json"), [])
    return rows


def build_data(project_id: str, scan_id: str | None = None) -> dict[str, Any]:
    project = db.fetch_one("SELECT * FROM projects WHERE id=?", (project_id,))
    if not project:
        raise ValueError("Projet introuvable.")
    scan = db.fetch_one("SELECT * FROM scans WHERE id=? AND project_id=?", (scan_id, project_id)) if scan_id else None
    findings = _findings(project_id, scan_id)
    counts = severity_counts(findings)
    deps = db.fetch_all(
        "SELECT package,version,vulnerable,vuln_id,severity,summary,fixed_version,source FROM dependencies WHERE scan_id=? ORDER BY vulnerable DESC, package",
        (scan_id,),
    ) if scan_id else []
    return {
        "project": project,
        "scan": scan,
        "findings": findings,
        "severity": counts,
        "risk_score": risk_score(findings),
        "dependencies": deps,
        "generated_at": now_iso(),
        "summary": db.json_loads(scan.get("summary_json"), {}) if scan else {},
    }


def _finding_html(f: dict[str, Any], index: int) -> str:
    sev = f.get("severity", "info")
    color = SEV_COLORS.get(sev, "#64748b")
    location = f.get("file_path") or f.get("url") or ""
    lines = f"{f.get('line_start') or ''}" + (f"-{f.get('line_end')}" if f.get("line_end") else "")
    refs = "".join(
        f'<li><a href="{_e(url)}">{_e(url)}</a></li>' for url in f.get("references", []) if url
    )
    return f"""
    <article class="finding">
      <header>
        <div class="finding-title"><span class="index">#{index:03d}</span> {_e(f.get('title'))}</div>
        <span class="badge" style="background:{color}">{_e(SEV_LABELS.get(sev, sev))}</span>
      </header>
      <div class="meta">
        <span>Moteur : <b>{_e(f.get('engine'))}</b></span>
        <span>Règle : <b>{_e(f.get('rule_id'))}</b></span>
        <span>Confiance : <b>{_e(f.get('confidence'))}</b></span>
        {f'<span>CWE : <b>{_e(f.get("cwe"))}</b></span>' if f.get('cwe') else ''}
        {f'<span>OWASP : <b>{_e(f.get("owasp"))}</b></span>' if f.get('owasp') else ''}
        {f'<span>Emplacement : <code>{_e(location)}{(":" + lines) if lines else ""}</code></span>' if location else ''}
      </div>
      <p>{_e(f.get('description'))}</p>
      {f'<div class="evidence"><div class="label">Preuve</div><pre>{_e(f.get("evidence"))}</pre></div>' if f.get('evidence') else ''}
      <div class="remediation"><div class="label">Remédiation</div><p>{_e(f.get('remediation'))}</p></div>
      {f'<div class="refs"><div class="label">Références</div><ul>{refs}</ul></div>' if refs else ''}
    </article>
    """


def _md_html(text: str) -> str:
    """Markdown minimal (titres, listes, gras, code) vers HTML échappé, pour la synthèse IA."""
    out, in_list = [], False
    for raw in text.splitlines():
        line = _e(raw.strip())
        line = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", line)
        line = re.sub(r"`([^`]+)`", r"<code>\1</code>", line)
        if re.match(r"^([-*]|\d+[.)])\s+", line):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append("<li>" + re.sub(r"^([-*]|\d+[.)])\s+", "", line) + "</li>")
            continue
        if in_list:
            out.append("</ul>")
            in_list = False
        if line.startswith("#"):
            out.append("<h3>" + line.lstrip("# ") + "</h3>")
        elif line and not line.startswith("```"):
            out.append(f"<p>{line}</p>")
    if in_list:
        out.append("</ul>")
    return "\n".join(out)


def render_html(project_id: str, scan_id: str | None = None, title: str | None = None, ai_summary: str = "") -> tuple[str, str]:
    data = build_data(project_id, scan_id)
    project = data["project"]
    scan = data["scan"]
    counts = data["severity"]
    findings = data["findings"]
    heading = title or (f"Rapport — {project['name']}" if not scan else f"Rapport {scan['kind']} — {project['name']}")
    scan_info = ""
    if scan:
        scan_info = f"""
        <div class="kv"><span>Type</span><b>{_e(scan.get('kind'))}</b></div>
        <div class="kv"><span>Cible</span><b>{_e(scan.get('target') or project.get('path') or project.get('base_url'))}</b></div>
        <div class="kv"><span>Statut</span><b>{_e(scan.get('status'))}</b></div>
        <div class="kv"><span>Début</span><b>{_e(scan.get('started_at'))}</b></div>
        <div class="kv"><span>Fin</span><b>{_e(scan.get('finished_at'))}</b></div>
        <div class="kv"><span>Mode</span><b>{_e(scan.get('mode'))} — aucun exploit</b></div>
        """
    deps_html = ""
    if data["dependencies"]:
        rows = "".join(
            f"<tr><td>{_e(d['package'])}</td><td>{_e(d['version'])}</td>"
            f"<td>{'Oui' if d['vulnerable'] else 'Non'}</td><td>{_e(d.get('vuln_id',''))}</td>"
            f"<td>{_e(d.get('severity',''))}</td><td>{_e(d.get('fixed_version',''))}</td></tr>"
            for d in data["dependencies"]
        )
        deps_html = f"""
        <section><h2>Dépendances</h2>
        <table><thead><tr><th>Paquet</th><th>Version</th><th>Vulnérable</th><th>ID</th><th>Gravité</th><th>Corrigé en</th></tr></thead>
        <tbody>{rows}</tbody></table></section>"""
    findings_html = "".join(_finding_html(f, i) for i, f in enumerate(findings, 1)) or '<p class="muted">Aucun résultat enregistré.</p>'
    ai_html = (
        '<section class="ai"><h2>Synthèse (assistant IA local)</h2>' + _md_html(ai_summary)
        + '<p class="muted" style="font-size:11px">Rédigée par un modèle local à partir des résultats ci-dessous : à relire avant diffusion.</p></section>'
    ) if ai_summary.strip() else ""
    active_used = bool(db.fetch_one("SELECT 1 FROM scans WHERE project_id=? AND mode='active' LIMIT 1", (project_id,)))
    mode_text = (
        "Analyse défensive statique et Web. Certaines analyses ont utilisé le mode actif : requêtes non destructives "
        "(OPTIONS, TRACE, en-tête Origin, marqueurs inoffensifs dans les paramètres), limitées au périmètre autorisé."
        if active_used else "Analyse défensive, passive et statique."
    )
    body = f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{_e(heading)}</title>
<style>
  :root {{ color-scheme: light; }}
  * {{ box-sizing: border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; background:#f1f5f9; color:#0f172a; line-height:1.55; }}
  .page {{ max-width: 1100px; margin: 0 auto; padding: 32px; background:#fff; min-height:100vh; }}
  .brand {{ display:flex; justify-content:space-between; align-items:flex-start; border-bottom:3px solid #0f172a; padding-bottom:18px; margin-bottom:24px; }}
  .brand h1 {{ margin:0 0 4px; font-size:28px; letter-spacing:-0.5px; }}
  .brand .sub {{ color:#475569; font-size:13px; }}
  .chip {{ background:#0f172a; color:#fff; padding:6px 10px; border-radius:6px; font-size:12px; font-weight:700; letter-spacing:.5px; }}
  .meta-grid {{ display:grid; grid-template-columns: repeat(3, 1fr); gap:10px 24px; margin:18px 0 26px; font-size:13px; }}
  .kv span {{ color:#64748b; display:block; font-size:11px; text-transform:uppercase; letter-spacing:.4px; }}
  .kv b {{ font-weight:600; word-break:break-word; }}
  .cards {{ display:grid; grid-template-columns: repeat(5, 1fr); gap:10px; margin:22px 0; }}
  .card {{ border:1px solid #e2e8f0; border-radius:10px; padding:12px; }}
  .card .n {{ font-size:28px; font-weight:800; line-height:1; }}
  .card .l {{ font-size:11px; color:#64748b; text-transform:uppercase; letter-spacing:.4px; margin-top:5px; }}
  .risk {{ border:1px solid #e2e8f0; border-radius:10px; padding:16px; margin:16px 0 24px; display:flex; align-items:center; gap:18px; }}
  .risk .score {{ font-size:34px; font-weight:800; }}
  .risk .bar {{ flex:1; height:10px; background:#e2e8f0; border-radius:99px; overflow:hidden; }}
  .risk .bar > i {{ display:block; height:100%; background:linear-gradient(90deg,#22c55e,#eab308,#ef4444); width:var(--w); }}
  h2 {{ font-size:18px; margin-top:30px; padding-bottom:6px; border-bottom:1px solid #e2e8f0; }}
  .finding {{ border:1px solid #e2e8f0; border-radius:10px; padding:16px; margin:14px 0; break-inside:avoid; }}
  .finding header {{ display:flex; justify-content:space-between; gap:12px; align-items:flex-start; }}
  .finding-title {{ font-weight:700; font-size:15px; }}
  .index {{ color:#94a3b8; font-variant-numeric:tabular-nums; }}
  .badge {{ color:#fff; border-radius:999px; padding:3px 9px; font-size:11px; font-weight:700; white-space:nowrap; }}
  .meta {{ display:flex; flex-wrap:wrap; gap:6px 16px; color:#475569; font-size:12px; margin:8px 0 10px; }}
  code, pre {{ font-family: ui-monospace, SFMono-Regular, Consolas, monospace; font-size:12px; }}
  pre {{ background:#0f172a; color:#e2e8f0; padding:12px; border-radius:8px; overflow:auto; white-space:pre-wrap; word-break:break-word; }}
  .evidence .label, .remediation .label, .refs .label {{ font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:.5px; color:#64748b; margin-bottom:4px; }}
  .remediation p {{ margin:4px 0; }}
  .refs ul {{ margin:4px 0; padding-left:20px; font-size:12px; word-break:break-all; }}
  table {{ width:100%; border-collapse:collapse; font-size:12px; margin-top:10px; }}
  th, td {{ border:1px solid #e2e8f0; padding:6px 8px; text-align:left; vertical-align:top; }}
  th {{ background:#f8fafc; }}
  .notice {{ background:#fff7ed; border:1px solid #fed7aa; border-radius:8px; padding:12px 14px; font-size:12px; color:#7c2d12; margin:18px 0; }}
  .muted {{ color:#64748b; }}
  .ai {{ background:#f0f9ff; border:1px solid #bae6fd; border-radius:10px; padding:4px 18px 10px; margin:18px 0; }}
  .ai ul {{ padding-left:20px; }}
  footer {{ margin-top:34px; padding-top:14px; border-top:1px solid #e2e8f0; color:#64748b; font-size:11px; }}
  @media print {{ body {{ background:#fff; }} .page {{ padding:0; }} .chip {{ -webkit-print-color-adjust: exact; }} }}
  @media (max-width: 800px) {{ .meta-grid, .cards {{ grid-template-columns: 1fr 1fr; }} }}
</style>
</head>
<body><div class="page">
  <div class="brand">
    <div><h1>CYBBIG — Rapport de sécurité</h1><div class="sub">{_e(heading)}</div></div>
    <div class="chip">DOCUMENT LOCAL</div>
  </div>
  <div class="meta-grid">
    <div class="kv"><span>Projet</span><b>{_e(project['name'])}</b></div>
    <div class="kv"><span>Client / organisation</span><b>{_e(project.get('client') or '—')}</b></div>
    <div class="kv"><span>Environnement</span><b>{_e(project.get('environment'))}</b></div>
    <div class="kv"><span>Périmètre URL</span><b>{_e(project.get('base_url') or '—')}</b></div>
    <div class="kv"><span>Dossier</span><b>{_e(project.get('path') or '—')}</b></div>
    <div class="kv"><span>Autorisation</span><b>{_e(project.get('authorization_ref') or 'non renseignée')}</b></div>
    <div class="kv"><span>Autorisé par</span><b>{_e(project.get('authorized_by') or '—')}</b></div>
    <div class="kv"><span>Niveau d'activité</span><b>{_e(project.get('activity_level'))}</b></div>
    <div class="kv"><span>Date du rapport</span><b>{_e(data['generated_at'])}</b></div>
    {scan_info}
  </div>
  <div class="risk"><div class="score">{data['risk_score']}</div><div style="flex:1"><div class="bar"><i style="--w:{data['risk_score']}%"></i></div><div class="muted" style="font-size:12px;margin-top:6px">Indice de risque pondéré (0–100), non normatif. À interpréter avec l'exposition et le contexte métier.</div></div></div>
  <div class="cards">
    <div class="card"><div class="n" style="color:{SEV_COLORS['critical']}">{counts.get('critical',0)}</div><div class="l">Critique</div></div>
    <div class="card"><div class="n" style="color:{SEV_COLORS['high']}">{counts.get('high',0)}</div><div class="l">Élevé</div></div>
    <div class="card"><div class="n" style="color:{SEV_COLORS['medium']}">{counts.get('medium',0)}</div><div class="l">Moyen</div></div>
    <div class="card"><div class="n" style="color:{SEV_COLORS['low']}">{counts.get('low',0)}</div><div class="l">Faible</div></div>
    <div class="card"><div class="n" style="color:{SEV_COLORS['info']}">{counts.get('info',0)}</div><div class="l">Info</div></div>
  </div>
  {ai_html}
  <h2>Méthodologie et limites</h2>
  <p>{mode_text} Le code PHP n'est pas exécuté. Les scans Web n'envoient aucune charge d'exploitation. Les vérifications de fichiers exposés se limitent à des requêtes GET tronquées, sans conservation du contenu. Les résultats sont heuristiques : ils doivent être confirmés par une revue manuelle et des tests autorisés en préproduction.</p>
  <div class="notice"><b>Usage responsable.</b> Ce rapport ne constitue ni une certification, ni une preuve d'absence de vulnérabilité. Cybbig ne fournit aucune autorisation juridique. Utilisez uniquement des systèmes possédés ou explicitement autorisés.</div>
  {deps_html}
  <section><h2>Résultats ({len(findings)})</h2>{findings_html}</section>
  <footer>Généré par Cybbig 0.1.0 — {_e(data['generated_at'])} — Données conservées localement. Rapport HTML imprimable en PDF (Ctrl+P).</footer>
</div></body></html>"""
    report_id = new_id("report")
    filename = f"{report_id}.html"
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    path = (REPORTS_DIR / filename).resolve()
    path.write_text(body, encoding="utf-8")
    db.execute(
        "INSERT INTO reports(id,project_id,scan_id,kind,title,path,meta_json,created_at) VALUES(?,?,?,?,?,?,?,?)",
        (report_id, project_id, scan_id, "html", heading[:300], str(path),
         json.dumps({"findings": len(findings), "severity": counts, "risk_score": data["risk_score"], "ai_summary": bool(ai_summary.strip())}, ensure_ascii=False),
         data["generated_at"]),
    )
    db.audit("report_generated", {"report_id": report_id, "project_id": project_id, "scan_id": scan_id})
    return report_id, str(path)


def report_path(report_id: str) -> Path | None:
    row = db.fetch_one("SELECT path FROM reports WHERE id=?", (report_id,))
    if not row:
        return None
    path = Path(row["path"]).resolve()
    try:
        path.relative_to(REPORTS_DIR.resolve())
    except ValueError:
        return None
    return path if path.exists() else None
