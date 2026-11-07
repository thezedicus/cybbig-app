import { useState } from 'react'
import { Gauge, KeyRound, ShieldCheck, Zap } from 'lucide-react'
import { api } from '../api'
import { AlertBox, CodeBlock, Modal, useToast } from './ui'

interface Issue { level: 'error' | 'warning' | 'info'; message: string }
interface Analysis { valid: boolean; endpoint: string; dns: string[]; full_tunnel: boolean; has_preshared_key: boolean; issues: Issue[] }
interface Bundle { profile: { id: string; label: string }; server_config: string; client_path: string; notes: string[] }
interface Ranked { id: string; label: string; host: string; ms: number | null }

export interface TunnelProfile { id: string; label: string; provider: string; kind: string; config_exists: boolean }

// « Cybbig Tunnel » : VPN personnel auto-hébergé, analyse des fuites et connexion rapide, bâtis sur WireGuard.
export default function TunnelPanel({ profiles, onChanged }: { profiles: TunnelProfile[]; onChanged: () => void }) {
  const toast = useToast()
  const [modal, setModal] = useState(false)
  const [busy, setBusy] = useState(false)
  const [form, setForm] = useState({ name: 'Mon VPN', endpoint_host: '', endpoint_port: 51820, subnet: '10.66.0.0/24', full_tunnel: true, use_preshared_key: true })
  const [bundle, setBundle] = useState<Bundle | null>(null)
  const [analysis, setAnalysis] = useState<Analysis | null>(null)
  const [ranking, setRanking] = useState<Ranked[] | null>(null)
  const wg = profiles.filter((p) => p.kind === 'wireguard' && p.config_exists)

  const run = async (fn: () => Promise<void>) => {
    setBusy(true)
    try { await fn() } catch (e) { toast.push((e as Error).message, 'error') } finally { setBusy(false) }
  }

  const create = (event: React.FormEvent) => {
    event.preventDefault()
    void run(async () => {
      setBundle(await api.post<Bundle>('/api/privacy/vpn/bundle', form))
      setModal(false); onChanged()
    })
  }
  const analyze = (p: TunnelProfile) => run(async () => setAnalysis(await api.get<Analysis>(`/api/privacy/vpn/profiles/${p.id}/analysis`)))
  const harden = (p: TunnelProfile) => run(async () => {
    const r = await api.post<{ analysis: Analysis }>(`/api/privacy/vpn/profiles/${p.id}/harden`)
    setAnalysis(r.analysis); toast.push('Copie durcie créée (l’original est intact).', 'success'); onChanged()
  })
  const rank = () => run(async () => setRanking((await api.get<{ items: Ranked[] }>('/api/privacy/vpn/ranking')).items))
  const quick = () => run(async () => {
    const r = await api.post<{ chosen: Ranked; result: { ok: boolean; hint?: string; stderr?: string } }>('/api/privacy/vpn/quick-connect')
    toast.push(r.result.ok ? `Tunnel demandé : ${r.chosen.label}` : (r.result.hint || r.result.stderr || 'Échec de connexion.'), r.result.ok ? 'success' : 'error')
    onChanged()
  })

  return (
    <div className="card mt-3">
      <div className="card-header">
        <div><h2><ShieldCheck size={15} style={{ verticalAlign: '-2px' }} /> Cybbig Tunnel</h2>
          <div className="sub">VPN personnel WireGuard, analyse des fuites, durcissement et connexion rapide</div></div>
        <div className="row" style={{ gap: 6 }}>
          <button className="btn sm" onClick={rank} disabled={busy || wg.length === 0}><Gauge size={12} /> Classer</button>
          <button className="btn sm" onClick={quick} disabled={busy || wg.length === 0}><Zap size={12} /> Connexion rapide</button>
          <button className="btn primary sm" onClick={() => setModal(true)}><KeyRound size={13} /> Créer mon VPN</button>
        </div>
      </div>
      <div className="card-pad stack" style={{ gap: 10 }}>
        <p className="small faint" style={{ margin: 0 }}>
          Cybbig génère les clés et les deux configurations d’un serveur WireGuard que <b>vous</b> hébergez. Le tunnel est établi par le client
          WireGuard officiel. Un profil en tunnel complet IPv4 + IPv6 active le coupe-circuit natif de WireGuard pour Windows.
        </p>
        {ranking && (
          <div className="table-wrap"><table className="data"><thead><tr><th>Profil</th><th>Serveur</th><th>Latence</th></tr></thead><tbody>
            {ranking.map((r) => <tr key={r.id}><td>{r.label}</td><td className="cell-mono tiny">{r.host}</td><td>{r.ms === null ? 'sans réponse ICMP' : `${r.ms} ms`}</td></tr>)}
          </tbody></table></div>
        )}
        {wg.length > 0 && (
          <div className="row wrap" style={{ gap: 6 }}>
            {wg.map((p) => (
              <span key={p.id} className="row" style={{ gap: 4 }}>
                <b className="small">{p.label || p.provider || p.id}</b>
                <button className="btn sm" onClick={() => analyze(p)} disabled={busy}>Analyser</button>
                <button className="btn sm" onClick={() => harden(p)} disabled={busy}>Durcir</button>
              </span>
            ))}
          </div>
        )}
        {analysis && (
          <div className="stack" style={{ gap: 6 }}>
            <div className="row wrap" style={{ gap: 8 }}>
              <span className={`pill ${analysis.full_tunnel ? 'completed' : 'failed'}`}>{analysis.full_tunnel ? 'tunnel complet IPv4 + IPv6' : 'tunnel partiel'}</span>
              <span className={`pill ${analysis.dns.length ? 'completed' : 'failed'}`}>DNS {analysis.dns.length ? analysis.dns.join(', ') : 'non imposé'}</span>
              <span className={`pill ${analysis.has_preshared_key ? 'completed' : ''}`}>{analysis.has_preshared_key ? 'clé pré-partagée' : 'sans clé pré-partagée'}</span>
            </div>
            {analysis.issues.map((i, n) => <div key={n} className="small" style={{ color: i.level === 'info' ? 'var(--text-faint)' : 'var(--high)' }}>• {i.message}</div>)}
          </div>
        )}
      </div>

      <Modal open={modal} onClose={() => setModal(false)} title="Créer mon VPN" subtitle="Serveur WireGuard que vous contrôlez">
        <form onSubmit={create}>
          <div className="form-grid">
            <div className="field"><label>Nom</label><input className="input" required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></div>
            <div className="field"><label>Adresse du serveur *</label><input className="input" required value={form.endpoint_host} onChange={(e) => setForm({ ...form, endpoint_host: e.target.value })} placeholder="vpn.mondomaine.fr ou 203.0.113.7" /></div>
            <div className="field"><label>Port UDP</label><input className="input" type="number" value={form.endpoint_port} onChange={(e) => setForm({ ...form, endpoint_port: Number(e.target.value) })} /></div>
            <div className="field"><label>Sous-réseau privé</label><input className="input" value={form.subnet} onChange={(e) => setForm({ ...form, subnet: e.target.value })} /></div>
            <label className="checkbox full"><input type="checkbox" checked={form.full_tunnel} onChange={(e) => setForm({ ...form, full_tunnel: e.target.checked })} /><span>Tunnel complet (tout le trafic, coupe-circuit natif)</span></label>
            <label className="checkbox full"><input type="checkbox" checked={form.use_preshared_key} onChange={(e) => setForm({ ...form, use_preshared_key: e.target.checked })} /><span>Clé pré-partagée</span></label>
          </div>
          <div className="form-actions"><button type="button" className="btn" onClick={() => setModal(false)}>Annuler</button><button className="btn primary" disabled={busy}>Générer</button></div>
        </form>
      </Modal>

      <Modal open={!!bundle} onClose={() => setBundle(null)} title="Configuration du serveur" subtitle="À copier maintenant : Cybbig ne la conserve pas" size="wide">
        {bundle && (
          <div className="stack" style={{ gap: 10 }}>
            <CodeBlock code={bundle.server_config} label="wg0.conf (serveur)" />
            {bundle.notes.map((n, i) => <div key={i} className="small">• {n}</div>)}
            <AlertBox>Profil client « {bundle.profile.label} » enregistré : <span className="cell-mono">{bundle.client_path}</span></AlertBox>
          </div>
        )}
      </Modal>
    </div>
  )
}
