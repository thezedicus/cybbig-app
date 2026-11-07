import { useEffect, useState } from 'react'
import { ExternalLink, Play, RefreshCw, Search, Sparkles, Wallet } from 'lucide-react'
import { api, formatDate } from '../api'
import Markdown from '../components/Markdown'
import { AlertBox, EmptyState, Loading, PageHeader, useToast } from '../components/ui'

type Status = 'new' | 'shortlisted' | 'proposal_prepared' | 'applied' | 'accepted' | 'declined' | 'completed'
type Opportunity = {
  id: string; method: string; title: string; url: string; source: string; snippet: string
  status: Status; note: string; proposal_draft: string; first_seen_at: string; last_seen_at: string
}
type Data = { items: Opportunity[]; counts: Record<string, number>; total: number }
type Review = { content: string; updated_at: string }
type Radar = { configured: boolean; enabled: boolean; interval_minutes?: number; last_status?: string; last_run_at?: string; next_run_at?: string; run_status?: string; run_log?: string }

const STATUS: Array<[Status, string]> = [
  ['new', 'À examiner'], ['shortlisted', 'Retenue'], ['proposal_prepared', 'Réponse préparée'],
  ['applied', 'Candidature envoyée'], ['accepted', 'Mission acceptée'], ['declined', 'Refusée'], ['completed', 'Terminée'],
]
const METHOD: Record<string, string> = {
  freelance: 'Freelance', remote_contracts: 'Contrat à distance', bug_bounty: 'Bug bounty autorisé', grants: 'Aides / appels à projets',
}

export default function Income() {
  const [data, setData] = useState<Data | null>(null)
  const [review, setReview] = useState<Review | null>(null)
  const [radar, setRadar] = useState<Radar | null>(null)
  const [status, setStatus] = useState('all')
  const [method, setMethod] = useState('all')
  const [query, setQuery] = useState('')
  const [notes, setNotes] = useState<Record<string, string>>({})
  const [busy, setBusy] = useState(false)
  const [searching, setSearching] = useState(false)
  const [drafting, setDrafting] = useState<string | null>(null)
  const [error, setError] = useState('')
  const toast = useToast()

  const load = () => {
    setBusy(true)
    Promise.all([api.get<Data>('/api/income/opportunities?limit=300'), api.get<Review>('/api/income/review'), api.get<Radar>('/api/income/status')])
      .then(([result, latestReview, radarStatus]) => { setData(result); setReview(latestReview); setRadar(radarStatus); setNotes(Object.fromEntries(result.items.map((item) => [item.id, item.note || '']))); setError('') })
      .catch((e) => setError((e as Error).message))
      .finally(() => setBusy(false))
  }

  useEffect(() => { load() }, [])

  const update = async (item: Opportunity, patch: { status?: Status; note?: string; proposal_draft?: string }) => {
    try {
      await api.patch(`/api/income/opportunities/${item.id}`, patch)
      toast.push(patch.status ? 'Suivi mis à jour.' : patch.proposal_draft !== undefined ? 'Brouillon enregistré.' : 'Note enregistrée.', 'success')
      load()
    } catch (e) { toast.push((e as Error).message, 'error') }
  }

  const prepareDraft = async (item: Opportunity) => {
    setDrafting(item.id)
    try {
      await api.post(`/api/income/opportunities/${item.id}/draft`)
      toast.push('Brouillon préparé par le modèle local. Vérifiez-le avant tout envoi.', 'success')
      load()
    } catch (e) { toast.push((e as Error).message, 'error') }
    finally { setDrafting(null) }
  }

  const runRadar = async () => {
    setSearching(true)
    try {
      const { items: automations } = await api.get<{ items: Array<{ id: string; kind: string; name: string }> }>('/api/automations')
      const radar = automations.find((item) => item.kind === 'income_watch')
      if (!radar) throw new Error('Créez d’abord un radar dans Automatisations.')
      const result = await api.post<{ status: string; error?: string }>(`/api/automations/${radar.id}/run`)
      if (result.status === 'failed') throw new Error(result.error || 'La recherche a échoué.')
      toast.push('Recherche terminée; les résultats sont enregistrés dans Opportunités.', 'success')
      load()
    } catch (e) { toast.push((e as Error).message, 'error') }
    finally { setSearching(false) }
  }

  const needle = query.trim().toLocaleLowerCase('fr')
  const items = (data?.items || []).filter((item) => (status === 'all' || item.status === status)
    && (method === 'all' || item.method === method)
    && (!needle || `${item.title} ${item.snippet} ${item.source} ${item.note}`.toLocaleLowerCase('fr').includes(needle)))

  return <>
    <PageHeader title="Opportunités rémunérées" description="Le radar autonome collecte les offres publiques, les déduplique, actualise leur suivi et demande une analyse à l’IA locale." actions={<div className="row"><button className="btn" onClick={load} disabled={busy}><RefreshCw size={14} /> Actualiser</button><button className="btn primary" onClick={runRadar} disabled={searching}>{searching ? <RefreshCw size={14} className="spin" /> : <Play size={14} />} {searching ? 'Recherche…' : 'Rechercher maintenant'}</button></div>} />
    {error && <AlertBox kind="error">{error}</AlertBox>}
    <div className="alert-banner info mb-2"><Wallet size={16} /><div className="small">Cybbig automatise la recherche et le suivi. Il ne postule pas, ne réalise pas de tests sur des cibles, ne garantit pas de revenus et ne reçoit aucun paiement. Vérifiez chaque annonce, son périmètre, ses conditions et son montant auprès de la source.</div></div>
    <div className={`alert-banner ${radar?.enabled ? 'success' : 'info'} mb-2`}><RefreshCw size={15} /><div className="small">{radar?.configured ? radar.enabled ? `Radar automatique actif · cycle toutes les ${radar.interval_minutes} min · prochain passage ${radar.next_run_at ? formatDate(radar.next_run_at) : 'planifié'}.` : 'Radar automatique en pause. Réactivez-le dans Automatisations.' : 'Radar en cours de configuration.'}{radar?.last_run_at ? ` Dernier passage : ${formatDate(radar.last_run_at)} (${radar.last_status || 'inconnu'}).` : ''}{radar?.run_log && <details style={{ marginTop: 8 }}><summary style={{ cursor: 'pointer' }}>Voir le journal du dernier cycle</summary><pre style={{ whiteSpace: 'pre-wrap', maxHeight: 260, overflow: 'auto', fontSize: 11, marginTop: 8 }}>{radar.run_log}</pre></details>}</div></div>
    <div className="grid cols-3 mb-2">
      <div className="card stat-card"><div className="stat-label"><Search size={13} /> Pistes repérées</div><div className="stat-value">{data?.total ?? '—'}</div><div className="stat-foot">liens issus de recherches publiques</div></div>
      <div className="card stat-card"><div className="stat-label">À examiner</div><div className="stat-value">{data?.counts.new ?? 0}</div><div className="stat-foot">nouveaux résultats du radar</div></div>
      <div className="card stat-card"><div className="stat-label">Suivies</div><div className="stat-value">{(data?.counts.shortlisted ?? 0) + (data?.counts.proposal_prepared ?? 0) + (data?.counts.applied ?? 0) + (data?.counts.accepted ?? 0)}</div><div className="stat-foot">retenues, préparées ou en cours</div></div>
    </div>
    <section className="card card-pad mb-2">
      <div className="row between"><div><b>Analyse du cerveau IA local</b><div className="tiny faint">Classement selon vos mots-clés, faits de l’annonce et vérifications suggérées</div></div><span className="tiny faint">{review?.updated_at ? `Mise à jour ${formatDate(review.updated_at)}` : 'En attente du premier cycle'}</span></div>
      <div className="mt-2">{review?.content ? <Markdown text={review.content} /> : <p className="small muted">Le radar fournit les liens sans inventer de revenus. Au premier passage, le modèle IA local analysera les pistes et indiquera les points à vérifier. Configurez et téléchargez un modèle local dans Paramètres &gt; IA.</p>}</div>
    </section>
    <section className="card card-pad mb-2">
      <div className="row between wrap"><div><b>Mes pistes</b><div className="tiny faint">{items.length} affichée(s) · réglages du radar dans Automatisations</div></div>
        <div className="row wrap"><input className="input" style={{ minWidth: 200 }} value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Rechercher dans mes pistes…" aria-label="Rechercher dans mes pistes" />
          <select className="select" value={method} onChange={(e) => setMethod(e.target.value)} aria-label="Filtrer par méthode"><option value="all">Toutes les méthodes</option>{Object.entries(METHOD).map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select>
          <select className="select" value={status} onChange={(e) => setStatus(e.target.value)} aria-label="Filtrer par statut"><option value="all">Tous les statuts</option>{STATUS.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select>
        </div>
      </div>
    </section>
    {busy && !data ? <Loading /> : items.length === 0 ? <div className="card"><EmptyState icon={<Search size={24} />} title="Aucune piste pour l’instant" description="Lancez « Radar quotidien d’opportunités rémunérées » depuis Automatisations pour faire une recherche immédiate." /></div> : (
      <div className="stack" style={{ gap: 10 }}>
        {items.map((item) => <article className="card card-pad" key={item.id}>
          <div className="row between wrap" style={{ gap: 10 }}>
            <div className="row wrap"><span className="pill">{METHOD[item.method] || item.method}</span><span className="tiny faint">{item.source} · vu {formatDate(item.last_seen_at)}</span></div>
            <select className="select" value={item.status} onChange={(e) => update(item, { status: e.target.value as Status })} aria-label={`Statut : ${item.title}`}>
              {STATUS.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
            </select>
          </div>
          <h3 style={{ margin: '10px 0 5px' }}><a href={item.url} target="_blank" rel="noreferrer">{item.title || item.url}</a></h3>
          <p className="small muted" style={{ lineHeight: 1.55 }}>{item.snippet || 'Aucun extrait fourni par le moteur de recherche.'}</p>
          <div className="row between wrap tiny faint"><span>Repérée le {formatDate(item.first_seen_at)}</span><a className="btn ghost sm" href={item.url} target="_blank" rel="noreferrer"><ExternalLink size={12} /> Vérifier la source</a></div>
          <div className="row mt-2"><button className="btn sm" onClick={() => prepareDraft(item)} disabled={drafting === item.id}>{drafting === item.id ? <RefreshCw size={13} className="spin" /> : <Sparkles size={13} />}{drafting === item.id ? 'Préparation…' : item.proposal_draft ? 'Régénérer le brouillon' : 'Préparer une réponse avec l’IA locale'}</button></div>
          {item.proposal_draft && <div className="mt-2"><label className="tiny faint" htmlFor={`draft-${item.id}`}>Brouillon local · à relire et personnaliser avant envoi</label><textarea id={`draft-${item.id}`} className="input" style={{ width: '100%', minHeight: 190, marginTop: 6, resize: 'vertical' }} value={item.proposal_draft} onChange={(e) => setData((current) => current ? { ...current, items: current.items.map((entry) => entry.id === item.id ? { ...entry, proposal_draft: e.target.value } : entry) } : current)} /><button className="btn sm mt-1" onClick={() => update(item, { proposal_draft: data?.items.find((entry) => entry.id === item.id)?.proposal_draft || '' })}>Enregistrer le brouillon</button></div>}
          <div className="row wrap mt-2"><input className="input" style={{ flex: 1, minWidth: 230 }} value={notes[item.id] ?? ''} onChange={(e) => setNotes({ ...notes, [item.id]: e.target.value })} placeholder="Note privée : échéance, rémunération annoncée, prochaines étapes…" aria-label="Note de suivi" /><button className="btn sm" onClick={() => update(item, { note: notes[item.id] || '' })}>Enregistrer la note</button></div>
        </article>)}
      </div>
    )}
  </>
}
