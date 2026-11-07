import { useEffect, useRef, useState } from 'react'
import { Copy, Sparkles, Square, Volume2 } from 'lucide-react'
import { api, relativeDate, streamNdjson } from '../api'
import { speak, speakIfEnabled } from '../voice'
import Markdown from './Markdown'
import { useToast } from './ui'

type AiEvent =
  | { type: 'meta'; model: string }
  | { type: 'token'; content: string }
  | { type: 'done'; model: string; offline: boolean }

// Panneau réutilisable : lance une tâche IA côté serveur et affiche la réponse au fil de l'eau.
export default function AiPanel({ task, params, label, title, endpoint = '/api/ai/run', headers, autoStart = false, compact = false, cacheKey, initialText }: {
  task: string
  params: Record<string, unknown>
  label: string
  title?: string
  endpoint?: string
  headers?: Record<string, string>
  autoStart?: boolean
  compact?: boolean
  cacheKey?: string // résultat déjà produit par le moteur IA de fond
  initialText?: string
}) {
  const [text, setText] = useState(initialText ?? '')
  const [model, setModel] = useState('')
  const [offline, setOffline] = useState(false)
  const [running, setRunning] = useState(false)
  const [generatedAt, setGeneratedAt] = useState('')

  useEffect(() => {
    if (!cacheKey || initialText) return
    api.get<{ item: { content: string; model: string; created_at: string } | null }>(`/api/ai/cache/${encodeURIComponent(cacheKey)}`)
      .then((d) => {
        if (d.item?.content) { setText(d.item.content); setModel(d.item.model); setGeneratedAt(d.item.created_at) }
      })
      .catch(() => undefined)
  }, [cacheKey])
  const abortRef = useRef<AbortController | null>(null)
  const toast = useToast()

  const run = async () => {
    if (running) return
    setText(''); setModel(''); setGeneratedAt(''); setRunning(true)
    const controller = new AbortController()
    abortRef.current = controller
    let full = ''
    try {
      await streamNdjson<AiEvent>(endpoint, { task, params }, (event) => {
        if (event.type === 'meta') setModel(event.model)
        else if (event.type === 'token') { full += event.content; setText(full) }
        else if (event.type === 'done') { setModel(event.model); setOffline(event.offline) }
      }, controller.signal, headers)
      speakIfEnabled(full)
    } catch (err) {
      if ((err as Error).name !== 'AbortError') toast.push((err as Error).message, 'error')
    } finally {
      setRunning(false)
      abortRef.current = null
    }
  }

  useEffect(() => {
    if (autoStart) run()
    return () => abortRef.current?.abort()
  }, [])

  return (
    <div className={`ai-panel${compact ? ' compact' : ''}`}>
      <div className="ai-panel-head">
        <Sparkles size={14} />
        <b className="small">{title ?? 'Analyse IA'}</b>
        {model && !running && <span className="tiny faint">{offline || model === 'fallback' ? 'sans modèle' : model}</span>}
        {generatedAt && !running && <span className="tiny faint">· généré automatiquement {relativeDate(generatedAt)}</span>}
        <div className="right" style={{ marginLeft: 'auto', display: 'flex', gap: 6 }}>
          {text && !running && (
            <>
              <button className="icon-btn" style={{ width: 26, height: 26 }} title="Lire à voix haute" onClick={() => speak(text)}><Volume2 size={12} /></button>
              <button className="icon-btn" style={{ width: 26, height: 26 }} title="Copier" onClick={() => navigator.clipboard.writeText(text).then(() => toast.push('Copié.', 'success')).catch(() => undefined)}><Copy size={12} /></button>
            </>
          )}
          {running
            ? <button className="btn sm" onClick={() => abortRef.current?.abort()}><Square size={12} /> Stop</button>
            : <button className="btn primary sm" onClick={run}><Sparkles size={12} /> {text ? 'Relancer' : label}</button>}
        </div>
      </div>
      {(text || running) && (
        <div className="ai-panel-body">
          {text ? <Markdown text={text} /> : <span className="faint small"><span className="spinner" style={{ width: 12, height: 12, display: 'inline-block', verticalAlign: 'middle', marginRight: 8 }} />Le modèle local réfléchit… (jusqu’à une minute sans carte graphique)</span>}
        </div>
      )}
    </div>
  )
}
