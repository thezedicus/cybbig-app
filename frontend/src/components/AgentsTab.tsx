import { useEffect, useState } from 'react'
import { Bot, Check, Play, RefreshCw, Settings2, X } from 'lucide-react'
import { api, adminApi, relativeDate } from '../api'
import { EmptyState, Loading, useToast } from './ui'

type Client = ReturnType<typeof adminApi>
type Guard = <T>(promise: Promise<T>) => Promise<T>
interface Agent { module: string; label: string; mission: string; last_run: string | null; new: number; applied: number; dismissed: number }
interface Suggestion {
  id: string; module: string; title: string; detail: string; kind: string; impact: string
  setting: { key: string; value: string } | null; status: string; model: string; created_at: string
}

const KIND_LABEL: Record<string, string> = { config: 'Réglage', rule: 'Règle', code: 'Code', process: 'Méthode' }

// Agents IA dédiés : un par module, chacun propose des améliorations de sa fonctionnalité.
export default function AgentsTab({ client, guard }: { client: Client; guard: Guard }) {
  const [agents, setAgents] = useState<Agent[] | null>(null)
  const [module, setModule] = useState('')
  const [showDone, setShowDone] = useState(false)
  const [items, setItems] = useState<Suggestion[] | null>(null)
  const toast = useToast()

  const load = () => {
    api.get<{ items: Agent[] }>('/api/ai/agents').then((d) => setAgents(d.items)).catch(() => undefined)
    const qs = new URLSearchParams()
    if (module) qs.set('module', module)
    if (!showDone) qs.set('status', 'new')
    api.get<{ items: Suggestion[] }>(`/api/ai/suggestions?${qs}`).then((d) => setItems(d.items)).catch(() => undefined)
  }
  useEffect(load, [module, showDone])

  const runAgent = async (name: string) => {
    try {
      const result = await api.post<{ queued: boolean }>(`/api/ai/agents/${name}/run`)
      toast.push(result.queued ? 'Agent mis en file : ses propositions arriveront d’ici une à deux minutes.' : 'Cet agent est déjà en file ou l’IA de fond est désactivée.', 'info')
    } catch (err) { toast.push((err as Error).message, 'error') }
  }

  const decide = async (item: Suggestion, action: 'apply' | 'done' | 'dismiss') => {
    try {
      await guard(client.post(`/api/admin/ai/suggestions/${item.id}/${action}`))
      toast.push(action === 'apply' ? `Réglage appliqué : ${item.setting?.key} = ${item.setting?.value}` : action === 'done' ? 'Marquée comme faite.' : 'Proposition écartée.', 'success')
      load()
    } catch (err) { toast.push((err as Error).message, 'error') }
  }

  return (
    <div className="stack" style={{ gap: 14 }}>
      <div className="grid auto">
        {!agents ? <Loading /> : agents.map((agent) => (
          <article key={agent.module} className={`card card-pad${module === agent.module ? ' selected' : ''}`} style={{ cursor: 'pointer', outline: module === agent.module ? '1px solid var(--accent)' : undefined }}
            onClick={() => setModule(module === agent.module ? '' : agent.module)}>
            <div className="row" style={{ gap: 8 }}>
              <div className="icon-wrap"><Bot size={14} /></div>
              <div style={{ minWidth: 0 }}>
                <div style={{ fontWeight: 650 }}>Agent {agent.label}</div>
                <div className="tiny faint">{agent.last_run ? `dernière passe ${relativeDate(agent.last_run)}` : 'jamais lancé'}</div>
              </div>
              {agent.new > 0 && <span className="nav-badge" style={{ marginLeft: 'auto' }}>{agent.new}</span>}
            </div>
            <p className="tiny muted" style={{ margin: '8px 0' }}>{agent.mission}</p>
            <div className="row between">
              <span className="tiny faint">{agent.applied} appliquée(s) · {agent.dismissed} écartée(s)</span>
              <button className="btn sm" onClick={(e) => { e.stopPropagation(); runAgent(agent.module) }}><Play size={12} /> Lancer</button>
            </div>
          </article>
        ))}
      </div>

      <section className="card">
        <div className="card-header">
          <div><h2>Propositions {module ? `de l’agent ${agents?.find((a) => a.module === module)?.label ?? module}` : 'de tous les agents'}</h2>
            <div className="sub">Les agents croisent les analyses et la base de connaissances. Les changements de code restent à valider dans l’onglet Code.</div></div>
          <div className="right">
            <label className="pill" style={{ cursor: 'pointer', gap: 6 }}><input type="checkbox" checked={showDone} onChange={(e) => setShowDone(e.target.checked)} /> Historique</label>
            <button className="btn ghost sm" onClick={load}><RefreshCw size={13} /> Actualiser</button>
          </div>
        </div>
        {!items ? <Loading /> : items.length === 0 ? (
          <EmptyState icon={<Bot size={26} />} title="Aucune proposition en attente"
            description="Les agents tournent automatiquement selon l’intensité choisie dans Paramètres. Vous pouvez aussi en lancer un tout de suite." />
        ) : (
          <div className="stack" style={{ gap: 10, padding: '4px 16px 16px' }}>
            {items.map((item) => (
              <article key={item.id} className="card card-pad" style={{ opacity: item.status === 'new' ? 1 : 0.6 }}>
                <div className="row wrap" style={{ gap: 6 }}>
                  <span className="tag">{agents?.find((a) => a.module === item.module)?.label ?? item.module}</span>
                  <span className="tag">{KIND_LABEL[item.kind] ?? item.kind}</span>
                  <span className={`pill ${item.impact === 'élevé' ? 'failed' : ''}`}>impact {item.impact}</span>
                  <span className="tiny faint" style={{ marginLeft: 'auto' }}>{relativeDate(item.created_at)} · {item.model}</span>
                </div>
                <div style={{ fontWeight: 650, marginTop: 6 }}>{item.title}</div>
                <p className="small muted" style={{ margin: '4px 0 8px', whiteSpace: 'pre-wrap' }}>{item.detail}</p>
                {item.setting && <div className="mono tiny" style={{ marginBottom: 8 }}><Settings2 size={11} /> {item.setting.key} = {item.setting.value}</div>}
                {item.status === 'new' ? (
                  <div className="row" style={{ gap: 6 }}>
                    {item.kind === 'config' && item.setting
                      ? <button className="btn primary sm" onClick={() => decide(item, 'apply')}><Check size={12} /> Appliquer le réglage</button>
                      : <button className="btn sm" onClick={() => decide(item, 'done')}><Check size={12} /> Marquer comme faite</button>}
                    <button className="btn ghost sm" onClick={() => decide(item, 'dismiss')}><X size={12} /> Écarter</button>
                  </div>
                ) : <span className="tiny faint">{item.status === 'applied' ? 'Appliquée' : 'Écartée'}</span>}
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  )
}
