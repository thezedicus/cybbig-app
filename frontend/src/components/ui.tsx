import {
  createContext, useCallback, useContext, useEffect, useMemo, useState,
  type ReactNode,
} from 'react'
import { AlertCircle, CheckCircle2, Info, X } from 'lucide-react'
import type { Severity, SeverityCounts } from '../types'

/* ------------------------------------------------------------------ toasts */

type ToastKind = 'success' | 'error' | 'info'
interface ToastItem { id: number; kind: ToastKind; message: string }
interface ToastApi { push: (message: string, kind?: ToastKind) => void }

const ToastContext = createContext<ToastApi>({ push: () => undefined })

export function ToastProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<ToastItem[]>([])
  const push = useCallback((message: string, kind: ToastKind = 'info') => {
    const id = Date.now() + Math.random()
    setItems((current) => [...current, { id, kind, message }])
    window.setTimeout(() => setItems((current) => current.filter((t) => t.id !== id)), 4800)
  }, [])
  const value = useMemo(() => ({ push }), [push])
  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="toast-wrap">
        {items.map((t) => (
          <div key={t.id} className={`toast ${t.kind}`}>
            {t.kind === 'success' ? <CheckCircle2 size={16} color="var(--green)" /> : t.kind === 'error' ? <AlertCircle size={16} color="var(--critical)" /> : <Info size={16} color="var(--accent)" />}
            <span>{t.message}</span>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  )
}

export function useToast() { return useContext(ToastContext) }

/* ------------------------------------------------------------------ badges */

const SEV_LABEL: Record<string, string> = {
  critical: 'Critique', high: 'Élevé', medium: 'Moyen', low: 'Faible', info: 'Info', unknown: 'Inconnu',
}

export function SeverityBadge({ severity, dot = false }: { severity: Severity | string; dot?: boolean }) {
  const key = (severity || 'info').toLowerCase()
  return (
    <span className={`badge ${key}`}>
      {dot && <span style={{ width: 5, height: 5, borderRadius: 99, background: 'currentColor' }} />}
      {SEV_LABEL[key] ?? key}
    </span>
  )
}

export function StatusPill({ status, label }: { status: string; label?: string }) {
  const text = label ?? ({
    queued: 'En attente', running: 'En cours', completed: 'Terminé', failed: 'Échec',
    blocked: 'Bloqué', cancelled: 'Annulé', open: 'Ouvert', acknowledged: 'Pris en compte',
    fixed: 'Corrigé', accepted_risk: 'Risque accepté', false_positive: 'Faux positif',
    never: 'Jamais', submitted: 'Soumis', ok: 'OK', error: 'Erreur',
  } as Record<string, string>)[status] ?? status
  return <span className={`pill ${status}`}>{text}</span>
}

/* ------------------------------------------------------------------ charts */

const SEV_COLOR: Record<string, string> = {
  critical: 'var(--critical)', high: 'var(--high)', medium: 'var(--medium)',
  low: 'var(--low)', info: 'var(--info)',
}

export function SeverityBar({ counts, showLegend = true }: { counts: SeverityCounts; showLegend?: boolean }) {
  const total = Object.values(counts).reduce((a, b) => a + b, 0)
  if (!total) {
    return <div className="sev-bar" aria-label="Aucun résultat" />
  }
  return (
    <div>
      <div className="sev-bar">
        {(['critical', 'high', 'medium', 'low', 'info'] as const).map((key) => (
          counts[key] > 0 ? (
            <i key={key} title={`${SEV_LABEL[key]} : ${counts[key]}`} style={{ width: `${(counts[key] / total) * 100}%`, background: SEV_COLOR[key] }} />
          ) : null
        ))}
      </div>
      {showLegend && (
        <div className="sev-legend">
          {(['critical', 'high', 'medium', 'low', 'info'] as const).map((key) => (
            <div className="sev-row" key={key}>
              <span className="sev-dot" style={{ background: SEV_COLOR[key] }} />
              <span>{SEV_LABEL[key]}</span>
              <b>{counts[key]}</b>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export function RiskGauge({ value, size = 132 }: { value: number; size?: number }) {
  const safe = Math.max(0, Math.min(100, value || 0))
  const radius = (size - 14) / 2
  const circumference = 2 * Math.PI * radius
  const dash = (safe / 100) * circumference
  const color = safe >= 70 ? 'var(--critical)' : safe >= 40 ? 'var(--high)' : safe >= 15 ? 'var(--medium)' : 'var(--green)'
  return (
    <div className="gauge" style={{ width: size, height: size }}>
      <svg width={size} height={size}>
        <circle cx={size / 2} cy={size / 2} r={radius} fill="none" stroke="#16293f" strokeWidth="9" />
        <circle
          cx={size / 2} cy={size / 2} r={radius} fill="none" stroke={color} strokeWidth="9"
          strokeLinecap="round" strokeDasharray={`${dash} ${circumference - dash}`}
          style={{ transition: 'stroke-dasharray .5s' }}
        />
      </svg>
      <div className="value"><div><b style={{ color }}>{safe.toFixed(0)}</b><span>risque</span></div></div>
    </div>
  )
}

export function TrendChart({ data }: { data: Array<{ date: string; total: number; critical: number; high: number }> }) {
  const max = Math.max(1, ...data.map((d) => d.total))
  return (
    <div className="trend" role="img" aria-label="Évolution des résultats sur 14 jours">
      {data.map((d) => {
        const height = Math.max(2, Math.round((d.total / max) * 100))
        const critShare = d.total ? (d.critical / d.total) * 100 : 0
        return (
          <div className="trend-col" key={d.date} title={`${d.date} — ${d.total} résultat(s), ${d.critical} critique(s), ${d.high} élevé(s)`}>
            <div style={{ height: 100, display: 'flex', alignItems: 'flex-end', width: '100%', justifyContent: 'center' }}>
              <div className={`trend-bar${critShare > 40 ? ' crit' : ''}`} style={{ height: `${height}%` }} />
            </div>
            <span className="trend-label">{d.date.slice(5).replace('-', '/')}</span>
          </div>
        )
      })}
    </div>
  )
}

/* ------------------------------------------------------------------ layout bits */

export function PageHeader({ title, description, actions }: { title: string; description?: string; actions?: ReactNode }) {
  return (
    <div className="page-header">
      <div>
        <h1>{title}</h1>
        {description && <p>{description}</p>}
      </div>
      {actions && <div className="page-actions">{actions}</div>}
    </div>
  )
}

export function EmptyState({ icon, title, description, action }: { icon?: ReactNode; title: string; description?: string; action?: ReactNode }) {
  return (
    <div className="empty">
      {icon}
      <h3>{title}</h3>
      {description && <p>{description}</p>}
      {action && <div className="mt-2">{action}</div>}
    </div>
  )
}

export function Loading({ label = 'Chargement…' }: { label?: string }) {
  return <div className="loading-block"><div className="spinner" /><span>{label}</span></div>
}

export function Progress({ value }: { value: number }) {
  return <div className="progress"><i style={{ width: `${Math.max(0, Math.min(100, value))}%` }} /></div>
}

/* ------------------------------------------------------------------ modal / drawer */

export function Modal({ open, title, subtitle, onClose, children, size = 'normal' }: {
  open: boolean; title: string; subtitle?: string; onClose: () => void; children: ReactNode
  size?: 'narrow' | 'normal' | 'wide'
}) {
  useEffect(() => {
    if (!open) return
    const onKey = (event: KeyboardEvent) => { if (event.key === 'Escape') onClose() }
    document.addEventListener('keydown', onKey)
    const previous = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    return () => { document.removeEventListener('keydown', onKey); document.body.style.overflow = previous }
  }, [open, onClose])
  if (!open) return null
  return (
    <div className="overlay" onMouseDown={(event) => { if (event.target === event.currentTarget) onClose() }}>
      <div className={`modal ${size !== 'normal' ? size : ''}`} role="dialog" aria-modal="true">
        <div className="modal-header">
          <div><h2>{title}</h2>{subtitle && <div className="sub">{subtitle}</div>}</div>
          <button className="modal-close" onClick={onClose} aria-label="Fermer"><X size={18} /></button>
        </div>
        <div className="modal-body">{children}</div>
      </div>
    </div>
  )
}

export function Drawer({ open, title, subtitle, onClose, children }: {
  open: boolean; title: ReactNode; subtitle?: string; onClose: () => void; children: ReactNode
}) {
  useEffect(() => {
    if (!open) return
    const onKey = (event: KeyboardEvent) => { if (event.key === 'Escape') onClose() }
    document.addEventListener('keydown', onKey)
    const previous = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    return () => { document.removeEventListener('keydown', onKey); document.body.style.overflow = previous }
  }, [open, onClose])
  if (!open) return null
  return (
    <div className="overlay" onMouseDown={(event) => { if (event.target === event.currentTarget) onClose() }}>
      <aside className="drawer" role="dialog" aria-modal="true">
        <div className="drawer-header">
          <h2>{title}</h2>
          {subtitle && <div className="small muted mt-1">{subtitle}</div>}
          <button className="modal-close drawer-close" onClick={onClose} aria-label="Fermer"><X size={18} /></button>
        </div>
        <div className="drawer-body">{children}</div>
      </aside>
    </div>
  )
}

/* ------------------------------------------------------------------ misc */

export function AlertBox({ kind = 'info', children }: { kind?: 'info' | 'error'; children: ReactNode }) {
  return (
    <div className={`alert-banner ${kind === 'error' ? 'error' : ''}`}>
      {kind === 'error' ? <AlertCircle size={16} /> : <Info size={16} />}
      <div>{children}</div>
    </div>
  )
}

export function CodeBlock({ code, label }: { code: string; label?: string }) {
  return (
    <div className="code-block">
      {label && <div className="code-label">{label}</div>}
      <pre>{code}</pre>
    </div>
  )
}
