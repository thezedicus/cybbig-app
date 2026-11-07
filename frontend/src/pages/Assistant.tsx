import { useEffect, useRef, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import {
  Bot, BrainCircuit, Check, CheckCircle2, CircleOff, Copy, Download, Eraser, Send, ShieldCheck, Square, User, X,
} from 'lucide-react'
import { api, formatDate, streamNdjson } from '../api'
import Markdown from '../components/Markdown'
import { speakIfEnabled } from '../voice'
import { AlertBox, Loading, PageHeader, Progress, SeverityBadge, useToast } from '../components/ui'
import type { AssistantMessage, Finding, OllamaStatus, Project } from '../types'

interface UiMessage extends AssistantMessage {
  sources?: Array<{ id: string; title: string; category: string }>
  offline?: boolean
  provider?: string
  streaming?: boolean
}

type ChatEvent =
  | { type: 'meta'; sources: UiMessage['sources']; model: string; provider?: string }
  | { type: 'token'; content: string }
  | { type: 'notice'; content: string; provider?: string }
  | { type: 'done'; model: string; provider?: string; offline: boolean; ollama: OllamaStatus }

interface PullEvent { status?: string; total?: number; completed?: number; error?: string }

const RECOMMENDED = [
  { name: 'qwen2.5-coder:7b', note: 'Code · 4,7 Go · 16 Go de RAM' },
  { name: 'qwen2.5-coder:3b', note: 'Code · 1,9 Go · plus rapide' },
  { name: 'qwen2.5:7b', note: 'Généraliste · 4,7 Go' },
  { name: 'llama3.2:3b', note: 'Généraliste · 2,0 Go' },
]

const SUGGESTIONS = [
  'Comment prioriser les résultats critiques de mon projet ?',
  'Corrige ce code PHP vulnérable à l’injection SQL et explique la correction.',
  'Explique les indicateurs de skimming détectés sur le checkout.',
  'Quels contrôles vérifier sur une API OpenAPI financière ?',
]

export default function Assistant() {
  const [params, setParams] = useSearchParams()
  const [messages, setMessages] = useState<UiMessage[]>([])
  const [status, setStatus] = useState<OllamaStatus | null>(null)
  const [projects, setProjects] = useState<Project[]>([])
  const [projectId, setProjectId] = useState('')
  const [finding, setFinding] = useState<Finding | null>(null)
  const [input, setInput] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [pullName, setPullName] = useState(RECOMMENDED[0].name)
  const [pull, setPull] = useState<{ status: string; percent: number } | null>(null)
  const abortRef = useRef<AbortController | null>(null)
  const endRef = useRef<HTMLDivElement>(null)
  const toast = useToast()
  const findingId = params.get('finding')

  const loadStatus = () => api.get<OllamaStatus>('/api/assistant/status').then(setStatus).catch(() => undefined)

  useEffect(() => {
    api.get<{ items: AssistantMessage[] }>('/api/assistant/history?limit=80')
      .then((d) => setMessages(d.items)).catch((e) => setError((e as Error).message))
    loadStatus()
    api.get<{ items: Project[] }>('/api/projects').then((d) => {
      setProjects(d.items)
      if (d.items[0] && !findingId) setProjectId(d.items[0].id)
    }).catch(() => undefined)
    return () => abortRef.current?.abort()
  }, [])

  useEffect(() => {
    if (!findingId) { setFinding(null); return }
    api.get<Finding>(`/api/findings/${findingId}`).then((f) => {
      setFinding(f)
      setProjectId(f.project_id)
      setInput((current) => current || 'Explique ce résultat, son impact réel et donne la correction avec le code corrigé.')
    }).catch(() => setParams({}))
  }, [findingId])

  useEffect(() => { endRef.current?.scrollIntoView({ block: 'end' }) }, [messages])

  const send = async (text: string) => {
    text = text.trim()
    if (!text || busy) return
    setInput('')
    const now = Date.now()
    const answerId = now + 1
    setMessages((current) => [
      ...current,
      { id: now, role: 'user', content: text, model: '', created_at: new Date().toISOString() },
      { id: answerId, role: 'assistant', content: '', model: '', created_at: new Date().toISOString(), streaming: true },
    ])
    const update = (patch: (m: UiMessage) => Partial<UiMessage>) =>
      setMessages((current) => current.map((m) => (m.id === answerId ? { ...m, ...patch(m) } : m)))
    setBusy(true)
    const controller = new AbortController()
    let answer = ''
    abortRef.current = controller
    try {
      await streamNdjson<ChatEvent>('/api/assistant/chat/stream', {
        message: text, project_id: projectId || null, finding_id: finding?.id ?? null,
        model: status?.selected_model || null,
      }, (event) => {
        if (event.type === 'meta') update(() => ({ sources: event.sources, model: event.model, provider: event.provider }))
        else if (event.type === 'notice') toast.push(event.content, 'info')
        else if (event.type === 'token') { answer += event.content; update((m) => ({ content: m.content + event.content })) }
        else if (event.type === 'done') { update(() => ({ model: event.model, offline: event.offline, provider: event.provider })); setStatus((current) => ({ ...(current ?? event.ollama), ...event.ollama })); speakIfEnabled(answer) }
      }, controller.signal)
    } catch (err) {
      if ((err as Error).name === 'AbortError') {
        update((m) => ({ content: `${m.content}\n\n_(Génération arrêtée)_` }))
      } else {
        toast.push((err as Error).message, 'error')
        setMessages((current) => current.filter((m) => m.id !== answerId && m.id !== now))
        setInput(text)
      }
    } finally {
      update(() => ({ streaming: false }))
      setBusy(false)
      abortRef.current = null
    }
  }

  const clear = async () => {
    if (!window.confirm('Effacer tout l’historique de conversation ?')) return
    try { await api.del('/api/assistant/history'); setMessages([]); toast.push('Historique effacé.', 'success') }
    catch (err) { toast.push((err as Error).message, 'error') }
  }

  const selectModel = async (model: string) => {
    try {
      setStatus(await api.put<OllamaStatus>('/api/assistant/model', { model, provider: status?.provider === 'cloud' ? 'cloud' : 'local' }))
      toast.push(`Modèle actif : ${model}`, 'success')
    } catch (err) { toast.push((err as Error).message, 'error') }
  }

  const pullModel = async () => {
    const name = pullName.trim()
    if (!name || pull) return
    setPull({ status: 'Connexion…', percent: 0 })
    let failed = ''
    try {
      await streamNdjson<PullEvent>('/api/assistant/models/pull', { model: name }, (event) => {
        if (event.error) { failed = event.error; return }
        const percent = event.total ? Math.round(((event.completed ?? 0) / event.total) * 100) : 0
        setPull((current) => ({ status: event.status ?? '', percent: event.total ? percent : current?.percent ?? 0 }))
      })
      if (failed) throw new Error(failed)
      toast.push(`Modèle ${name} installé.`, 'success')
      const fresh = await api.get<OllamaStatus>('/api/assistant/status')
      setStatus(fresh)
      if (fresh.models.includes(name)) await selectModel(name)
    } catch (err) {
      toast.push(`Téléchargement impossible : ${(err as Error).message}`, 'error')
    } finally {
      setPull(null)
    }
  }

  const copy = async (text: string) => {
    try { await navigator.clipboard.writeText(text); toast.push('Réponse copiée.', 'success') } catch { /* refusé */ }
  }

  return (
    <>
      <PageHeader
        title="Assistant IA local"
        description="Analyse vos résultats, corrige du code et explique les vulnérabilités avec votre modèle Ollama local. Un mode déterministe prend le relais hors ligne."
        actions={<button className="btn ghost" onClick={clear}><Eraser size={14} /> Effacer l’historique</button>}
      />

      {error && <AlertBox kind="error">{error}</AlertBox>}

      <div className="chat-layout">
        <div className="card chat-panel">
          <div className="card-header">
            <div className="brand-mark" style={{ width: 32, height: 32 }}><Bot size={17} /></div>
            <div><h2>Cybbig Analyst</h2><div className="sub">{status?.available && status.selected_model ? `${status.selected_model}${status.provider === 'cloud' ? ' · en ligne' : ' · local'}` : 'Mode déterministe'} · mémoire des 4 derniers échanges</div></div>
            <div className="right">
              <select className="select" style={{ width: 'auto' }} value={projectId} onChange={(e) => setProjectId(e.target.value)}>
                <option value="">Tous les projets</option>
                {projects.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
              </select>
            </div>
          </div>

          <div className="chat-messages">
            {messages.length === 0 && (
              <div className="empty" style={{ margin: 'auto' }}>
                <BrainCircuit size={38} />
                <h3>Posez une question ou collez du code</h3>
                <p>L’assistant utilise vos résultats, vos documents et votre modèle local. Il ne remplace pas une revue humaine.</p>
                <div className="grid cols-2 mt-3" style={{ textAlign: 'left' }}>
                  {SUGGESTIONS.map((s) => (
                    <button key={s} className="btn sm" style={{ justifyContent: 'flex-start', whiteSpace: 'normal', textAlign: 'left' }} onClick={() => setInput(s)}>{s}</button>
                  ))}
                </div>
              </div>
            )}
            {messages.map((message) => (
              <div key={message.id} className={`msg ${message.role}`}>
                <div className="msg-avatar">{message.role === 'user' ? <User size={14} /> : <Bot size={14} />}</div>
                <div style={{ minWidth: 0 }}>
                  <div className={`msg-bubble${message.role === 'assistant' ? ' md-bubble' : ''}`}>
                    {message.role === 'assistant'
                      ? (message.content ? <Markdown text={message.content} /> : <span className="faint"><span className="spinner" style={{ width: 13, height: 13, display: 'inline-block', verticalAlign: 'middle', marginRight: 8 }} />Réflexion…</span>)
                      : message.content}
                    {message.streaming && message.content && <span className="md-caret" />}
                  </div>
                  <div className="row tiny faint mt-1" style={{ gap: 8 }}>
                    <span>{formatDate(message.created_at)}</span>
                    {message.role === 'assistant' && !message.streaming && <span>{message.offline || message.model === 'fallback' ? 'mode déterministe' : `${message.model}${message.provider === 'cloud' ? ' · en ligne' : ''}`}</span>}
                    {message.sources?.length ? <span title={message.sources.map((s) => s.title).join('\n')}>{message.sources.length} source(s)</span> : null}
                    {message.role === 'assistant' && !message.streaming && message.content && (
                      <button className="link-btn" onClick={() => copy(message.content)}><Copy size={11} /> Copier</button>
                    )}
                  </div>
                </div>
              </div>
            ))}
            <div ref={endRef} />
          </div>

          {finding && (
            <div className="chat-focus">
              <SeverityBadge severity={finding.severity} />
              <span className="small" style={{ minWidth: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>À propos de : <b>{finding.title}</b></span>
              <button className="icon-btn" style={{ width: 24, height: 24, marginLeft: 'auto' }} title="Retirer" onClick={() => setParams({})}><X size={12} /></button>
            </div>
          )}

          <form className="chat-input" onSubmit={(e) => { e.preventDefault(); send(input) }}>
            <textarea className="textarea" placeholder="Votre question ou votre code… (Entrée pour envoyer, Maj+Entrée pour une nouvelle ligne)" value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(input) } }} />
            {busy
              ? <button className="btn" type="button" onClick={() => abortRef.current?.abort()}><Square size={13} /> Stop</button>
              : <button className="btn primary" type="submit" disabled={!input.trim()}><Send size={15} /> Envoyer</button>}
          </form>
        </div>

        <div className="stack chat-side" style={{ gap: 14 }}>
          <div className="card">
            <div className="card-header"><h2>Modèle</h2></div>
            <div className="card-pad" style={{ paddingTop: 6 }}>
              {!status ? <Loading label="Vérification…" /> : (
                <>
                  <div className="row" style={{ gap: 8 }}>
                    {status.available ? <CheckCircle2 size={16} color="var(--green)" /> : <CircleOff size={16} color="var(--high)" />}
                    <b className="small">{status.available ? (status.provider === 'cloud' ? 'IA en ligne connectée' : 'Ollama local connecté') : 'Aucun modèle joignable'}</b>
                  </div>
                  <div className="tiny faint mono mt-1">{status.url}</div>
                  {status.models.length > 0 ? (
                    <div className="field mt-2">
                      <label>Modèle actif</label>
                      <select className="select" value={status.selected_model} onChange={(e) => selectModel(e.target.value)}>
                        {status.models.map((m) => <option key={m} value={m}>{m}</option>)}
                      </select>
                    </div>
                  ) : status.available && (
                    <div className="tiny mt-2" style={{ color: 'var(--high)' }}>Aucun modèle installé : téléchargez-en un ci-dessous.</div>
                  )}
                  {status.error && <div className="tiny mt-2" style={{ color: 'var(--high)' }}>{status.error}</div>}
                </>
              )}
            </div>
          </div>

          {status?.available && status.provider !== 'cloud' && (
            <div className="card">
              <div className="card-header"><h2>Télécharger un modèle</h2></div>
              <div className="card-pad stack" style={{ paddingTop: 6, gap: 8 }}>
                {RECOMMENDED.map((m) => (
                  <label key={m.name} className="checkbox" style={{ alignItems: 'flex-start' }}>
                    <input type="radio" name="pull" checked={pullName === m.name} onChange={() => setPullName(m.name)} disabled={!!pull} />
                    <span><span className="mono small">{m.name}</span>{status.models.includes(m.name) && <Check size={12} color="var(--green)" style={{ marginLeft: 4 }} />}<br /><span className="tiny faint">{m.note}</span></span>
                  </label>
                ))}
                <input className="input mono" value={pullName} onChange={(e) => setPullName(e.target.value)} disabled={!!pull} placeholder="nom:taille" />
                {pull ? (
                  <div className="stack" style={{ gap: 4 }}>
                    <Progress value={pull.percent} />
                    <div className="tiny faint">{pull.status} {pull.percent ? `· ${pull.percent} %` : ''}</div>
                  </div>
                ) : (
                  <button className="btn sm" onClick={pullModel} disabled={!pullName.trim()}><Download size={13} /> Télécharger</button>
                )}
              </div>
            </div>
          )}

          <div className="card card-pad">
            <div className="row" style={{ gap: 7 }}><ShieldCheck size={15} color="var(--accent)" /><b className="small">Garde-fous</b></div>
            <ul className="refs mt-2" style={{ color: 'var(--muted)', paddingLeft: 16 }}>
              <li>Aucune instruction d’exploitation contre des tiers.</li>
              <li>Le modèle tourne sur ce PC : vos données ne partent pas sur Internet.</li>
              <li>Les réponses distinguent faits, hypothèses et limites.</li>
              <li>Validation humaine obligatoire avant correction.</li>
            </ul>
          </div>
        </div>
      </div>
    </>
  )
}
