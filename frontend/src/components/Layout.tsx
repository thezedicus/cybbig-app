import { useEffect, useRef, useState } from 'react'
import { Link, NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom'
import {
  Activity, Bell, BookOpen, Bot, Boxes, ChevronRight, ClipboardList, Coins, FileText,
  Fingerprint, FlaskConical, Gauge, GraduationCap, LayoutDashboard, Lock, Plus, Radar, Search, Settings, Terminal, Timer, Volume2, VolumeX, X, Zap,
} from 'lucide-react'
import logo from '../assets/logo.png'
import { api, relativeDate } from '../api'
import CloudSwitch from './CloudSwitch'
import { APPEARANCE_KEYS, applyAppearance, cacheAppearance, hiddenNav, readCachedAppearance, type Appearance } from '../appearance'
import { isAutoRead, onAutoReadChange, setAutoRead } from '../voice'
import type { Alert, OllamaStatus } from '../types'

const NAV = [
  { to: '/', label: 'Tableau de bord', icon: LayoutDashboard, section: 'Pilotage' },
  { to: '/scans', label: 'Analyses', icon: Activity, section: 'Pilotage' },
  { to: '/findings', label: 'Résultats', icon: ClipboardList, section: 'Pilotage' },
  { to: '/income', label: 'Opportunités', icon: Coins, section: 'Pilotage' },
  { to: '/projects', label: 'Projets', icon: Boxes, section: 'Périmètre' },
  { to: '/intel', label: 'Threat Intel', icon: Radar, section: 'Veille' },
  { to: '/knowledge', label: 'Connaissances', icon: BookOpen, section: 'Veille' },
  { to: '/web-search', label: 'Recherche web', icon: Search, section: 'Veille' },
  { to: '/assistant', label: 'Assistant IA', icon: Bot, section: 'Veille' },
  { to: '/training', label: 'Entraînement IA', icon: GraduationCap, section: 'Veille' },
  { to: '/reports', label: 'Rapports', icon: FileText, section: 'Livrables' },
  { to: '/automations', label: 'Automatisations', icon: Timer, section: 'Livrables' },
  { to: '/lab', label: 'Laboratoire', icon: FlaskConical, section: 'Livrables' },
  { to: '/terminal', label: 'Terminal', icon: Terminal, section: 'Livrables' },
  { to: '/privacy', label: 'Confidentialité', icon: Fingerprint, section: 'Système' },
  { to: '/settings', label: 'Paramètres', icon: Settings, section: 'Système' },
  { to: '/admin', label: 'Administration', icon: Lock, section: 'Système' },
]

const TITLES: Record<string, string> = {
  '/': 'Tableau de bord', '/scans': 'Analyses', '/findings': 'Résultats', '/income': 'Opportunités rémunérées', '/projects': 'Projets',
  '/intel': 'Threat Intelligence', '/knowledge': 'Base de connaissances', '/web-search': 'Recherche web', '/assistant': 'Assistant IA', '/training': 'Entraînement de l’IA',
  '/reports': 'Rapports', '/automations': 'Automatisations', '/lab': 'Laboratoire', '/terminal': 'Terminal interne', '/privacy': 'Confidentialité & Accessibilité', '/settings': 'Paramètres', '/admin': 'Administration',
}

export default function Layout() {
  const location = useLocation()
  const navigate = useNavigate()
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [panel, setPanel] = useState(false)
  const [health, setHealth] = useState<{ ok: boolean; ollama?: OllamaStatus }>({ ok: true })
  const [version, setVersion] = useState('')
  const panelRef = useRef<HTMLDivElement>(null)
  const [appearance, setAppearance] = useState<Partial<Appearance>>(readCachedAppearance)

  const loadAlerts = () => {
    api.get<{ items: Alert[] }>('/api/alerts?unread_only=true&limit=50')
      .then((data) => setAlerts(data.items))
      .catch(() => undefined)
  }

  useEffect(() => {
    loadAlerts()
    api.get<{ status: string; version?: string; ai: { available: boolean } }>('/api/health')
      .then((data) => { setHealth({ ok: data.status === 'ok' }); setVersion(data.version || '') })
      .catch(() => setHealth({ ok: false }))
    const timer = window.setInterval(loadAlerts, 45000)
    return () => window.clearInterval(timer)
  }, [])

  useEffect(() => { setPanel(false) }, [location.pathname])

  // Apparence choisie par le propriétaire : copie locale appliquée tout de suite, puis valeurs enregistrées.
  useEffect(() => {
    applyAppearance(readCachedAppearance())
    api.get<{ values: Record<string, string> }>('/api/settings').then((d) => {
      const saved: Partial<Appearance> = {}
      for (const key of APPEARANCE_KEYS) if (d.values[key] !== undefined) saved[key] = d.values[key]
      applyAppearance(saved); cacheAppearance(saved); setAppearance(saved)
    }).catch(() => undefined)
  }, [])

  const [activeMode, setActiveMode] = useState(false)
  const [autoRead, setAutoReadState] = useState(isAutoRead)
  useEffect(() => onAutoReadChange(setAutoReadState), [])
  // Relu à chaque navigation : le mode se change depuis l'onglet Administration.
  useEffect(() => {
    api.get<{ active: boolean }>('/api/mode').then((d) => setActiveMode(d.active)).catch(() => undefined)
  }, [location.pathname])

  useEffect(() => {
    const onClick = (event: MouseEvent) => {
      if (panelRef.current && !panelRef.current.contains(event.target as Node)) setPanel(false)
    }
    document.addEventListener('mousedown', onClick)
    return () => document.removeEventListener('mousedown', onClick)
  }, [])

  const hidden = hiddenNav(appearance)
  const group = (section: string) => NAV.filter((item) => item.section === section && !hidden.includes(item.to))
  const title = TITLES[location.pathname] ?? (location.pathname.startsWith('/scans/') ? 'Détail de l’analyse'
    : location.pathname.startsWith('/projects/') ? 'Détail du projet'
      : location.pathname.startsWith('/lab/') ? 'Scénario de laboratoire' : 'Cybbig')

  const markAllRead = async () => {
    await api.post('/api/alerts/read-all')
    setAlerts([])
  }

  const openAlert = async (alert: Alert) => {
    try { await api.patch(`/api/alerts/${alert.id}/read`) } catch { /* ignore */ }
    setAlerts((current) => current.filter((a) => a.id !== alert.id))
    setPanel(false)
    if (alert.link) navigate(alert.link)
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <img className="brand-logo" src={logo} alt="" />
          <div className="brand-text">
            <div className="brand-name">CYBBIG</div>
            <div className="brand-sub">Défense locale</div>
          </div>
        </div>
        {['Pilotage', 'Périmètre', 'Veille', 'Livrables', 'Système'].filter((section) => group(section).length > 0).map((section) => (
          <div key={section}>
            <div className="nav-section">{section}</div>
            {group(section).map((item) => (
              <NavLink key={item.to} to={item.to} end={item.to === '/'} className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}>
                <item.icon size={17} />
                <span>{item.label}</span>
                {item.to === '/findings' && alerts.length > 0 && <span className="nav-badge">{alerts.length}</span>}
              </NavLink>
            ))}
          </div>
        ))}
        <div className="sidebar-footer">
          <div className="sidebar-status">
            <span className={`status-dot ${health.ok ? '' : 'off'}`} />
            <span className="text">{health.ok ? 'Backend local actif' : 'Backend injoignable'}</span>
          </div>
          <div className="text">Cybbig{version ? ` ${version}` : ''} · 127.0.0.1</div>
        </div>
      </aside>

      <div className="app-main">
        <header className="topbar">
          <div className="topbar-title"><span className="topbar-crumb">Cybbig /</span>{title}</div>
          <div className="topbar-right">
            <button className={`topbar-chip mode-chip hide-sm${activeMode ? ' active' : ''}`} onClick={() => navigate('/admin')}
              title={activeMode ? 'Mode actif : contrôles non destructifs dans le périmètre autorisé. Modifiable dans Administration.' : 'Mode passif. Le mode actif s’active dans Administration.'}>
              {activeMode ? <Zap size={13} /> : <Gauge size={13} />} {activeMode ? 'Mode actif' : 'Mode passif'}
            </button>
            <CloudSwitch />
            <button className="btn sm hide-sm" onClick={() => navigate('/automations')} title="Créer et gérer les tâches récurrentes"><Timer size={14} /> Automatisations</button>
            <button className={`icon-btn${autoRead ? ' on' : ''}`} onClick={() => setAutoRead(!autoRead)}
              title={autoRead ? 'Lecture vocale des réponses IA : activée' : 'Lecture vocale des réponses IA : désactivée'} aria-pressed={autoRead}>
              {autoRead ? <Volume2 size={16} color="var(--accent)" /> : <VolumeX size={16} />}
            </button>
            <button className="btn primary sm" onClick={() => navigate('/scans?launch=1')}><Plus size={14} /> Nouvelle analyse</button>
            <button className="icon-btn" onClick={() => navigate('/settings')} aria-label="Paramètres" title="Paramètres"><Settings size={16} /></button>
            <div ref={panelRef} style={{ position: 'relative' }}>
              <button className="icon-btn" onClick={() => setPanel((open) => !open)} aria-label="Alertes">
                <Bell size={16} />
                {alerts.length > 0 && <span className="dot" />}
              </button>
              {panel && (
                <div className="card" style={{ position: 'absolute', right: 0, top: 42, width: 360, maxHeight: 430, overflow: 'auto', zIndex: 60 }}>
                  <div className="card-header">
                    <div><h2>Alertes</h2><div className="sub">{alerts.length} non lue(s)</div></div>
                    <div className="right">
                      {alerts.length > 0 && <button className="btn ghost sm" onClick={markAllRead}>Tout lire</button>}
                      <button className="modal-close" onClick={() => setPanel(false)}><X size={16} /></button>
                    </div>
                  </div>
                  {alerts.length === 0 ? (
                    <div className="empty" style={{ padding: '26px 18px' }}><Bell size={24} /><p>Aucune alerte non lue.</p></div>
                  ) : (
                    <div style={{ padding: '4px 14px 10px' }}>
                      {alerts.map((alert) => (
                        <button key={alert.id} onClick={() => openAlert(alert)} style={{
                          display: 'block', width: '100%', textAlign: 'left', background: 'none',
                          border: 0, borderBottom: '1px solid var(--line-soft)', padding: '11px 2px', cursor: 'pointer',
                        }}>
                          <div className="row" style={{ gap: 6 }}>
                            <span className={`badge ${alert.severity}`}>{alert.severity}</span>
                            <span className="tiny faint" style={{ marginLeft: 'auto' }}>{relativeDate(alert.created_at)}</span>
                          </div>
                          <div style={{ fontSize: 12.5, fontWeight: 600, marginTop: 5 }}>{alert.title}</div>
                          <div className="tiny faint clamp-2" style={{ marginTop: 2 }}>{alert.message}</div>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </header>
        <main className="page">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export function SectionLink({ to, children }: { to: string; children: React.ReactNode }) {
  return <Link to={to} className="row" style={{ gap: 4, fontSize: 12 }}>{children}<ChevronRight size={13} /></Link>
}
