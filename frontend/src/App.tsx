import { Suspense, lazy, useCallback, useEffect, useState } from 'react'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { RefreshCw, ShieldAlert } from 'lucide-react'
import { api } from './api'
import Layout from './components/Layout'
import { Loading, ToastProvider } from './components/ui'
import Consent from './pages/Consent'
const Admin = lazy(() => import('./pages/Admin'))
const Assistant = lazy(() => import('./pages/Assistant'))
const Automations = lazy(() => import('./pages/Automations'))
const Dashboard = lazy(() => import('./pages/Dashboard'))
const Findings = lazy(() => import('./pages/Findings'))
const Income = lazy(() => import('./pages/Income'))
const Intel = lazy(() => import('./pages/Intel'))
const Knowledge = lazy(() => import('./pages/Knowledge'))
const Lab = lazy(() => import('./pages/Lab'))
const LabDetail = lazy(() => import('./pages/LabDetail'))
const Privacy = lazy(() => import('./pages/Privacy'))
const ProjectDetail = lazy(() => import('./pages/ProjectDetail'))
const Projects = lazy(() => import('./pages/Projects'))
const Reports = lazy(() => import('./pages/Reports'))
const ScanDetail = lazy(() => import('./pages/ScanDetail'))
const Scans = lazy(() => import('./pages/Scans'))
const Settings = lazy(() => import('./pages/Settings'))
const TerminalPage = lazy(() => import('./pages/Terminal'))
const Training = lazy(() => import('./pages/Training'))
const WebSearch = lazy(() => import('./pages/WebSearch'))
import type { ConsentStatus } from './types'

export default function App() {
  return (
    <BrowserRouter>
      <AppGate />
    </BrowserRouter>
  )
}

function AppGate() {
  const [status, setStatus] = useState<ConsentStatus | null>(null)
  const [error, setError] = useState('')

  const load = useCallback(() => {
    setError('')
    api.get<ConsentStatus>('/api/consent')
      .then((data) => setStatus(data))
      .catch((e) => setError((e as Error).message))
  }, [])

  useEffect(() => { load() }, [load])

  if (error) {
    return (
      <div className="consent-shell">
        <div className="consent-card" style={{ padding: 30, textAlign: 'center' }}>
          <div className="brand-mark" style={{ margin: '0 auto 14px', width: 46, height: 46 }}><ShieldAlert size={24} /></div>
          <h1 style={{ fontSize: 21 }}>Backend Cybbig injoignable</h1>
          <p className="muted small" style={{ maxWidth: 460, margin: '8px auto 18px' }}>{error}</p>
          <button className="btn primary" onClick={load}><RefreshCw size={14} /> Réessayer</button>
        </div>
      </div>
    )
  }

  if (!status) return <div className="consent-shell"><Loading label="Connexion au service local…" /></div>

  return (
    <ToastProvider>
      {!status.accepted ? (
        <Consent status={status} onAccepted={load} />
      ) : (
        <Suspense fallback={<Loading label="Ouverture de la page…" />}><Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/scans" element={<Scans />} />
            <Route path="/scans/:id" element={<ScanDetail />} />
            <Route path="/findings" element={<Findings />} />
            <Route path="/income" element={<Income />} />
            <Route path="/projects" element={<Projects />} />
            <Route path="/projects/:id" element={<ProjectDetail />} />
            <Route path="/intel" element={<Intel />} />
            <Route path="/knowledge" element={<Knowledge />} />
            <Route path="/web-search" element={<WebSearch />} />
            <Route path="/assistant" element={<Assistant />} />
            <Route path="/training" element={<Training />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/automations" element={<Automations />} />
            <Route path="/lab" element={<Lab />} />
            <Route path="/lab/:slug" element={<LabDetail />} />
            <Route path="/privacy" element={<Privacy />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/terminal" element={<TerminalPage />} />
            <Route path="/admin" element={<Admin />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes></Suspense>
      )}
    </ToastProvider>
  )
}
