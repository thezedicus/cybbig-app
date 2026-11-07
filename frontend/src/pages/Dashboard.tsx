import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
  Activity, AlertTriangle, ArrowRight, BookOpen, Bot, Boxes, ChevronRight,
  ClipboardList, FileWarning, Radar, ScanLine, ShieldAlert, Sparkles,
} from 'lucide-react'
import { api, engineLabel, formatDate, relativeDate, scanLabel } from '../api'
import AiPanel from '../components/AiPanel'
import { AlertBox, EmptyState, Loading, RiskGauge, SeverityBadge, SeverityBar, StatusPill, TrendChart } from '../components/ui'
import type { DashboardData } from '../types'

export default function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const load = () => {
    api.get<DashboardData>('/api/dashboard')
      .then((d) => { setData(d); setError('') })
      .catch((e) => setError((e as Error).message))
  }

  useEffect(() => {
    load()
    const timer = window.setInterval(load, 30000)
    return () => window.clearInterval(timer)
  }, [])

  if (error && !data) return <AlertBox kind="error">{error}</AlertBox>
  if (!data) return <Loading label="Chargement du tableau de bord…" />

  const { counts, severity } = data
  const intel = data.intel

  return (
    <div className="stack dashboard-root" style={{ gap: 16 }}>
      <div className="hero">
        <RiskGauge value={data.risk_score} size={126} />
        <div style={{ flex: 1, minWidth: 260 }}>
          <div className="row" style={{ gap: 7 }}>
            <span className="status-dot" />
            <span className="tiny" style={{ color: 'var(--green)', letterSpacing: '.1em', textTransform: 'uppercase', fontWeight: 700 }}>Posture actuelle</span>
          </div>
          <h2 className="mt-1">Votre surface d’attaque, sous contrôle.</h2>
          <p>
            {counts.findings} résultat(s) ouvert(s) sur {counts.projects} projet(s), dont {counts.critical} critique(s)
            et {counts.high} élevé(s). Les analyses sont passives ou statiques et ne quittent pas votre machine.
          </p>
          <div className="row wrap mt-2">
            <button className="btn primary sm" onClick={() => navigate('/scans?launch=1')}><ScanLine size={14} /> Lancer une analyse</button>
            <Link to="/findings" className="btn sm"><ClipboardList size={14} /> Voir les résultats</Link>
            <Link to="/intel" className="btn ghost sm"><Radar size={14} /> Veille : {intel.items} fiche(s)</Link>
          </div>
        </div>
        <div className="grid" style={{ gridTemplateColumns: 'repeat(2, minmax(100px, 1fr))', gap: 10, minWidth: 280 }}>
          <MiniStat label="Critiques" value={counts.critical} color="var(--critical)" />
          <MiniStat label="Élevés" value={counts.high} color="var(--high)" />
          <MiniStat label="Analyses" value={counts.scans} color="var(--accent)" />
          <MiniStat label="Projets" value={counts.projects} color="var(--green)" />
        </div>
      </div>

      <div className="mb-2">
        <AiPanel task="dashboard_priorities" params={{}} cacheKey="dashboard" title="Plan de la semaine (IA)" label="Proposer les priorités" />
      </div>

      <div className="grid cols-4">
        <div className="card stat-card">
          <div className="stat-label"><ClipboardList size={13} /> Résultats ouverts</div>
          <div className="stat-value">{counts.findings}</div>
          <div className="stat-foot">{counts.findings_total} au total · {counts.alerts_unread} alerte(s)</div>
        </div>
        <div className="card stat-card">
          <div className="stat-label"><ShieldAlert size={13} /> Risque pondéré</div>
          <div className="stat-value" style={{ color: data.risk_score >= 70 ? 'var(--critical)' : data.risk_score >= 40 ? 'var(--high)' : 'var(--green)' }}>{data.risk_score.toFixed(1)}<span style={{ fontSize: 13, color: 'var(--faint)' }}>/100</span></div>
          <div className="stat-foot">Indice non normatif, à contextualiser</div>
        </div>
        <div className="card stat-card">
          <div className="stat-label"><Radar size={13} /> Threat Intel</div>
          <div className="stat-value">{intel.items}</div>
          <div className="stat-foot">{intel.exploited} exploitée(s) · {intel.last_fetch ? relativeDate(intel.last_fetch) : 'jamais synchronisé'}</div>
        </div>
        <div className="card stat-card">
          <div className="stat-label"><Bot size={13} /> Assistant IA</div>
          <div className="stat-value" style={{ fontSize: 20, paddingTop: 4 }}>{data.ai.available ? 'Ollama prêt' : 'Hors ligne'}</div>
          <div className="stat-foot">{data.ai.available ? (data.ai.selected_model || 'modèle à choisir') : 'mode déterministe local'}</div>
        </div>
      </div>

      <div className="two-col dashboard-two-col">
        <div className="card">
          <div className="card-header">
            <div><h2>Activité des 14 derniers jours</h2><div className="sub">Résultats enregistrés par jour</div></div>
            <div className="right"><span className="tag">détections</span></div>
          </div>
          <div className="card-pad">
            <TrendChart data={data.trend} />
            <div className="row mt-2 tiny faint" style={{ gap: 16 }}>
              <span><i style={{ display: 'inline-block', width: 7, height: 7, background: 'var(--accent)', borderRadius: 2, marginRight: 5 }} />Total</span>
              <span><i style={{ display: 'inline-block', width: 7, height: 7, background: 'var(--critical)', borderRadius: 2, marginRight: 5 }} />Part critique forte</span>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="card-header"><div><h2>Répartition par gravité</h2><div className="sub">Résultats ouverts</div></div></div>
          <div className="card-pad">
            <SeverityBar counts={severity} />
            <div className="row between mt-3">
              <Link to="/findings" className="btn sm">Ouvrir les résultats <ArrowRight size={13} /></Link>
              {data.by_engine[0] && <span className="tiny faint">Moteur principal : {engineLabel(data.by_engine[0].engine)}</span>}
            </div>
          </div>
        </div>
      </div>

      <div className="two-col dashboard-two-col">
        <div className="card">
          <div className="card-header">
            <div><h2>Priorités de correction</h2><div className="sub">Les résultats les plus graves, tous périmètres</div></div>
            <div className="right"><Link to="/findings" className="btn ghost sm">Tout voir <ChevronRight size={13} /></Link></div>
          </div>
          {data.top_findings.length === 0 ? (
            <EmptyState icon={<ShieldAlert size={26} />} title="Aucun résultat" description="Lancez une analyse pour commencer." />
          ) : (
            <div className="table-wrap">
              <table className="data">
                <thead><tr><th>Gravité</th><th>Résultat</th><th>Moteur</th><th>Projet</th></tr></thead>
                <tbody>
                  {data.top_findings.map((f) => (
                    <tr key={f.id} className="clickable" onClick={() => navigate(`/findings?focus=${f.id}`)}>
                      <td><SeverityBadge severity={f.severity} /></td>
                      <td><div className="cell-title clamp-2">{f.title}</div><div className="cell-sub truncate">{f.file_path || f.url}</div></td>
                      <td><span className="tag">{engineLabel(f.engine)}</span></td>
                      <td className="small muted">{f.project_name || '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <div className="card">
          <div className="card-header">
            <div><h2>Alertes récentes</h2><div className="sub">Veille et analyses</div></div>
            <div className="right"><Link to="/intel" className="btn ghost sm">Veille <ChevronRight size={13} /></Link></div>
          </div>
          <div className="card-pad" style={{ paddingTop: 6 }}>
            {data.alerts.length === 0 ? (
              <EmptyState icon={<AlertTriangle size={24} />} title="Aucune alerte" description="Les alertes apparaîtront après les scans et la veille." />
            ) : data.alerts.map((a) => (
              <div className="list-item" key={a.id}>
                <div className="icon-wrap"><AlertTriangle size={14} /></div>
                <div className="list-main">
                  <div className="title clamp-2">{a.title}</div>
                  <div className="sub">{a.source} · {relativeDate(a.created_at)}</div>
                </div>
                <SeverityBadge severity={a.severity} />
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="two-col dashboard-two-col">
        <div className="card">
          <div className="card-header">
            <div><h2>Analyses récentes</h2><div className="sub">Derniers moteurs exécutés</div></div>
            <div className="right"><Link to="/scans" className="btn ghost sm">Toutes <ChevronRight size={13} /></Link></div>
          </div>
          {data.recent_scans.length === 0 ? (
            <EmptyState icon={<Activity size={26} />} title="Aucune analyse" description="Lancez un scan PHP, Web, API ou checkout." action={<button className="btn primary sm" onClick={() => navigate('/scans?launch=1')}>Nouvelle analyse</button>} />
          ) : (
            <div className="table-wrap">
              <table className="data">
                <thead><tr><th>Analyse</th><th>Projet</th><th>Statut</th><th>Résultats</th><th>Date</th></tr></thead>
                <tbody>
                  {data.recent_scans.map((s) => (
                    <tr key={s.id} className="clickable" onClick={() => navigate(`/scans/${s.id}`)}>
                      <td><span className="tag">{scanLabel(s.kind)}</span> <span className="cell-mono">{s.target ? s.target.split('/').slice(-1)[0] : '—'}</span></td>
                      <td className="small">{s.project_name || '—'}</td>
                      <td><StatusPill status={s.status} /></td>
                      <td className="mono small">{s.summary?.findings ?? '—'}</td>
                      <td className="tiny faint">{formatDate(s.created_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <div className="card">
          <div className="card-header">
            <div><h2>Projets</h2><div className="sub">Périmètres et risque courant</div></div>
            <div className="right"><Link to="/projects" className="btn ghost sm">Gérer <ChevronRight size={13} /></Link></div>
          </div>
          <div className="card-pad" style={{ paddingTop: 4 }}>
            {data.projects.length === 0 ? (
              <EmptyState icon={<Boxes size={24} />} title="Aucun projet" description="Créez un périmètre autorisé." />
            ) : data.projects.map((p) => (
              <Link to={`/projects/${p.id}`} key={p.id} className="list-item" style={{ color: 'inherit' }}>
                <div className="icon-wrap"><Boxes size={14} /></div>
                <div className="list-main">
                  <div className="title">{p.name}</div>
                  <div className="sub">{p.client || 'Sans client'} · niveau {p.activity_level} · {p.findings} résultat(s)</div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontWeight: 750, color: p.risk_score >= 70 ? 'var(--critical)' : p.risk_score >= 40 ? 'var(--high)' : 'var(--green)' }}>{p.risk_score.toFixed(0)}</div>
                  <div className="tiny faint">risque</div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </div>

      <div className="card card-pad row wrap" style={{ gap: 16 }}>
        <div className="row" style={{ gap: 10 }}>
          <div className="brand-mark" style={{ width: 34, height: 34 }}><FileWarning size={17} /></div>
          <div><div style={{ fontWeight: 650 }}>Rappels de méthode</div><div className="tiny faint">Analyse passive, aucun exploit, validation humaine requise.</div></div>
        </div>
        <div className="spacer" />
        <Link to="/knowledge" className="btn sm"><BookOpen size={14} /> Base de connaissances</Link>
        <Link to="/lab" className="btn sm"><Sparkles size={14} /> Laboratoire</Link>
      </div>
    </div>
  )
}

function MiniStat({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div style={{ border: '1px solid var(--line-soft)', borderRadius: 10, padding: '10px 12px', background: 'rgba(6,14,25,.35)' }}>
      <div style={{ fontSize: 22, fontWeight: 750, color, lineHeight: 1.1 }}>{value}</div>
      <div className="tiny faint" style={{ marginTop: 2 }}>{label}</div>
    </div>
  )
}
