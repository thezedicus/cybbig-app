import { useCallback, useEffect, useState } from 'react'
import { Cloud, Code2, Cpu, Download } from 'lucide-react'
import { api, streamNdjson } from '../api'
import { Progress, useToast } from './ui'
import type { OllamaStatus } from '../types'

interface PullEvent { status?: string; total?: number; completed?: number; error?: string }

// Modèles de code proposés au téléchargement : petits modèles locaux (CPU) et modèles « -cloud » servis par ollama.com.
const CATALOG = [
  { name: 'qwen2.5-coder:1.5b', note: 'Local · 1 Go · rapide sur processeur', cloud: false },
  { name: 'qwen2.5-coder:3b', note: 'Local · 1,9 Go · bon compromis', cloud: false },
  { name: 'qwen2.5-coder:7b', note: 'Local · 4,7 Go · 16 Go de RAM', cloud: false },
  { name: 'deepseek-coder:1.3b', note: 'Local · 0,8 Go · complétion', cloud: false },
  { name: 'starcoder2:3b', note: 'Local · 1,7 Go · multi-langages', cloud: false },
]

// Section « Modèles de code » : télécharge des modèles via Ollama et choisit ceux que le mode local et le mode en ligne utilisent.
export default function CodeModelsPanel({ values, setValue }: { values: Record<string, string>; setValue: (key: string, value: string) => void }) {
  const toast = useToast()
  const [status, setStatus] = useState<OllamaStatus | null>(null)
  const [pull, setPull] = useState<{ name: string; status: string; percent: number } | null>(null)
  const [custom, setCustom] = useState('')

  const refresh = useCallback(() => api.get<OllamaStatus>('/api/assistant/status?refresh=true').then(setStatus).catch(() => undefined), [])
  useEffect(() => { void refresh() }, [refresh])

  const localModels = status?.local?.models ?? []
  const onlineModels = [...new Set([...(status?.local?.daemon_cloud_models ?? []), ...(status?.cloud?.models ?? [])])]
  const installed = new Set([...localModels, ...onlineModels])

  const use = async (model: string, online: boolean) => {
    const key = online ? 'ai_model_code' : 'ai_model_code_local'
    try {
      await api.put('/api/settings', { values: { [key]: model } })
      setValue(key, model)
      toast.push(`Modèle de code ${online ? 'en ligne' : 'local'} : ${model}`, 'success')
      void refresh()
    } catch (err) { toast.push((err as Error).message, 'error') }
  }

  const download = async (name: string) => {
    name = name.trim()
    if (!name || pull) return
    setPull({ name, status: 'Connexion…', percent: 0 })
    let failed = ''
    try {
      await streamNdjson<PullEvent>('/api/assistant/models/pull', { model: name }, (event) => {
        if (event.error) { failed = event.error; return }
        setPull((cur) => ({ name, status: event.status ?? '', percent: event.total ? Math.round(((event.completed ?? 0) / event.total) * 100) : cur?.percent ?? 0 }))
      })
      if (failed) throw new Error(failed)
      toast.push(`Modèle ${name} installé.`, 'success')
      await refresh()
    } catch (err) { toast.push(`Téléchargement impossible : ${(err as Error).message}`, 'error') } finally { setPull(null) }
  }

  const row = (name: string, online: boolean) => {
    const current = (online ? values.ai_model_code : values.ai_model_code_local) === name
    return (
      <div key={name} className="row" style={{ gap: 8 }}>
        {online ? <Cloud size={13} /> : <Cpu size={13} />}
        <span className="cell-mono small">{name}</span>
        {current
          ? <span className="pill completed" style={{ marginLeft: 'auto' }}><Code2 size={11} /> modèle de code</span>
          : <button className="btn sm" style={{ marginLeft: 'auto' }} onClick={() => use(name, online)}>Utiliser pour le code</button>}
      </div>
    )
  }

  return (
    <div className="stack" style={{ gap: 10 }}>
      <div><b>Modèles de code</b><div className="tiny faint">Les modèles déjà installés sont listés ; le choix s’applique à l’atelier IA, au générateur et aux tâches de code.</div></div>
      <label className="checkbox">
        <input type="checkbox" checked={values.ai_auto_route !== 'false'} onChange={(e) => {
          const value = e.target.checked ? 'true' : 'false'
          api.put('/api/settings', { values: { ai_auto_route: value } }).then(() => setValue('ai_auto_route', value)).catch((err) => toast.push((err as Error).message, 'error'))
        }} />
        <span><b>Routage automatique</b> : une question de code, ou une commande en erreur dans le terminal, passe par le modèle de code ; le reste par le modèle de l’assistant</span>
      </label>
      <div className="stack" style={{ gap: 6 }}>
        <span className="tiny faint">Installés sur ce poste (mode local)</span>
        {localModels.length ? localModels.map((m) => row(m, false)) : <span className="tiny faint">Aucun modèle local détecté (Ollama est-il lancé ?).</span>}
        <span className="tiny faint" style={{ marginTop: 4 }}>Modèles en ligne disponibles</span>
        {onlineModels.length ? onlineModels.map((m) => row(m, true)) : <span className="tiny faint">Aucun (connectez Ollama avec « ollama signin » ou saisissez une clé).</span>}
      </div>
      <div className="stack" style={{ gap: 6 }}>
        <span className="tiny faint">Télécharger un modèle de code</span>
        {CATALOG.map((m) => (
          <div key={m.name} className="row" style={{ gap: 8 }}>
            <span className="cell-mono small">{m.name}</span><span className="tiny faint">{m.note}</span>
            {installed.has(m.name)
              ? <span className="pill completed" style={{ marginLeft: 'auto' }}>installé</span>
              : <button className="btn sm" style={{ marginLeft: 'auto' }} onClick={() => download(m.name)} disabled={!!pull}><Download size={12} /> {m.cloud ? 'Ajouter' : 'Télécharger'}</button>}
          </div>
        ))}
        <div className="row" style={{ gap: 8 }}>
          <input className="input mono" value={custom} onChange={(e) => setCustom(e.target.value)} placeholder="autre modèle : nom:taille" disabled={!!pull} />
          <button className="btn sm" onClick={() => download(custom)} disabled={!!pull || !custom.trim()}><Download size={12} /> Télécharger</button>
        </div>
        {pull && <div><Progress value={pull.percent} /><div className="tiny faint">{pull.name} · {pull.status} {pull.percent ? `· ${pull.percent} %` : ''}</div></div>}
      </div>
    </div>
  )
}
