import { useState } from 'react'
import { CheckCircle2, Cloud, RefreshCw, ShieldAlert, XCircle } from 'lucide-react'
import { api } from '../api'
import { useToast } from './ui'
import CodeModelsPanel from './CodeModelsPanel'
import type { OllamaStatus } from '../types'

// Section « IA en ligne » des Paramètres : les valeurs passent par le formulaire commun (values/setValue).
export default function CloudSettings({ values, setValue }: { values: Record<string, string>; setValue: (key: string, value: string) => void }) {
  const [status, setStatus] = useState<OllamaStatus | null>(null)
  const [testing, setTesting] = useState(false)
  const toast = useToast()
  const flag = (key: string, fallback = true) => (values[key] === undefined ? fallback : values[key] !== 'false')
  const provider = values.ai_provider || 'auto'
  const cloud = status?.cloud

  // Enregistre tout de suite les réglages en ligne (sans attendre le bouton Enregistrer de la page), puis teste.
  const saveAndTest = async () => {
    setTesting(true)
    try {
      const payload: Record<string, string> = {}
      for (const key of ['ai_provider', 'ai_allow_cloud', 'ollama_cloud_url', 'ollama_cloud_key', 'ollama_cloud_model', 'brave_search_key', 'ai_model_code', 'ai_model_code_local', 'ai_browse', 'ai_search', 'web_respect_robots', 'ai_warmup']) {
        if (values[key] !== undefined) payload[key] = values[key]
      }
      await api.put('/api/settings', { values: payload })
      if (values.ollama_cloud_key && values.ollama_cloud_key !== '********') setValue('ollama_cloud_key', '********')
      if (values.brave_search_key && values.brave_search_key !== '********') setValue('brave_search_key', '********')
      const result = await api.get<OllamaStatus>('/api/assistant/status?refresh=true&retry_cloud=true')
      setStatus(result)
      if (result.cloud?.available) toast.push(`Enregistré. IA en ligne joignable : ${result.cloud.selected_model}`, 'success')
      else toast.push(`Enregistré, mais : ${result.cloud?.error || 'IA en ligne indisponible.'}`, 'info')
    } catch (err) {
      toast.push((err as Error).message, 'error')
    } finally {
      setTesting(false)
    }
  }

  return (
    <section className="card">
      <div className="card-header">
        <div><h2>IA en ligne (Ollama Cloud)</h2><div className="sub">Modèle hébergé : réponses bien plus rapides qu’un modèle local sur processeur</div></div>
        <Cloud size={16} style={{ marginLeft: 'auto', color: 'var(--accent)' }} />
      </div>
      <div className="card-pad stack" style={{ gap: 12 }}>
        <div className="field">
          <label htmlFor="ai-provider">Quel modèle utiliser ?</label>
          <select id="ai-provider" className="select" value={provider} onChange={(e) => setValue('ai_provider', e.target.value)}>
            <option value="auto">Automatique : modèle en ligne s’il répond, sinon modèle local</option>
            <option value="local">Coupé (local uniquement) : aucune donnée ne quitte ce poste</option>
            <option value="training">Entraînement seulement : le chat reste local, la bibliothèque part chez le professeur en ligne</option>
            <option value="cloud">En ligne uniquement : jamais de repli sur le modèle local</option>
          </select>
        </div>

        <label className="checkbox">
          <input type="checkbox" checked={flag('ai_allow_cloud')} onChange={(e) => setValue('ai_allow_cloud', e.target.checked ? 'true' : 'false')} />
          <span><b>Autoriser l’IA en ligne</b> (sans clé API ci-dessous, rien n’est envoyé)</span>
        </label>

        <div className="form-grid">
          <div className="field">
            <label htmlFor="cloud-url">Adresse du service (HTTPS)</label>
            <input id="cloud-url" className="input" value={values.ollama_cloud_url ?? 'https://ollama.com'} onChange={(e) => setValue('ollama_cloud_url', e.target.value)} />
          </div>
          <div className="field">
            <label htmlFor="cloud-model">Modèle en ligne</label>
            <input id="cloud-model" className="input" list="cloud-models" value={values.ollama_cloud_model ?? ''} onChange={(e) => setValue('ollama_cloud_model', e.target.value)} placeholder="Automatique (gpt-oss:120b…)" />
            <datalist id="cloud-models">{(cloud?.models ?? []).map((m) => <option key={m} value={m} />)}</datalist>
          </div>
          <div className="field full">
            <label htmlFor="cloud-key">Clé API Ollama (facultative)</label>
            <input id="cloud-key" className="input" type="password" autoComplete="off" placeholder="Créez une clé sur ollama.com, collez-la ici (******** = clé conservée)"
              value={values.ollama_cloud_key ?? ''} onChange={(e) => setValue('ollama_cloud_key', e.target.value)} />
            <span className="hint">Sans clé, Cybbig utilise les modèles « -cloud » de votre Ollama local s’il est connecté à ollama.com (<code>ollama signin</code>). Distincte de la clé d’un serveur local protégé ; jamais affichée en clair. <a href="https://ollama.com/settings/keys" target="_blank" rel="noreferrer">Gérer les clés Ollama</a>.</span>
          </div>
        </div>

        <CodeModelsPanel values={values} setValue={setValue} />

        <div className="row wrap" style={{ gap: 8 }}>
          <button type="button" className="btn primary sm" onClick={saveAndTest} disabled={testing}>
            <RefreshCw size={13} className={testing ? 'spin' : ''} /> {testing ? 'Enregistrement…' : 'Enregistrer et tester'}
          </button>
          {cloud && (cloud.available
            ? <span className="pill completed"><CheckCircle2 size={12} /> En ligne · {cloud.selected_model}{cloud.route === 'daemon' ? ' (via Ollama local)' : ''}</span>
            : <span className="pill"><XCircle size={12} /> {cloud.error || 'Indisponible'}</span>)}
          {status && <span className="tiny faint">Serveur actif : {status.provider === 'cloud' ? 'en ligne' : status.provider === 'local' ? 'local' : 'aucun (mode déterministe)'}</span>}
        </div>
        <span className="tiny faint">« Enregistrer et tester » conserve immédiatement ces réglages en ligne (le reste de la page demande « Enregistrer »). Mode rapide : bouton nuage de la barre du haut.</span>

        <div className="alert" style={{ display: 'flex', gap: 10, alignItems: 'flex-start' }}>
          <ShieldAlert size={16} style={{ flex: '0 0 auto', marginTop: 2, color: 'var(--high)' }} />
          <span className="small">
            <b>Confidentialité.</b> Avec l’IA en ligne, vos questions, l’historique récent, les extraits de la base de connaissances et le contexte de vos projets
            (titres et descriptions de résultats d’analyse) sont envoyés au service pour produire la réponse. Les clés, jetons, mots de passe et clés privées reconnus sont masqués avant l’envoi.
            Pour des projets confidentiels, choisissez « Local uniquement ».
          </span>
        </div>

        <div className="stack" style={{ gap: 6 }}>
          <label className="checkbox">
            <input type="checkbox" checked={flag('ai_search', false)} onChange={(e) => setValue('ai_search', e.target.checked ? 'true' : 'false')} />
            <span><b>Recherche web automatique de l’assistant</b> : cherche des références sans lien fourni, puis lit jusqu’à deux pages publiques. Le sujet de la question est transmis au moteur de recherche.</span>
          </label>
          <label className="checkbox">
            <input type="checkbox" checked={flag('ai_browse')} onChange={(e) => setValue('ai_browse', e.target.checked ? 'true' : 'false')} />
            <span><b>Lire les liens collés dans l’assistant</b> : visite les URL publiques que vous incluez dans une question.</span>
          </label>
          <label className="checkbox">
            <input type="checkbox" checked={flag('web_respect_robots')} onChange={(e) => setValue('web_respect_robots', e.target.checked ? 'true' : 'false')} />
            <span><b>Respecter robots.txt</b> lors des visites de sites</span>
          </label>
          <label className="checkbox">
            <input type="checkbox" checked={flag('ai_warmup')} onChange={(e) => setValue('ai_warmup', e.target.checked ? 'true' : 'false')} />
            <span><b>Précharger le modèle local</b> au démarrage (supprime 10 à 40 s d’attente à la première question, occupe la mémoire)</span>
          </label>
        </div>
        <div className="field">
          <label htmlFor="brave-search-key">Clé Brave Search (facultative)</label>
          <input id="brave-search-key" className="input" type="password" autoComplete="off" value={values.brave_search_key === '********' ? '' : (values.brave_search_key ?? '')}
            onChange={(e) => setValue('brave_search_key', e.target.value)} placeholder="Clé API Brave · ******** = clé conservée" />
          <span className="hint">Avec une clé configurée, Brave fournit les résultats prioritaires ; Bing et DuckDuckGo servent de moteurs de repli. La recherche complète utilise plusieurs index publics, avec les limites et quotas de chaque service. <a href="https://api-dashboard.search.brave.com/" target="_blank" rel="noreferrer">Créer ou gérer une clé Brave</a>.</span>
        </div>
      </div>
    </section>
  )
}
