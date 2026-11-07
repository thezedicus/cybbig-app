import { useState } from 'react'
import type { FormEvent } from 'react'
import { ExternalLink, Globe2, Loader2, Search, ShieldCheck } from 'lucide-react'
import { api } from '../api'
import { AlertBox, PageHeader, useToast } from '../components/ui'

type SearchResult = { title: string; url: string; snippet: string; source: string }
type SearchResponse = { query: string; provider: string; domains: string[]; items: SearchResult[]; total: number; cached: boolean; warnings: string[] }
const DOMAIN_PRESETS = [
  ['owasp.org', 'OWASP'], ['cisa.gov', 'CISA'], ['cert.ssi.gouv.fr', 'CERT-FR'],
  ['nist.gov', 'NIST'], ['github.com', 'GitHub'], ['reddit.com', 'Reddit'],
]

export default function WebSearch() {
  const [query, setQuery] = useState('')
  const [provider, setProvider] = useState<'auto' | 'duckduckgo' | 'brave'>('auto')
  const [selectedDomains, setSelectedDomains] = useState<string[]>([])
  const [customDomains, setCustomDomains] = useState('')
  const [data, setData] = useState<SearchResponse | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const toast = useToast()

  const search = async (event: FormEvent) => {
    event.preventDefault()
    if (query.trim().length < 2) return
    setBusy(true); setError('')
    try {
      const qs = new URLSearchParams({ q: query.trim(), lang: 'fr', provider })
      const domains = [...new Set([...selectedDomains, ...customDomains.split(/[\s,;]+/).map((value) => value.trim()).filter(Boolean)])].slice(0, 8)
      domains.forEach((domain) => qs.append('domains', domain))
      setData(await api.get<SearchResponse>(`/api/web/search?${qs}`))
    } catch (err) { setError((err as Error).message); setData(null) }
    finally { setBusy(false) }
  }

  const save = async (item: SearchResult) => {
    try {
      await api.post('/api/web/visit', { url: item.url, save: true, category: 'Recherche Web', tags: `web-search,${item.source.toLowerCase()}` })
      toast.push('Page ajoutée à la base de connaissances.', 'success')
    } catch (err) { toast.push((err as Error).message, 'error') }
  }

  return <>
    <PageHeader title="Recherche web" description="Cherchez des sources publiques, consultez les références et ajoutez les pages utiles à la base locale." />
    {error && <AlertBox kind="error">{error}</AlertBox>}
    <section className="card">
      <form className="card-pad" onSubmit={search}>
        <div className="row wrap" style={{ gap: 10 }}>
          <div className="searchbar" style={{ flex: 1, minWidth: 240 }}>
            <Search size={16} />
            <input className="input" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Ex. correctif CVE-2026-… pour PHP ou Python" aria-label="Requête de recherche web" />
          </div>
          <select className="select" aria-label="Moteur de recherche" value={provider} onChange={(e) => setProvider(e.target.value as typeof provider)} style={{ minWidth: 170 }}>
            <option value="auto">Moteurs disponibles</option><option value="duckduckgo">DuckDuckGo</option><option value="brave">Brave Search</option>
          </select>
          <button className="btn primary" type="submit" disabled={busy || query.trim().length < 2}>
            {busy ? <Loader2 size={14} className="spin" /> : <Search size={14} />}{busy ? 'Recherche…' : 'Rechercher'}
          </button>
        </div>
        <div className="field" style={{ marginTop: 14 }}>
          <label>Limiter aux sites sélectionnés <span className="tiny faint">(facultatif, 8 domaines max.)</span></label>
          <div className="row wrap" style={{ gap: 7, marginTop: 7 }}>
            {DOMAIN_PRESETS.map(([domain, label]) => <label key={domain} className="pill" style={{ cursor: 'pointer', gap: 5 }}>
              <input type="checkbox" checked={selectedDomains.includes(domain)} onChange={(event) => setSelectedDomains(event.target.checked ? [...selectedDomains, domain] : selectedDomains.filter((item) => item !== domain))} />{label}
            </label>)}
          </div>
          <input className="input" style={{ marginTop: 8 }} value={customDomains} onChange={(event) => setCustomDomains(event.target.value)} placeholder="Autres domaines, séparés par des virgules (ex. docs.python.org)" aria-label="Autres domaines à rechercher" />
        </div>
        <div className="row wrap tiny faint" style={{ marginTop: 10, gap: 12 }}>
          <span><Globe2 size={12} style={{ verticalAlign: 'middle' }} /> DuckDuckGo sans clé · Brave Search facultatif dans les paramètres</span>
          <span><ShieldCheck size={12} style={{ verticalAlign: 'middle' }} /> Les pages ne sont ouvertes que sur action ; les URL privées sont refusées</span>
        </div>
      </form>
    </section>
    {data && <>
      <div className="row between wrap" style={{ margin: '14px 2px' }}>
        <span className="small muted">{data.total} résultat(s) · {data.provider}{data.domains?.length ? ` · ${data.domains.join(', ')}` : ''}{data.cached ? ' · cache' : ''}</span>
        {data.warnings.length > 0 && <span className="tiny faint">Moteurs indisponibles : {data.warnings.join(', ')}</span>}
      </div>
      <div className="stack" style={{ gap: 10 }}>
        {data.items.map((item, i) => <article key={`${item.url}-${i}`} className="card card-pad">
          <div className="row between" style={{ gap: 10 }}>
            <div className="tiny faint">{i + 1}. {item.source} · {new URL(item.url).hostname}</div>
            <a className="btn ghost sm" href={item.url} target="_blank" rel="noreferrer"><ExternalLink size={12} /> Ouvrir</a>
          </div>
          <h3 style={{ margin: '8px 0 5px' }}><a href={item.url} target="_blank" rel="noreferrer">{item.title || item.url}</a></h3>
          <p className="small muted" style={{ margin: '0 0 10px', lineHeight: 1.6 }}>{item.snippet || 'Aucun extrait fourni par le moteur.'}</p>
          <div className="row between wrap" style={{ gap: 8 }}>
            <a className="tiny faint truncate" href={item.url} target="_blank" rel="noreferrer" style={{ maxWidth: '75%' }}>{item.url}</a>
            <button className="btn sm" onClick={() => save(item)}>Ajouter à la base</button>
          </div>
        </article>)}
      </div>
      {data.total === 0 && <div className="card card-pad muted">Aucun résultat. Reformulez la recherche ou vérifiez la connexion Internet.</div>}
    </>}
  </>
}
