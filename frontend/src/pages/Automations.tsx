import { useEffect, useState } from 'react'
import {
  Clock3, Pencil, Play, Plus, Power, RefreshCw, Timer, Trash2,
} from 'lucide-react'
import { api, formatDate, relativeDate, scanLabel } from '../api'
import {
  AlertBox, EmptyState, Loading, Modal, PageHeader, StatusPill, useToast,
} from '../components/ui'
import type { Automation, Project, SchedulerStatus } from '../types'

const KINDS = [
  ['intel_sync', 'Veille cyber'], ['web_watch', 'Veille web ciblée'], ['php', 'Analyse PHP'], ['web', 'Analyse Web'],
  ['api', 'Audit API'], ['checkout', 'Intégrité checkout'], ['reverse', 'Analyse statique de binaire'],
  ['project_suite', 'Pack d’analyses projet'], ['improvement_review', 'Bilan IA des améliorations'],
  ['income_watch', 'Radar d’opportunités rémunérées'],
  ['report', 'Rapport de projet'], ['backup', 'Sauvegarde de la base'],
]
// Types sans projet associé.
const GLOBAL_KINDS = ['intel_sync', 'web_watch', 'income_watch', 'improvement_review', 'backup']
const KIND_LABEL: Record<string, string> = Object.fromEntries(KINDS)

export default function Automations() {
  const [items, setItems] = useState<Automation[] | null>(null)
  const [scheduler, setScheduler] = useState<SchedulerStatus | null>(null)
  const [projects, setProjects] = useState<Project[]>([])
  const [error, setError] = useState('')
  const [modal, setModal] = useState(false)
  const [editing, setEditing] = useState<Automation | null>(null)
  const [runsFor, setRunsFor] = useState<Automation | null>(null)
  const [form, setForm] = useState({
    name: '', kind: 'intel_sync', project_id: '', interval_minutes: 1440,
    enabled: true, sources: ['cisa_kev', 'cert_fr', 'php_releases', 'nvd'] as string[], ai_summary: true,
    web_query: '', web_domains: 'owasp.org, cisa.gov, cert.ssi.gouv.fr',
    web_limit: 10, web_lang: 'fr', web_provider: 'auto', reverse_target: '',
    suite_scans: ['php', 'web', 'api', 'checkout'] as string[],
    income_methods: ['freelance', 'remote_contracts', 'bug_bounty', 'grants'] as string[],
    income_location: 'France', income_skills: 'développement web, Python, cybersécurité', income_limit: 5,
  })
  const [saving, setSaving] = useState(false)
  const toast = useToast()

  const load = () => {
    api.get<{ items: Automation[]; status: SchedulerStatus }>('/api/automations')
      .then((d) => { setItems(d.items); setScheduler(d.status); setError('') })
      .catch((e) => setError((e as Error).message))
  }

  useEffect(() => {
    load()
    api.get<{ items: Project[] }>('/api/projects').then((d) => setProjects(d.items)).catch(() => undefined)
  }, [])

  const create = async (event: React.FormEvent) => {
    event.preventDefault()
    setSaving(true)
    try {
      const config = form.kind === 'intel_sync' ? { sources: form.sources }
        : form.kind === 'report' ? { ai_summary: form.ai_summary }
        : form.kind === 'web_watch' ? { query: form.web_query, domains: form.web_domains.split(/[\s,;]+/).map((domain) => domain.trim()).filter(Boolean).slice(0, 8), limit: form.web_limit, lang: form.web_lang, provider: form.web_provider }
        : form.kind === 'reverse' ? { target: form.reverse_target }
        : form.kind === 'project_suite' ? { scans: form.suite_scans }
        : form.kind === 'income_watch' ? { methods: form.income_methods, location: form.income_location, skills: form.income_skills, limit: form.income_limit }
        : {}
      const payload = {
        name: form.name, kind: form.kind, project_id: GLOBAL_KINDS.includes(form.kind) ? null : form.project_id,
        interval_minutes: form.interval_minutes, config, enabled: form.enabled,
      }
      if (editing) await api.patch(`/api/automations/${editing.id}`, payload)
      else await api.post('/api/automations', payload)
      toast.push(editing ? 'Automatisation mise à jour.' : 'Automatisation créée.', 'success')
      setModal(false); setEditing(null); load()
    } catch (err) {
      toast.push((err as Error).message, 'error')
    } finally {
      setSaving(false)
    }
  }

  const edit = (auto: Automation) => {
    const config = auto.config || {}
    setEditing(auto)
    setForm({
      name: auto.name, kind: auto.kind, project_id: auto.project_id || '', interval_minutes: auto.interval_minutes,
      enabled: Boolean(auto.enabled), sources: Array.isArray(config.sources) ? config.sources : [], ai_summary: Boolean(config.ai_summary),
      web_query: String(config.query || ''), web_domains: Array.isArray(config.domains) ? config.domains.join(', ') : '',
      web_limit: Number(config.limit || 10), web_lang: String(config.lang || 'fr'), web_provider: String(config.provider || 'auto'),
      reverse_target: String(config.target || ''), suite_scans: Array.isArray(config.scans) ? config.scans : ['php', 'web', 'api', 'checkout'],
      income_methods: Array.isArray(config.methods) ? config.methods : ['freelance', 'remote_contracts', 'bug_bounty', 'grants'],
      income_location: String(config.location || 'France'), income_skills: String(config.skills || 'développement web, Python, cybersécurité'), income_limit: Number(config.limit || 5),
    })
    setModal(true)
  }

  const newAutomation = () => {
    setEditing(null)
    setForm({ name: '', kind: 'intel_sync', project_id: '', interval_minutes: 1440, enabled: true,
      sources: ['cisa_kev', 'cert_fr', 'php_releases', 'nvd'], ai_summary: true,
      web_query: '', web_domains: 'owasp.org, cisa.gov, cert.ssi.gouv.fr', web_limit: 10,
      web_lang: 'fr', web_provider: 'auto', reverse_target: '', suite_scans: ['php', 'web', 'api', 'checkout'],
      income_methods: ['freelance', 'remote_contracts', 'bug_bounty', 'grants'], income_location: 'France',
      income_skills: 'développement web, Python, cybersécurité', income_limit: 5 })
    setModal(true)
  }

  const toggle = async (auto: Automation) => {
    try {
      await api.patch(`/api/automations/${auto.id}`, { enabled: !auto.enabled })
      load()
    } catch (err) {
      toast.push((err as Error).message, 'error')
    }
  }

  const run = async (auto: Automation) => {
    try {
      const result = await api.post<{ status: string; error?: string }>(`/api/automations/${auto.id}/run`)
      if (result.status === 'failed') toast.push(result.error || 'Échec de l’exécution.', 'error')
      else toast.push('Exécution démarrée.', 'success')
      load()
    } catch (err) {
      toast.push((err as Error).message, 'error')
    }
  }

  const remove = async (auto: Automation) => {
    if (!window.confirm(`Supprimer « ${auto.name} » ?`)) return
    try {
      await api.del(`/api/automations/${auto.id}`)
      toast.push('Automatisation supprimée.', 'success'); load()
    } catch (err) {
      toast.push((err as Error).message, 'error')
    }
  }

  return (
    <>
      <PageHeader
        title="Automatisations"
        description="Planifiez veille, analyses combinées et rapports. Le cycle IA apprend des résultats récents et enrichit le contexte de connaissance."
        actions={<button className="btn primary" onClick={newAutomation}><Plus size={14} /> Nouvelle automatisation</button>}
      />

      {error && <AlertBox kind="error">{error}</AlertBox>}

      <div className="grid cols-3 mb-2">
        <div className="card stat-card"><div className="stat-label"><Timer size={13} /> Planificateur</div><div className="stat-value" style={{ fontSize: 20, paddingTop: 5 }}>{scheduler?.running ? 'Actif' : 'Arrêté'}</div><div className="stat-foot">{scheduler?.executing ?? 0} en cours · {scheduler?.queued ?? 0} en file · 2 tâches parallèles max</div></div>
        <div className="card stat-card"><div className="stat-label"><Power size={13} /> Activées</div><div className="stat-value">{scheduler?.enabled ?? 0}<span style={{ fontSize: 13, color: 'var(--faint)' }}>/{scheduler?.total ?? 0}</span></div><div className="stat-foot">tâches planifiées</div></div>
        <div className="card stat-card"><div className="stat-label"><Clock3 size={13} /> Prochaine</div><div className="stat-value" style={{ fontSize: 16, paddingTop: 8 }}>{scheduler?.next_runs[0] ? relativeDate(scheduler.next_runs[0].next_run_at) : '—'}</div><div className="stat-foot">{scheduler?.next_runs[0]?.name || 'aucune exécution planifiée'}</div></div>
      </div>

      {!items ? <Loading /> : items.length === 0 ? (
        <div className="card"><EmptyState icon={<Timer size={30} />} title="Aucune automatisation" description="Créez une veille, un pack de scans, un bilan IA récurrent, un rapport ou une sauvegarde." action={<button className="btn primary sm" onClick={newAutomation}><Plus size={14} /> Créer</button>} /></div>
      ) : (
        <div className="grid auto">
          {items.map((auto) => (
            <article className="card card-pad" key={auto.id} style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              <div className="row" style={{ gap: 8 }}>
                <div className="icon-wrap" style={{ width: 30, height: 30, borderRadius: 8, display: 'grid', placeItems: 'center', background: 'var(--panel-2)' }}><RefreshCw size={14} color="var(--accent)" /></div>
                <div style={{ minWidth: 0 }}>
                  <div style={{ fontWeight: 650, fontSize: 13.5 }}>{auto.name}</div>
                  <div className="tiny faint">{KIND_LABEL[auto.kind] ?? scanLabel(auto.kind)} · {auto.project_name || 'sans projet'}</div>
                </div>
                <label className="pill" style={{ marginLeft: 'auto', cursor: 'pointer', gap: 5 }}>
                  <input type="checkbox" checked={Boolean(auto.enabled)} onChange={() => toggle(auto)} style={{ accentColor: 'var(--accent-strong)' }} />
                  {auto.enabled ? 'Active' : 'Inactive'}
                </label>
              </div>
              <div className="kv-list">
                <div className="kv-item"><span>Intervalle</span><b>{intervalLabel(auto.interval_minutes)}</b></div>
                <div className="kv-item"><span>Dernière exécution</span><b>{auto.last_run_at ? relativeDate(auto.last_run_at) : 'jamais'}</b></div>
                <div className="kv-item"><span>Prochaine</span><b>{relativeDate(auto.next_run_at)}</b></div>
                <div className="kv-item"><span>Statut</span><b><StatusPill status={auto.last_status} /></b></div>
              </div>
              <div className="row wrap" style={{ gap: 5 }}>
                <button className="btn sm" onClick={() => run(auto)}><Play size={12} /> Exécuter</button>
                <button className="btn ghost sm" onClick={() => edit(auto)}><Pencil size={12} /> Modifier</button>
                <button className="btn ghost sm" onClick={() => setRunsFor(auto)}>Historique ({auto.runs?.length ?? 0})</button>
                <button className="icon-btn" style={{ width: 28, height: 28, marginLeft: 'auto' }} onClick={() => remove(auto)} title="Supprimer"><Trash2 size={12} /></button>
              </div>
            </article>
          ))}
        </div>
      )}

      <Modal open={modal} onClose={() => { setModal(false); setEditing(null) }} title={editing ? 'Modifier l’automatisation' : 'Nouvelle automatisation'} subtitle="Planification locale">
        <form onSubmit={create}>
          <div className="form-grid">
            <div className="field full"><label>Nom *</label><input className="input" required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Veille quotidienne, scan PHP hebdomadaire…" /></div>
            <div className="field"><label>Type</label><select className="select" disabled={Boolean(editing)} value={form.kind} onChange={(e) => { const kind = e.target.value; setForm({ ...form, kind, interval_minutes: kind === 'income_watch' ? 2 : Math.max(5, form.interval_minutes) }) }}>{KINDS.map(([v, l]) => <option key={v} value={v}>{l}</option>)}</select></div>
            <div className="field"><label>Répéter toutes les (minutes)</label><input className="input" type="number" min={form.kind === 'income_watch' ? 2 : 5} max={525600} step={form.kind === 'income_watch' ? 1 : 5} required value={form.interval_minutes} onChange={(e) => setForm({ ...form, interval_minutes: Number(e.target.value) })} /><span className="hint">Le radar peut vérifier son état toutes les 2 min. Les flux externes sont actualisés depuis leur cache aux cadences autorisées; les autres automatisations restent à 5 min minimum.</span></div>
            {form.kind === 'report' && (
              <div className="field full"><label className="checkbox"><input type="checkbox" checked={form.ai_summary} onChange={(e) => setForm({ ...form, ai_summary: e.target.checked })} /><span>Inclure une synthèse exécutive rédigée par l’IA locale</span></label></div>
            )}
            {form.kind === 'web_watch' && <>
              <div className="field full"><label>Requête *</label><input className="input" required minLength={2} value={form.web_query} onChange={(event) => setForm({ ...form, web_query: event.target.value })} placeholder="Correctifs récents de sécurité PHP" /></div>
              <div className="field full"><label>Sites ciblés <span className="tiny faint">(jusqu’à 8, séparés par des virgules)</span></label><input className="input" value={form.web_domains} onChange={(event) => setForm({ ...form, web_domains: event.target.value })} placeholder="owasp.org, cisa.gov, github.com" /><span className="hint">Les exécutions enregistrent les titres et les liens dans l’historique de cette automatisation.</span></div>
              <div className="field"><label>Résultats par recherche</label><input className="input" type="number" min={5} max={20} value={form.web_limit} onChange={(e) => setForm({ ...form, web_limit: Number(e.target.value) })} /></div>
              <div className="field"><label>Langue</label><select className="select" value={form.web_lang} onChange={(e) => setForm({ ...form, web_lang: e.target.value })}><option value="fr">Français</option><option value="en">Anglais</option></select></div>
              <div className="field"><label>Moteur</label><select className="select" value={form.web_provider} onChange={(e) => setForm({ ...form, web_provider: e.target.value })}><option value="auto">Automatique</option><option value="brave">Brave Search</option><option value="ddg">DuckDuckGo</option></select></div>
            </>}
            {form.kind === 'reverse' && <div className="field full"><label>Fichier binaire dans le projet *</label><input className="input" required value={form.reverse_target} onChange={(e) => setForm({ ...form, reverse_target: e.target.value })} placeholder="bin/application.exe" /><span className="hint">L’analyse reste limitée au périmètre du projet et aux outils locaux configurés.</span></div>}
            {form.kind === 'project_suite' && <div className="field full"><label>Analyses à lancer à chaque cycle</label><div className="row wrap">{[['php', 'PHP local'], ['web', 'Web passive'], ['api', 'API'], ['checkout', 'Checkout']].map(([value, label]) => <label key={value} className="pill" style={{ cursor: 'pointer', gap: 5 }}><input type="checkbox" checked={form.suite_scans.includes(value)} onChange={(e) => setForm({ ...form, suite_scans: e.target.checked ? [...form.suite_scans, value] : form.suite_scans.filter((item) => item !== value) })} style={{ accentColor: 'var(--accent-strong)' }} />{label}</label>)}</div><span className="hint">Les scans démarrent uniquement si le projet possède la cible correspondante.</span></div>}
            {form.kind === 'income_watch' && <>
              <div className="field full"><label>Méthodes de recherche</label><div className="row wrap">{[['freelance', 'Missions freelance'], ['remote_contracts', 'Contrats à distance'], ['bug_bounty', 'Bug bounty autorisé'], ['grants', 'Aides, appels et marchés UE']].map(([value, label]) => <label key={value} className="pill" style={{ cursor: 'pointer', gap: 5 }}><input type="checkbox" checked={form.income_methods.includes(value)} onChange={(e) => setForm({ ...form, income_methods: e.target.checked ? [...form.income_methods, value] : form.income_methods.filter((item) => item !== value) })} style={{ accentColor: 'var(--accent-strong)' }} />{label}</label>)}</div></div>
              <div className="field"><label>Pays ou zone</label><input className="input" maxLength={100} value={form.income_location} onChange={(e) => setForm({ ...form, income_location: e.target.value })} placeholder="France" /></div>
              <div className="field"><label>Compétences / mots-clés</label><input className="input" maxLength={180} value={form.income_skills} onChange={(e) => setForm({ ...form, income_skills: e.target.value })} placeholder="Python, cybersécurité…" /></div>
              <div className="field"><label>Résultats par méthode</label><input className="input" type="number" min={3} max={10} value={form.income_limit} onChange={(e) => setForm({ ...form, income_limit: Number(e.target.value) })} /></div>
              <div className="field full"><span className="hint">Le radar agrège les flux Remote OK, Remotive et Funding &amp; Tenders de l’UE (cache 6 h), complète avec une recherche ciblée et transmet les pistes à l’IA locale. Les brouillons de réponse sont enregistrés sur ce PC. Cybbig ne postule pas, n’ouvre pas de comptes, ne réalise pas de tests de sécurité et ne garantit aucun revenu. Vérifiez l’annonce et ses conditions avant d’agir.</span></div>
            </>}
            {!GLOBAL_KINDS.includes(form.kind) && (
              <div className="field full"><label>Projet *</label><select className="select" required value={form.project_id} onChange={(e) => setForm({ ...form, project_id: e.target.value })}><option value="">Sélectionner…</option>{projects.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}</select></div>
            )}
            {form.kind === 'intel_sync' && (
              <div className="field full">
                <label>Sources</label>
                <div className="row wrap">
                  {[['cisa_kev', 'CISA KEV'], ['nvd', 'NVD'], ['cert_fr', 'CERT-FR'], ['php_releases', 'PHP']].map(([value, label]) => (
                    <label key={value} className="pill" style={{ cursor: 'pointer', gap: 5 }}>
                      <input type="checkbox" checked={form.sources.includes(value)} onChange={(e) => setForm({
                        ...form, sources: e.target.checked ? [...form.sources, value] : form.sources.filter((s) => s !== value),
                      })} style={{ accentColor: 'var(--accent-strong)' }} />
                      {label}
                    </label>
                  ))}
                </div>
              </div>
            )}
            <div className="field full"><label className="checkbox"><input type="checkbox" checked={form.enabled} onChange={(e) => setForm({ ...form, enabled: e.target.checked })} /><span>Activer immédiatement</span></label></div>
          </div>
          <div className="form-actions"><button type="button" className="btn" onClick={() => setModal(false)}>Annuler</button><button className="btn primary" disabled={saving}>{saving ? 'Création…' : 'Créer'}</button></div>
        </form>
      </Modal>

      <Modal open={Boolean(runsFor)} onClose={() => setRunsFor(null)} title={`Historique — ${runsFor?.name ?? ''}`} subtitle="5 dernières exécutions" size="wide">
        {!runsFor?.runs?.length ? <EmptyState title="Aucune exécution" description="L’historique apparaîtra après la première exécution." /> : (
          <div className="stack">
            {runsFor.runs.map((r) => (
              <div key={r.id} className="card card-pad" style={{ padding: 13 }}>
                <div className="row between"><div className="row" style={{ gap: 7 }}><StatusPill status={r.status} /><span className="small">{formatDate(r.started_at)}</span></div><span className="tiny faint">{r.finished_at ? formatDate(r.finished_at) : 'en cours'}</span></div>
                {r.log && <pre className="evidence mt-2" style={{ maxHeight: 130 }}>{r.log}</pre>}
              </div>
            ))}
          </div>
        )}
      </Modal>
    </>
  )
}

function intervalLabel(minutes: number): string {
  if (minutes % 10080 === 0) return `${minutes / 10080} semaine(s)`
  if (minutes % 1440 === 0) return `${minutes / 1440} jour(s)`
  if (minutes % 60 === 0) return `${minutes / 60} heure(s)`
  return `${minutes} min`
}
