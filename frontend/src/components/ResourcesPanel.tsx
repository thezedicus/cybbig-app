import { useEffect, useState } from 'react'
import { Cpu, Flame, MemoryStick, MonitorCog } from 'lucide-react'
import { api } from '../api'
import { Progress, useToast } from './ui'

interface Gpu { name: string; vendor: string; vram_mb: number; driver: string; dedicated: boolean; ollama_usable: boolean }
interface Resources {
  hardware: { cpu_name: string; cores_physical: number; cores_logical: number; ram_total_mb: number; gpus: Gpu[]; os: string }
  live: {
    cpu_percent: number | null
    memory: { total_mb: number; free_mb: number; used_percent: number }
    gpus: Array<{ name: string; load_percent: number; vram_used_mb: number; vram_total_mb: number; temperature_c: number }>
  }
  ollama: { reachable: boolean; models: Array<{ name: string; size_mb: number; gpu_percent: number }> }
  profile: string
  profile_effective: string
  profiles: Record<string, string>
  options: { num_thread: number; num_ctx: number; num_batch: number }
  workers: { scans: number; ai_cloud: number; ai_local: number }
  recommendations: string[]
}

const gb = (mb: number) => `${(mb / 1024).toFixed(1)} Go`

// Panneau « Ressources du PC » : matériel détecté, charge en direct et profil de performance appliqué à Ollama.
// Le profil s'applique immédiatement (il n'attend pas le bouton Enregistrer des Paramètres).
export default function ResourcesPanel() {
  const [data, setData] = useState<Resources | null>(null)
  const [busy, setBusy] = useState(false)
  const toast = useToast()

  const load = () => { api.get<Resources>('/api/resources').then(setData).catch(() => undefined) }
  useEffect(() => {
    load()
    const timer = window.setInterval(load, 5000)
    return () => window.clearInterval(timer)
  }, [])

  const setProfile = async (profile: string) => {
    try { setData(await api.put<Resources>('/api/resources/profile', { profile })); toast.push('Profil de performance appliqué.', 'success') }
    catch (err) { toast.push((err as Error).message, 'error') }
  }
  const warmup = async () => {
    setBusy(true)
    try {
      const result = await api.post<{ warmed: boolean }>('/api/resources/warmup')
      toast.push(result.warmed ? 'Modèle local chargé en mémoire.' : 'Aucun modèle local à précharger.', result.warmed ? 'success' : 'info')
      load()
    } catch (err) { toast.push((err as Error).message, 'error') } finally { setBusy(false) }
  }

  const hw = data?.hardware
  const usableGpu = hw?.gpus.some((g) => g.ollama_usable)
  return (
    <section className="card">
      <div className="card-header">
        <div><h2>Ressources du PC</h2><div className="sub">Processeur, mémoire et carte graphique utilisés par l’IA locale et les analyses</div></div>
        <MonitorCog size={16} style={{ marginLeft: 'auto', color: 'var(--accent)' }} />
      </div>
      <div className="card-pad stack" style={{ gap: 14 }}>
        {!data || !hw ? <span className="small faint">Détection du matériel…</span> : (
          <>
            <div className="kv-list">
              <div className="kv-item"><span><Cpu size={12} /> Processeur</span><b>{hw.cpu_name} · {hw.cores_physical} cœurs / {hw.cores_logical} threads</b></div>
              <div className="kv-item"><span><MemoryStick size={12} /> Mémoire</span><b>{gb(hw.ram_total_mb)} (libre : {gb(data.live.memory.free_mb)})</b></div>
              <div className="kv-item"><span>Carte graphique</span><b>{hw.gpus.length ? hw.gpus.map((g) => `${g.name}${g.dedicated ? '' : ' (intégrée)'}${g.ollama_usable ? ' ✓ utilisable par Ollama' : ' — non utilisée par Ollama'}`).join(' ; ') : 'aucune détectée'}</b></div>
            </div>

            <div className="stack" style={{ gap: 8 }}>
              <div><div className="row between tiny"><span>Charge du processeur</span><b>{data.live.cpu_percent ?? '—'} %</b></div><Progress value={data.live.cpu_percent ?? 0} /></div>
              <div><div className="row between tiny"><span>Mémoire utilisée</span><b>{data.live.memory.used_percent} %</b></div><Progress value={data.live.memory.used_percent} /></div>
              {data.live.gpus.map((g) => (
                <div key={g.name}><div className="row between tiny"><span>{g.name} · {g.vram_used_mb}/{g.vram_total_mb} Mo · {g.temperature_c} °C</span><b>{g.load_percent} %</b></div><Progress value={g.load_percent} /></div>
              ))}
            </div>

            <div className="kv-list">
              <div className="kv-item"><span>Modèle chargé dans Ollama</span>
                <b>{data.ollama.models.length ? data.ollama.models.map((m) => `${m.name} (${gb(m.size_mb)}, ${m.gpu_percent} % sur GPU)`).join(' ; ') : data.ollama.reachable ? 'aucun (chargé à la première question)' : 'Ollama local injoignable'}</b></div>
              <div className="kv-item"><span>Réglages envoyés à Ollama</span><b>{data.options.num_thread} threads · contexte {data.options.num_ctx} · lot {data.options.num_batch}</b></div>
              <div className="kv-item"><span>Tâches en parallèle</span><b>analyses : {data.workers.scans} · IA locale : {data.workers.ai_local} · IA en ligne : {data.workers.ai_cloud}</b></div>
            </div>

            <div className="field">
              <label htmlFor="perf-profile">Profil de performance</label>
              <select id="perf-profile" className="select" value={data.profile} onChange={(e) => setProfile(e.target.value)}>
                {Object.entries(data.profiles).map(([key, label]) => <option key={key} value={key}>{label}</option>)}
              </select>
              <span className="hint">Profil appliqué : {data.profiles[data.profile_effective]}. Économe : 2048 jetons de contexte, moitié des cœurs. Maximum : 8192 jetons, tous les cœurs physiques.
                Changer de profil recharge le modèle une fois (quelques secondes).</span>
            </div>

            <div className="row wrap" style={{ gap: 8 }}>
              <button type="button" className="btn sm" onClick={warmup} disabled={busy}><Flame size={13} /> {busy ? 'Chargement…' : 'Précharger le modèle local'}</button>
              {!usableGpu && <span className="tiny faint">Sans GPU compatible, l’IA locale reste limitée par le processeur.</span>}
            </div>

            {data.recommendations.length > 0 && (
              <ul className="small" style={{ margin: 0, paddingLeft: 18, display: 'grid', gap: 6, color: 'var(--text-soft)' }}>
                {data.recommendations.map((tip) => <li key={tip}>{tip}</li>)}
              </ul>
            )}
          </>
        )}
      </div>
    </section>
  )
}
