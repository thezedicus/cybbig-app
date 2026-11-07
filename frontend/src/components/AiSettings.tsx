import { useEffect, useState } from 'react'
import { BrainCircuit, RefreshCw } from 'lucide-react'
import { api, relativeDate } from '../api'

interface AiStatus {
  enabled: boolean
  running: boolean
  boost: string
  boosts: Record<string, string>
  sections: Record<string, { label: string; enabled: boolean }>
  queue: Array<{ key: string; task: string }>
  queue_size: number
  current: { key: string; task: string; started_at: string } | null
  processed: number
  failed: number
  last_error: string
  last_done_at: string | null
}

const TASK_LABEL: Record<string, string> = {
  scan_summary: 'Synthèse d’analyse', finding_triage: 'Triage d’un résultat', intel_digest: 'Digest de veille',
  dashboard_priorities: 'Plan de la semaine', agent: 'Agent d’amélioration',
}

// Section « IA intégrée » des Paramètres : les valeurs passent par le formulaire commun (values/setValue).
export default function AiSettings({ values, setValue }: { values: Record<string, string>; setValue: (key: string, value: string) => void }) {
  const [status, setStatus] = useState<AiStatus | null>(null)
  const load = () => { api.get<AiStatus>('/api/ai/status').then(setStatus).catch(() => undefined) }
  useEffect(() => {
    load()
    const timer = window.setInterval(load, 10000)
    return () => window.clearInterval(timer)
  }, [])
  const on = (key: string) => (values[key] ?? 'true') !== 'false'

  return (
    <section className="card">
      <div className="card-header">
        <div><h2>IA intégrée</h2><div className="sub">Le modèle local travaille en continu dans chaque module</div></div>
        <BrainCircuit size={16} style={{ marginLeft: 'auto', color: 'var(--accent)' }} />
      </div>
      <div className="card-pad stack" style={{ gap: 12 }}>
        <label className="checkbox">
          <input type="checkbox" checked={on('ai_auto')} onChange={(e) => setValue('ai_auto', e.target.checked ? 'true' : 'false')} />
          <span><b>Moteur IA de fond</b> : synthèses, triages, veille et agents d’amélioration s’exécutent automatiquement à partir des analyses et des connaissances locales</span>
        </label>
        <div className="field">
          <label htmlFor="ai-boost">Intensité</label>
          <select id="ai-boost" className="select" value={values.ai_boost || 'balanced'} onChange={(e) => setValue('ai_boost', e.target.value)}>
            <option value="eco">Économe : 3 triages par analyse, plan et agents toutes les 24 h</option>
            <option value="balanced">Équilibré : 8 triages par analyse, plan toutes les 6 h, agents toutes les 8 h</option>
            <option value="intense">Intensif : 20 triages par analyse, plan et agents toutes les 2 h, réponses plus longues</option>
          </select>
          <span className="hint">Les agents proposent des réglages ou des corrections ; le code et les actions sensibles demandent toujours une validation. Sans carte graphique, l’intensif sollicite fortement le processeur.</span>
        </div>
        <div className="stack" style={{ gap: 6 }}>
          {Object.entries(status?.sections ?? {}).map(([key, section]) => (
            <label key={key} className="checkbox">
              <input type="checkbox" checked={on(key)} disabled={!on('ai_auto')} onChange={(e) => setValue(key, e.target.checked ? 'true' : 'false')} />
              <span>{section.label}</span>
            </label>
          ))}
        </div>
        {status && (
          <div className="kv-list">
            <div className="kv-item"><span>État</span><b>{!status.enabled ? 'Désactivé' : status.running ? 'En marche' : 'Arrêté'}</b></div>
            <div className="kv-item"><span>En cours</span><b>{status.current ? `${TASK_LABEL[status.current.task] ?? status.current.task} (${relativeDate(status.current.started_at)})` : '—'}</b></div>
            <div className="kv-item"><span>En attente</span><b>{status.queue_size}{status.queue.length ? ` · ${status.queue.slice(0, 3).map((q) => TASK_LABEL[q.task] ?? q.task).join(', ')}` : ''}</b></div>
            <div className="kv-item"><span>Traitées / échecs</span><b>{status.processed} / {status.failed}</b></div>
            <div className="kv-item"><span>Dernière tâche</span><b>{status.last_done_at ? relativeDate(status.last_done_at) : '—'}</b></div>
            {status.last_error && <div className="kv-item"><span>Dernière erreur</span><b className="tiny" style={{ color: 'var(--high)' }}>{status.last_error}</b></div>}
          </div>
        )}
        <div className="row" style={{ gap: 8 }}>
          <button type="button" className="btn sm" onClick={load}><RefreshCw size={13} /> Actualiser</button>
          <span className="tiny faint">Enregistrez la page pour appliquer les changements.</span>
        </div>
      </div>
    </section>
  )
}
