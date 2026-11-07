import { useEffect, useMemo, useState } from 'react'
import {
  Activity, Bot, CheckCircle2, Database, FlaskConical, KeyRound, ListChecks, Lock,
  RefreshCw, Save, ServerCog, ShieldCheck, Timer, XCircle,
} from 'lucide-react'
import { Link } from 'react-router-dom'
import AiSettings from '../components/AiSettings'
import AppearanceSettings from '../components/AppearanceSettings'
import CloudSettings from '../components/CloudSettings'
import ResourcesPanel from '../components/ResourcesPanel'
import { api, formatDate, relativeDate } from '../api'
import {
  AlertBox, EmptyState, Loading, PageHeader, StatusPill, useToast,
} from '../components/ui'
import type {
  AuditEntry, ConsentStatus, EngineInfo, OllamaStatus, SchedulerStatus,
} from '../types'

interface DatabaseHealth {
  ok: boolean
  schema_version: number
  fts5: boolean
  path: string
}

interface HealthResponse {
  app: string
  version: string
  status: string
  time: string
  database: DatabaseHealth
  consent: boolean
  scheduler: SchedulerStatus
  engines: string[]
}

interface EnginesResponse {
  engines: EngineInfo[]
  limitations: string[]
}

const EDITABLE_KEYS = [
  'intel_nvd_days', 'intel_max_items', 'nvd_api_key', 'ollama_api_key', 'user_agent',
  'ollama_url', 'ollama_model', 'max_files', 'max_pages',
  'probe_exposed_files', 'enable_external_tools', 'trusted_script_domains', 'osv_online',
  'ai_auto', 'ai_boost', 'ai_auto_scans', 'ai_auto_triage', 'ai_auto_intel', 'ai_auto_dashboard', 'ai_agents',
  'ai_provider', 'ai_allow_cloud', 'ollama_cloud_url', 'ollama_cloud_key', 'ollama_cloud_model', 'brave_search_key', 'ai_warmup', 'ai_browse', 'ai_search', 'web_respect_robots',
  'ui_accent', 'ui_font_size', 'ui_radius', 'ui_hidden_nav', 'ui_custom_css',
]

export default function Settings() {
  const [tab, setTab] = useState<'settings' | 'engines' | 'audit'>('settings')
  const [values, setValues] = useState<Record<string, string> | null>(null)
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [consent, setConsent] = useState<ConsentStatus | null>(null)
  const [ollama, setOllama] = useState<OllamaStatus | null>(null)
  const [engines, setEngines] = useState<EnginesResponse | null>(null)
  const [audit, setAudit] = useState<AuditEntry[] | null>(null)
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)
  const [testing, setTesting] = useState(false)
  const [auditFilter, setAuditFilter] = useState('')
  const toast = useToast()

  const loadHealth = () => {
    api.get<HealthResponse>('/api/health').then(setHealth).catch((e) => setError((e as Error).message))
    api.get<OllamaStatus>('/api/assistant/status').then(setOllama).catch(() => undefined)
    api.get<ConsentStatus>('/api/consent').then(setConsent).catch(() => undefined)
  }

  const loadSettings = () => {
    api.get<{ values: Record<string, string>; editable: string[] }>('/api/settings')
      .then((d) => setValues({ probe_exposed_files: 'true', enable_external_tools: 'true', trusted_script_domains: '', ollama_api_key: '', ollama_cloud_key: '', brave_search_key: '', ...d.values }))
      .catch((e) => setError((e as Error).message))
  }

  const loadEngines = () => {
    api.get<EnginesResponse>('/api/engines').then(setEngines).catch((e) => setError((e as Error).message))
  }

  const loadAudit = () => {
    api.get<{ items: AuditEntry[] }>('/api/audit?limit=200')
      .then((d) => setAudit(d.items))
      .catch((e) => setError((e as Error).message))
  }

  useEffect(() => {
    loadSettings(); loadHealth(); loadEngines(); loadAudit()
  }, [])

  const setValue = (key: string, value: string) => setValues((current) => ({ ...(current ?? {}), [key]: value }))
  const boolValue = (key: string, fallback = false) => {
    const value = values?.[key]
    if (value === undefined) return fallback
    return value === 'true' || value === '1'
  }

  const save = async () => {
    if (!values) return
    setSaving(true); setError('')
    try {
      const payload: Record<string, string> = {}
      for (const key of EDITABLE_KEYS) {
        if (values[key] !== undefined) payload[key] = values[key]
      }
      const result = await api.put<{ ok: boolean; changed: Record<string, string> }>('/api/settings', { values: payload })
      const masked = result.changed.nvd_api_key === '********'
      toast.push(`Paramètres enregistrés${masked ? ' (clé NVD conservée)' : ''}.`, 'success')
      loadSettings(); loadHealth()
    } catch (err) {
      toast.push((err as Error).message, 'error')
    } finally {
      setSaving(false)
    }
  }

  const testOllama = async () => {
    setTesting(true)
    try {
      const status = await api.get<OllamaStatus>('/api/assistant/status')
      setOllama(status)
      toast.push(status.available ? `Ollama joignable (${status.models.length} modèle(s)).` : 'Ollama indisponible, mode déterministe actif.', status.available ? 'success' : 'info')
    } catch (err) {
      toast.push((err as Error).message, 'error')
    } finally {
      setTesting(false)
    }
  }

  const filteredAudit = useMemo(() => {
    if (!audit) return []
    const needle = auditFilter.trim().toLowerCase()
    if (!needle) return audit
    return audit.filter((entry) =>
      [entry.action, entry.actor, entry.details].some((value) => (value ?? '').toLowerCase().includes(needle)))
  }, [audit, auditFilter])

  return (
    <>
      <PageHeader
        title="Paramètres"
        description="Configuration locale du poste. Les secrets restent sur cette machine et les clés sont masquées après enregistrement."
        actions={tab === 'settings' ? (
          <button className="btn primary" onClick={save} disabled={saving || !values}>
            <Save size={14} /> {saving ? 'Enregistrement…' : 'Enregistrer'}
          </button>
        ) : undefined}
      />

      {error && <AlertBox kind="error">{error}</AlertBox>}

      <div className="tabs">
        <button className={`tab${tab === 'settings' ? ' active' : ''}`} onClick={() => setTab('settings')}>Réglages</button>
        <button className={`tab${tab === 'engines' ? ' active' : ''}`} onClick={() => setTab('engines')}>Moteurs & intégrité</button>
        <button className={`tab${tab === 'audit' ? ' active' : ''}`} onClick={() => setTab('audit')}>Journal d’audit</button>
      </div>

      {tab === 'settings' && (
        !values ? <Loading /> : (
          <div className="settings-grid">
            <div className="stack" style={{ gap: 14 }}>
              <section className="card">
                <div className="card-header">
                  <div><h2>Veille et sources</h2><div className="sub">CISA KEV, NVD, CERT-FR, PHP et OSV</div></div>
                  <Activity size={16} style={{ marginLeft: 'auto', color: 'var(--accent)' }} />
                </div>
                <div className="card-pad">
                  <div className="form-grid">
                    <div className="field">
                      <label htmlFor="nvd-days">Fenêtre NVD (jours)</label>
                      <input id="nvd-days" className="input" type="number" min={1} max={120} value={values.intel_nvd_days ?? '14'} onChange={(e) => setValue('intel_nvd_days', e.target.value)} />
                      <span className="hint">CVE publiées ou modifiées sur cette période.</span>
                    </div>
                    <div className="field">
                      <label htmlFor="intel-max">Nombre maximal de fiches</label>
                      <input id="intel-max" className="input" type="number" min={10} max={2000} value={values.intel_max_items ?? '150'} onChange={(e) => setValue('intel_max_items', e.target.value)} />
                      <span className="hint">Limite par synchronisation.</span>
                    </div>
                    <div className="field full">
                      <label htmlFor="nvd-key">Clé API NVD (facultative)</label>
                      <input id="nvd-key" className="input" type="password" autoComplete="off" placeholder="Laisser vide ou ******** pour conserver" value={values.nvd_api_key ?? ''} onChange={(e) => setValue('nvd_api_key', e.target.value)} />
                      <span className="hint">Une clé augmente le quota NVD. Elle est stockée localement et masquée à la lecture. <a href="https://nvd.nist.gov/developers/request-an-api-key" target="_blank" rel="noreferrer">Demander une clé NVD</a>.</span>
                    </div>
                    <div className="field full">
                      <label htmlFor="user-agent">User-Agent des requêtes</label>
                      <input id="user-agent" className="input" value={values.user_agent ?? ''} onChange={(e) => setValue('user_agent', e.target.value)} maxLength={200} />
                      <span className="hint">Identifiant honnête, sans prétendre à un navigateur. Les analyses Web restent passives.</span>
                    </div>
                  </div>
                </div>
              </section>

              <section className="card">
                <div className="card-header">
                  <div><h2>Assistant local (Ollama)</h2><div className="sub">Serveur Ollama de ce poste ; repli déterministe hors ligne</div></div>
                  <Bot size={16} style={{ marginLeft: 'auto', color: 'var(--accent)' }} />
                </div>
                <div className="card-pad">
                  <div className="form-grid">
                    <div className="field">
                      <label htmlFor="ollama-url">URL Ollama</label>
                      <input id="ollama-url" className="input" value={values.ollama_url ?? ''} onChange={(e) => setValue('ollama_url', e.target.value)} placeholder="http://127.0.0.1:11434" />
                    </div>
                    <div className="field">
                      <label htmlFor="ollama-model">Modèle</label>
                      <input id="ollama-model" className="input" value={values.ollama_model ?? ''} onChange={(e) => setValue('ollama_model', e.target.value)} placeholder="llama3.2, qwen2.5…" />
                    </div>
                    <div className="field full">
                      <label htmlFor="ollama-key">Clé API Ollama (serveur local protégé uniquement)</label>
                      <input id="ollama-key" className="input" type="password" autoComplete="off" placeholder="Laisser vide, ou ******** pour conserver" value={values.ollama_api_key ?? ''} onChange={(e) => setValue('ollama_api_key', e.target.value)} />
                      <span className="hint">Ce champ n’accepte qu’un serveur de ce poste ou du réseau privé (127.0.0.1, localhost, 192.168.x.x…). Le service en ligne se règle dans « IA en ligne » ci-dessous.</span>
                    </div>
                  </div>
                  <div className="row wrap mt-3" style={{ gap: 8 }}>
                    <button type="button" className="btn sm" onClick={testOllama} disabled={testing}>
                      <RefreshCw size={13} className={testing ? 'spin' : ''} /> {testing ? 'Test…' : 'Tester la connexion'}
                    </button>
                    <button type="button" className="btn sm" onClick={async () => {
                      try {
                        const result = await api.get<{ installed: boolean; paths: string[] }>('/api/system/ollama/detect')
                        toast.push(result.installed ? `Ollama détecté : ${result.paths.join(', ')}` : 'Ollama non détecté.', result.installed ? 'success' : 'info')
                      } catch (err) { toast.push((err as Error).message, 'error') }
                    }}>
                      <RefreshCw size={13} /> Détecter
                    </button>
                    <button type="button" className="btn primary sm" onClick={async () => {
                      try {
                        const result = await api.post<{ started: boolean; message: string }>('/api/system/ollama/install')
                        toast.push(result.message, 'success')
                      } catch (err) { toast.push((err as Error).message, 'error') }
                    }}>
                      Installer Ollama
                    </button>
                    {ollama?.available ? (
                      <span className="pill completed"><CheckCircle2 size={12} /> Ollama joignable · {ollama.models.length} modèle(s)</span>
                    ) : (
                      <span className="pill"><XCircle size={12} /> Hors ligne · repli local</span>
                    )}
                  </div>
                  <p className="tiny faint mt-2" style={{ marginBottom: 0 }}>
                    En mode « Local uniquement », aucune donnée n’est envoyée à un service en ligne. En mode « Automatique », le modèle en ligne est utilisé dès qu’une clé API est configurée (voir « IA en ligne »).
                  </p>
                </div>
              </section>

              <AppearanceSettings values={values} setValue={setValue} />

              <CloudSettings values={values} setValue={setValue} />

              <ResourcesPanel />

              <AiSettings values={values} setValue={setValue} />

              <section className="card">
                <div className="card-header">
                  <div><h2>Limites d’analyse</h2><div className="sub">Garde-fous appliqués aux scans</div></div>
                  <ShieldCheck size={16} style={{ marginLeft: 'auto', color: 'var(--green)' }} />
                </div>
                <div className="card-pad">
                  <div className="form-grid">
                    <div className="field">
                      <label htmlFor="max-files">Fichiers PHP maximum</label>
                      <input id="max-files" className="input" type="number" min={1} max={10000} value={values.max_files ?? '2500'} onChange={(e) => setValue('max_files', e.target.value)} />
                    </div>
                    <div className="field">
                      <label htmlFor="max-pages">Pages Web maximum</label>
                      <input id="max-pages" className="input" type="number" min={1} max={10} value={values.max_pages ?? '3'} onChange={(e) => setValue('max_pages', e.target.value)} />
                    </div>
                    <div className="field full">
                      <label htmlFor="trusted-domains">Domaines de scripts autorisés</label>
                      <input id="trusted-domains" className="input" value={values.trusted_script_domains ?? ''} onChange={(e) => setValue('trusted_script_domains', e.target.value)} placeholder="js.stripe.com, cdn.jsdelivr.net, googletagmanager.com" />
                      <span className="hint">Liste séparée par des virgules. Laisser vide pour utiliser la liste de référence intégrée.</span>
                    </div>
                    <div className="field full">
                      <label className="checkbox">
                        <input type="checkbox" checked={boolValue('enable_external_tools', true)} onChange={(e) => setValue('enable_external_tools', e.target.checked ? 'true' : 'false')} />
                        <span>Utiliser les outils externes installés (Semgrep, Composer audit) s’ils sont disponibles</span>
                      </label>
                      <span className="hint">Optionnel et passif : Cybbig n’installe rien et ignore l’outil s’il est absent.</span>
                    </div>
                    <div className="field full">
                      <label className="checkbox">
                        <input type="checkbox" checked={boolValue('osv_online', false)} onChange={(e) => setValue('osv_online', e.target.checked ? 'true' : 'false')} />
                        <span>Vérifier les dépendances Composer auprès d’OSV.dev</span>
                      </label>
                      <span className="hint">Désactivé par défaut : l’activer envoie les noms et versions des paquets analysés à api.osv.dev. Sinon, l’inventaire reste purement local.</span>
                    </div>
                  </div>
                  <AlertBox kind="info">
                    Ces limites s’appliquent aussi aux automatisations. Aucun paramètre ne permet d’activer un exploit, du fuzzing ou du contournement d’authentification.
                  </AlertBox>
                </div>
              </section>

              <section className="card">
                <div className="card-header">
                  <div><h2>Administration</h2><div className="sub">Configuration complète, terminal et base de données</div></div>
                  <Lock size={16} style={{ marginLeft: 'auto', color: 'var(--critical)' }} />
                </div>
                <div className="card-pad">
                  <p className="small muted" style={{ marginTop: 0 }}>
                    L’accès à toutes les clés internes, au terminal libre et à la console SQL est protégé par identifiant et mot de passe.
                  </p>
                  <Link className="btn sm" to="/admin"><Lock size={13} /> Ouvrir l’administration</Link>
                </div>
              </section>
            </div>

            <div className="stack" style={{ gap: 14 }}>
              <section className="card">
                <div className="card-header"><div><h2>État du poste</h2><div className="sub">Contrôles locaux</div></div><ServerCog size={16} style={{ marginLeft: 'auto', color: 'var(--accent)' }} /></div>
                <div className="card-pad">
                  <div className="kv-list">
                    <div className="kv-item"><span>Backend</span><b>{health ? `${health.app} ${health.version}` : '—'}</b></div>
                    <div className="kv-item"><span>API locale</span><b><span className="status-dot" style={{ display: 'inline-block', marginRight: 5 }} />127.0.0.1:8765</b></div>
                    <div className="kv-item"><span>Base SQLite</span><b>{health?.database.ok ? <span style={{ color: 'var(--green)' }}>OK · schéma {health.database.schema_version}</span> : '—'}</b></div>
                    <div className="kv-item"><span>Recherche FTS5</span><b>{health?.database.fts5 ? 'Disponible' : 'Indisponible'}</b></div>
                    <div className="kv-item"><span>Planificateur</span><b>{health?.scheduler.running ? <span style={{ color: 'var(--green)' }}>Actif · {health.scheduler.enabled}/{health.scheduler.total}</span> : 'Arrêté'}</b></div>
                    <div className="kv-item"><span>Assistant</span><b>{ollama?.available ? 'Ollama' : 'Repli local'}</b></div>
                    <div className="kv-item"><span>Dernière vérification</span><b>{health ? relativeDate(health.time) : '—'}</b></div>
                  </div>
                </div>
              </section>

              <section className="card">
                <div className="card-header"><div><h2>Consentement</h2><div className="sub">Cadre d’utilisation</div></div><ListChecks size={16} style={{ marginLeft: 'auto', color: 'var(--green)' }} /></div>
                <div className="card-pad">
                  {!consent ? <Loading /> : consent.accepted ? (
                    <>
                      <div className="row" style={{ gap: 7 }}><CheckCircle2 size={15} color="var(--green)" /><b className="small">Accepté</b><span className="tag" style={{ marginLeft: 'auto' }}>v{consent.version}</span></div>
                      <div className="kv-list mt-2">
                        <div className="kv-item"><span>Date</span><b>{formatDate(consent.record?.accepted_at)}</b></div>
                        <div className="kv-item"><span>Organisation</span><b>{consent.record?.organization || 'non renseignée'}</b></div>
                        <div className="kv-item"><span>Usage prévu</span><b>{consent.record?.purpose || 'non renseigné'}</b></div>
                        <div className="kv-item"><span>Empreinte</span><b className="mono tiny">{consent.record?.text_hash ? `${consent.record.text_hash.slice(0, 16)}…` : '—'}</b></div>
                      </div>
                    </>
                  ) : (
                    <AlertBox kind="error">Le cadre d’utilisation doit être accepté.</AlertBox>
                  )}
                </div>
              </section>

              <section className="card">
                <div className="card-header"><div><h2>Confidentialité</h2><div className="sub">Local par conception</div></div><Database size={16} style={{ marginLeft: 'auto', color: 'var(--muted)' }} /></div>
                <div className="card-pad">
                  <p className="small muted" style={{ marginTop: 0 }}>
                    Les résultats, rapports et journaux restent sur ce poste. Aucune télémétrie n’est activée.
                    Les secrets détectés sont masqués dans les preuves.
                  </p>
                  <div className="field">
                    <label>Fichier de données</label>
                    <code className="tiny" style={{ wordBreak: 'break-all', color: 'var(--muted)' }}>{health?.database.path || '—'}</code>
                  </div>
                </div>
              </section>
            </div>
          </div>
        )
      )}

      {tab === 'engines' && (
        !engines ? <Loading /> : (
          <div className="stack" style={{ gap: 14 }}>
            <AlertBox kind="info">
              <b>Limites assumées.</b> Aucun moteur n’exécute le code analysé, n’envoie de charge d’exploitation ni ne contourne une authentification.
              Les résultats sont heuristiques et exigent une validation humaine.
            </AlertBox>
            <div className="grid auto">
              {engines.engines.map((engine) => (
                <article className="card card-pad" key={engine.id}>
                  <div className="row" style={{ gap: 8 }}>
                    <div className="icon-wrap"><FlaskConical size={14} /></div>
                    <div><div style={{ fontWeight: 650 }}>{engine.name}</div><div className="tiny faint">{engine.mode}</div></div>
                    <span className="pill completed" style={{ marginLeft: 'auto' }}>{engine.status}</span>
                  </div>
                  <div className="row wrap mt-2" style={{ gap: 5 }}>
                    {engine.capabilities.map((capability) => <span className="tag" key={capability}>{capability}</span>)}
                  </div>
                </article>
              ))}
            </div>
            <section className="card">
              <div className="card-header"><div><h2>Garanties techniques</h2><div className="sub">Ce que Cybbig ne fait pas</div></div><ShieldCheck size={16} style={{ marginLeft: 'auto', color: 'var(--green)' }} /></div>
              <div className="card-pad">
                <div className="kv-list">
                  {engines.limitations.map((limitation, index) => (
                    <div className="kv-item" key={index}><span>{index + 1}</span><b style={{ textAlign: 'left', fontWeight: 500 }}>{limitation}</b></div>
                  ))}
                  <div className="kv-item"><span>Réseau</span><b style={{ textAlign: 'left', fontWeight: 500 }}>Écoute uniquement sur 127.0.0.1, jamais exposé au LAN.</b></div>
                  <div className="kv-item"><span>Secrets</span><b style={{ textAlign: 'left', fontWeight: 500 }}>Masquage des valeurs sensibles dans les preuves et les rapports.</b></div>
                </div>
              </div>
            </section>
          </div>
        )
      )}

      {tab === 'audit' && (
        <section className="card">
          <div className="card-header">
            <div><h2>Journal d’audit</h2><div className="sub">Actions locales horodatées, 200 dernières entrées</div></div>
            <div className="right">
              <input className="input" style={{ width: 220 }} placeholder="Filtrer…" value={auditFilter} onChange={(e) => setAuditFilter(e.target.value)} />
              <button className="btn ghost sm" onClick={loadAudit}><RefreshCw size={13} /> Recharger</button>
            </div>
          </div>
          {!audit ? <Loading /> : filteredAudit.length === 0 ? (
            <EmptyState icon={<Timer size={26} />} title="Aucune entrée" description={auditFilter ? 'Aucune entrée ne correspond au filtre.' : 'Les actions apparaîtront ici.'} />
          ) : (
            <div className="table-wrap">
              <table className="data">
                <thead><tr><th>Date</th><th>Action</th><th>Acteur</th><th>Détails</th></tr></thead>
                <tbody>
                  {filteredAudit.map((entry) => (
                    <tr key={entry.id}>
                      <td className="tiny faint" style={{ whiteSpace: 'nowrap' }}>{formatDate(entry.created_at)}</td>
                      <td><span className="tag">{entry.action}</span></td>
                      <td className="small muted">{entry.actor}</td>
                      <td><code className="cell-mono" style={{ display: 'block', maxWidth: 620, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={entry.details}>{entry.details || '—'}</code></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      )}

      <div className="card card-pad mt-3 row wrap" style={{ gap: 14 }}>
        <KeyRound size={16} color="var(--muted)" />
        <span className="small muted">Les clés API sont stockées en clair dans la base locale, protégée par les permissions de votre compte Windows. Ne partagez jamais le fichier <span className="mono">cybbig.db</span>.</span>
      </div>
    </>
  )
}
