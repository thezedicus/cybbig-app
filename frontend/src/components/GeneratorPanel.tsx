import { useEffect, useState } from 'react'
import { Cloud, Cpu, Sparkles } from 'lucide-react'
import { api } from '../api'
import { AlertBox, CodeBlock, useToast } from './ui'

interface Kind { id: string; title: string }
interface Result { text: string; model: string; provider: string; route?: string }

const EXAMPLES: Record<string, string> = {
  proxy: 'Squid sur le port 3128, accès limité à 192.168.1.0/24, journaux désactivés pour les requêtes locales',
  vpn: 'Client WireGuard : tunnel complet, DNS 1.1.1.1, keepalive 25 s, MTU 1380',
  code: 'Fonction qui vérifie qu’une adresse hôte:port WireGuard est valide',
}

// Génération par Ollama (modèle « code » du serveur actif, local ou en ligne). Le texte produit est à relire : rien n'est appliqué.
export default function GeneratorPanel() {
  const toast = useToast()
  const [kinds, setKinds] = useState<Kind[]>([])
  const [languages, setLanguages] = useState<string[]>([])
  const [kind, setKind] = useState('proxy')
  const [language, setLanguage] = useState('')
  const [description, setDescription] = useState('')
  const [busy, setBusy] = useState(false)
  const [result, setResult] = useState<Result | null>(null)

  useEffect(() => {
    api.get<{ items: Kind[]; languages: string[] }>('/api/assistant/generate/kinds')
      .then((d) => { setKinds(d.items); setLanguages(d.languages) }).catch(() => undefined)
  }, [])

  const generate = async () => {
    setBusy(true); setResult(null)
    try { setResult(await api.post<Result>('/api/assistant/generate', { kind, description, language: kind === 'code' ? language : '' })) }
    catch (e) { toast.push((e as Error).message, 'error') } finally { setBusy(false) }
  }

  return (
    <div className="card mt-3">
      <div className="card-header">
        <div><h2><Sparkles size={15} style={{ verticalAlign: '-2px' }} /> Générateur Ollama</h2>
          <div className="sub">Configuration de proxy, de VPN ou code, écrits par le modèle « code » du serveur actif</div></div>
      </div>
      <div className="card-pad stack" style={{ gap: 10 }}>
        <div className="row wrap" style={{ gap: 10, alignItems: 'flex-end' }}>
          <div className="field" style={{ minWidth: 200 }}><label>Type</label>
            <select className="select" value={kind} onChange={(e) => setKind(e.target.value)}>{kinds.map((k) => <option key={k.id} value={k.id}>{k.title}</option>)}</select></div>
          {kind === 'code' && (
            <div className="field" style={{ minWidth: 160 }}><label>Langage</label>
              <select className="select" value={language} onChange={(e) => setLanguage(e.target.value)}>
                <option value="">Au choix du modèle</option>{languages.map((l) => <option key={l} value={l}>{l}</option>)}</select></div>
          )}
          <button className="btn sm" onClick={() => setDescription(EXAMPLES[kind] ?? '')}>Exemple</button>
        </div>
        <textarea className="input" rows={3} value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Décrivez ce que vous voulez obtenir…" style={{ resize: 'vertical' }} />
        <div className="row" style={{ gap: 10 }}>
          <button className="btn primary" onClick={generate} disabled={busy || !description.trim()}>{busy ? 'Génération…' : 'Générer'}</button>
          {result && <span className="pill">{result.provider === 'cloud' ? <Cloud size={12} /> : <Cpu size={12} />} {result.model}{result.provider === 'cloud' ? ' · en ligne' : ' · local'}</span>}
        </div>
        {result && (
          <>
            <CodeBlock code={result.text} label="Résultat à relire avant tout usage" />
            {result.provider === 'cloud' && <AlertBox>Cette description a été traitée par un modèle en ligne (secrets reconnus masqués avant l’envoi).</AlertBox>}
          </>
        )}
      </div>
    </div>
  )
}
