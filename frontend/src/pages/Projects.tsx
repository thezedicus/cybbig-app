import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
  Boxes, FolderOpen, Pencil, Plus, Search, ShieldCheck, Trash2, TriangleAlert,
} from 'lucide-react'
import { api, formatDate } from '../api'
import { AlertBox, EmptyState, Loading, Modal, PageHeader, SeverityBar, useToast } from '../components/ui'
import type { Project } from '../types'

const LEVELS = [
  ['A', 'A — Recherche documentaire'],
  ['B', 'B — Simulation locale'],
  ['C', 'C — Infrastructure contrôlée'],
  ['D', 'D — Tiers autorisé'],
  ['E', 'E — Impact potentiel (non implémenté)'],
]

const EMPTY_FORM = {
  name: '', client: '', description: '', path: '', base_url: '', environment: 'laboratory',
  authorization_ref: '', authorized_by: '', authorization_confirmed: false,
  scope_domains: '', scope_paths: '', activity_level: 'B',
}

type FormState = typeof EMPTY_FORM

export default function Projects() {
  const [items, setItems] = useState<Project[] | null>(null)
  const [error, setError] = useState('')
  const [query, setQuery] = useState('')
  const [modal, setModal] = useState<{ open: boolean; project?: Project }>({ open: false })
  const [form, setForm] = useState<FormState>(EMPTY_FORM)
  const [saving, setSaving] = useState(false)
  const [deleteTarget, setDeleteTarget] = useState<Project | null>(null)
  const toast = useToast()
  const navigate = useNavigate()

  const load = () => {
    api.get<{ items: Project[] }>('/api/projects')
      .then((d) => { setItems(d.items); setError('') })
      .catch((e) => setError((e as Error).message))
  }

  useEffect(load, [])

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase()
    if (!items) return []
    if (!q) return items
    return items.filter((p) => `${p.name} ${p.client} ${p.base_url} ${p.path}`.toLowerCase().includes(q))
  }, [items, query])

  const openCreate = () => { setForm(EMPTY_FORM); setModal({ open: true }) }

  const openEdit = (project: Project) => {
    const domains = Array.isArray(project.scope_domains) ? project.scope_domains.join('\n') : String(project.scope_domains || '')
    setForm({
      name: project.name, client: project.client, description: project.description,
      path: project.path, base_url: project.base_url, environment: project.environment,
      authorization_ref: project.authorization_ref, authorized_by: project.authorized_by,
      authorization_confirmed: Boolean(project.authorization_confirmed),
      scope_domains: domains, scope_paths: (project.scope_paths || []).join('\n'),
      activity_level: project.activity_level,
    })
    setModal({ open: true, project })
  }

  const save = async (event: React.FormEvent) => {
    event.preventDefault()
    setSaving(true)
    const payload = {
      ...form,
      scope_domains: form.scope_domains.split(/[\n,;]+/).map((v) => v.trim()).filter(Boolean),
      scope_paths: form.scope_paths.split('\n').map((v) => v.trim()).filter(Boolean),
    }
    try {
      if (modal.project) {
        await api.put(`/api/projects/${modal.project.id}`, payload)
        toast.push('Projet mis à jour.', 'success')
      } else {
        const created = await api.post<Project>('/api/projects', payload)
        toast.push('Projet créé.', 'success')
        setModal({ open: false })
        navigate(`/projects/${created.id}`)
        return
      }
      setModal({ open: false })
      load()
    } catch (err) {
      toast.push((err as Error).message, 'error')
    } finally {
      setSaving(false)
    }
  }

  const remove = async () => {
    if (!deleteTarget) return
    try {
      await api.del(`/api/projects/${deleteTarget.id}`)
      toast.push('Projet supprimé.', 'success')
      setDeleteTarget(null)
      load()
    } catch (err) {
      toast.push((err as Error).message, 'error')
    }
  }

  return (
    <>
      <PageHeader
        title="Projets & périmètres"
        description="Chaque analyse est rattachée à un périmètre autorisé. Les cibles distantes exigent une référence d’autorisation et le niveau D."
        actions={<button className="btn primary" onClick={openCreate}><Plus size={15} /> Nouveau projet</button>}
      />

      {error && <AlertBox kind="error">{error}</AlertBox>}

      <div className="card mb-2">
        <div className="card-header">
          <div className="searchbar" style={{ flex: 1, maxWidth: 460 }}>
            <Search size={15} />
            <input className="input" placeholder="Rechercher un projet, un client, une URL…" value={query} onChange={(e) => setQuery(e.target.value)} />
          </div>
          <div className="right"><span className="tag">{filtered.length} projet(s)</span></div>
        </div>
        {!items ? <Loading /> : filtered.length === 0 ? (
          <EmptyState
            icon={<Boxes size={30} />}
            title={items.length === 0 ? 'Aucun projet pour le moment' : 'Aucun projet ne correspond'}
            description={items.length === 0 ? 'Créez un projet pour définir le périmètre, les autorisations et les cibles.' : 'Modifiez votre recherche.'}
            action={<button className="btn primary sm" onClick={openCreate}><Plus size={14} /> Créer un projet</button>}
          />
        ) : (
          <div className="table-wrap">
            <table className="data">
              <thead>
                <tr><th>Projet</th><th>Client</th><th>Environnement</th><th>Activité</th><th>Résultats</th><th>Risque</th><th>Dernière analyse</th><th></th></tr>
              </thead>
              <tbody>
                {filtered.map((p) => (
                  <tr key={p.id} className="clickable" onClick={() => navigate(`/projects/${p.id}`)}>
                    <td>
                      <div className="cell-title">{p.name}</div>
                      <div className="cell-sub cell-mono truncate" style={{ maxWidth: 300 }}>{p.base_url || p.path || '—'}</div>
                    </td>
                    <td className="small">{p.client || '—'}</td>
                    <td><span className="tag">{p.environment}</span></td>
                    <td><span className="pill">Niveau {p.activity_level}</span></td>
                    <td>
                      <div className="row" style={{ gap: 6 }}>
                        <span className="mono">{p.open_findings}</span>
                        <span className="tiny faint">/ {p.findings_count}</span>
                      </div>
                      <div style={{ minWidth: 90, marginTop: 4 }}><SeverityBar counts={p.severity} showLegend={false} /></div>
                    </td>
                    <td>
                      <b style={{ color: p.risk_score >= 70 ? 'var(--critical)' : p.risk_score >= 40 ? 'var(--high)' : 'var(--green)' }}>{p.risk_score.toFixed(0)}</b>
                      <span className="tiny faint">/100</span>
                    </td>
                    <td className="small faint">{p.last_scan ? formatDate(p.last_scan.created_at) : '—'}</td>
                    <td onClick={(e) => e.stopPropagation()}>
                      <div className="row" style={{ gap: 2 }}>
                        <button className="icon-btn" style={{ width: 28, height: 28 }} onClick={() => openEdit(p)} title="Modifier"><Pencil size={13} /></button>
                        <button className="icon-btn" style={{ width: 28, height: 28 }} onClick={() => setDeleteTarget(p)} title="Supprimer"><Trash2 size={13} /></button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="grid cols-2">
        <div className="card card-pad">
          <div className="row" style={{ gap: 9 }}><ShieldCheck size={17} color="var(--accent)" /><b>Garde-fous appliqués</b></div>
          <p className="small muted mt-1" style={{ marginBottom: 0 }}>
            Les domaines hors périmètre sont refusés au lancement et revalidés à l’exécution. Le consentement logiciel ne remplace pas une autorisation écrite.
          </p>
        </div>
        <div className="card card-pad">
          <div className="row" style={{ gap: 9 }}><FolderOpen size={17} color="var(--accent)" /><b>Chemins locaux</b></div>
          <p className="small muted mt-1" style={{ marginBottom: 0 }}>
            Le scanner PHP lit uniquement le dossier déclaré, sans exécuter le code. Les dossiers système et le profil utilisateur entier sont exclus.
          </p>
        </div>
      </div>

      <Modal open={modal.open} onClose={() => setModal({ open: false })} title={modal.project ? 'Modifier le projet' : 'Nouveau projet'} subtitle="Périmètre, autorisation et cibles" size="wide">
        <form onSubmit={save}>
          <div className="form-grid">
            <div className="field"><label>Nom du projet *</label><input className="input" required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Boutique, API publique, application interne…" /></div>
            <div className="field"><label>Client / organisation</label><input className="input" value={form.client} onChange={(e) => setForm({ ...form, client: e.target.value })} placeholder="Interne, client, laboratoire" /></div>
            <div className="field full"><label>Description</label><textarea className="textarea" style={{ minHeight: 70 }} value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="Contexte, périmètre fonctionnel, exclusions…" /></div>
            <div className="field"><label>Dossier local (code PHP)</label><input className="input" value={form.path} onChange={(e) => setForm({ ...form, path: e.target.value })} placeholder="C:\\Projets\\mon-site" /></div>
            <div className="field"><label>URL de base</label><input className="input" value={form.base_url} onChange={(e) => setForm({ ...form, base_url: e.target.value })} placeholder="https://staging.exemple.fr" /></div>
            <div className="field"><label>Environnement</label><select className="select" value={form.environment} onChange={(e) => setForm({ ...form, environment: e.target.value })}><option value="laboratory">Laboratoire</option><option value="staging">Préproduction</option><option value="production">Production autorisée</option><option value="development">Développement</option></select></div>
            <div className="field"><label>Niveau d’activité</label><select className="select" value={form.activity_level} onChange={(e) => setForm({ ...form, activity_level: e.target.value })}>{LEVELS.map(([v, l]) => <option key={v} value={v}>{l}</option>)}</select><span className="hint">Les cibles distantes exigent le niveau D.</span></div>
            <div className="field"><label>Domaines autorisés</label><textarea className="textarea" style={{ minHeight: 68 }} value={form.scope_domains} onChange={(e) => setForm({ ...form, scope_domains: e.target.value })} placeholder={'staging.exemple.fr\napi.exemple.fr'} /><span className="hint">Un domaine par ligne. Les sous-domaines sont couverts.</span></div>
            <div className="field"><label>Chemins autorisés</label><textarea className="textarea" style={{ minHeight: 68 }} value={form.scope_paths} onChange={(e) => setForm({ ...form, scope_paths: e.target.value })} placeholder="C:\\Projets\\mon-site" /><span className="hint">Un chemin par ligne, indicatif pour la traçabilité.</span></div>
            <div className="field"><label>Référence d’autorisation</label><input className="input" value={form.authorization_ref} onChange={(e) => setForm({ ...form, authorization_ref: e.target.value })} placeholder="Contrat, ticket, e-mail, référence interne" /></div>
            <div className="field"><label>Autorisé par</label><input className="input" value={form.authorized_by} onChange={(e) => setForm({ ...form, authorized_by: e.target.value })} placeholder="Nom et fonction" /></div>
            <div className="field full">
              <label className="checkbox">
                <input type="checkbox" checked={form.authorization_confirmed} onChange={(e) => setForm({ ...form, authorization_confirmed: e.target.checked })} />
                <span>Je confirme disposer de l’autorisation nécessaire pour ce périmètre. Les scans resteront passifs et sans exploitation.</span>
              </label>
            </div>
          </div>
          <div className="form-actions">
            <button type="button" className="btn" onClick={() => setModal({ open: false })}>Annuler</button>
            <button type="submit" className="btn primary" disabled={saving}>{saving ? 'Enregistrement…' : modal.project ? 'Enregistrer' : 'Créer le projet'}</button>
          </div>
        </form>
      </Modal>

      <Modal open={Boolean(deleteTarget)} onClose={() => setDeleteTarget(null)} title="Supprimer le projet ?" size="narrow">
        <div className="alert-banner error"><TriangleAlert size={16} /><div>Les analyses, résultats et rapports liés à <b>{deleteTarget?.name}</b> seront également supprimés. Cette action est irréversible.</div></div>
        <div className="form-actions">
          <button className="btn" onClick={() => setDeleteTarget(null)}>Annuler</button>
          <button className="btn danger" onClick={remove}>Supprimer définitivement</button>
        </div>
      </Modal>
    </>
  )
}
