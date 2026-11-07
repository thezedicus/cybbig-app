import { useEffect, useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import {
  ClipboardList, Download, Search, SlidersHorizontal, X,
} from 'lucide-react'
import { api, engineLabel, formatDate } from '../api'
import FindingDrawer from '../components/FindingDrawer'
import {
  AlertBox, EmptyState, Loading, PageHeader, SeverityBadge, SeverityBar, StatusPill,
} from '../components/ui'
import type { Finding, Project, Severity, SeverityCounts } from '../types'

const PAGE = 50

export default function Findings() {
  const [params, setParams] = useSearchParams()
  const [items, setItems] = useState<Finding[] | null>(null)
  const [total, setTotal] = useState(0)
  const [counts, setCounts] = useState<SeverityCounts>({ critical: 0, high: 0, medium: 0, low: 0, info: 0 })
  const [projects, setProjects] = useState<Project[]>([])
  const [error, setError] = useState('')
  const [query, setQuery] = useState('')
  const [searchInput, setSearchInput] = useState('')
  const [severity, setSeverity] = useState((params.get('severity') as Severity | null) ?? '')
  const [status, setStatus] = useState(params.get('status') ?? '')
  const [engine, setEngine] = useState('')
  const [project, setProject] = useState(params.get('project') ?? '')
  const [scan] = useState(params.get('scan') ?? '')
  const [offset, setOffset] = useState(0)
  const [focus, setFocus] = useState<string | null>(params.get('focus'))

  useEffect(() => {
    api.get<{ items: Project[] }>('/api/projects').then((d) => setProjects(d.items)).catch(() => undefined)
  }, [])

  useEffect(() => {
    const timer = window.setTimeout(() => { setQuery(searchInput.trim()); setOffset(0) }, 350)
    return () => window.clearTimeout(timer)
  }, [searchInput])

  const load = () => {
    const qs = new URLSearchParams()
    if (project) qs.set('project_id', project)
    if (scan) qs.set('scan_id', scan)
    if (severity) qs.set('severity', severity)
    if (status) qs.set('status', status)
    if (engine) qs.set('engine', engine)
    if (query) qs.set('q', query)
    qs.set('limit', String(PAGE)); qs.set('offset', String(offset))
    api.get<{ items: Finding[]; total: number; severity: SeverityCounts }>(`/api/findings?${qs}`)
      .then((d) => { setItems(d.items); setTotal(d.total); setCounts(d.severity); setError('') })
      .catch((e) => setError((e as Error).message))
  }

  useEffect(load, [project, scan, severity, status, engine, query, offset])

  useEffect(() => {
    if (!params.get('scan') && !params.get('project')) return
    const next = new URLSearchParams(params)
    next.delete('scan'); next.delete('project')
    setParams(next, { replace: true })
  }, [])

  const exportUrl = useMemo(() => {
    const qs = new URLSearchParams()
    if (project) qs.set('project_id', project)
    if (severity) qs.set('severity', severity)
    if (status) qs.set('status', status)
    return `/api/findings/export.csv?${qs}`
  }, [project, severity, status])

  const clearFilters = () => {
    setProject(''); setSeverity(''); setStatus(''); setEngine(''); setSearchInput(''); setQuery(''); setOffset(0)
  }

  const hasFilters = project || severity || status || engine || query

  return (
    <>
      <PageHeader
        title="Résultats"
        description="Consultez, qualifiez et priorisez les résultats. Chaque fiche conserve sa preuve expurgée, sa remédiation et ses références."
        actions={
          <>
            <a className="btn" href={exportUrl}><Download size={14} /> Export CSV</a>
            {hasFilters && <button className="btn ghost" onClick={clearFilters}><X size={14} /> Réinitialiser</button>}
          </>
        }
      />

      {error && <AlertBox kind="error">{error}</AlertBox>}

      <div className="grid cols-4 mb-2">
        <div className="card stat-card"><div className="stat-label">Total filtré</div><div className="stat-value">{total}</div><div className="stat-foot">résultat(s)</div></div>
        <div className="card stat-card"><div className="stat-label">Critiques</div><div className="stat-value" style={{ color: 'var(--critical)' }}>{counts.critical}</div><div className="stat-foot">à traiter en priorité</div></div>
        <div className="card stat-card"><div className="stat-label">Élevés</div><div className="stat-value" style={{ color: 'var(--high)' }}>{counts.high}</div><div className="stat-foot">revue rapide</div></div>
        <div className="card stat-card"><div className="stat-label">Répartition</div><div style={{ marginTop: 14 }}><SeverityBar counts={counts} showLegend={false} /></div><div className="stat-foot">{counts.medium} moyen(s) · {counts.low} faible(s)</div></div>
      </div>

      <div className="card">
        <div className="card-header" style={{ flexWrap: 'wrap', gap: 10 }}>
          <div className="searchbar" style={{ flex: 1, minWidth: 200 }}>
            <Search size={15} />
            <input className="input" placeholder="Rechercher un titre, une règle, un fichier, une URL…" value={searchInput} onChange={(e) => setSearchInput(e.target.value)} />
          </div>
          <div className="filters">
            <select className="select" value={project} onChange={(e) => { setProject(e.target.value); setOffset(0) }}>
              <option value="">Tous les projets</option>
              {projects.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
            </select>
            <select className="select" value={severity} onChange={(e) => { setSeverity(e.target.value as Severity | ''); setOffset(0) }}>
              <option value="">Toutes gravités</option>
              <option value="critical">Critique</option><option value="high">Élevé</option>
              <option value="medium">Moyen</option><option value="low">Faible</option><option value="info">Info</option>
            </select>
            <select className="select" value={status} onChange={(e) => { setStatus(e.target.value); setOffset(0) }}>
              <option value="">Tous statuts</option>
              <option value="open">Ouvert</option><option value="acknowledged">Pris en compte</option>
              <option value="fixed">Corrigé</option><option value="accepted_risk">Risque accepté</option>
              <option value="false_positive">Faux positif</option>
            </select>
            <select className="select" value={engine} onChange={(e) => { setEngine(e.target.value); setOffset(0) }}>
              <option value="">Tous moteurs</option>
              <option value="php">PHP</option><option value="web">Web</option>
              <option value="api">API</option><option value="checkout">Checkout</option>
            </select>
          </div>
        </div>

        {!items ? <Loading /> : items.length === 0 ? (
          <EmptyState icon={<ClipboardList size={30} />} title={hasFilters ? 'Aucun résultat pour ces filtres' : 'Aucun résultat'} description={hasFilters ? 'Essayez d’élargir les filtres ou de lancer une analyse.' : 'Les résultats des analyses apparaîtront ici.'} action={hasFilters ? <button className="btn sm" onClick={clearFilters}>Réinitialiser les filtres</button> : undefined} />
        ) : (
          <>
            <div className="table-wrap">
              <table className="data">
                <thead><tr><th>Gravité</th><th>Résultat</th><th>Moteur</th><th>Projet</th><th>Emplacement</th><th>Statut</th><th title="Verdict du triage automatique par l’IA locale">IA</th><th>Date</th></tr></thead>
                <tbody>
                  {items.map((f) => (
                    <tr key={f.id} className="clickable" onClick={() => setFocus(f.id)}>
                      <td><SeverityBadge severity={f.severity} /></td>
                      <td style={{ maxWidth: 420 }}>
                        <div className="cell-title clamp-2">{f.title}</div>
                        <div className="cell-sub"><span className="mono">{f.rule_id}</span> · {f.category}</div>
                      </td>
                      <td><span className="tag">{engineLabel(f.engine)}</span></td>
                      <td className="small muted">{f.project_name || '—'}</td>
                      <td className="cell-mono truncate" style={{ maxWidth: 230 }}>{f.file_path || f.url || '—'}{f.line_start ? `:${f.line_start}` : ''}</td>
                      <td><StatusPill status={f.status} /></td>
                      <td>{f.ai_verdict ? <span className={`pill ${f.ai_verdict === "faux positif" ? "" : f.ai_verdict === "vrai positif" ? "failed" : ""}`} title="Triage automatique par l’IA locale">{f.ai_verdict}</span> : <span className="faint tiny">—</span>}</td>
                      <td className="tiny faint">{formatDate(f.created_at, false)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="row between" style={{ padding: '12px 16px', borderTop: '1px solid var(--line-soft)' }}>
              <span className="tiny faint">Affichage {offset + 1}–{Math.min(offset + PAGE, total)} sur {total}</span>
              <div className="row" style={{ gap: 6 }}>
                <button className="btn sm" disabled={offset === 0} onClick={() => setOffset(Math.max(0, offset - PAGE))}>Précédent</button>
                <button className="btn sm" disabled={offset + PAGE >= total} onClick={() => setOffset(offset + PAGE)}>Suivant</button>
              </div>
            </div>
          </>
        )}
      </div>

      <div className="row tiny faint mt-2" style={{ gap: 6 }}>
        <SlidersHorizontal size={12} /> Astuce : filtrez par gravité et statut pour préparer un plan de remédiation.
      </div>

      <FindingDrawer findingId={focus} onClose={() => setFocus(null)} onUpdated={load} />
    </>
  )
}
