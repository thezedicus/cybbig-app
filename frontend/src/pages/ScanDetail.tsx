import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import {
  AlertTriangle, ArrowLeft, Ban, CheckCircle2, Clock3, Download, ExternalLink,
  FileText, GitBranch, Play, RefreshCw, ShieldCheck, XCircle,
} from 'lucide-react'
import { api, engineLabel, formatDate, scanLabel } from '../api'
import AiPanel from '../components/AiPanel'
import FindingDrawer from '../components/FindingDrawer'
import {
  AlertBox, CodeBlock, EmptyState, Loading, PageHeader, Progress, SeverityBadge,
  SeverityBar, StatusPill, useToast,
} from '../components/ui'
import type { Scan } from '../types'

const EXTRA_LABELS: Record<string, string> = {
  files_scanned: 'Fichiers PHP analysés', config_files: 'Fichiers de configuration', manifest_files: 'Manifestes',
  visited: 'Fichiers parcourus', root: 'Racine analysée', php_requirement: 'Version PHP déclarée',
  dependency_audit: 'Audit OSV', dependency_audit_warning: 'Avertissement OSV',
  final_url: 'URL finale', mode: 'Mode', file: 'Fichier', title: 'Titre de page', source: 'Source',
  version: 'Version', operation_count: 'Opérations', financial_operations: 'Opérations financières',
  unauthenticated_operations: 'Opérations sans auth.', spec_version: 'Version de spécification',
  has_card_fields: 'Champs carte détectés', checkout_context: 'Contexte checkout', scanned_at: 'Analysé le',
  status: 'Statut HTTP', elapsed_ms: 'Temps de réponse (ms)', generator: 'Générateur',
}

export default function ScanDetail() {
  const { id = '' } = useParams()
  const [scan, setScan] = useState<Scan | null>(null)
  const [error, setError] = useState('')
  const [focus, setFocus] = useState<string | null>(null)
  const [reportUrl, setReportUrl] = useState('')
  const [busy, setBusy] = useState(false)
  const toast = useToast()
  const navigate = useNavigate()

  const load = useCallback(() => {
    api.get<Scan>(`/api/scans/${id}`)
      .then((d) => { setScan(d); setError('') })
      .catch((e) => setError((e as Error).message))
  }, [id])

  useEffect(() => { load() }, [load])

  useEffect(() => {
    if (!scan) return
    if (!['queued', 'running'].includes(scan.status)) return
    const timer = window.setInterval(load, 1800)
    return () => window.clearInterval(timer)
  }, [scan, load])

  const extra = useMemo(() => {
    const raw = (scan?.summary?.extra ?? {}) as Record<string, unknown>
    return Object.entries(raw).filter(([key, value]) =>
      key in EXTRA_LABELS && (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean'))
  }, [scan])

  if (error) return <AlertBox kind="error">{error}</AlertBox>
  if (!scan) return <Loading label="Chargement de l’analyse…" />

  const findings = scan.findings ?? []
  const counts = scan.severity ?? { critical: 0, high: 0, medium: 0, low: 0, info: 0 }
  const active = scan.status === 'queued' || scan.status === 'running'

  const cancel = async () => {
    if (!window.confirm('Annuler cette analyse ?')) return
    try {
      await api.post(`/api/scans/${scan.id}/cancel`)
      toast.push('Annulation demandée.', 'info')
      load()
    } catch (err) {
      toast.push((err as Error).message, 'error')
    }
  }

  const rerun = async () => {
    setBusy(true)
    try {
      const created = await api.post<Scan>(`/api/scans/${scan.id}/rerun`)
      toast.push('Analyse relancée.', 'success')
      navigate(`/scans/${created.id}`)
    } catch (err) {
      toast.push((err as Error).message, 'error')
    } finally {
      setBusy(false)
    }
  }

  const makeReport = async () => {
    setBusy(true)
    try {
      const report = await api.post<{ download_url: string }>('/api/reports', { project_id: scan.project_id, scan_id: scan.id })
      setReportUrl(report.download_url)
      toast.push('Rapport HTML généré.', 'success')
    } catch (err) {
      toast.push((err as Error).message, 'error')
    } finally {
      setBusy(false)
    }
  }

  return (
    <>
      <PageHeader
        title={`Analyse ${scanLabel(scan.kind)}`}
        description={`${scan.project?.name || 'Projet'} · ${scan.target || '—'} · ${formatDate(scan.created_at)}`}
        actions={
          <>
            <button className="btn ghost" onClick={() => navigate('/scans')}><ArrowLeft size={14} /> Analyses</button>
            <button className="btn" onClick={load} title="Rafraîchir"><RefreshCw size={14} /></button>
            {active ? <button className="btn danger" onClick={cancel}><Ban size={14} /> Annuler</button>
              : <button className="btn" onClick={rerun} disabled={busy}><Play size={14} /> Relancer</button>}
            <button className="btn primary" onClick={makeReport} disabled={busy}><FileText size={14} /> Générer un rapport</button>
          </>
        }
      />

      {reportUrl && (
        <div className="alert-banner info mb-2">
          <CheckCircle2 size={15} />
          <div>Rapport prêt. <a href={reportUrl} target="_blank" rel="noreferrer">Ouvrir le rapport HTML <ExternalLink size={11} /></a></div>
        </div>
      )}

      {scan.status === 'failed' && (
        <div className="alert-banner error mb-2"><XCircle size={16} /><div><b>Échec :</b> {scan.error || scan.message}</div></div>
      )}
      {scan.status === 'blocked' && (
        <div className="alert-banner error mb-2"><ShieldCheck size={16} /><div><b>Bloquée par le périmètre :</b> {scan.error || scan.message}</div></div>
      )}

      {scan.status === 'completed' && (
        <div className="mb-2">
          <AiPanel key={scan.id} task="scan_summary" params={{ scan_id: scan.id }} cacheKey={`scan:${scan.id}`} title="Synthèse de l’analyse (IA)" label="Résumer cette analyse" />
        </div>
      )}

      <div className="grid cols-5 mb-2">
        <div className="card stat-card"><div className="stat-label">Statut</div><div style={{ marginTop: 9 }}><StatusPill status={scan.status} /></div><div className="stat-foot">{scan.progress}%</div></div>
        <div className="card stat-card"><div className="stat-label">Résultats</div><div className="stat-value">{scan.summary?.findings ?? findings.length}</div><div className="stat-foot">{counts.critical} critique(s)</div></div>
        <div className="card stat-card"><div className="stat-label">Risque</div><div className="stat-value">{Number(scan.summary?.risk_score ?? 0).toFixed(1)}<span style={{ fontSize: 12, color: 'var(--faint)' }}>/100</span></div><div className="stat-foot">indice pondéré</div></div>
        <div className="card stat-card"><div className="stat-label">Dépendances</div><div className="stat-value">{scan.summary?.dependencies ?? scan.dependencies?.length ?? 0}</div><div className="stat-foot">{scan.summary?.vulnerable_dependencies ?? 0} vulnérable(s)</div></div>
        <div className="card stat-card"><div className="stat-label">Durée</div><div className="stat-value" style={{ fontSize: 20 }}>{duration(scan.started_at, scan.finished_at)}</div><div className="stat-foot">{scan.finished_at ? formatDate(scan.finished_at) : 'en cours'}</div></div>
      </div>

      {active && (
        <div className="card card-pad mb-2">
          <div className="row between"><span className="small"><Clock3 size={13} /> {scan.message || 'Analyse en cours…'}</span><span className="mono small">{scan.progress}%</span></div>
          <div className="mt-2"><Progress value={scan.progress} /></div>
        </div>
      )}

      <div className="detail-layout">
        <div className="stack" style={{ gap: 14 }}>
          <div className="card">
            <div className="card-header">
              <div><h2>Résultats ({findings.length})</h2><div className="sub">Cliquez une ligne pour ouvrir la fiche complète</div></div>
              <div className="right"><Link className="btn ghost sm" to={`/findings?scan=${scan.id}`}>Filtrer</Link></div>
            </div>
            {findings.length === 0 ? (
              <EmptyState icon={<ShieldCheck size={28} />} title={active ? 'Analyse en cours…' : 'Aucun résultat'} description={active ? 'Les résultats apparaîtront à la fin de l’analyse.' : 'Aucun écart n’a été détecté sur ce périmètre, ou le moteur n’a produit aucun résultat.'} />
            ) : (
              <div className="table-wrap">
                <table className="data">
                  <thead><tr><th>Gravité</th><th>Résultat</th><th>Moteur</th><th>Emplacement</th><th>Statut</th></tr></thead>
                  <tbody>
                    {findings.map((f) => (
                      <tr key={f.id} className="clickable" onClick={() => setFocus(f.id)}>
                        <td><SeverityBadge severity={f.severity} /></td>
                        <td><div className="cell-title clamp-2">{f.title}</div><div className="cell-sub">{f.category}</div></td>
                        <td><span className="tag">{engineLabel(f.engine)}</span></td>
                        <td className="cell-mono truncate" style={{ maxWidth: 240 }}>{f.file_path || f.url || '—'}{f.line_start ? `:${f.line_start}` : ''}</td>
                        <td><StatusPill status={f.status} /></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {scan.dependencies && scan.dependencies.length > 0 && (
            <div className="card">
              <div className="card-header"><div><h2>Dépendances</h2><div className="sub">Composer / OSV</div></div></div>
              <div className="table-wrap">
                <table className="data">
                  <thead><tr><th>Paquet</th><th>Version</th><th>Vulnérable</th><th>ID</th><th>Corrigé en</th></tr></thead>
                  <tbody>
                    {scan.dependencies.map((d) => (
                      <tr key={d.id}>
                        <td className="cell-mono">{d.package}</td>
                        <td className="mono">{d.version}</td>
                        <td>{d.vulnerable ? <span className="badge high">Oui</span> : <span className="badge info">Non</span>}</td>
                        <td className="cell-mono">{d.vuln_id || '—'}</td>
                        <td className="mono">{d.fixed_version || '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          <div className="card">
            <div className="card-header"><div><h2>Détails techniques</h2><div className="sub">Données normalisées du moteur</div></div></div>
            <div className="card-pad">
              <CodeBlock label="summary.extra" code={JSON.stringify(scan.summary?.extra ?? {}, null, 2)} />
            </div>
          </div>
        </div>

        <div className="stack" style={{ gap: 14 }}>
          <div className="card">
            <div className="card-header"><h2>Synthèse</h2></div>
            <div className="card-pad" style={{ paddingTop: 6 }}>
              <SeverityBar counts={counts} />
            </div>
          </div>

          <div className="card">
            <div className="card-header"><h2>Contexte</h2></div>
            <div className="card-pad" style={{ paddingTop: 4 }}>
              <div className="kv-list">
                <div className="kv-item"><span>Projet</span><b><Link to={`/projects/${scan.project_id}`}>{scan.project?.name || scan.project_id}</Link></b></div>
                <div className="kv-item"><span>Type</span><b>{scanLabel(scan.kind)}</b></div>
                <div className="kv-item"><span>Mode</span><b>{scan.mode} · sans exploit</b></div>
                <div className="kv-item"><span>Cible</span><b className="mono" style={{ fontSize: 10.5 }}>{scan.target || '—'}</b></div>
                <div className="kv-item"><span>Démarrée</span><b>{formatDate(scan.started_at || scan.created_at)}</b></div>
                <div className="kv-item"><span>Terminée</span><b>{formatDate(scan.finished_at)}</b></div>
                <div className="kv-item"><span>ID</span><b className="mono" style={{ fontSize: 10 }}>{scan.id}</b></div>
              </div>
            </div>
          </div>

          {extra.length > 0 && (
            <div className="card">
              <div className="card-header"><h2>Indicateurs</h2></div>
              <div className="card-pad" style={{ paddingTop: 4 }}>
                <div className="kv-list">
                  {extra.map(([key, value]) => (
                    <div className="kv-item" key={key}><span>{EXTRA_LABELS[key]}</span><b className={key === 'final_url' || key === 'root' || key === 'file' ? 'mono' : ''} style={{ fontSize: key === 'final_url' || key === 'root' ? 10.5 : undefined }}>{String(value)}</b></div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {Boolean((scan.summary?.extra as Record<string, unknown>)?.warnings) && (
            <div className="alert-banner"><AlertTriangle size={15} /><div className="small">{JSON.stringify((scan.summary?.extra as Record<string, unknown>).warnings)}</div></div>
          )}

          {(() => {
            const content = ((scan.summary?.extra as Record<string, unknown> | undefined)?.content ?? null) as Record<string, unknown> | null
            if (!content) return null
            const markdown = typeof content.markdown_excerpt === 'string' ? content.markdown_excerpt : ''
            const securityTxt = content.security_txt as { url?: string; content?: string } | undefined
            return (
              <div className="card">
                <div className="card-header"><h2>Extraction de contenu</h2><div className="sub">Lecture passive de la page et de ses métadonnées</div></div>
                <div className="card-pad">
                  <div className="kv-list">
                    <div className="kv-item"><span>Mots extraits</span><b>{String(content.word_count ?? '—')}</b></div>
                    <div className="kv-item"><span>Liens internes / externes</span><b>{String(content.internal_links ?? 0)} / {String(content.external_links ?? 0)}</b></div>
                    <div className="kv-item"><span>Titres détectés</span><b>{Array.isArray(content.headings) ? content.headings.length : 0}</b></div>
                    <div className="kv-item"><span>Candidats d’API</span><b>{Array.isArray(content.api_candidates) ? content.api_candidates.length : 0}</b></div>
                  </div>
                  {markdown && <div className="mt-3"><CodeBlock code={markdown} label="Extrait Markdown" /></div>}
                  {securityTxt?.content && <div className="mt-3"><CodeBlock code={securityTxt.content} label={`security.txt — ${securityTxt.url ?? ''}`} /></div>}
                </div>
              </div>
            )
          })()}

          <div className="card card-pad">
            <div className="row" style={{ gap: 8 }}><GitBranch size={14} color="var(--accent)" /><b className="small">Traçabilité</b></div>
            <p className="tiny faint mt-1" style={{ marginBottom: 0 }}>Le périmètre a été revalidé au démarrage du moteur. Les preuves sont expurgées et conservées localement.</p>
          </div>
        </div>
      </div>

      <FindingDrawer findingId={focus} onClose={() => setFocus(null)} onUpdated={load} />
    </>
  )
}

function duration(start?: string | null, end?: string | null): string {
  if (!start || !end) return '—'
  const ms = new Date(end).getTime() - new Date(start).getTime()
  if (Number.isNaN(ms) || ms < 0) return '—'
  if (ms < 1000) return `${ms} ms`
  if (ms < 60000) return `${(ms / 1000).toFixed(1)} s`
  return `${Math.floor(ms / 60000)} min ${Math.round((ms % 60000) / 1000)} s`
}
