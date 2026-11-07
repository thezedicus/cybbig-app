import { useEffect, useMemo, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import {
  Activity, CheckCircle2, Clock3, Filter, Play, Plus, RefreshCw, ScanLine, Search, ShieldQuestion, XCircle,
} from 'lucide-react'
import { api, formatDate, scanLabel } from '../api'
import { AlertBox, EmptyState, Loading, Modal, PageHeader, Progress, StatusPill, useToast } from '../components/ui'
import type { Project, Scan, ScanKind } from '../types'

const KIND_OPTIONS: Array<{ value: ScanKind; label: string; description: string }> = [
  { value: 'php', label: 'Analyse PHP', description: 'Statique : règles, taint heuristique, secrets, configuration, Composer/OSV.' },
  { value: 'web', label: 'Analyse Web passive', description: 'En-têtes, TLS, cookies, formulaires, scripts, fichiers exposés.' },
  { value: 'api', label: 'Audit API OpenAPI', description: 'Contrat : authentification, BOLA (revue), idempotence, transport.' },
  { value: 'checkout', label: 'Intégrité checkout', description: 'Scripts, SRI, SVG, WebSocket, indicateurs de skimmer.' },
]

export default function Scans() {
  const [items, setItems] = useState<Scan[] | null>(null)
  const [projects, setProjects] = useState<Project[]>([])
  const [error, setError] = useState('')
  const [projectFilter, setProjectFilter] = useState('')
  const [kindFilter, setKindFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [search, setSearch] = useState('')
  const [launch, setLaunch] = useState(false)
  const [params, setParams] = useSearchParams()
  const navigate = useNavigate()
  const toast = useToast()

  const [form, setForm] = useState({
    project_id: '', kind: 'php' as ScanKind, target: '', max_files: 2500,
    max_exposed_paths: 12, probe_exposed_files: true,
  })
  const [submitting, setSubmitting] = useState(false)

  const load = () => {
    const query = new URLSearchParams()
    if (projectFilter) query.set('project_id', projectFilter)
    if (kindFilter) query.set('kind', kindFilter)
    if (statusFilter) query.set('status', statusFilter)
    query.set('limit', '200')
    api.get<{ items: Scan[] }>(`/api/scans?${query}`)
      .then((d) => { setItems(d.items); setError('') })
      .catch((e) => setError((e as Error).message))
  }

  useEffect(() => {
    api.get<{ items: Project[] }>('/api/projects').then((d) => setProjects(d.items)).catch(() => undefined)
  }, [])

  useEffect(load, [projectFilter, kindFilter, statusFilter])

  useEffect(() => {
    if (!items?.some((s) => s.status === 'queued' || s.status === 'running')) return
    const timer = window.setInterval(load, 2500)
    return () => window.clearInterval(timer)
  }, [items, projectFilter, kindFilter, statusFilter])

  useEffect(() => {
    if (params.get('launch') !== '1') return
    const projectId = params.get('project') || projects[0]?.id || ''
    setForm((current) => ({ ...current, project_id: projectId, kind: (params.get('kind') as ScanKind) || 'php' }))
    setLaunch(true)
  }, [params, projects])

  const filtered = useMemo(() => {
    if (!items) return []
    const q = search.trim().toLowerCase()
    if (!q) return items
    return items.filter((s) => `${s.id} ${s.target} ${s.project?.name} ${s.message}`.toLowerCase().includes(q))
  }, [items, search])

  const selectedProject = projects.find((p) => p.id === form.project_id)

  const openLaunch = (projectId = '') => {
    setForm({ project_id: projectId || projects[0]?.id || '', kind: 'php', target: '', max_files: 2500, max_exposed_paths: 12, probe_exposed_files: true })
    setLaunch(true)
  }

  const closeLaunch = () => {
    setLaunch(false)
    if (params.get('launch')) {
      const next = new URLSearchParams(params)
      next.delete('launch'); next.delete('project'); next.delete('kind')
      setParams(next, { replace: true })
    }
  }

  const submit = async (event: React.FormEvent) => {
    event.preventDefault()
    if (!form.project_id) { toast.push('Sélectionnez un projet.', 'error'); return }
    setSubmitting(true)
    try {
      const config: Record<string, unknown> = {}
      if (form.kind === 'php') config.max_files = form.max_files
      if (form.kind === 'web' || form.kind === 'checkout') {
        config.max_exposed_paths = form.max_exposed_paths
        config.probe_exposed_files = form.probe_exposed_files
      }
      const scan = await api.post<Scan>('/api/scans', {
        project_id: form.project_id, kind: form.kind, target: form.target, config,
      })
      toast.push('Analyse lancée.', 'success')
      closeLaunch()
      navigate(`/scans/${scan.id}`)
    } catch (err) {
      toast.push((err as Error).message, 'error')
    } finally {
      setSubmitting(false)
    }
  }

  const counts = {
    running: items?.filter((s) => s.status === 'running').length ?? 0,
    queued: items?.filter((s) => s.status === 'queued').length ?? 0,
    completed: items?.filter((s) => s.status === 'completed').length ?? 0,
  }

  return (
    <>
      <PageHeader
        title="Analyses"
        description="Lancez et suivez les moteurs PHP, Web, API et checkout. Toutes les analyses sont passives ou statiques."
        actions={<button className="btn primary" onClick={() => openLaunch()}><Plus size={15} /> Nouvelle analyse</button>}
      />

      {error && <AlertBox kind="error">{error}</AlertBox>}

      <div className="grid cols-3 mb-2">
        <div className="card card-pad"><div className="stat-label"><RefreshCw size={13} /> En cours</div><div className="stat-value">{counts.running}</div><div className="stat-foot">{counts.queued} en attente</div></div>
        <div className="card card-pad"><div className="stat-label"><CheckCircle2 size={13} /> Terminées</div><div className="stat-value">{counts.completed}</div><div className="stat-foot">sur {items?.length ?? 0} analyses affichées</div></div>
        <div className="card card-pad"><div className="stat-label"><ShieldQuestion size={13} /> Périmètre</div><div className="stat-value" style={{ fontSize: 19, paddingTop: 7 }}>Revalidé à l’exécution</div><div className="stat-foot">Consentement + autorisation + domaines</div></div>
      </div>

      <div className="card">
        <div className="card-header" style={{ flexWrap: 'wrap', gap: 10 }}>
          <div className="searchbar" style={{ flex: 1, minWidth: 220 }}>
            <Search size={15} />
            <input className="input" placeholder="Rechercher une analyse, une cible…" value={search} onChange={(e) => setSearch(e.target.value)} />
          </div>
          <div className="filters">
            <select className="select" value={projectFilter} onChange={(e) => setProjectFilter(e.target.value)}>
              <option value="">Tous les projets</option>
              {projects.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
            </select>
            <select className="select" value={kindFilter} onChange={(e) => setKindFilter(e.target.value)}>
              <option value="">Tous les types</option>
              {KIND_OPTIONS.map((k) => <option key={k.value} value={k.value}>{k.label}</option>)}
            </select>
            <select className="select" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
              <option value="">Tous les statuts</option>
              <option value="queued">En attente</option><option value="running">En cours</option>
              <option value="completed">Terminées</option><option value="failed">Échecs</option>
              <option value="blocked">Bloquées</option><option value="cancelled">Annulées</option>
            </select>
            <button className="icon-btn" onClick={load} title="Rafraîchir"><RefreshCw size={14} /></button>
          </div>
        </div>

        {!items ? <Loading /> : filtered.length === 0 ? (
          <EmptyState icon={<Activity size={30} />} title="Aucune analyse" description="Lancez une première analyse sur un projet autorisé." action={<button className="btn primary sm" onClick={() => openLaunch()}><Play size={14} /> Lancer une analyse</button>} />
        ) : (
          <div className="table-wrap">
            <table className="data">
              <thead><tr><th>Type</th><th>Projet</th><th>Cible</th><th>Statut</th><th>Progression</th><th>Résultats</th><th>Date</th></tr></thead>
              <tbody>
                {filtered.map((s) => (
                  <tr key={s.id} className="clickable" onClick={() => navigate(`/scans/${s.id}`)}>
                    <td><span className="tag">{scanLabel(s.kind)}</span></td>
                    <td className="small">{s.project?.name || '—'}</td>
                    <td className="cell-mono truncate" style={{ maxWidth: 260 }}>{s.target || '—'}</td>
                    <td><StatusPill status={s.status} /></td>
                    <td style={{ minWidth: 110 }}>
                      <Progress value={s.status === 'completed' ? 100 : s.progress} />
                      <div className="tiny faint" style={{ marginTop: 3 }}>{s.status === 'completed' ? 100 : s.progress}% · {s.message || '—'}</div>
                    </td>
                    <td className="mono">{s.summary?.findings ?? '—'}</td>
                    <td className="tiny faint">{formatDate(s.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <Modal open={launch} onClose={closeLaunch} title="Nouvelle analyse" subtitle="Le périmètre est vérifié avant et pendant l’exécution" size="wide">
        <form onSubmit={submit}>
          <div className="form-grid">
            <div className="field">
              <label>Projet *</label>
              <select className="select" value={form.project_id} onChange={(e) => setForm({ ...form, project_id: e.target.value })} required>
                <option value="">Sélectionner…</option>
                {projects.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
              </select>
            </div>
            <div className="field">
              <label>Type d’analyse *</label>
              <select className="select" value={form.kind} onChange={(e) => setForm({ ...form, kind: e.target.value as ScanKind })}>
                {KIND_OPTIONS.map((k) => <option key={k.value} value={k.value}>{k.label}</option>)}
              </select>
            </div>
            <div className="field full">
              <label>Cible (facultatif)</label>
              <input className="input" value={form.target} onChange={(e) => setForm({ ...form, target: e.target.value })}
                placeholder={form.kind === 'php' ? (selectedProject?.path || 'Le dossier du projet sera utilisé') : form.kind === 'api' ? 'https://exemple.fr/openapi.json ou fichier du projet' : (selectedProject?.base_url || 'https://exemple.fr')} />
              <span className="hint">
                {form.kind === 'php' ? 'Le chemin du projet est utilisé. Le code n’est jamais exécuté.' :
                  form.kind === 'api' ? 'Laissez vide pour résoudre /openapi.json sur l’URL de base du projet.' :
                    'Laissez vide pour utiliser l’URL de base du projet.'}
              </span>
            </div>
            {form.kind === 'php' && (
              <div className="field"><label>Nombre maximal de fichiers</label><input type="number" min={1} max={10000} className="input" value={form.max_files} onChange={(e) => setForm({ ...form, max_files: Number(e.target.value) })} /><span className="hint">Plafonné à 10 000 par le backend.</span></div>
            )}
            {(form.kind === 'web' || form.kind === 'checkout') && (
              <>
                <div className="field"><label>Chemins exposés à tester</label><input type="number" min={0} max={24} className="input" value={form.max_exposed_paths} onChange={(e) => setForm({ ...form, max_exposed_paths: Number(e.target.value) })} /><span className="hint">GET tronqués, contenu non conservé.</span></div>
                <div className="field"><label className="checkbox"><input type="checkbox" checked={form.probe_exposed_files} onChange={(e) => setForm({ ...form, probe_exposed_files: e.target.checked })} /><span>Vérifier les fichiers sensibles exposés</span></label></div>
              </>
            )}
            <div className="field full">
              <div className="alert-banner info"><CheckCircle2 size={15} /><div>L’analyse est passive : aucune exploitation, aucune mutation, aucun contournement d’authentification. Les cibles distantes nécessitent un projet de niveau D avec référence d’autorisation.</div></div>
            </div>
          </div>
          <div className="form-actions">
            <button type="button" className="btn" onClick={closeLaunch}>Annuler</button>
            <button type="submit" className="btn primary" disabled={submitting}>{submitting ? 'Lancement…' : <><Play size={14} /> Lancer l’analyse</>}</button>
          </div>
        </form>
      </Modal>
    </>
  )
}
