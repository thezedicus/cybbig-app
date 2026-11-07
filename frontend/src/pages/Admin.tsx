import { useEffect, useMemo, useRef, useState } from 'react'
import {
  Database, Download, HardDrive, KeyRound, Lock, LogOut, Play, Plus, RefreshCw, Sparkles, X, Zap,
  Save, Search, ShieldCheck, Terminal as TerminalIcon, Trash2,
} from 'lucide-react'
import { ApiError, adminApi, api, formatBytes, formatDate } from '../api'
import AgentsTab from '../components/AgentsTab'
import AiPanel from '../components/AiPanel'
import CodeAssistantTab from '../components/CodeAssistantTab'
import CodeEditorTab from '../components/CodeEditorTab'
import { AlertBox, EmptyState, Loading, PageHeader, useToast } from '../components/ui'

const TOKEN_KEY = 'cybbig-admin-token'

type Tab = 'overview' | 'config' | 'code' | 'atelier' | 'agents' | 'terminal' | 'database' | 'security'
const TABS: Tab[] = ['overview', 'config', 'code', 'atelier', 'agents', 'terminal', 'database', 'security']

interface Overview {
  tables: Record<string, number>
  database_bytes: number
  data_bytes: number
  data_dir: string
  project_dir: string
  sessions: number
  must_change: boolean
}

interface ExecResult {
  id: string
  shell: string
  cwd: string
  code: string
  exit_code: number
  status: string
  stdout: string
  stderr: string
  duration_ms?: number
  started_at: string
  cwd_after?: string
}

interface SqlResult {
  columns: string[]
  rows: unknown[][]
  truncated: boolean
  rowcount: number
}

interface Backup { name: string; bytes: number; modified: number }

function readToken(): string {
  try { return sessionStorage.getItem(TOKEN_KEY) ?? '' } catch { return '' }
}

function storeToken(token: string) {
  try {
    if (token) sessionStorage.setItem(TOKEN_KEY, token)
    else sessionStorage.removeItem(TOKEN_KEY)
  } catch { /* stockage indisponible */ }
}

export default function Admin() {
  const [token, setToken] = useState(readToken)
  const [checking, setChecking] = useState(!!token)
  const [mustChange, setMustChange] = useState(false)
  const [tab, setTab] = useState<Tab>(() => {
    const wanted = new URLSearchParams(window.location.search).get('tab') as Tab | null
    return wanted && TABS.includes(wanted) ? wanted : 'overview'
  })
  const toast = useToast()
  const client = useMemo(() => adminApi(token), [token])

  const signOut = (message?: string) => {
    storeToken('')
    setToken('')
    if (message) toast.push(message, 'info')
  }

  useEffect(() => {
    if (!token) return
    client.get<{ must_change: boolean }>('/api/admin/session')
      .then((d) => { setMustChange(d.must_change); if (d.must_change) setTab('security') })
      .catch(() => signOut())
      .finally(() => setChecking(false))
  }, [])

  // Toute réponse 401 ramène à l'écran de connexion.
  const guard = async <T,>(promise: Promise<T>): Promise<T> => {
    try {
      return await promise
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) signOut('Session expirée, reconnectez-vous.')
      throw err
    }
  }

  if (checking) return <Loading label="Vérification de la session…" />
  if (!token) {
    return <LoginForm onLogin={(t, change) => {
      storeToken(t); setToken(t); setMustChange(change)
      if (change) setTab('security')
    }} />
  }

  const logout = async () => {
    try { await client.post('/api/admin/logout') } catch { /* déjà expirée */ }
    signOut('Déconnecté.')
  }

  return (
    <>
      <PageHeader
        title="Administration"
        description="Espace propriétaire : configuration complète, terminal, base de données et sécurité. Chaque action est journalisée."
        actions={<button className="btn" onClick={logout}><LogOut size={14} /> Se déconnecter</button>}
      />

      {mustChange && (
        <AlertBox kind="error">
          <b>Changement d’identifiants demandé.</b> Choisissez un nouvel identifiant et un nouveau mot de passe dans l’onglet Sécurité.
        </AlertBox>
      )}

      <div className="tabs">
        {([
          ['overview', 'Vue d’ensemble'], ['config', 'Configuration'], ['code', 'Code'], ['atelier', 'Atelier IA'], ['agents', 'Agents IA'], ['terminal', 'Terminal'],
          ['database', 'Base de données'], ['security', 'Sécurité'],
        ] as Array<[Tab, string]>).map(([id, label]) => (
          <button key={id} className={`tab${tab === id ? ' active' : ''}`} onClick={() => setTab(id)}>{label}</button>
        ))}
      </div>

      {tab === 'overview' && <OverviewTab client={client} guard={guard} />}
      {tab === 'config' && <ConfigTab client={client} guard={guard} />}
      {tab === 'terminal' && <TerminalTab client={client} guard={guard} token={token} />}
      {tab === 'database' && <DatabaseTab client={client} guard={guard} />}
      {tab === 'code' && <CodeEditorTab client={client} guard={guard} />}
      {tab === 'atelier' && <CodeAssistantTab client={client} guard={guard} token={token} />}
      {tab === 'agents' && <AgentsTab client={client} guard={guard} />}
      {tab === 'security' && <SecurityTab client={client} guard={guard} onChanged={() => signOut('Identifiants modifiés. Reconnectez-vous.')} />}
    </>
  )
}

type Client = ReturnType<typeof adminApi>
type Guard = <T>(promise: Promise<T>) => Promise<T>

function OwnerActivation({ configured, onDone, onCancel }: { configured: boolean; onDone: () => void; onCancel?: () => void }) {
  const [challenge, setChallenge] = useState('')
  const [signature, setSignature] = useState('')
  const [identifier, setIdentifier] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const toast = useToast()

  const newChallenge = async () => {
    try {
      const d = await api.post<{ challenge: string }>('/api/admin/owner/challenge')
      setChallenge(d.challenge); setSignature('')
    } catch (err) { setError((err as Error).message) }
  }
  useEffect(() => { newChallenge() }, [])

  const submit = async (event: React.FormEvent) => {
    event.preventDefault()
    if (password !== confirm) { setError('Les deux mots de passe diffèrent.'); return }
    setBusy(true); setError('')
    try {
      await api.post('/api/admin/owner/activate', { challenge, signature, identifier, password })
      toast.push('Administration activée. Connectez-vous avec vos nouveaux identifiants.', 'success')
      onDone()
    } catch (err) {
      setError((err as Error).message)
      newChallenge()
    } finally { setBusy(false) }
  }

  const command = `python scripts/owner-sign.py sign ${challenge}`
  return (
    <div className="admin-login">
      <form className="card card-pad stack" style={{ gap: 14, maxWidth: 560, width: '100%' }} onSubmit={submit}>
        <div className="row" style={{ gap: 10 }}>
          <div className="brand-mark"><KeyRound size={20} /></div>
          <div>
            <h1 style={{ fontSize: 18, margin: 0 }}>Activation propriétaire</h1>
            <div className="small muted">{configured ? 'Réinitialisation des identifiants administrateur' : 'Aucun administrateur n’est configuré sur ce poste'}</div>
          </div>
        </div>
        <p className="small muted" style={{ margin: 0 }}>
          Cybbig n’est livré avec aucun identifiant administrateur. Seul le propriétaire, détenteur de la clé privée,
          peut activer l’administration en signant ce défi sur son propre poste. Les utilisateurs n’en ont pas besoin :
          toutes les analyses et leurs propres clés API se règlent dans <b>Paramètres</b>.
        </p>
        {error && <AlertBox kind="error">{error}</AlertBox>}
        <div className="field">
          <label>Défi (valable 10 minutes, usage unique)</label>
          <div className="row" style={{ gap: 8 }}>
            <code className="input" style={{ flex: 1, minWidth: 0, wordBreak: 'break-all', whiteSpace: 'normal', height: 'auto' }}>{challenge || '…'}</code>
            <button type="button" className="btn" disabled={!challenge}
              onClick={() => { navigator.clipboard?.writeText(command); toast.push('Commande copiée.', 'info') }}>Copier la commande</button>
            <button type="button" className="btn" onClick={newChallenge} title="Nouveau défi"><RefreshCw size={14} /></button>
          </div>
        </div>
        <div className="field">
          <label htmlFor="owner-sig">Signature</label>
          <input id="owner-sig" className="input" autoComplete="off" spellCheck={false} required value={signature}
            onChange={(e) => setSignature(e.target.value.trim())} placeholder="128 caractères hexadécimaux" />
        </div>
        <div className="field">
          <label htmlFor="owner-id">Nouvel identifiant</label>
          <input id="owner-id" className="input" autoComplete="username" required minLength={4} value={identifier} onChange={(e) => setIdentifier(e.target.value)} />
        </div>
        <div className="field">
          <label htmlFor="owner-pw">Nouveau mot de passe (10 caractères minimum)</label>
          <input id="owner-pw" className="input" type="password" autoComplete="new-password" required minLength={10} value={password} onChange={(e) => setPassword(e.target.value)} />
        </div>
        <div className="field">
          <label htmlFor="owner-pw2">Confirmer le mot de passe</label>
          <input id="owner-pw2" className="input" type="password" autoComplete="new-password" required minLength={10} value={confirm} onChange={(e) => setConfirm(e.target.value)} />
        </div>
        <div className="row" style={{ gap: 8 }}>
          <button className="btn primary" disabled={busy || !challenge}>{busy ? 'Vérification…' : 'Activer'}</button>
          {onCancel && <button type="button" className="btn" onClick={onCancel}>Retour à la connexion</button>}
        </div>
      </form>
    </div>
  )
}

function LoginForm({ onLogin }: { onLogin: (token: string, mustChange: boolean) => void }) {
  const [identifier, setIdentifier] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [configured, setConfigured] = useState<boolean | null>(null)
  const [activating, setActivating] = useState(false)
  const [refresh, setRefresh] = useState(0)

  useEffect(() => {
    api.get<{ configured: boolean }>('/api/admin/status').then((d) => setConfigured(d.configured)).catch(() => setConfigured(true))
  }, [refresh])

  const submit = async (event: React.FormEvent) => {
    event.preventDefault()
    setBusy(true); setError('')
    try {
      const result = await api.post<{ token: string; must_change: boolean }>('/api/admin/login', { identifier, password })
      onLogin(result.token, result.must_change)
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setBusy(false)
    }
  }

  if (configured === null) return <Loading label="Vérification…" />
  if (activating || !configured) {
    return <OwnerActivation configured={configured} onDone={() => { setActivating(false); setRefresh((n) => n + 1) }} onCancel={configured ? () => setActivating(false) : undefined} />
  }

  return (
    <div className="admin-login">
      <form className="card card-pad stack" style={{ gap: 14 }} onSubmit={submit}>
        <div className="row" style={{ gap: 10 }}>
          <div className="brand-mark"><Lock size={20} /></div>
          <div>
            <h1 style={{ fontSize: 18, margin: 0 }}>Administration</h1>
            <div className="small muted">Accès réservé au propriétaire</div>
          </div>
        </div>
        {error && <AlertBox kind="error">{error}</AlertBox>}
        <div className="field">
          <label htmlFor="admin-id">Identifiant</label>
          <input id="admin-id" className="input" autoComplete="username" required autoFocus value={identifier} onChange={(e) => setIdentifier(e.target.value)} />
        </div>
        <div className="field">
          <label htmlFor="admin-pw">Mot de passe</label>
          <input id="admin-pw" className="input" type="password" autoComplete="current-password" required value={password} onChange={(e) => setPassword(e.target.value)} />
        </div>
        <button className="btn primary" disabled={busy}>{busy ? 'Connexion…' : 'Se connecter'}</button>
        <p className="tiny faint" style={{ margin: 0 }}>5 essais ratés bloquent l’accès 5 minutes. La session expire après 30 minutes d’inactivité.</p>
        <button type="button" className="btn" onClick={() => setActivating(true)}>Identifiants oubliés ? Activation propriétaire</button>
      </form>
    </div>
  )
}

function ActiveModeCard({ client, guard }: { client: Client; guard: Guard }) {
  const [active, setActive] = useState<boolean | null>(null)
  const toast = useToast()
  useEffect(() => { api.get<{ active: boolean }>('/api/mode').then((d) => setActive(d.active)).catch(() => undefined) }, [])

  const toggle = async () => {
    const next = !active
    if (next && !window.confirm('Activer le mode actif ? Les analyses Web enverront des requêtes de test non destructives (OPTIONS, TRACE, en-tête Origin, marqueurs inoffensifs) aux cibles autorisées des projets.')) return
    try {
      const result = await guard(client.put<{ active: boolean }>('/api/admin/active-mode', { enabled: next }))
      setActive(result.active)
      toast.push(result.active ? 'Mode actif activé.' : 'Mode passif rétabli.', 'success')
    } catch (err) {
      toast.push((err as Error).message, 'error')
    }
  }

  return (
    <section className="card" style={{ gridColumn: '1 / -1' }}>
      <div className="card-header">
        <div>
          <h2>Mode d’analyse</h2>
          <div className="sub">{active ? 'Actif : contrôles Web non destructifs en plus des vérifications passives' : 'Passif : observation uniquement'}</div>
        </div>
        <button className={`btn ${active ? '' : 'primary'} sm`} style={{ marginLeft: 'auto' }} onClick={toggle} disabled={active === null}>
          <Zap size={13} /> {active ? 'Revenir en mode passif' : 'Activer le mode actif'}
        </button>
      </div>
      <div className="card-pad small muted">
        Le mode actif ajoute aux analyses Web : méthodes HTTP sensibles (OPTIONS/TRACE), CORS permissif, paramètres reflétés sans encodage, redirections ouvertes
        et la liste complète des fichiers sensibles. Toutes les requêtes restent dans le périmètre autorisé du projet, sont plafonnées (40 par analyse) et espacées.
        Aucune charge d’exploitation n’est envoyée.
      </div>
    </section>
  )
}

function OverviewTab({ client, guard }: { client: Client; guard: Guard }) {
  const [data, setData] = useState<Overview | null>(null)
  const [researchMode, setResearchMode] = useState<boolean | null>(null)
  const [researchBusy, setResearchBusy] = useState(false)
  const toast = useToast()
  const load = () => { guard(client.get<Overview>('/api/admin/overview')).then(setData).catch(() => undefined) }
  useEffect(load, [])
  useEffect(() => { guard(client.get<{ enabled: boolean }>('/api/admin/web-research-mode')).then((d) => setResearchMode(d.enabled)).catch(() => setResearchMode(false)) }, [])
  const toggleResearch = async () => {
    if (researchMode === null) return
    setResearchBusy(true)
    try {
      const result = await guard(client.put<{ enabled: boolean }>('/api/admin/web-research-mode', { enabled: !researchMode }))
      setResearchMode(result.enabled)
      toast.push(result.enabled ? 'Recherche étendue activée.' : 'Recherche standard rétablie.', 'success')
    } catch (err) { toast.push((err as Error).message, 'error') }
    finally { setResearchBusy(false) }
  }
  if (!data) return <Loading />
  const total = Object.values(data.tables).reduce((a, b) => a + b, 0)
  return (
    <div className="settings-grid">
      <ActiveModeCard client={client} guard={guard} />
      <section className="card">
        <div className="card-header"><div><h2>Puissance de recherche web</h2><div className="sub">Mode propriétaire · {researchMode ? 'étendu' : 'standard'}</div></div><Search size={16} style={{ marginLeft: 'auto', color: 'var(--accent)' }} /></div>
        <div className="card-pad stack" style={{ gap: 12 }}>
          <p className="small muted" style={{ margin: 0 }}>Le mode étendu augmente le nombre de références cherchées et les pages consultées par l’assistant. Les protections contre les adresses privées, les métadonnées cloud et les URL dangereuses restent actives.</p>
          <button className={`btn ${researchMode ? '' : 'primary'} sm`} onClick={toggleResearch} disabled={researchMode === null || researchBusy}>
            {researchBusy ? <RefreshCw size={13} className="spin" /> : <Search size={13} />}{researchMode ? 'Désactiver la recherche étendue' : 'Activer la recherche étendue'}
          </button>
        </div>
      </section>
      <section className="card">
        <div className="card-header">
          <div><h2>Tables</h2><div className="sub">{total} enregistrements au total</div></div>
          <button className="btn ghost sm" style={{ marginLeft: 'auto' }} onClick={load}><RefreshCw size={13} /> Actualiser</button>
        </div>
        <div className="table-wrap">
          <table className="data">
            <thead><tr><th>Table</th><th style={{ textAlign: 'right' }}>Lignes</th></tr></thead>
            <tbody>
              {Object.entries(data.tables).map(([name, count]) => (
                <tr key={name}><td className="cell-mono">{name}</td><td className="mono small" style={{ textAlign: 'right' }}>{count}</td></tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
      <section className="card">
        <div className="card-header"><div><h2>Stockage</h2><div className="sub">Données locales</div></div><HardDrive size={16} style={{ marginLeft: 'auto', color: 'var(--accent)' }} /></div>
        <div className="card-pad">
          <div className="kv-list">
            <div className="kv-item"><span>Base SQLite</span><b>{formatBytes(data.database_bytes)}</b></div>
            <div className="kv-item"><span>Dossier de données</span><b>{formatBytes(data.data_bytes)}</b></div>
            <div className="kv-item"><span>Sessions admin actives</span><b>{data.sessions}</b></div>
            <div className="kv-item"><span>Projet</span><b className="mono tiny" style={{ wordBreak: 'break-all' }}>{data.project_dir}</b></div>
            <div className="kv-item"><span>Données</span><b className="mono tiny" style={{ wordBreak: 'break-all' }}>{data.data_dir}</b></div>
          </div>
        </div>
      </section>
    </div>
  )
}

function ConfigTab({ client, guard }: { client: Client; guard: Guard }) {
  const [values, setValues] = useState<Record<string, string> | null>(null)
  const [original, setOriginal] = useState<Record<string, string>>({})
  const [filter, setFilter] = useState('')
  const [newKey, setNewKey] = useState('')
  const [newValue, setNewValue] = useState('')
  const [saving, setSaving] = useState(false)
  const toast = useToast()

  const load = () => {
    guard(client.get<{ values: Record<string, string> }>('/api/admin/settings'))
      .then((d) => { setValues(d.values); setOriginal(d.values) })
      .catch((e) => toast.push((e as Error).message, 'error'))
  }
  useEffect(load, [])

  const dirty = values ? Object.keys(values).filter((k) => values[k] !== original[k]) : []

  const save = async () => {
    if (!values || !dirty.length) return
    setSaving(true)
    try {
      const payload = Object.fromEntries(dirty.map((k) => [k, values[k]]))
      await guard(client.put('/api/admin/settings', { values: payload }))
      toast.push(`${dirty.length} clé(s) enregistrée(s).`, 'success')
      load()
    } catch (err) {
      toast.push((err as Error).message, 'error')
    } finally {
      setSaving(false)
    }
  }

  const remove = async (key: string) => {
    if (!window.confirm(`Supprimer la clé « ${key} » ?`)) return
    try {
      await guard(client.del(`/api/admin/settings/${encodeURIComponent(key)}`))
      toast.push('Clé supprimée.', 'success')
      load()
    } catch (err) {
      toast.push((err as Error).message, 'error')
    }
  }

  if (!values) return <Loading />
  const keys = Object.keys(values).sort().filter((k) => k.toLowerCase().includes(filter.trim().toLowerCase()))

  return (
    <section className="card">
      <div className="card-header">
        <div><h2>Toutes les clés de configuration</h2><div className="sub">{Object.keys(values).length} clés · {dirty.length} modifiée(s)</div></div>
        <div className="right">
          <input className="input" style={{ width: 200 }} placeholder="Filtrer…" value={filter} onChange={(e) => setFilter(e.target.value)} />
          <button className="btn primary sm" onClick={save} disabled={saving || !dirty.length}><Save size={13} /> {saving ? 'Enregistrement…' : 'Enregistrer'}</button>
        </div>
      </div>
      <div className="card-pad stack" style={{ gap: 8 }}>
        <AlertBox kind="info">Les clés sont écrites telles quelles. Une valeur incorrecte peut perturber un moteur : faites une sauvegarde (onglet Base de données) avant un changement important.</AlertBox>
        {keys.map((key) => (
          <div className="admin-kv" key={key}>
            <label className="mono small" htmlFor={`cfg-${key}`}>{key}{values[key] !== original[key] && <span style={{ color: 'var(--accent)' }}> •</span>}</label>
            <input id={`cfg-${key}`} className="input" value={values[key]} onChange={(e) => setValues({ ...values, [key]: e.target.value })} />
            <button className="icon-btn" style={{ width: 30, height: 30 }} title="Supprimer" onClick={() => remove(key)}><Trash2 size={13} /></button>
          </div>
        ))}
        <div className="admin-kv" style={{ marginTop: 8 }}>
          <input className="input mono" placeholder="nouvelle_cle" value={newKey} onChange={(e) => setNewKey(e.target.value)} />
          <input className="input" placeholder="Valeur" value={newValue} onChange={(e) => setNewValue(e.target.value)} />
          <button className="btn sm" onClick={() => {
            const key = newKey.trim()
            if (!key) return
            setValues({ ...values, [key]: newValue })
            setNewKey(''); setNewValue('')
          }}><Plus size={13} /> Ajouter</button>
        </div>
      </div>
    </section>
  )
}

interface TermSession { id: number; shell: string; cwd: string; timeout: number; stdin: string; entries: ExecResult[] }

const SNIPPETS: Record<string, Array<[string, string]>> = {
  powershell: [
    ['Ports à l’écoute', 'Get-NetTCPConnection -State Listen | Sort-Object LocalPort | Select-Object LocalAddress,LocalPort,OwningProcess -First 30 | Format-Table -Auto'],
    ['Réseau', 'Get-NetIPAddress -AddressFamily IPv4 | Select-Object InterfaceAlias,IPAddress | Format-Table -Auto'],
    ['Modèles Ollama', 'ollama list'],
    ['Processus gourmands', 'Get-Process | Sort-Object WS -Descending | Select-Object -First 10 Name,Id,@{n="Mo";e={[int]($_.WS/1MB)}} | Format-Table -Auto'],
    ['Espace disque', 'Get-PSDrive -PSProvider FileSystem | Select-Object Name,@{n="Libre Go";e={[math]::Round($_.Free/1GB,1)}},@{n="Utilisé Go";e={[math]::Round($_.Used/1GB,1)}} | Format-Table -Auto'],
    ['Pare-feu', 'Get-NetFirewallProfile | Select-Object Name,Enabled | Format-Table -Auto'],
  ],
  cmd: [['ipconfig', 'ipconfig'], ['netstat', 'netstat -ano | findstr LISTENING'], ['Version', 'ver']],
  python: [['Version', 'import sys; print(sys.version)'], ['Paquets', 'import importlib.metadata as m; print(sorted(d.metadata["Name"] for d in m.distributions())[:60])']],
}

let nextSessionId = 1

function TerminalTab({ client, guard, token }: { client: Client; guard: Guard; token: string }) {
  const [sessions, setSessions] = useState<TermSession[]>([{ id: nextSessionId++, shell: 'powershell', cwd: 'root', timeout: 120, stdin: '', entries: [] }])
  const [currentId, setCurrentId] = useState(sessions[0].id)
  const [code, setCode] = useState('')
  const [running, setRunning] = useState(false)
  const [cursor, setCursor] = useState(-1)
  const [explainId, setExplainId] = useState<string | null>(null)
  const outputRef = useRef<HTMLDivElement>(null)
  const toast = useToast()
  const current = sessions.find((s) => s.id === currentId) ?? sessions[0]

  const patch = (id: number, change: (s: TermSession) => Partial<TermSession>) =>
    setSessions((list) => list.map((s) => (s.id === id ? { ...s, ...change(s) } : s)))

  useEffect(() => {
    guard(client.get<{ items: ExecResult[] }>('/api/admin/exec/history?limit=30'))
      .then((d) => patch(sessions[0].id, () => ({ entries: d.items.reverse() })))
      .catch(() => undefined)
  }, [])

  useEffect(() => {
    outputRef.current?.scrollTo({ top: outputRef.current.scrollHeight })
  }, [current.entries, explainId])

  const addSession = () => {
    const session = { id: nextSessionId++, shell: current.shell, cwd: current.cwd, timeout: current.timeout, stdin: '', entries: [] }
    setSessions((list) => [...list, session])
    setCurrentId(session.id)
  }

  const closeSession = (id: number) => {
    if (sessions.length === 1) return
    const rest = sessions.filter((s) => s.id !== id)
    setSessions(rest)
    if (id === currentId) setCurrentId(rest[rest.length - 1].id)
  }

  const run = async (source = code) => {
    if (!source.trim() || running) return
    const sessionId = current.id
    setRunning(true)
    try {
      const result = await guard(client.post<ExecResult>('/api/admin/exec', { code: source, shell: current.shell, cwd: current.cwd, timeout: current.timeout, stdin: current.stdin }))
      patch(sessionId, (s) => ({ entries: [...s.entries, result], cwd: result.cwd_after || s.cwd }))
      if (source === code) { setCode(''); setCursor(-1) }
    } catch (err) {
      toast.push((err as Error).message, 'error')
    } finally {
      setRunning(false)
    }
  }

  const onKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === 'Enter' && (event.ctrlKey || !code.includes('\n')) && !event.shiftKey) {
      event.preventDefault(); run(); return
    }
    if (event.key === 'l' && event.ctrlKey) {
      event.preventDefault(); patch(current.id, () => ({ entries: [] })); return
    }
    const history = current.entries.map((e) => e.code)
    if (event.key === 'ArrowUp' && !code.includes('\n') && history.length) {
      event.preventDefault()
      const next = cursor < 0 ? history.length - 1 : Math.max(0, cursor - 1)
      setCursor(next); setCode(history[next])
    }
    if (event.key === 'ArrowDown' && cursor >= 0) {
      event.preventDefault()
      const next = cursor + 1
      if (next >= history.length) { setCursor(-1); setCode('') } else { setCursor(next); setCode(history[next]) }
    }
  }

  return (
    <section className="card">
      <div className="card-header">
        <div><h2>Terminal propriétaire</h2><div className="sub">PowerShell, cmd et Python · « cd » conservé · historique · entrée standard · délai jusqu’à 15 min</div></div>
        <div className="right">
          <select className="select" value={current.shell} onChange={(e) => patch(current.id, () => ({ shell: e.target.value }))}>
            <option value="powershell">PowerShell</option>
            <option value="cmd">cmd</option>
            <option value="python">Python</option>
          </select>
          <input className="input mono" style={{ width: 260 }} value={current.cwd} onChange={(e) => patch(current.id, () => ({ cwd: e.target.value }))} title="root, backend, frontend ou chemin absolu" placeholder="root" />
          <select className="select" value={current.timeout} onChange={(e) => patch(current.id, () => ({ timeout: Number(e.target.value) }))} title="Délai maximal de la commande">
            <option value={120}>2 min</option><option value={300}>5 min</option><option value={900}>15 min</option>
          </select>
          <button className="btn ghost sm" onClick={() => patch(current.id, () => ({ entries: [] }))}>Effacer</button>
        </div>
      </div>
      <div className="term-tabs">
        {sessions.map((s, index) => (
          <button key={s.id} className={`term-tab${s.id === current.id ? ' active' : ''}`} onClick={() => setCurrentId(s.id)}>
            <TerminalIcon size={11} /> {s.shell} {index + 1}
            {sessions.length > 1 && <span role="button" aria-label="Fermer" onClick={(e) => { e.stopPropagation(); closeSession(s.id) }}><X size={11} /></span>}
          </button>
        ))}
        <button className="term-tab" onClick={addSession} title="Nouvel onglet"><Plus size={11} /></button>
      </div>
      <div className="admin-console" ref={outputRef}>
        {current.entries.length === 0 && <div className="faint">Tapez une commande puis Entrée. Maj+Entrée pour une nouvelle ligne, Ctrl+Entrée pour exécuter un bloc, ↑/↓ pour l’historique.</div>}
        {current.entries.map((entry) => (
          <div key={entry.id} className="admin-console-entry">
            <div className="admin-console-prompt"><span>{entry.shell} {entry.cwd}&gt;</span> {entry.code}</div>
            {entry.stdout && <pre>{entry.stdout}</pre>}
            {entry.stderr && <pre className="err">{entry.stderr}</pre>}
            <div className={`admin-console-meta ${entry.exit_code === 0 ? 'ok' : 'ko'}`}>
              code {entry.exit_code}{entry.duration_ms !== undefined ? ` · ${entry.duration_ms} ms` : ''} · {formatDate(entry.started_at)}
              {entry.exit_code !== 0 && explainId !== entry.id && (
                <button className="link-btn" style={{ marginLeft: 10 }} onClick={() => setExplainId(entry.id)}><Sparkles size={11} /> Expliquer l’erreur</button>
              )}
            </div>
            {explainId === entry.id && (
              <div style={{ marginTop: 8, fontFamily: 'var(--font)' }}>
                <AiPanel task="terminal_explain" endpoint="/api/admin/ai/run" headers={{ 'X-Admin-Token': token }} autoStart compact
                  title="Explication de l’erreur" label="Expliquer"
                  params={{ shell: entry.shell, code: entry.code, exit_code: entry.exit_code, stdout: entry.stdout, stderr: entry.stderr }} />
              </div>
            )}
          </div>
        ))}
        {running && <div className="faint">Exécution…</div>}
      </div>
      <div style={{ padding: '8px 14px 0' }}>
        <label className="tiny faint" htmlFor="terminal-stdin">Entrée standard facultative (utile à Python input() ou aux commandes qui lisent stdin)</label>
        <textarea id="terminal-stdin" className="input mono" rows={2} value={current.stdin}
          onChange={(e) => patch(current.id, () => ({ stdin: e.target.value }))} placeholder="Texte envoyé au programme à son démarrage…" spellCheck={false} style={{ display: 'block', width: '100%', resize: 'vertical', marginTop: 4 }} />
      </div>
      <div className="admin-console-input">
        <TerminalIcon size={14} style={{ color: 'var(--accent)', marginTop: 9 }} />
        <textarea
          className="input mono" rows={Math.min(8, Math.max(1, code.split('\n').length))} value={code}
          onChange={(e) => setCode(e.target.value)} onKeyDown={onKeyDown} spellCheck={false}
          placeholder={current.shell === 'python' ? 'print("bonjour")' : 'Get-ChildItem'} autoFocus
        />
        <button className="btn primary sm" onClick={() => run()} disabled={running || !code.trim()}><Play size={13} /> Exécuter</button>
      </div>
      <div className="term-snippets">
        <span className="tiny faint" style={{ alignSelf: 'center' }}>Raccourcis :</span>
        {(SNIPPETS[current.shell] ?? []).map(([label, snippet]) => (
          <button key={label} className="btn ghost sm" onClick={() => run(snippet)} disabled={running} title={snippet}>{label}</button>
        ))}
      </div>
    </section>
  )
}

function DatabaseTab({ client, guard }: { client: Client; guard: Guard }) {
  const [sql, setSql] = useState('SELECT key, value FROM settings ORDER BY key;')
  const [result, setResult] = useState<SqlResult | null>(null)
  const [error, setError] = useState('')
  const [running, setRunning] = useState(false)
  const [backups, setBackups] = useState<Backup[] | null>(null)
  const toast = useToast()

  const loadBackups = () => {
    guard(client.get<{ items: Backup[] }>('/api/admin/backups')).then((d) => setBackups(d.items)).catch(() => undefined)
  }
  useEffect(loadBackups, [])

  const runSql = async () => {
    const statement = sql.trim()
    if (!statement) return
    if (/^\s*(delete|drop|update|alter|insert|replace)\b/i.test(statement) && !window.confirm('Cette requête modifie la base. Continuer ?')) return
    setRunning(true); setError('')
    try {
      setResult(await guard(client.post<SqlResult>('/api/admin/sql', { sql: statement })))
    } catch (err) {
      setError((err as Error).message); setResult(null)
    } finally {
      setRunning(false)
    }
  }

  const backup = async () => {
    try {
      const created = await guard(client.post<Backup>('/api/admin/backups'))
      toast.push(`Sauvegarde créée : ${created.name}`, 'success')
      loadBackups()
    } catch (err) {
      toast.push((err as Error).message, 'error')
    }
  }

  const removeBackup = async (name: string) => {
    if (!window.confirm(`Supprimer définitivement ${name} ?`)) return
    try {
      await guard(client.del(`/api/admin/backups/${encodeURIComponent(name)}`))
      loadBackups()
    } catch (err) {
      toast.push((err as Error).message, 'error')
    }
  }

  return (
    <div className="stack" style={{ gap: 14 }}>
      <section className="card">
        <div className="card-header">
          <div><h2>Console SQL</h2><div className="sub">SQLite · 500 lignes max affichées · Ctrl+Entrée pour exécuter</div></div>
          <button className="btn primary sm" style={{ marginLeft: 'auto' }} onClick={runSql} disabled={running}><Play size={13} /> {running ? 'Exécution…' : 'Exécuter'}</button>
        </div>
        <div className="card-pad stack" style={{ gap: 10 }}>
          <textarea className="input mono" rows={5} value={sql} spellCheck={false} onChange={(e) => setSql(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter' && e.ctrlKey) { e.preventDefault(); runSql() } }} />
          {error && <AlertBox kind="error">{error}</AlertBox>}
          {result && (result.columns.length ? (
            <div className="table-wrap" style={{ maxHeight: 420 }}>
              <table className="data">
                <thead><tr>{result.columns.map((c) => <th key={c}>{c}</th>)}</tr></thead>
                <tbody>
                  {result.rows.map((row, i) => (
                    <tr key={i}>{row.map((cell, j) => <td key={j} className="cell-mono" style={{ maxWidth: 380, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={String(cell ?? '')}>{cell === null ? <span className="faint">NULL</span> : String(cell)}</td>)}</tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : <div className="small muted">Requête exécutée · {result.rowcount} ligne(s) affectée(s).</div>)}
          {result?.truncated && <div className="tiny faint">Résultat tronqué à 500 lignes.</div>}
        </div>
      </section>

      <section className="card">
        <div className="card-header">
          <div><h2>Sauvegardes</h2><div className="sub">Copie cohérente de cybbig.db dans data/backups</div></div>
          <button className="btn sm" style={{ marginLeft: 'auto' }} onClick={backup}><Database size={13} /> Sauvegarder maintenant</button>
        </div>
        {!backups ? <Loading /> : backups.length === 0 ? (
          <EmptyState icon={<Database size={26} />} title="Aucune sauvegarde" description="Créez une sauvegarde avant toute modification importante." />
        ) : (
          <div className="table-wrap">
            <table className="data">
              <thead><tr><th>Fichier</th><th>Taille</th><th>Date</th><th /></tr></thead>
              <tbody>
                {backups.map((b) => (
                  <tr key={b.name}>
                    <td className="cell-mono">{b.name}</td>
                    <td className="small">{formatBytes(b.bytes)}</td>
                    <td className="tiny faint">{formatDate(new Date(b.modified * 1000).toISOString())}</td>
                    <td style={{ textAlign: 'right', whiteSpace: 'nowrap' }}>
                      <button className="icon-btn" style={{ width: 28, height: 28 }} title="Télécharger" onClick={() => guard(client.download(`/api/admin/backups/${encodeURIComponent(b.name)}/download`, b.name)).catch((e) => toast.push((e as Error).message, 'error'))}><Download size={12} /></button>
                      <button className="icon-btn" style={{ width: 28, height: 28, marginLeft: 4 }} title="Supprimer" onClick={() => removeBackup(b.name)}><Trash2 size={12} /></button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  )
}

function SecurityTab({ client, guard, onChanged }: { client: Client; guard: Guard; onChanged: () => void }) {
  const [form, setForm] = useState({ current: '', identifier: '', password: '', confirm: '' })
  const [busy, setBusy] = useState(false)
  const toast = useToast()

  const submit = async (event: React.FormEvent) => {
    event.preventDefault()
    if (form.password !== form.confirm) { toast.push('Les deux mots de passe ne correspondent pas.', 'error'); return }
    setBusy(true)
    try {
      await guard(client.post('/api/admin/credentials', {
        current_password: form.current, new_identifier: form.identifier, new_password: form.password,
      }))
      onChanged()
    } catch (err) {
      toast.push((err as Error).message, 'error')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="settings-grid">
      <section className="card">
        <div className="card-header"><div><h2>Changer les identifiants</h2><div className="sub">Toutes les sessions seront fermées</div></div><KeyRound size={16} style={{ marginLeft: 'auto', color: 'var(--accent)' }} /></div>
        <form className="card-pad" onSubmit={submit}>
          <div className="form-grid">
            <div className="field full"><label>Mot de passe actuel</label><input className="input" type="password" autoComplete="current-password" required value={form.current} onChange={(e) => setForm({ ...form, current: e.target.value })} /></div>
            <div className="field full"><label>Nouvel identifiant (4 caractères min.)</label><input className="input" autoComplete="username" required minLength={4} value={form.identifier} onChange={(e) => setForm({ ...form, identifier: e.target.value })} /></div>
            <div className="field"><label>Nouveau mot de passe (10 min.)</label><input className="input" type="password" autoComplete="new-password" required minLength={10} value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} /></div>
            <div className="field"><label>Confirmation</label><input className="input" type="password" autoComplete="new-password" required minLength={10} value={form.confirm} onChange={(e) => setForm({ ...form, confirm: e.target.value })} /></div>
          </div>
          <div className="form-actions"><button className="btn primary" disabled={busy}>{busy ? 'Enregistrement…' : 'Mettre à jour'}</button></div>
        </form>
      </section>
      <section className="card">
        <div className="card-header"><div><h2>Protection en place</h2><div className="sub">Comment l’accès est protégé</div></div><ShieldCheck size={16} style={{ marginLeft: 'auto', color: 'var(--green)' }} /></div>
        <div className="card-pad">
          <div className="kv-list">
            <div className="kv-item"><span>Stockage</span><b style={{ textAlign: 'left', fontWeight: 500 }}>Identifiant et mot de passe hachés (PBKDF2-SHA256, sel aléatoire), jamais en clair.</b></div>
            <div className="kv-item"><span>Session</span><b style={{ textAlign: 'left', fontWeight: 500 }}>Jeton aléatoire en mémoire, expire après 30 min d’inactivité ou au redémarrage.</b></div>
            <div className="kv-item"><span>Force brute</span><b style={{ textAlign: 'left', fontWeight: 500 }}>Blocage de 5 minutes après 5 échecs.</b></div>
            <div className="kv-item"><span>Journal</span><b style={{ textAlign: 'left', fontWeight: 500 }}>Connexions, commandes, requêtes SQL et changements consignés dans le journal d’audit.</b></div>
          </div>
        </div>
      </section>
    </div>
  )
}
