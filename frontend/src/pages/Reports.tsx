import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import {
  Download, ExternalLink, FileDown, FileJson, FileText, Plus, Sparkles, Trash2,
} from 'lucide-react'
import { api, formatDate, scanLabel } from '../api'
import {
  AlertBox, EmptyState, Loading, Modal, PageHeader, useToast,
} from '../components/ui'
import type { Project, Report, Scan } from '../types'

export default function Reports() {
  const [params] = useSearchParams()
  const [items, setItems] = useState<Report[] | null>(null)
  const [projects, setProjects] = useState<Project[]>([])
  const [scans, setScans] = useState<Scan[]>([])
  const [projectFilter, setProjectFilter] = useState(params.get('project') ?? '')
  const [error, setError] = useState('')
  const [modal, setModal] = useState(false)
  const [form, setForm] = useState({ project_id: params.get('project') ?? '', scan_id: '', title: '', ai_summary: true })
  const [pdfId, setPdfId] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)
  const toast = useToast()

  const load = () => {
    const qs = projectFilter ? `?project_id=${projectFilter}` : ''
    api.get<{ items: Report[] }>(`/api/reports${qs}`)
      .then((d) => { setItems(d.items); setError('') })
      .catch((e) => setError((e as Error).message))
  }

  useEffect(() => {
    api.get<{ items: Project[] }>('/api/projects').then((d) => {
      setProjects(d.items)
      if (!form.project_id && d.items[0]) setForm((f) => ({ ...f, project_id: d.items[0].id }))
    }).catch(() => undefined)
  }, [])

  useEffect(load, [projectFilter])

  useEffect(() => {
    if (!form.project_id) { setScans([]); return }
    api.get<{ items: Scan[] }>(`/api/scans?project_id=${form.project_id}&limit=50`)
      .then((d) => setScans(d.items)).catch(() => undefined)
  }, [form.project_id])

  useEffect(() => {
    if (params.get('project')) {
      setModal(true)
      setForm((f) => ({ ...f, project_id: params.get('project') || f.project_id }))
    }
  }, [])

  const generate = async (event: React.FormEvent) => {
    event.preventDefault()
    setSaving(true)
    try {
      const report = await api.post<Report>('/api/reports', {
        project_id: form.project_id, scan_id: form.scan_id || null, title: form.title || null, ai_summary: form.ai_summary,
      })
      toast.push(report.ai_summary ? 'Rapport généré avec synthèse IA.' : 'Rapport généré.', 'success')
      setModal(false); setForm((f) => ({ ...f, scan_id: '', title: '' })); load()
      window.open(report.download_url, '_blank')
    } catch (err) {
      toast.push((err as Error).message, 'error')
    } finally {
      setSaving(false)
    }
  }

  const savePdf = async (report: Report) => {
    if (!window.cybbigDesktop) { window.open(report.download_url, '_blank'); toast.push('Utilisez Ctrl+P puis « Enregistrer en PDF ».', 'info'); return }
    setPdfId(report.id)
    try {
      const path = await window.cybbigDesktop.saveReportPdf(report.id, report.title)
      toast.push(`PDF enregistré : ${path}`, 'success')
    } catch (err) {
      toast.push((err as Error).message, 'error')
    } finally {
      setPdfId(null)
    }
  }

  const remove = async (report: Report) => {
    if (!window.confirm(`Supprimer le rapport « ${report.title} » ?`)) return
    try {
      await api.del(`/api/reports/${report.id}`)
      toast.push('Rapport supprimé.', 'success'); load()
    } catch (err) {
      toast.push((err as Error).message, 'error')
    }
  }

  return (
    <>
      <PageHeader
        title="Rapports"
        description="Générez un rapport HTML ou PDF, avec synthèse exécutive rédigée par l’IA locale, ou un export JSON structuré. Les rapports sont stockés localement et expurgés."
        actions={<button className="btn primary" onClick={() => setModal(true)}><Plus size={14} /> Nouveau rapport</button>}
      />

      {error && <AlertBox kind="error">{error}</AlertBox>}

      <div className="card">
        <div className="card-header">
          <div><h2>Rapports générés</h2><div className="sub">HTML, JSON et données de synthèse</div></div>
          <div className="right">
            <select className="select" style={{ width: 'auto' }} value={projectFilter} onChange={(e) => setProjectFilter(e.target.value)}>
              <option value="">Tous les projets</option>
              {projects.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
            </select>
          </div>
        </div>
        {!items ? <Loading /> : items.length === 0 ? (
          <EmptyState icon={<FileText size={30} />} title="Aucun rapport" description="Créez un rapport de projet ou d’analyse après vos scans." action={<button className="btn primary sm" onClick={() => setModal(true)}><Plus size={14} /> Créer un rapport</button>} />
        ) : (
          <div className="table-wrap">
            <table className="data">
              <thead><tr><th>Rapport</th><th>Projet</th><th>Périmètre</th><th>Résultats</th><th>Risque</th><th>Date</th><th></th></tr></thead>
              <tbody>
                {items.map((r) => {
                  const project = projects.find((p) => p.id === r.project_id)
                  return (
                    <tr key={r.id}>
                      <td><div className="cell-title">{r.title}{r.meta?.ai_summary && <span className="tag" style={{ marginLeft: 6 }}><Sparkles size={10} /> IA</span>}</div><div className="cell-sub cell-mono">{r.id}</div></td>
                      <td className="small">{project?.name || r.project_id}</td>
                      <td className="small">{r.scan_id ? <span className="tag">Analyse ciblée</span> : <span className="tag">Projet complet</span>}</td>
                      <td className="mono">{r.meta?.findings ?? '—'}</td>
                      <td><b style={{ color: (r.meta?.risk_score ?? 0) >= 70 ? 'var(--critical)' : (r.meta?.risk_score ?? 0) >= 40 ? 'var(--high)' : 'var(--green)' }}>{Number(r.meta?.risk_score ?? 0).toFixed(0)}</b></td>
                      <td className="tiny faint">{formatDate(r.created_at)}</td>
                      <td>
                        <div className="row" style={{ gap: 4 }}>
                          <a className="btn sm" href={r.download_url} target="_blank" rel="noreferrer" title="HTML"><Download size={12} /> HTML</a>
                          <button className="btn sm" onClick={() => savePdf(r)} disabled={pdfId === r.id} title="PDF"><FileDown size={12} /> {pdfId === r.id ? 'PDF…' : 'PDF'}</button>
                          <a className="btn sm" href={r.json_url} target="_blank" rel="noreferrer" title="JSON"><FileJson size={12} /> JSON</a>
                          <button className="icon-btn" style={{ width: 28, height: 28 }} onClick={() => remove(r)} title="Supprimer"><Trash2 size={12} /></button>
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="grid cols-3 mt-3">
        <div className="card card-pad"><div className="row" style={{ gap: 7 }}><FileText size={16} color="var(--accent)" /><b className="small">HTML autonome</b></div><p className="tiny faint mt-1" style={{ marginBottom: 0 }}>Rapport imprimable avec preuves, remédiations et références. Aucun accès réseau requis.</p></div>
        <div className="card card-pad"><div className="row" style={{ gap: 7 }}><FileJson size={16} color="var(--accent)" /><b className="small">JSON structuré</b></div><p className="tiny faint mt-1" style={{ marginBottom: 0 }}>Données normalisées pour intégration, archivage ou comparaison entre versions.</p></div>
        <div className="card card-pad"><div className="row" style={{ gap: 7 }}><ExternalLink size={16} color="var(--accent)" /><b className="small">Traçabilité</b></div><p className="tiny faint mt-1" style={{ marginBottom: 0 }}>Chaque rapport conserve le projet, la date, le scan source et l’indice de risque calculé.</p></div>
      </div>

      <Modal open={modal} onClose={() => setModal(false)} title="Nouveau rapport" subtitle="Choisissez un projet et, si besoin, une analyse précise">
        <form onSubmit={generate}>
          <div className="form-grid">
            <div className="field full">
              <label>Projet *</label>
              <select className="select" required value={form.project_id} onChange={(e) => setForm({ ...form, project_id: e.target.value, scan_id: '' })}>
                <option value="">Sélectionner…</option>
                {projects.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
              </select>
            </div>
            <div className="field full">
              <label>Analyse (facultatif)</label>
              <select className="select" value={form.scan_id} onChange={(e) => setForm({ ...form, scan_id: e.target.value })}>
                <option value="">Tout le projet</option>
                {scans.map((s) => <option key={s.id} value={s.id}>{scanLabel(s.kind)} — {formatDate(s.created_at)} — {s.status}</option>)}
              </select>
            </div>
            <div className="field full">
              <label>Titre personnalisé (facultatif)</label>
              <input className="input" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} placeholder="Rapport de sécurité — version de préproduction" />
            </div>
            <div className="field full">
              <label className="checkbox"><input type="checkbox" checked={form.ai_summary} onChange={(e) => setForm({ ...form, ai_summary: e.target.checked })} /><span>Ajouter une synthèse exécutive rédigée par l’IA locale (une à deux minutes de plus)</span></label>
            </div>
          </div>
          <div className="form-actions"><button type="button" className="btn" onClick={() => setModal(false)}>Annuler</button><button className="btn primary" disabled={saving || !form.project_id}>{saving ? (form.ai_summary ? 'Rédaction par l’IA…' : 'Génération…') : 'Générer le rapport'}</button></div>
        </form>
      </Modal>
    </>
  )
}
