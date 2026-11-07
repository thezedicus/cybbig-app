import { useCallback, useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { Check, Cloud, CloudCog, CloudOff } from 'lucide-react'
import { api } from '../api'
import { useToast } from './ui'
import type { OllamaStatus } from '../types'

type Mode = 'local' | 'training' | 'auto'
const MODES: Array<{ id: Mode; label: string; text: string }> = [
  { id: 'local', label: 'Coupé', text: 'Rien ne quitte ce PC : ni questions, ni projets, ni entraînement.' },
  { id: 'training', label: 'Entraînement seulement', text: 'Le chat reste local. Seule la bibliothèque de connaissances part chez le modèle en ligne pour entraîner le vôtre ; jamais vos projets.' },
  { id: 'auto', label: 'Actif', text: 'Le chat et les tâches IA utilisent aussi le modèle en ligne (questions et contexte de projet envoyés, secrets masqués).' },
]
const SHORT: Record<Mode, string> = { local: 'Cloud coupé', training: 'Cloud : entraînement', auto: 'Cloud actif' }

// Interrupteur du mode en ligne (barre du haut) : couper, n'autoriser que l'entraînement, ou tout autoriser.
export default function CloudSwitch() {
  const [status, setStatus] = useState<OllamaStatus | null>(null)
  const [open, setOpen] = useState(false)
  const [busy, setBusy] = useState(false)
  const ref = useRef<HTMLDivElement>(null)
  const toast = useToast()

  const load = useCallback(() => { api.get<OllamaStatus>('/api/assistant/status').then(setStatus).catch(() => undefined) }, [])
  useEffect(() => {
    load()
    const timer = window.setInterval(load, 30000)
    return () => window.clearInterval(timer)
  }, [load])
  useEffect(() => {
    if (!open) return
    const close = (event: MouseEvent) => { if (!ref.current?.contains(event.target as Node)) setOpen(false) }
    document.addEventListener('mousedown', close)
    return () => document.removeEventListener('mousedown', close)
  }, [open])

  const raw = status?.preferred
  const mode: Mode = raw === 'local' || raw === 'training' ? raw : 'auto'  // « cloud » seul est un réglage avancé : affiché comme actif
  const cloud = status?.cloud
  const Icon = mode === 'local' ? CloudOff : mode === 'training' ? CloudCog : Cloud

  const choose = async (next: Mode) => {
    setBusy(true)
    try {
      await api.put('/api/settings', { values: next === 'local' ? { ai_provider: 'local' } : { ai_provider: next, ai_allow_cloud: 'true' } })
      toast.push(next === 'local' ? 'Mode en ligne coupé : plus rien ne quitte ce PC.' : next === 'training' ? 'Entraînement en ligne autorisé, chat local.' : 'Mode en ligne actif.', 'success')
      load()
    } catch (err) { toast.push((err as Error).message, 'error') } finally { setBusy(false) }
  }

  return (
    <div ref={ref} style={{ position: 'relative' }}>
      <button className={`topbar-chip hide-sm${mode !== 'local' ? ' active' : ''}`} onClick={() => setOpen((v) => !v)} aria-haspopup="menu" aria-expanded={open}
        title="Mode en ligne (Ollama Cloud) : couper, entraînement seulement ou actif">
        <Icon size={13} /> {SHORT[mode]}
      </button>
      {open && (
        <div className="card" role="menu" style={{ position: 'absolute', right: 0, top: 42, width: 340, zIndex: 60 }}>
          <div className="card-header"><div><h2>Mode en ligne</h2>
            <div className="sub">{cloud?.available ? `Connecté : ${cloud.selected_model}` : cloud?.configured ? `Injoignable : ${cloud.error}` : 'Clé API non enregistrée'}</div></div></div>
          <div className="card-pad stack" style={{ gap: 6 }}>
            {MODES.map((item) => (
              <button key={item.id} role="menuitemradio" aria-checked={mode === item.id} disabled={busy} onClick={() => choose(item.id)} className="nav-link cat-link"
                style={{ alignItems: 'flex-start', border: '1px solid var(--line-soft)', background: mode === item.id ? 'var(--accent-soft)' : 'transparent' }}>
                {mode === item.id ? <Check size={14} color="var(--accent)" /> : <span style={{ width: 14 }} />}
                <span><b className="small">{item.label}</b><br /><span className="tiny faint">{item.text}</span></span>
              </button>
            ))}
            {!cloud?.configured && <Link to="/settings" className="tiny" onClick={() => setOpen(false)}>Enregistrer la clé API dans Paramètres &gt; IA en ligne</Link>}
          </div>
        </div>
      )}
    </div>
  )
}
