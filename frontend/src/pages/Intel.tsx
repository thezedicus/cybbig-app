import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import {
  AlertTriangle, ExternalLink, Eye, Radar, RefreshCw, Search, ShieldAlert, Wifi, WifiOff,
} from 'lucide-react'
import { api, formatDate, relativeDate } from '../api'
import {
  AlertBox, Drawer, EmptyState, Loading, PageHeader, SeverityBadge, useToast,
} from '../components/ui'
import AiPanel from '../components/AiPanel'
import type { IntelItem, IntelStats } from '../types'

const SOURCE_LABEL: Record<string, string> = {
  cisa_kev: 'CISA KEV', nvd: 'NVD', cert_fr: 'CERT-FR', php_releases: 'PHP', osv: 'OSV',
}

export default function Intel() {
  const [stats, setStats] = useState<IntelStats | null>(null)
  const [items, setItems] = useState<IntelItem[] | null>(null)
  const [total, setTotal] = useState(0)
  const [error, setError] = useState('')
  const [syncing, setSyncing] = useState(false)
  const [archiveStatus, setArchiveStatus] = useState<Record<string, any> | null>(null)
  const [query, setQuery] = useState('')
  const [source, setSource] = useState('')
  const [severity, setSeverity] = useState('')
  const [exploited, setExploited] = useState(false)
  const [selected, setSelected] = useState<IntelItem | null>(null)
  const [params, setParams] = useSearchParams()
  const [sort, setSort] = useState('recent')
  const [watchlist, setWatchlist] = useState('')
  const [savedWatchlist, setSavedWatchlist] = useState('')
  const toast = useToast()

  const load = () => {
    api.get<IntelStats>('/api/intel/stats').then(setStats).catch((e) => setError((e as Error).message))
    const qs = new URLSearchParams({ limit: '200', sort })
    if (query) qs.set('q', query)
    if (source) qs.set('source', source)
    if (severity) qs.set('severity', severity)
    if (exploited) qs.set('exploited', 'true')
    api.get<{ items: IntelItem[]; total: number }>(`/api/intel/items?${qs}`)
      .then((d) => { setItems(d.items); setTotal(d.total) })
      .catch((e) => setError((e as Error).message))
  }

  useEffect(load, [source, severity, exploited, sort])

  const loadArchiveStatus = () => api.get<Record<string, any>>('/api/intel/archive/status').then(setArchiveStatus).catch(() => undefined)
  useEffect(() => { loadArchiveStatus() }, [])
  useEffect(() => {
    if (!archiveStatus?.running) return undefined
    const timer = window.setInterval(() => {
      api.get<Record<string, any>>('/api/intel/archive/status').then((next) => {
        setArchiveStatus(next)
        if (!next.running) load()
      }).catch(() => undefined)
    }, 3000)
    return () => window.clearInterval(timer)
  }, [archiveStatus?.running])

  useEffect(() => {
    // Lien depuis une alerte de veille : /intel?q=CVE-…
    const q = params.get('q')
    if (q) { setQuery(q); setParams({}, { replace: true }) }
    api.get<{ values: Record<string, string> }>('/api/settings')
      .then((d) => { setWatchlist(d.values.intel_watchlist ?? ''); setSavedWatchlist(d.values.intel_watchlist ?? '') })
      .catch(() => undefined)
  }, [])

  useEffect(() => { if (query && items === null) load() }, [query])

  const saveWatchlist = async () => {
    try {
      await api.put('/api/settings', { values: { intel_watchlist: watchlist } })
      setSavedWatchlist(watchlist)
      toast.push('Liste de surveillance enregistrée : les prochaines synchronisations créeront des alertes ciblées.', 'success')
    } catch (err) { toast.push((err as Error).message, 'error') }
  }

  const search = (event: React.FormEvent) => { event.preventDefault(); load() }

  const sync = async () => {
    setSyncing(true)
    try {
      const result = await api.post<{ results: Array<{ source: string; status: string; new?: number; error?: string }> }>('/api/intel/sync', { sources: [] })
      const ok = result.results.filter((r) => r.status === 'ok').length
      const failed = result.results.filter((r) => r.status === 'error')
      if (ok) toast.push(`Veille synchronisée : ${ok} source(s).`, 'success')
      if (failed.length) toast.push(`Échec : ${failed.map((f) => SOURCE_LABEL[f.source] || f.source).join(', ')}.`, 'error')
      load()
    } catch (err) {
      toast.push((err as Error).message, 'error')
    } finally {
      setSyncing(false)
    }
  }

  const importArchive = async () => {
    try {
      const result = await api.post<Record<string, any>>('/api/intel/archive/start', {})
      setArchiveStatus(result)
      toast.push('Import de l’historique NVD lancé. Les données sont conservées et indexées localement.', 'success')
    } catch (err) { toast.push((err as Error).message, 'error') }
  }

  const archiveLabel = archiveStatus?.running
    ? `${archiveStatus.phase === 'download' ? 'Téléchargement' : 'Indexation'} ${archiveStatus.current_year ?? ''} · ${archiveStatus.feeds_ready ?? 0}/${archiveStatus.years_total ?? 25}`
    : archiveStatus?.phase === 'complete'
      ? `Terminé · ${archiveStatus.nvd_total?.toLocaleString('fr-FR') ?? '—'} CVE indexées`
      : archiveStatus?.phase === 'error'
        ? `Interrompu : ${archiveStatus.error}`
        : 'Non importé sur ce poste'

  return (
    <>
      <PageHeader
        title="Threat Intelligence"
        description="Veille CISA KEV, historique NVD, CERT-FR et PHP. Les avis sont conservés localement avec leur provenance."
        actions={<div className="row wrap" style={{ gap: 8 }}><button className="btn" onClick={importArchive} disabled={Boolean(archiveStatus?.running)}><ShieldAlert size={14} /> {archiveStatus?.running ? 'Import en cours…' : 'Importer l’historique NVD'}</button><button className="btn primary" onClick={sync} disabled={syncing}><RefreshCw size={14} className={syncing ? 'spin' : ''} /> {syncing ? 'Synchronisation…' : 'Synchroniser'}</button></div>}
      />

      {error && <AlertBox kind="error">{error}</AlertBox>}

      <div className="card card-pad mb-2 row between wrap" style={{ gap: 12 }}>
        <div><b className="small">Historique CVE NVD 2.0</b><div className="tiny faint">Flux annuels officiels vérifiés par SHA-256, conservés et indexés pour la veille et l’assistant IA.</div></div>
        <span className={`tag ${archiveStatus?.phase === 'error' ? 'critical' : ''}`}>{archiveLabel}</span>
      </div>

      <div className="mb-2">
        <AiPanel task="intel_digest" params={{ days: 7 }} cacheKey="intel:digest" title="Digest de veille (IA)" label="Résumer les menaces de la semaine" />
      </div>

      <div className="card card-pad mb-2 row wrap" style={{ gap: 10, alignItems: 'center' }}>
        <Eye size={15} color="var(--accent)" />
        <b className="small">Technologies surveillées</b>
        <input className="input" style={{ flex: 1, minWidth: 260 }} value={watchlist} onChange={(e) => setWatchlist(e.target.value)} placeholder="php, wordpress, stripe, nginx, laravel…" />
        <button className="btn sm" onClick={saveWatchlist} disabled={watchlist === savedWatchlist}>Enregistrer</button>
        <span className="tiny faint" style={{ flexBasis: '100%' }}>Chaque nouvelle fiche qui cite l’une de ces technologies déclenche une alerte. L’IA s’en sert aussi pour prioriser le digest.</span>
      </div>

      <div className="grid cols-4 mb-2">
        <div className="card stat-card"><div className="stat-label"><Radar size={13} /> Fiches</div><div className="stat-value">{stats?.total ?? '—'}</div><div className="stat-foot">{stats?.last_fetch ? `maj ${relativeDate(stats.last_fetch)}` : 'jamais synchronisé'}</div></div>
        <div className="card stat-card"><div className="stat-label"><ShieldAlert size={13} /> Exploitées</div><div className="stat-value" style={{ color: 'var(--critical)' }}>{stats?.exploited ?? '—'}</div><div className="stat-foot">connues dans la nature (KEV)</div></div>
        <div className="card stat-card"><div className="stat-label"><Wifi size={13} /> Sources actives</div><div className="stat-value">{stats?.sources.filter((s) => s.status === 'ok').length ?? 0}<span style={{ fontSize: 13, color: 'var(--faint)' }}>/{stats?.sources.length ?? 0}</span></div><div className="stat-foot">dernier cycle de collecte</div></div>
        <div className="card stat-card"><div className="stat-label"><AlertTriangle size={13} /> Critiques</div><div className="stat-value" style={{ color: 'var(--high)' }}>{stats?.by_severity.find((s) => s.severity === 'critical')?.count ?? 0}</div><div className="stat-foot">sévérité normalisée</div></div>
      </div>

      <div className="grid cols-5 mb-2">
        {(stats?.sources ?? []).map((s) => (
          <div key={s.name} className="card card-pad" style={{ padding: '12px 14px' }}>
            <div className="row between">
              <b className="small">{s.label.split('—')[0].trim()}</b>
              {s.status === 'ok' ? <Wifi size={13} color="var(--green)" /> : s.status === 'error' ? <WifiOff size={13} color="var(--critical)" /> : <WifiOff size={13} color="var(--faint)" />}
            </div>
            <div className="tiny faint mt-1">{s.items_count} fiche(s) · {s.last_sync_at ? relativeDate(s.last_sync_at) : 'jamais'}</div>
            {s.error && <div className="tiny" style={{ color: 'var(--critical)' }} title={s.error}>Erreur de collecte</div>}
          </div>
        ))}
      </div>

      <div className="card">
        <div className="card-header" style={{ flexWrap: 'wrap', gap: 10 }}>
          <form className="searchbar" style={{ flex: 1, minWidth: 220 }} onSubmit={search}>
            <Search size={15} />
            <input className="input" placeholder="CVE, produit, mot-clé…" value={query} onChange={(e) => setQuery(e.target.value)} />
          </form>
          <div className="filters">
            <select className="select" value={source} onChange={(e) => setSource(e.target.value)}>
              <option value="">Toutes sources</option>
              {Object.entries(SOURCE_LABEL).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
            </select>
            <select className="select" value={severity} onChange={(e) => setSeverity(e.target.value)}>
              <option value="">Toutes gravités</option>
              <option value="critical">Critique</option><option value="high">Élevé</option>
              <option value="medium">Moyen</option><option value="low">Faible</option>
            </select>
            <select className="select" value={sort} onChange={(e) => setSort(e.target.value)} title="Tri">
              <option value="recent">Exploitées puis récentes</option>
              <option value="epss">Probabilité d’exploitation (EPSS)</option>
              <option value="cvss">Score CVSS</option>
            </select>
            <label className="pill" style={{ cursor: 'pointer', gap: 6 }}>
              <input type="checkbox" checked={exploited} onChange={(e) => setExploited(e.target.checked)} style={{ accentColor: 'var(--accent-strong)' }} />
              Exploitées
            </label>
            <button className="btn sm" type="submit" onClick={search}>Rechercher</button>
          </div>
        </div>

        {!items ? <Loading /> : items.length === 0 ? (
          <EmptyState
            icon={<Radar size={30} />}
            title="Aucune fiche pour le moment"
            description="Lancez une synchronisation pour collecter CISA KEV, CERT-FR, PHP et NVD. Une connexion Internet est nécessaire ; les résultats restent locaux."
            action={<button className="btn primary sm" onClick={sync} disabled={syncing}><RefreshCw size={14} /> Synchroniser maintenant</button>}
          />
        ) : (
          <>
            <div className="table-wrap">
              <table className="data">
                <thead><tr><th>Gravité</th><th>Fiche</th><th>Source</th><th>CVE</th><th title="Probabilité d’exploitation sous 30 jours (FIRST EPSS)">EPSS</th><th>Exploitée</th><th>Publiée</th></tr></thead>
                <tbody>
                  {items.map((item) => (
                    <tr key={item.id} className="clickable" onClick={() => setSelected(item)}>
                      <td><SeverityBadge severity={item.severity as never} /></td>
                      <td style={{ maxWidth: 480 }}><div className="cell-title clamp-2">{item.title}</div><div className="cell-sub clamp-2">{item.product || item.summary}</div></td>
                      <td><span className="tag">{SOURCE_LABEL[item.source] || item.source}</span></td>
                      <td className="cell-mono">{item.cve || '—'}</td>
                      <td className="mono small" style={{ color: (item.epss ?? 0) >= 0.1 ? 'var(--critical)' : (item.epss ?? 0) >= 0.01 ? 'var(--high)' : 'var(--faint)' }}>{item.epss ? `${(item.epss * 100).toFixed(item.epss >= 0.1 ? 0 : 1)} %` : '—'}</td>
                      <td>{item.exploited ? <span className="badge critical">KEV</span> : <span className="faint small">—</span>}</td>
                      <td className="tiny faint">{formatDate(item.published_at, false)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="row between" style={{ padding: '12px 16px', borderTop: '1px solid var(--line-soft)' }}>
              <span className="tiny faint">{total} fiche(s) correspondante(s)</span>
              <span className="tiny faint">EPSS : probabilité d’exploitation dans les 30 jours (FIRST.org)</span>
            </div>
          </>
        )}
      </div>

      <Drawer open={Boolean(selected)} onClose={() => setSelected(null)} title={selected?.title ?? ''} subtitle={selected ? `${SOURCE_LABEL[selected.source] || selected.source} · ${formatDate(selected.published_at)}` : undefined}>
        {selected && (
          <>
            <div className="detail-meta">
              <SeverityBadge severity={selected.severity} />
              {selected.cve && <span className="tag">{selected.cve}</span>}
              {selected.cvss != null && <span className="pill">CVSS {selected.cvss}</span>}
              {selected.exploited ? <span className="badge critical">Exploitée</span> : null}
            </div>
            <div className="detail-section"><h3>Résumé</h3><p>{selected.summary || 'Aucun résumé.'}</p></div>
            {selected.product && <div className="detail-section"><h3>Produit</h3><p>{selected.product}</p></div>}
            {selected.tags?.length > 0 && <div className="detail-section"><h3>Tags</h3><div className="row wrap">{selected.tags.map((t) => <span className="tag" key={t}>{t}</span>)}</div></div>}
            <div className="kv-list">
              <div className="kv-item"><span>Identifiant source</span><b className="mono">{selected.external_id}</b></div>
              <div className="kv-item"><span>Publiée</span><b>{formatDate(selected.published_at)}</b></div>
              <div className="kv-item"><span>Récupérée</span><b>{formatDate(selected.fetched_at)}</b></div>
            </div>
            <div className="row">
              {selected.url && <a className="btn sm" href={selected.url} target="_blank" rel="noreferrer">Source d’origine <ExternalLink size={12} /></a>}
              {selected.cve && <a className="btn sm" href={`https://nvd.nist.gov/vuln/detail/${selected.cve}`} target="_blank" rel="noreferrer">NVD <ExternalLink size={12} /></a>}
            </div>
            <div className="alert-banner info"><AlertTriangle size={15} /><div className="small">Une fiche de veille n’est pas une preuve d’exposition. Corrélez le produit, la version, l’exposition réseau et l’exploitation connue avant de prioriser.</div></div>
          </>
        )}
      </Drawer>
    </>
  )
}
