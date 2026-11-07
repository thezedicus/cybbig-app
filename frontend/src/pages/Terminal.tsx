import { useEffect, useState } from 'react'
import { ArrowUpRight, Play, Plus, Terminal as TerminalIcon, Trash2 } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { api, formatDate } from '../api'
import { AlertBox, CodeBlock, EmptyState, Loading, Modal, PageHeader, useToast } from '../components/ui'

interface Guardrail {
  id: string
  name: string
  command: string[]
  working_dir: string
  description: string
  enabled: boolean
  created_at: string
}

interface RunResult {
  id: string
  guardrail_id: string
  command: string[]
  working_dir: string
  started_at: string
  finished_at: string
  exit_code: number
  stdout: string
  stderr: string
  status: string
}

export default function TerminalPage() {
  const [items, setItems] = useState<Guardrail[] | null>(null)
  const [runs, setRuns] = useState<RunResult[]>([])
  const [selectedRun, setSelectedRun] = useState<RunResult | null>(null)
  const [error, setError] = useState('')
  const [modal, setModal] = useState(false)
  const [saving, setSaving] = useState(false)
  const [runningId, setRunningId] = useState<string | null>(null)
  const [form, setForm] = useState({ name: '', command: '', working_dir: 'root', description: '', enabled: true })
  const toast = useToast()
  const navigate = useNavigate()

  const load = () => {
    api.get<{ items: Guardrail[] }>('/api/terminal/guardrails')
      .then((d) => { setItems(d.items); setError('') })
      .catch((e) => setError((e as Error).message))
    api.get<{ items: RunResult[] }>('/api/terminal/runs?limit=20')
      .then((d) => setRuns(d.items))
      .catch(() => undefined)
  }

  useEffect(load, [])

  const create = async (event: React.FormEvent) => {
    event.preventDefault()
    const command = form.command.trim().split(/\s+/).filter(Boolean)
    if (!command.length) { toast.push('Commande vide.', 'error'); return }
    setSaving(true)
    try {
      await api.post('/api/terminal/guardrails', {
        name: form.name, command, working_dir: form.working_dir,
        description: form.description, enabled: form.enabled,
      })
      toast.push('Garde-fou enregistré.', 'success')
      setModal(false)
      setForm({ name: '', command: '', working_dir: 'root', description: '', enabled: true })
      load()
    } catch (err) {
      toast.push((err as Error).message, 'error')
    } finally {
      setSaving(false)
    }
  }

  const remove = async (guardrail: Guardrail) => {
    if (!window.confirm(`Supprimer le garde-fou « ${guardrail.name} » ?`)) return
    try {
      await api.del(`/api/terminal/guardrails/${guardrail.id}`)
      toast.push('Garde-fou supprimé.', 'success')
      load()
    } catch (err) {
      toast.push((err as Error).message, 'error')
    }
  }

  const toggle = async (guardrail: Guardrail) => {
    try {
      await api.patch(`/api/terminal/guardrails/${guardrail.id}`, { enabled: !guardrail.enabled })
      load()
    } catch (err) {
      toast.push((err as Error).message, 'error')
    }
  }

  const run = async (guardrail: Guardrail) => {
    setRunningId(guardrail.id)
    try {
      const result = await api.post<RunResult>('/api/terminal/run', { guardrail_id: guardrail.id })
      setSelectedRun(result)
      toast.push(result.status === 'completed' ? 'Exécution terminée.' : `Exécution : ${result.status}`, result.status === 'completed' ? 'success' : 'info')
      load()
    } catch (err) {
      toast.push((err as Error).message, 'error')
    } finally {
      setRunningId(null)
    }
  }

  return (
    <>
      <PageHeader
        title="Terminal interne"
        description="Commandes rapides validées. Le terminal interactif PowerShell, cmd et Python est disponible dans l’espace propriétaire."
        actions={<><button className="btn" onClick={() => navigate('/admin?tab=terminal')}><ArrowUpRight size={14} /> Terminal interactif</button><button className="btn primary" onClick={() => setModal(true)}><Plus size={14} /> Nouvelle commande</button></>}
      />

      {error && <AlertBox kind="error">{error}</AlertBox>}

      <AlertBox kind="info">
        Les commandes rapides utilisent une liste d’exécutables autorisés. Pour exécuter des scripts complets, choisir le répertoire, fournir une entrée standard ou ajuster le délai, ouvrez le terminal interactif propriétaire; les opérations y sont authentifiées et journalisées.
      </AlertBox>

      {!items ? <Loading /> : items.length === 0 ? (
        <div className="card mt-3"><EmptyState icon={<TerminalIcon size={30} />} title="Aucun garde-fou" description="Enregistrez une commande sûre pour commencer." /></div>
      ) : (
        <div className="grid auto mt-3">
          {items.map((guardrail) => (
            <article className="card card-pad" key={guardrail.id}>
              <div className="row" style={{ gap: 8 }}>
                <div className="icon-wrap"><TerminalIcon size={14} /></div>
                <div style={{ minWidth: 0 }}>
                  <div style={{ fontWeight: 650, fontSize: 13.5 }}>{guardrail.name}</div>
                  <div className="tiny faint">{guardrail.working_dir} · {guardrail.command.join(' ')}</div>
                </div>
                <label className="pill" style={{ marginLeft: 'auto', cursor: 'pointer', gap: 5 }}>
                  <input type="checkbox" checked={guardrail.enabled} onChange={() => toggle(guardrail)} style={{ accentColor: 'var(--accent-strong)' }} />
                  {guardrail.enabled ? 'Actif' : 'Inactif'}
                </label>
              </div>
              {guardrail.description && <p className="small muted" style={{ margin: 0 }}>{guardrail.description}</p>}
              <div className="row wrap" style={{ gap: 6, marginTop: 4 }}>
                <button className="btn sm" onClick={() => run(guardrail)} disabled={runningId === guardrail.id || !guardrail.enabled}>
                  <Play size={12} /> {runningId === guardrail.id ? 'Exécution…' : 'Exécuter'}
                </button>
                <button className="icon-btn" style={{ width: 28, height: 28, marginLeft: 'auto' }} onClick={() => remove(guardrail)} title="Supprimer">
                  <Trash2 size={12} />
                </button>
              </div>
            </article>
          ))}
        </div>
      )}

      {selectedRun && (
        <div className="card mt-3">
          <div className="card-header">
            <div>
              <h2>Résultat</h2>
              <div className="sub">{selectedRun.command.join(' ')} · code {selectedRun.exit_code} · {selectedRun.status}</div>
            </div>
            <button className="btn ghost sm" onClick={() => setSelectedRun(null)}>Fermer</button>
          </div>
          <div className="card-pad">
            <div className="kv-list mb-2">
              <div className="kv-item"><span>Répertoire</span><b>{selectedRun.working_dir}</b></div>
              <div className="kv-item"><span>Démarré</span><b>{formatDate(selectedRun.started_at)}</b></div>
              <div className="kv-item"><span>Terminé</span><b>{formatDate(selectedRun.finished_at)}</b></div>
              <div className="kv-item"><span>Statut</span><b>{selectedRun.status}</b></div>
            </div>
            {selectedRun.stdout && <CodeBlock code={selectedRun.stdout} label="stdout" />}
            {selectedRun.stderr && <div className="mt-2"><CodeBlock code={selectedRun.stderr} label="stderr" /></div>}
            {!selectedRun.stdout && !selectedRun.stderr && <div className="small faint">Aucune sortie.</div>}
          </div>
        </div>
      )}

      {runs.length > 0 && (
        <div className="card mt-3">
          <div className="card-header"><div><h2>Historique</h2><div className="sub">20 dernières exécutions</div></div></div>
          <div className="table-wrap">
            <table className="data">
              <thead><tr><th>Date</th><th>Commande</th><th>Statut</th><th>Code</th></tr></thead>
              <tbody>
                {runs.map((run) => (
                  <tr key={run.id} className="clickable" onClick={() => setSelectedRun(run)}>
                    <td className="tiny faint">{formatDate(run.started_at)}</td>
                    <td className="cell-mono">{run.command.join(' ')}</td>
                    <td><span className={`pill ${run.status === 'completed' ? 'completed' : 'failed'}`}>{run.status}</span></td>
                    <td className="mono small">{run.exit_code}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <Modal open={modal} onClose={() => setModal(false)} title="Nouveau garde-fou" subtitle="Commande préenregistrée et validée">
        <form onSubmit={create}>
          <div className="form-grid">
            <div className="field full"><label>Nom *</label><input className="input" required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Tests backend, build frontend…" /></div>
            <div className="field full"><label>Commande (arguments séparés par des espaces) *</label><input className="input" required value={form.command} onChange={(e) => setForm({ ...form, command: e.target.value })} placeholder="python -m pytest -q tests" /><span className="hint">Exécutables autorisés : python, npm, pytest, git, etc. Aucun shell arbitraire.</span></div>
            <div className="field"><label>Répertoire</label><select className="select" value={form.working_dir} onChange={(e) => setForm({ ...form, working_dir: e.target.value })}><option value="root">Racine</option><option value="backend">Backend</option><option value="frontend">Frontend</option></select></div>
            <div className="field full"><label>Description</label><input className="input" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="À quoi sert cette commande" /></div>
            <div className="field full"><label className="checkbox"><input type="checkbox" checked={form.enabled} onChange={(e) => setForm({ ...form, enabled: e.target.checked })} /><span>Activer immédiatement</span></label></div>
          </div>
          <div className="form-actions"><button type="button" className="btn" onClick={() => setModal(false)}>Annuler</button><button className="btn primary" disabled={saving}>{saving ? 'Enregistrement…' : 'Enregistrer'}</button></div>
        </form>
      </Modal>
    </>
  )
}
