import { useEffect, useRef, useState } from 'react'
import {
  Fingerprint, Globe, Play, Plus, Power, Square, TestTube, Trash2, Volume2, Wifi, WifiOff,
} from 'lucide-react'
import { api, ApiError, formatDate } from '../api'
import { AlertBox, EmptyState, Loading, Modal, PageHeader, useToast } from '../components/ui'
import GeneratorPanel from '../components/GeneratorPanel'
import TunnelPanel from '../components/TunnelPanel'

interface ProxyPreset { id: string; label: string; scheme: string; host: string; port: number; note: string }

interface Voice { name: string; culture: string; gender: string; age: string }
interface Proxy {
  id: string; label: string; scheme: string; host: string; port: number; username: string
  has_password: boolean; enabled: boolean; note: string; active: boolean; url: string
  last_test_at: string | null; last_test_ok: number | null; last_test_ip: string; last_test_ms: number | null
}
interface ProxyStatus { active: Proxy | null; route_scans: boolean; route_research: boolean; count: number }
interface VpnProfile {
  id: string; label: string; provider: string; kind: string; config_path: string; config_exists: boolean
}
interface VpnClients { wireguard: { available: boolean; path: string }; openvpn: { available: boolean; path: string } }
interface VpnStatus {
  clients: VpnClients; connected: boolean; wireguard_tunnels: string[]; openvpn_running: boolean
  profiles: number; public_ip?: { ok: boolean; ip: string; error?: string }
  provider_apps?: Array<{ name: string; installed: boolean }>
}

const API_BASE = (import.meta.env.VITE_API_BASE as string | undefined) ?? ''

export default function Privacy() {
  const toast = useToast()
  // TTS
  const [ttsAvailable, setTtsAvailable] = useState(true)
  const [voices, setVoices] = useState<Voice[]>([])
  const [text, setText] = useState('')
  const [voice, setVoice] = useState('')
  const [rate, setRate] = useState(0)
  const [speaking, setSpeaking] = useState(false)
  // Proxies
  const [proxies, setProxies] = useState<Proxy[] | null>(null)
  const [proxyStatus, setProxyStatus] = useState<ProxyStatus | null>(null)
  const [proxyModal, setProxyModal] = useState(false)
  const [testing, setTesting] = useState<string | null>(null)
  const [proxyForm, setProxyForm] = useState({ scheme: 'http', host: '', port: 8080, label: '', username: '', password: '', note: '' })
  // VPN
  const [vpn, setVpn] = useState<VpnStatus | null>(null)
  const [vpnProfiles, setVpnProfiles] = useState<VpnProfile[] | null>(null)
  const [vpnModal, setVpnModal] = useState(false)
  const [vpnBusy, setVpnBusy] = useState(false)
  const [vpnForm, setVpnForm] = useState({ config_path: '', label: '', provider: '', kind: '' })
  const pollRef = useRef<number | null>(null)
  const [presets, setPresets] = useState<ProxyPreset[]>([])
  const vpnPollRef = useRef<number | null>(null)

  const loadVoices = () => api.get<{ available: boolean; voices: Voice[] }>('/api/privacy/tts/voices')
    .then((d) => { setTtsAvailable(d.available); setVoices(d.voices) })
    .catch(() => setTtsAvailable(false))

  const loadProxies = () => api.get<{ items: Proxy[]; status: ProxyStatus }>('/api/privacy/proxies')
    .then((d) => { setProxies(d.items); setProxyStatus(d.status) })
    .catch((e) => toast.push((e as Error).message, 'error'))

  const loadVpn = () => {
    api.get<VpnStatus>('/api/privacy/vpn').then(setVpn).catch(() => undefined)
    api.get<{ items: VpnProfile[]; clients: VpnClients }>('/api/privacy/vpn/profiles')
      .then((d) => setVpnProfiles(d.items)).catch(() => setVpnProfiles([]))
  }

  useEffect(() => {
    loadVoices(); loadProxies(); loadVpn()
    api.get<{ items: ProxyPreset[] }>('/api/privacy/proxies/presets').then((d) => setPresets(d.items)).catch(() => undefined)
    const poll = () => api.get<{ tts: { speaking: boolean } }>('/api/privacy').then((d) => setSpeaking(d.tts.speaking)).catch(() => undefined)
    pollRef.current = window.setInterval(poll, 4000)
    return () => { if (pollRef.current) window.clearInterval(pollRef.current) }
  }, [])

  useEffect(() => {
    vpnPollRef.current = window.setInterval(loadVpn, 10000)
    return () => { if (vpnPollRef.current) window.clearInterval(vpnPollRef.current) }
  }, [])

  // --- TTS actions ---
  const speak = async () => {
    if (!text.trim()) { toast.push('Entrez un texte à lire.', 'error'); return }
    try { await api.post('/api/privacy/tts/speak', { text, voice, rate }); setSpeaking(true) }
    catch (e) { toast.push((e as Error).message, 'error') }
  }
  const stopSpeak = async () => { try { await api.post('/api/privacy/tts/stop'); setSpeaking(false) } catch { /* ignore */ } }
  const downloadWav = async () => {
    if (!text.trim()) { toast.push('Entrez un texte à lire.', 'error'); return }
    try {
      const res = await fetch(`${API_BASE}/api/privacy/tts/wav`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ text, voice, rate }),
      })
      if (!res.ok) throw new ApiError(res.status, (await res.json().catch(() => ({ detail: res.statusText })) as { detail: string }).detail)
      const url = URL.createObjectURL(await res.blob())
      const link = document.createElement('a'); link.href = url; link.download = 'cybbig-lecture.wav'; link.click()
      URL.revokeObjectURL(url)
    } catch (e) { toast.push((e as Error).message, 'error') }
  }

  // --- Proxy actions ---
  const addProxy = async (event: React.FormEvent) => {
    event.preventDefault()
    try {
      await api.post('/api/privacy/proxies', proxyForm)
      toast.push('Proxy ajouté.', 'success'); setProxyModal(false)
      setProxyForm({ scheme: 'http', host: '', port: 8080, label: '', username: '', password: '', note: '' })
      loadProxies()
    } catch (e) { toast.push((e as Error).message, 'error') }
  }
  const addPreset = async (preset: ProxyPreset) => {
    try { await api.post(`/api/privacy/proxies/presets/${preset.id}`); toast.push(`${preset.label} ajouté.`, 'success'); loadProxies() }
    catch (e) { toast.push((e as Error).message, 'error') }
  }
  const activate = async (p: Proxy) => {
    try { await api.post(p.active ? '/api/privacy/proxies/deactivate' : `/api/privacy/proxies/${p.id}/activate`); loadProxies() }
    catch (e) { toast.push((e as Error).message, 'error') }
  }
  const testProxy = async (p: Proxy) => {
    setTesting(p.id)
    try {
      const r = await api.post<{ ok: boolean; ip: string; ms: number | null; error: string }>(`/api/privacy/proxies/${p.id}/test`)
      toast.push(r.ok ? `Proxy OK — IP de sortie ${r.ip} (${r.ms} ms)` : `Échec : ${r.error}`, r.ok ? 'success' : 'error')
      loadProxies()
    } catch (e) { toast.push((e as Error).message, 'error') } finally { setTesting(null) }
  }
  const deleteProxy = async (p: Proxy) => {
    if (!window.confirm(`Supprimer le proxy ${p.url} ?`)) return
    try { await api.del(`/api/privacy/proxies/${p.id}`); loadProxies() } catch (e) { toast.push((e as Error).message, 'error') }
  }
  const toggleRoute = async (enabled: boolean) => {
    try { await api.post('/api/privacy/proxies/route', { enabled }); loadProxies() } catch (e) { toast.push((e as Error).message, 'error') }
  }
  const toggleResearchRoute = async (enabled: boolean) => {
    try { await api.post('/api/privacy/proxies/route-research', { enabled }); loadProxies() } catch (e) { toast.push((e as Error).message, 'error') }
  }

  // --- VPN actions ---
  const addVpn = async (event: React.FormEvent) => {
    event.preventDefault()
    try {
      await api.post('/api/privacy/vpn/profiles', vpnForm)
      toast.push('Profil VPN ajouté.', 'success'); setVpnModal(false)
      setVpnForm({ config_path: '', label: '', provider: '', kind: '' }); loadVpn()
    } catch (e) { toast.push((e as Error).message, 'error') }
  }
  const connectVpn = async (p: VpnProfile) => {
    setVpnBusy(true)
    try {
      const r = await api.post<{ ok: boolean; stderr: string; hint?: string }>(`/api/privacy/vpn/profiles/${p.id}/connect`)
      toast.push(r.ok ? 'Tunnel demandé.' : (r.hint || r.stderr || 'Échec de connexion.'), r.ok ? 'success' : 'error')
      loadVpn()
    } catch (e) { toast.push((e as Error).message, 'error') } finally { setVpnBusy(false) }
  }
  const disconnectVpn = async () => {
    setVpnBusy(true)
    try { await api.post('/api/privacy/vpn/disconnect'); toast.push('Déconnexion demandée.', 'info'); loadVpn() }
    catch (e) { toast.push((e as Error).message, 'error') } finally { setVpnBusy(false) }
  }
  const deleteVpn = async (p: VpnProfile) => {
    if (!window.confirm(`Supprimer le profil « ${p.label || p.config_path} » ?`)) return
    try { await api.del(`/api/privacy/vpn/profiles/${p.id}`); loadVpn() } catch (e) { toast.push((e as Error).message, 'error') }
  }
  const refreshIp = async () => {
    try { const d = await api.get<VpnStatus>('/api/privacy/vpn?with_ip=true'); setVpn(d) }
    catch (e) { toast.push((e as Error).message, 'error') }
  }

  return (
    <>
      <PageHeader
        title="Confidentialité & Accessibilité"
        description="Synthèse vocale locale, gestion de proxies et pilotage de vos clients VPN (configurations fournies par vous)."
      />

      <AlertBox kind="info">
        <b>Local et sous votre contrôle.</b> La synthèse vocale est 100 % hors ligne. Les proxies et VPN utilisent
        vos propres serveurs et fichiers de configuration. Cybbig ne fournit aucun service d’anonymat ni numéro
        de téléphone, et ne stocke aucun identifiant VPN.
      </AlertBox>

      {/* ---------- TTS ---------- */}
      <div className="card mt-3">
        <div className="card-header">
          <div><h2><Volume2 size={15} style={{ verticalAlign: '-2px' }} /> Synthèse vocale</h2>
            <div className="sub">Lire à voix haute un rapport ou un texte (voix SAPI du poste)</div></div>
        </div>
        <div className="card-pad">
          {!ttsAvailable ? (
            <AlertBox kind="error">La synthèse vocale n’est disponible que sous Windows.</AlertBox>
          ) : (
            <>
              <textarea className="input" rows={4} value={text} onChange={(e) => setText(e.target.value)}
                placeholder="Collez un texte, un résumé de rapport ou un finding à écouter…" style={{ resize: 'vertical' }} />
              <div className="row wrap" style={{ gap: 10, marginTop: 10, alignItems: 'flex-end' }}>
                <div className="field" style={{ minWidth: 220 }}>
                  <label>Voix</label>
                  <select className="select" value={voice} onChange={(e) => setVoice(e.target.value)}>
                    <option value="">Voix par défaut</option>
                    {voices.map((v) => <option key={v.name} value={v.name}>{v.name} ({v.culture})</option>)}
                  </select>
                </div>
                <div className="field" style={{ minWidth: 180 }}>
                  <label>Vitesse : {rate}</label>
                  <input type="range" min={-10} max={10} value={rate} onChange={(e) => setRate(Number(e.target.value))} style={{ accentColor: 'var(--accent-strong)' }} />
                </div>
                <div className="row" style={{ gap: 6, marginLeft: 'auto' }}>
                  {speaking
                    ? <button className="btn" onClick={stopSpeak}><Square size={13} /> Arrêter</button>
                    : <button className="btn primary" onClick={speak}><Play size={13} /> Lire</button>}
                  <button className="btn" onClick={downloadWav}>Télécharger .wav</button>
                </div>
              </div>
            </>
          )}
        </div>
      </div>

      {/* ---------- Proxies ---------- */}
      <div className="card mt-3">
        <div className="card-header">
          <div><h2><Globe size={15} style={{ verticalAlign: '-2px' }} /> Proxies</h2>
            <div className="sub">{proxyStatus ? `${proxyStatus.count} proxy(s)` : '…'}{proxyStatus?.active ? ` · actif : ${proxyStatus.active.url}` : ' · aucun actif'}</div></div>
          <button className="btn primary sm" onClick={() => setProxyModal(true)}><Plus size={14} /> Ajouter</button>
        </div>
        <div className="card-pad">
          <label className="checkbox" style={{ marginBottom: 10 }}>
            <input type="checkbox" checked={!!proxyStatus?.route_scans} onChange={(e) => toggleRoute(e.target.checked)} />
            <span>Router les analyses du projet via le proxy actif</span>
          </label>
          <label className="checkbox" style={{ marginBottom: 12 }}>
            <input type="checkbox" checked={!!proxyStatus?.route_research} onChange={(e) => toggleResearchRoute(e.target.checked)} />
            <span>Router la recherche web et la lecture de pages via le proxy actif</span>
          </label>
          {presets.length > 0 && (
            <div className="row wrap" style={{ gap: 6, marginBottom: 10, alignItems: 'center' }}>
              <span className="tiny faint">Modèles :</span>
              {presets.map((preset) => (
                <button key={preset.id} className="btn sm" onClick={() => addPreset(preset)} title={`${preset.scheme}://${preset.host}:${preset.port} — ${preset.note}`}>{preset.label}</button>
              ))}
            </div>
          )}
          {!proxies ? <Loading /> : proxies.length === 0 ? (
            <EmptyState icon={<Globe size={28} />} title="Aucun proxy" description="Ajoutez un proxy que vous contrôlez pour router vos analyses." />
          ) : (
            <div className="table-wrap">
              <table className="data">
                <thead><tr><th>Proxy</th><th>Dernier test</th><th style={{ textAlign: 'right' }}>Actions</th></tr></thead>
                <tbody>
                  {proxies.map((p) => (
                    <tr key={p.id}>
                      <td>
                        <div style={{ fontWeight: 600 }}>{p.label || p.url}</div>
                        <div className="tiny faint cell-mono">{p.url}{p.active && <span className="pill completed" style={{ marginLeft: 6 }}>actif</span>}</div>
                      </td>
                      <td className="tiny faint">
                        {p.last_test_at
                          ? <>{p.last_test_ok ? `OK · ${p.last_test_ip} · ${p.last_test_ms} ms` : 'échec'}<br />{formatDate(p.last_test_at)}</>
                          : 'jamais testé'}
                      </td>
                      <td>
                        <div className="row" style={{ gap: 6, justifyContent: 'flex-end' }}>
                          <button className="btn sm" onClick={() => activate(p)}>{p.active ? 'Désactiver' : 'Activer'}</button>
                          <button className="btn sm" onClick={() => testProxy(p)} disabled={testing === p.id}><TestTube size={12} /> {testing === p.id ? '…' : 'Tester'}</button>
                          <button className="icon-btn" style={{ width: 28, height: 28 }} onClick={() => deleteProxy(p)} title="Supprimer"><Trash2 size={12} /></button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* ---------- VPN ---------- */}
      <div className="card mt-3">
        <div className="card-header">
          <div><h2>{vpn?.connected ? <Wifi size={15} style={{ verticalAlign: '-2px' }} /> : <WifiOff size={15} style={{ verticalAlign: '-2px' }} />} Client VPN</h2>
            <div className="sub">
              {vpn ? (vpn.connected ? `Connecté${vpn.wireguard_tunnels.length ? ` · ${vpn.wireguard_tunnels.join(', ')}` : vpn.openvpn_running ? ' · OpenVPN' : ''}` : 'Non connecté') : '…'}
            </div></div>
          <div className="row" style={{ gap: 6 }}>
            <button className="btn sm" onClick={refreshIp}><Globe size={12} /> IP de sortie</button>
            {vpn?.connected && <button className="btn sm" onClick={disconnectVpn} disabled={vpnBusy}><Power size={12} /> Déconnecter</button>}
            <button className="btn primary sm" onClick={() => setVpnModal(true)}><Plus size={14} /> Profil</button>
          </div>
        </div>
        <div className="card-pad">
          {vpn && (
            <div className="row wrap" style={{ gap: 8, marginBottom: 10 }}>
              <span className={`pill ${vpn.clients.wireguard.available ? 'completed' : 'failed'}`}>WireGuard {vpn.clients.wireguard.available ? 'détecté' : 'absent'}</span>
              <span className={`pill ${vpn.clients.openvpn.available ? 'completed' : 'failed'}`}>OpenVPN {vpn.clients.openvpn.available ? 'détecté' : 'absent'}</span>
              {vpn.provider_apps?.filter((a) => a.installed).map((a) => <span key={a.name} className="pill" title="Détectée, non pilotée par Cybbig">{a.name} installé</span>)}
              {vpn.public_ip && <span className="pill">IP de sortie : {vpn.public_ip.ok ? vpn.public_ip.ip : '—'}</span>}
            </div>
          )}
          {(!vpn?.clients.wireguard.available && !vpn?.clients.openvpn.available) && (
            <AlertBox kind="info">Aucun client VPN détecté. Installez WireGuard ou OpenVPN, puis ajoutez le fichier de configuration exporté depuis votre fournisseur (Proton VPN, Hide.me…).</AlertBox>
          )}
          {!vpnProfiles ? <Loading /> : vpnProfiles.length === 0 ? (
            <EmptyState icon={<Fingerprint size={28} />} title="Aucun profil VPN" description="Ajoutez un fichier .conf (WireGuard) ou .ovpn (OpenVPN) exporté depuis votre fournisseur." />
          ) : (
            <div className="grid auto">
              {vpnProfiles.map((p) => (
                <article className="card card-pad" key={p.id}>
                  <div className="row" style={{ gap: 8 }}>
                    <div style={{ minWidth: 0 }}>
                      <div style={{ fontWeight: 650, fontSize: 13.5 }}>{p.label || p.provider || p.kind}</div>
                      <div className="tiny faint">{p.kind} · {p.provider || '—'}</div>
                      <div className="tiny faint cell-mono clamp-2">{p.config_path}</div>
                    </div>
                    <span className={`pill ${p.config_exists ? 'completed' : 'failed'}`} style={{ marginLeft: 'auto' }}>{p.config_exists ? 'config OK' : 'config manquante'}</span>
                  </div>
                  <div className="row wrap" style={{ gap: 6, marginTop: 4 }}>
                    <button className="btn sm" onClick={() => connectVpn(p)} disabled={vpnBusy || !p.config_exists}><Power size={12} /> Connecter</button>
                    <button className="icon-btn" style={{ width: 28, height: 28, marginLeft: 'auto' }} onClick={() => deleteVpn(p)} title="Supprimer"><Trash2 size={12} /></button>
                  </div>
                </article>
              ))}
            </div>
          )}
          <p className="tiny faint" style={{ marginTop: 10 }}>
            Établir un tunnel nécessite généralement des droits administrateur : lancez Cybbig en administrateur si la connexion échoue.
          </p>
        </div>
      </div>

      <TunnelPanel profiles={vpnProfiles ?? []} onChanged={loadVpn} />
      <GeneratorPanel />

      {/* ---------- Modals ---------- */}
      <Modal open={proxyModal} onClose={() => setProxyModal(false)} title="Ajouter un proxy" subtitle="Serveur que vous contrôlez">
        <form onSubmit={addProxy}>
          <div className="form-grid">
            <div className="field"><label>Schéma</label>
              <select className="select" value={proxyForm.scheme} onChange={(e) => setProxyForm({ ...proxyForm, scheme: e.target.value })}>
                <option value="http">http</option><option value="https">https</option>
                <option value="socks5">socks5</option><option value="socks5h">socks5h</option><option value="socks4">socks4</option>
              </select></div>
            <div className="field"><label>Hôte *</label><input className="input" required value={proxyForm.host} onChange={(e) => setProxyForm({ ...proxyForm, host: e.target.value })} placeholder="127.0.0.1" /></div>
            <div className="field"><label>Port *</label><input className="input" type="number" required value={proxyForm.port} onChange={(e) => setProxyForm({ ...proxyForm, port: Number(e.target.value) })} /></div>
            <div className="field"><label>Libellé</label><input className="input" value={proxyForm.label} onChange={(e) => setProxyForm({ ...proxyForm, label: e.target.value })} placeholder="Proxy labo" /></div>
            <div className="field"><label>Utilisateur</label><input className="input" value={proxyForm.username} onChange={(e) => setProxyForm({ ...proxyForm, username: e.target.value })} /></div>
            <div className="field"><label>Mot de passe</label><input className="input" type="password" value={proxyForm.password} onChange={(e) => setProxyForm({ ...proxyForm, password: e.target.value })} /></div>
            <div className="field full"><label>Note</label><input className="input" value={proxyForm.note} onChange={(e) => setProxyForm({ ...proxyForm, note: e.target.value })} /></div>
          </div>
          <div className="form-actions"><button type="button" className="btn" onClick={() => setProxyModal(false)}>Annuler</button><button className="btn primary">Ajouter</button></div>
        </form>
      </Modal>

      <Modal open={vpnModal} onClose={() => setVpnModal(false)} title="Ajouter un profil VPN" subtitle="Pointeur vers votre fichier de configuration">
        <form onSubmit={addVpn}>
          <div className="form-grid">
            <div className="field full"><label>Chemin du fichier (.conf / .ovpn) *</label><input className="input" required value={vpnForm.config_path} onChange={(e) => setVpnForm({ ...vpnForm, config_path: e.target.value })} placeholder="C:\Users\...\proton-fr.conf" /><span className="hint">Fichier exporté depuis votre fournisseur. Cybbig ne lit pas vos identifiants.</span></div>
            <div className="field"><label>Type</label>
              <select className="select" value={vpnForm.kind} onChange={(e) => setVpnForm({ ...vpnForm, kind: e.target.value })}>
                <option value="">Auto (extension)</option><option value="wireguard">WireGuard</option><option value="openvpn">OpenVPN</option>
              </select></div>
            <div className="field"><label>Fournisseur</label><input className="input" value={vpnForm.provider} onChange={(e) => setVpnForm({ ...vpnForm, provider: e.target.value })} placeholder="Proton VPN, Hide.me…" /></div>
            <div className="field full"><label>Libellé</label><input className="input" value={vpnForm.label} onChange={(e) => setVpnForm({ ...vpnForm, label: e.target.value })} placeholder="Proton — France" /></div>
          </div>
          <div className="form-actions"><button type="button" className="btn" onClick={() => setVpnModal(false)}>Annuler</button><button className="btn primary">Ajouter</button></div>
        </form>
      </Modal>
    </>
  )
}
