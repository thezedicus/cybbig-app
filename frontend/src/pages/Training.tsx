import { useCallback, useEffect, useState } from 'react'
import { Bot, Check, Download, GraduationCap, Library, MessageSquareQuote, Sparkles, Trash2, X } from 'lucide-react'
import { Link } from 'react-router-dom'
import { api, relativeDate } from '../api'
import { AlertBox, EmptyState, Loading, PageHeader, Progress, useToast } from '../components/ui'

interface Job {
  id: string; kind: string; status: string
  progress: { done?: number; total?: number; current?: string; step?: string; teacher?: string; base?: string; examples?: number }
  result: { steps?: Record<string, { created?: number; examples_added?: number; model?: string; skipped?: string; error?: string }>; approved?: number; created?: number; requested?: number; examples_added?: number; documents?: number; skipped?: number; errors?: string[]; error?: string; model?: string; base?: string; examples?: number; provider?: string; teacher?: string; activated?: boolean }
}
interface Overview {
  teacher: { provider: 'cloud' | 'local'; selected_model: string } | null
  teacher_error: string
  local_available: boolean; local_models: string[]; local_model: string
  documents: number; generated_documents: number; web_documents: number
  curriculum_total: number; curriculum_missing: number
  examples: { pending: number; approved: number; rejected: number }
  docs_without_examples: number
  custom_model: string; custom_model_present: boolean; base_model: string; active_model: string
  jobs: Job[]
  auto: { enabled: boolean; hours: number; approve: boolean; last: string; message: string }
  mode: string
}
interface Example { id: string; question: string; answer: string; teacher: string; status: string; doc_title: string | null }

const KIND_LABEL: Record<string, string> = { auto: 'Cycle automatique', enrich: 'Enrichissement de la bibliothèque', qa: 'Génération de questions/réponses', build_model: 'Création du modèle local' }
const RUNNING = ['queued', 'running']

export default function Training() {
  const [data, setData] = useState<Overview | null>(null)
  const [error, setError] = useState('')
  const [job, setJob] = useState<Job | null>(null)
  const [examples, setExamples] = useState<Example[] | null>(null)
  const [filter, setFilter] = useState('pending')
  const [open, setOpen] = useState<string | null>(null)
  const [enrichN, setEnrichN] = useState(10)
  const [qaN, setQaN] = useState(12)
  const [perDoc, setPerDoc] = useState(3)
  const [model, setModel] = useState({ name: 'cybbig-analyst', base: '', max: 12, activate: true })
  const toast = useToast()

  const load = useCallback(() => {
    api.get<Overview>('/api/training').then((d) => { setData(d); setError('') }).catch((e) => setError((e as Error).message))
  }, [])
  const loadExamples = useCallback(() => {
    api.get<{ items: Example[] }>(`/api/training/examples?status=${filter}&limit=40`).then((d) => setExamples(d.items)).catch(() => undefined)
  }, [filter])

  useEffect(load, [load])
  useEffect(loadExamples, [loadExamples])

  // Tâche déjà en cours à l'ouverture de la page.
  useEffect(() => {
    if (!job && data?.jobs[0] && RUNNING.includes(data.jobs[0].status)) setJob(data.jobs[0])
  }, [data, job])

  useEffect(() => {
    if (!job || !RUNNING.includes(job.status)) return
    const timer = window.setInterval(() => {
      api.get<Job>(`/api/training/jobs/${job.id}`).then((fresh) => {
        setJob(fresh)
        if (!RUNNING.includes(fresh.status)) { load(); loadExamples() }
      }).catch(() => undefined)
    }, 1200)
    return () => window.clearInterval(timer)
  }, [job, load, loadExamples])

  const start = async (path: string, body: unknown) => {
    try { setJob(await api.post<Job>(path, body)); setError('') } catch (err) { setError((err as Error).message) }
  }
  const setStatus = async (id: string, status: string) => {
    try { await api.patch(`/api/training/examples/${id}`, { status }); load(); loadExamples() } catch (err) { toast.push((err as Error).message, 'error') }
  }
  const saveAuto = async (values: Record<string, string>) => {
    try { await api.put('/api/settings', { values }); load() } catch (err) { toast.push((err as Error).message, 'error') }
  }
  const approveAll = async () => {
    try {
      const r = await api.post<{ updated: number }>('/api/training/examples/bulk', { from_status: 'pending', to_status: 'approved' })
      toast.push(`${r.updated} exemple(s) approuvé(s).`, 'success'); load(); loadExamples()
    } catch (err) { toast.push((err as Error).message, 'error') }
  }
  const removeModel = async () => {
    if (!window.confirm('Supprimer le modèle local personnalisé ? Le modèle de base est conservé.')) return
    try { await api.del('/api/training/model'); toast.push('Modèle supprimé.', 'success'); load() } catch (err) { toast.push((err as Error).message, 'error') }
  }

  if (!data) return <>{error ? <AlertBox kind="error">{error}</AlertBox> : <Loading />}</>
  const running = Boolean(job && RUNNING.includes(job.status))
  const teacherText = data.teacher ? `${data.teacher.selected_model} (${data.teacher.provider === 'cloud' ? 'en ligne' : 'local — lent'})` : 'indisponible'
  const percent = job?.progress.total ? 100 * (job.progress.done ?? 0) / job.progress.total : 0

  return (
    <>
      <PageHeader
        title="Entraînement de l’IA"
        description="Le modèle en ligne (professeur) enrichit la bibliothèque et prépare des exemples ; le modèle local (élève) en profite par la recherche documentaire et un profil personnalisé."
      />
      {error && <AlertBox kind="error">{error}</AlertBox>}
      {!data.teacher && <AlertBox kind="info">Aucun professeur disponible : {data.teacher_error} Configurez l’IA en ligne dans Paramètres, ou lancez Ollama en local.</AlertBox>}

      <div className="grid auto" style={{ marginBottom: 16 }}>
        <div className="card card-pad"><div className="tiny faint">Professeur</div><b>{teacherText}</b></div>
        <div className="card card-pad"><div className="tiny faint">Bibliothèque</div><b>{data.documents} fiches</b><div className="tiny faint">{data.generated_documents} générées par IA · {data.web_documents} du web</div></div>
        <div className="card card-pad"><div className="tiny faint">Programme de rédaction</div><b>{data.curriculum_total - data.curriculum_missing} / {data.curriculum_total} sujets</b></div>
        <div className="card card-pad"><div className="tiny faint">Exemples Q/R</div><b>{data.examples.approved} approuvés</b><div className="tiny faint">{data.examples.pending} à relire · {data.examples.rejected} rejetés</div></div>
        <div className="card card-pad"><div className="tiny faint">Modèle local personnalisé</div><b>{data.custom_model_present ? data.custom_model : 'non créé'}</b>{data.base_model && <div className="tiny faint">base : {data.base_model}</div>}</div>
      </div>

      <section className="card" style={{ marginBottom: 16 }}>
        <div className="card-header">
          <div><h2>Pilote automatique</h2><div className="sub">Rédige les fiches manquantes, prépare les exemples et met à jour votre modèle local, tout seul</div></div>
          <Bot size={16} style={{ marginLeft: 'auto', color: 'var(--accent)' }} />
        </div>
        <div className="card-pad stack" style={{ gap: 10 }}>
          <label className="checkbox">
            <input type="checkbox" checked={data.auto.enabled} onChange={(e) => saveAuto({ training_auto: e.target.checked ? 'true' : 'false' })} />
            <span><b>Entraîner automatiquement</b> : un cycle toutes les
              <select className="select" style={{ width: 'auto', margin: '0 6px', display: 'inline-block' }} aria-label="Fréquence" value={String(data.auto.hours)} onChange={(e) => saveAuto({ training_auto_hours: e.target.value })}>
                <option value="6">6 h</option><option value="12">12 h</option><option value="24">24 h</option><option value="72">3 jours</option><option value="168">7 jours</option>
              </select>
              tant que l’application est ouverte et que le mode en ligne autorise l’entraînement</span>
          </label>
          <label className="checkbox">
            <input type="checkbox" checked={data.auto.approve} onChange={(e) => saveAuto({ training_auto_approve: e.target.checked ? 'true' : 'false' })} />
            <span>Approuver automatiquement les exemples <span className="faint">(contrôles automatiques : longueur, CVE non inventées ; sans relecture humaine, décochez pour tout valider vous-même)</span></span>
          </label>
          <div className="row wrap" style={{ gap: 10 }}>
            <button className="btn primary sm" disabled={running || !data.teacher || data.teacher.provider !== 'cloud'} onClick={() => start('/api/training/auto-run', {})}><Sparkles size={13} /> Lancer un cycle maintenant</button>
            <span className="tiny faint">
              Mode en ligne : {data.mode === 'local' ? 'coupé' : data.mode === 'training' ? 'entraînement seulement' : 'actif'}
              {data.auto.last ? ` · dernier cycle ${relativeDate(data.auto.last)}` : ' · aucun cycle encore'}
            </span>
          </div>
          {data.mode === 'local' && <AlertBox kind="info">Le mode en ligne est coupé (aucune donnée ne part). Réactivez-le avec le bouton nuage de la barre du haut pour entraîner.</AlertBox>}
          {data.auto.message && <AlertBox kind="error">{data.auto.message} <Link to="/settings">Paramètres</Link></AlertBox>}
        </div>
      </section>

      {job && (
        <section className="card" style={{ marginBottom: 16 }}>
          <div className="card-pad stack" style={{ gap: 8 }}>
            <div className="row between"><b>{KIND_LABEL[job.kind] ?? job.kind}</b>
              <span className={`pill ${job.status}`}>{running ? 'En cours' : job.status === 'completed' ? 'Terminé' : job.status === 'cancelled' ? 'Annulé' : 'Échec'}</span></div>
            {running ? (
              <>
                <Progress value={percent} />
                <span className="small">{job.progress.step ?? (job.progress.total ? `${job.progress.done ?? 0}/${job.progress.total}` : 'Préparation…')} {job.progress.current ? `· ${job.progress.current}` : ''}</span>
                <div><button className="btn sm" onClick={() => api.post(`/api/training/jobs/${job.id}/cancel`)}>Annuler</button></div>
              </>
            ) : (
              <span className="small">
                {job.result.error ? `Erreur : ${job.result.error}` : job.kind === 'auto'
                  ? `Cycle terminé : ${job.result.steps?.enrich?.created ?? 0} fiche(s), ${job.result.steps?.qa?.examples_added ?? 0} exemple(s), ${job.result.approved ?? 0} approuvé(s) ; modèle : ${job.result.steps?.model?.model ?? job.result.steps?.model?.skipped ?? job.result.steps?.model?.error ?? '—'}.`
                  : job.kind === 'enrich' ? `${job.result.created ?? 0} fiche(s) créée(s) sur ${job.result.requested ?? 0} demandée(s) par ${job.result.teacher ?? '—'}.`
                  : job.kind === 'qa' ? `${job.result.examples_added ?? 0} exemple(s) ajouté(s) à relire, à partir de ${job.result.documents ?? 0} fiche(s).`
                    : `Modèle ${job.result.model ?? '—'} créé à partir de ${job.result.base ?? '—'} avec ${job.result.examples ?? 0} exemple(s)${job.result.activated ? ' ; il est maintenant le modèle local actif.' : '.'}`}
              </span>
            )}
            {job.result.errors?.map((e) => <span key={e} className="tiny" style={{ color: 'var(--high)' }}>{e}</span>)}
          </div>
        </section>
      )}

      <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))' }}>
        <section className="card">
          <div className="card-header"><div><h2>1 · Enrichir la bibliothèque</h2><div className="sub">Le professeur rédige les fiches manquantes du programme</div></div><Library size={16} style={{ marginLeft: 'auto', color: 'var(--accent)' }} /></div>
          <div className="card-pad stack" style={{ gap: 10 }}>
            <p className="small" style={{ margin: 0 }}>{data.curriculum_missing} sujet(s) restent à rédiger (durcissement serveurs, conformité, authentification, sécurité de l’IA, tests…). Les fiches sont étiquetées « généré par IA, non vérifié ».</p>
            <div className="field"><label htmlFor="tr-enrich">Nombre de fiches à rédiger</label>
              <input id="tr-enrich" className="input" type="number" min={1} max={60} value={enrichN} onChange={(e) => setEnrichN(Number(e.target.value))} /></div>
            <div><button className="btn primary" disabled={running || !data.teacher || data.curriculum_missing === 0} onClick={() => start('/api/training/enrich', { limit: enrichN })}><Sparkles size={14} /> Rédiger avec le professeur</button></div>
          </div>
        </section>

        <section className="card">
          <div className="card-header"><div><h2>2 · Générer des questions/réponses</h2><div className="sub">Exemples tirés des fiches de la bibliothèque</div></div><MessageSquareQuote size={16} style={{ marginLeft: 'auto', color: 'var(--accent)' }} /></div>
          <div className="card-pad stack" style={{ gap: 10 }}>
            <p className="small" style={{ margin: 0 }}>{data.docs_without_examples} fiche(s) sans exemple. Le contenu importé du web n’est jamais utilisé pour l’entraînement.</p>
            <div className="form-grid">
              <div className="field"><label htmlFor="tr-qa">Fiches à traiter</label><input id="tr-qa" className="input" type="number" min={1} max={60} value={qaN} onChange={(e) => setQaN(Number(e.target.value))} /></div>
              <div className="field"><label htmlFor="tr-per">Questions par fiche</label><input id="tr-per" className="input" type="number" min={1} max={5} value={perDoc} onChange={(e) => setPerDoc(Number(e.target.value))} /></div>
            </div>
            <div><button className="btn primary" disabled={running || !data.teacher || data.docs_without_examples === 0} onClick={() => start('/api/training/qa', { limit: qaN, per_doc: perDoc })}><Sparkles size={14} /> Générer</button></div>
          </div>
        </section>

      </div>

      <section className="card" style={{ marginTop: 16 }}>
        <div className="card-header">
          <div><h2>3 · Relire les exemples</h2><div className="sub">Seuls les exemples approuvés servent à l’entraînement</div></div>
          <div className="right row" style={{ gap: 8 }}>
            <select className="select" aria-label="Filtrer les exemples" value={filter} onChange={(e) => setFilter(e.target.value)}>
              <option value="pending">À relire ({data.examples.pending})</option>
              <option value="approved">Approuvés ({data.examples.approved})</option>
              <option value="rejected">Rejetés ({data.examples.rejected})</option>
            </select>
            {filter === 'pending' && data.examples.pending > 0 && <button className="btn sm" onClick={approveAll}><Check size={13} /> Tout approuver</button>}
          </div>
        </div>
        {!examples ? <Loading /> : examples.length === 0 ? (
          <EmptyState icon={<MessageSquareQuote size={28} />} title="Aucun exemple" description="Lancez l’étape 2 pour que le professeur prépare des questions/réponses à relire." />
        ) : (
          <div className="stack" style={{ padding: 16, gap: 10 }}>
            {examples.map((ex) => (
              <article key={ex.id} className="card" style={{ padding: 12 }}>
                <div className="row between" style={{ gap: 10, alignItems: 'flex-start' }}>
                  <div style={{ minWidth: 0, flex: 1 }}>
                    <b className="small">{ex.question}</b>
                    <div className="small mt-1" style={{ color: 'var(--text-soft)', whiteSpace: 'pre-wrap' }}>{open === ex.id ? ex.answer : `${ex.answer.slice(0, 220)}${ex.answer.length > 220 ? '…' : ''}`}</div>
                    <div className="tiny faint mt-1">{ex.doc_title ?? 'fiche supprimée'} · {ex.teacher}{ex.answer.length > 220 && <> · <button className="btn sm" style={{ padding: '0 6px' }} onClick={() => setOpen(open === ex.id ? null : ex.id)}>{open === ex.id ? 'Réduire' : 'Tout lire'}</button></>}</div>
                  </div>
                  <div className="row" style={{ gap: 6 }}>
                    {ex.status !== 'approved' && <button className="btn sm" aria-label="Approuver" onClick={() => setStatus(ex.id, 'approved')}><Check size={13} /></button>}
                    {ex.status !== 'rejected' && <button className="btn danger sm" aria-label="Rejeter" onClick={() => setStatus(ex.id, 'rejected')}><X size={13} /></button>}
                  </div>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>

      <section className="card" style={{ marginTop: 16 }}>
          <div className="card-header"><div><h2>4 · Créer le modèle local</h2><div className="sub">Profil Ollama personnalisé (consigne système + exemples)</div></div><GraduationCap size={16} style={{ marginLeft: 'auto', color: 'var(--accent)' }} /></div>
          <div className="card-pad stack" style={{ gap: 10 }}>
            <div className="form-grid">
              <div className="field"><label htmlFor="tr-name">Nom du modèle</label><input id="tr-name" className="input mono" value={model.name} onChange={(e) => setModel({ ...model, name: e.target.value })} /></div>
              <div className="field"><label htmlFor="tr-base">Modèle de base</label>
                <select id="tr-base" className="select" value={model.base} onChange={(e) => setModel({ ...model, base: e.target.value })}>
                  <option value="">{data.base_model || data.local_model || 'Modèle local actif'}</option>
                  {data.local_models.filter((m) => !m.startsWith(model.name)).map((m) => <option key={m} value={m}>{m}</option>)}
                </select></div>
              <div className="field"><label htmlFor="tr-max">Exemples intégrés (0 à 30)</label><input id="tr-max" className="input" type="number" min={0} max={30} value={model.max} onChange={(e) => setModel({ ...model, max: Number(e.target.value) })} /></div>
            </div>
            <label className="checkbox"><input type="checkbox" checked={model.activate} onChange={(e) => setModel({ ...model, activate: e.target.checked })} /><span>Utiliser ce modèle comme modèle local de l’assistant</span></label>
            <p className="tiny faint" style={{ margin: 0 }}>Cela ne modifie pas les poids du modèle (ce n’est pas un fine-tuning) : le profil fixe son rôle, son style et des exemples. La mémoire de connaissances reste la bibliothèque. {data.examples.approved} exemple(s) approuvé(s) disponible(s).</p>
            <div className="row wrap" style={{ gap: 8 }}>
              <button className="btn primary" disabled={running || !data.local_available} onClick={() => start('/api/training/model', { name: model.name, base: model.base, max_examples: model.max, activate: model.activate })}><GraduationCap size={14} /> {data.custom_model_present ? 'Mettre à jour le modèle' : 'Créer le modèle'}</button>
              {data.custom_model_present && <button className="btn danger sm" onClick={removeModel}><Trash2 size={13} /> Supprimer</button>}
              <a className="btn sm" href="/api/training/export" download><Download size={13} /> Exporter en JSONL (fine-tuning)</a>
            </div>
          </div>
      </section>
    </>
  )
}
