import { useEffect, useRef, useState } from 'react'
import { FileUp, Globe, Table2, Type } from 'lucide-react'
import { api } from '../api'
import { AlertBox, Modal, Progress, useToast } from './ui'

type Tab = 'text' | 'files' | 'web' | 'bulk'

interface Preview { url: string; title: string; description: string; text: string; chars: number; links: string[]; saved?: { id: string; status: string } }
interface WebJob {
  id: string; status: string; url: string
  progress: { pages?: number; max_pages?: number; current?: string }
  result: { created?: number; updated?: number; unchanged?: number; failed?: number; errors?: string[] }
}

const STATUS_TEXT: Record<string, string> = { created: 'ajoutée', updated: 'mise à jour', unchanged: 'déjà à jour' }
const STRUCTURED = /\.(json|jsonl|ndjson|csv)$/i

// Fenêtre « Ajouter des données » de la base de connaissances : texte, fichiers, site web (une page ou exploration) et import en lot.
export default function AddDataModal({ open, onClose, onDone, category }: { open: boolean; onClose: () => void; onDone: () => void; category: string }) {
  const [tab, setTab] = useState<Tab>('files')
  const [cat, setCat] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [text, setText] = useState({ title: '', content: '', source: '', tags: '' })
  const [structured, setStructured] = useState(true)
  const [bulk, setBulk] = useState('')
  const [web, setWeb] = useState({ url: '', selector: '', tags: '', crawl: false, maxPages: 10, depth: 1 })
  const [preview, setPreview] = useState<Preview | null>(null)
  const [job, setJob] = useState<WebJob | null>(null)
  const fileRef = useRef<HTMLInputElement>(null)
  const toast = useToast()

  useEffect(() => { if (open) { setCat(category && !category.endsWith('*') ? category : ''); setError(''); setPreview(null) } }, [open, category])

  // Suivi de l'exploration en cours.
  useEffect(() => {
    if (!job || !['queued', 'running'].includes(job.status)) return
    const timer = window.setInterval(() => {
      api.get<WebJob>(`/api/web/jobs/${job.id}`).then((fresh) => {
        setJob(fresh)
        if (!['queued', 'running'].includes(fresh.status)) { onDone(); setBusy(false) }
      }).catch(() => undefined)
    }, 1000)
    return () => window.clearInterval(timer)
  }, [job, onDone])

  const fail = (err: unknown) => { setError((err as Error).message); setBusy(false) }

  const saveText = async (event: React.FormEvent) => {
    event.preventDefault()
    setBusy(true); setError('')
    try {
      await api.post('/api/knowledge', { title: text.title, content: text.content, category: cat || 'Général', source: text.source, tags: text.tags })
      toast.push('Fiche ajoutée.', 'success')
      setText({ title: '', content: '', source: '', tags: '' }); onDone()
    } catch (err) { setError((err as Error).message) } finally { setBusy(false) }
  }

  const importFiles = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files ?? [])
    if (!files.length) return
    setBusy(true); setError('')
    let docs = 0; const problems: string[] = []
    for (const file of files) {
      try {
        if (structured && STRUCTURED.test(file.name)) {
          try {
            const result = await api.post<{ added: number; skipped: number }>('/api/knowledge/bulk', { text: await file.text(), category: cat || 'Import' })
            docs += result.added
            continue
          } catch { /* pas un lot de fiches : le fichier est importé comme un seul document ci-dessous */ }
        }
        await api.upload('/api/knowledge/import', file, { category: cat || 'Import' })
        docs += 1
      } catch (err) { problems.push(`${file.name} : ${(err as Error).message}`) }
    }
    setBusy(false)
    if (fileRef.current) fileRef.current.value = ''
    if (docs) { toast.push(`${docs} fiche(s) ajoutée(s).`, 'success'); onDone() }
    if (problems.length) setError(problems.join('\n'))
  }

  const sendBulk = async () => {
    setBusy(true); setError('')
    try {
      const result = await api.post<{ added: number; skipped: number }>('/api/knowledge/bulk', { text: bulk, category: cat || 'Import' })
      toast.push(`${result.added} fiche(s) ajoutée(s)${result.skipped ? `, ${result.skipped} déjà présente(s)` : ''}.`, 'success')
      setBulk(''); onDone()
    } catch (err) { setError((err as Error).message) } finally { setBusy(false) }
  }

  const body = (save: boolean) => ({ url: web.url, selector: web.selector, tags: web.tags, category: cat || 'Web', save })

  const readPage = async () => {
    setBusy(true); setError(''); setPreview(null)
    try { setPreview(await api.post<Preview>('/api/web/visit', body(false))) } catch (err) { setError((err as Error).message) } finally { setBusy(false) }
  }

  const addWeb = async () => {
    setBusy(true); setError('')
    try {
      if (web.crawl) {
        setJob(await api.post<WebJob>('/api/web/crawl', { ...body(true), max_pages: web.maxPages, depth: web.depth }))
        return // le suivi remet busy à false à la fin
      }
      const page = await api.post<Preview>('/api/web/visit', body(true))
      setPreview(page)
      toast.push(`Page ${STATUS_TEXT[page.saved?.status ?? 'created']}.`, 'success'); onDone()
    } catch (err) { fail(err); return }
    setBusy(false)
  }

  const running = Boolean(job && ['queued', 'running'].includes(job.status))
  return (
    <Modal open={open} onClose={onClose} title="Ajouter des données" subtitle="Alimente la base de connaissances de l’assistant" size="wide">
      <div className="tabs">
        <button className={`tab${tab === 'files' ? ' active' : ''}`} onClick={() => setTab('files')}><FileUp size={13} /> Fichiers</button>
        <button className={`tab${tab === 'web' ? ' active' : ''}`} onClick={() => setTab('web')}><Globe size={13} /> Site web</button>
        <button className={`tab${tab === 'bulk' ? ' active' : ''}`} onClick={() => setTab('bulk')}><Table2 size={13} /> Données structurées</button>
        <button className={`tab${tab === 'text' ? ' active' : ''}`} onClick={() => setTab('text')}><Type size={13} /> Texte</button>
      </div>

      <div className="field" style={{ marginBottom: 12 }}>
        <label htmlFor="add-category">Catégorie des fiches ajoutées</label>
        <input id="add-category" className="input" value={cat} onChange={(e) => setCat(e.target.value)} placeholder={tab === 'web' ? 'Web' : tab === 'text' ? 'Général' : 'Import'} />
      </div>

      {error && <AlertBox kind="error"><span style={{ whiteSpace: 'pre-wrap' }}>{error}</span></AlertBox>}

      {tab === 'files' && (
        <div className="stack" style={{ gap: 10 }}>
          <input ref={fileRef} type="file" multiple hidden onChange={importFiles} accept=".md,.txt,.json,.jsonl,.ndjson,.csv,.log,.html,.htm" />
          <button className="btn primary" onClick={() => fileRef.current?.click()} disabled={busy}><FileUp size={14} /> {busy ? 'Import…' : 'Choisir des fichiers'}</button>
          <label className="checkbox">
            <input type="checkbox" checked={structured} onChange={(e) => setStructured(e.target.checked)} />
            <span>Les fichiers JSON, JSONL et CSV contiennent plusieurs fiches (champs <span className="mono">title</span> et <span className="mono">content</span>) ; sinon chaque fichier devient une seule fiche</span>
          </label>
          <span className="tiny faint">Formats : Markdown, texte, JSON, JSONL, CSV, HTML (le texte principal est extrait), journaux. 2 Mo maximum par fichier.</span>
        </div>
      )}

      {tab === 'web' && (
        <div className="stack" style={{ gap: 10 }}>
          <div className="form-grid">
            <div className="field full"><label htmlFor="web-url">Adresse de la page ou du site</label>
              <input id="web-url" className="input" value={web.url} onChange={(e) => setWeb({ ...web, url: e.target.value })} placeholder="https://owasp.org/www-project-top-ten/" /></div>
            <div className="field"><label htmlFor="web-sel">Sélecteur CSS (facultatif)</label>
              <input id="web-sel" className="input mono" value={web.selector} onChange={(e) => setWeb({ ...web, selector: e.target.value })} placeholder="article, main, #contenu" />
              <span className="hint">Ne garde que cette zone de la page (analyse Scrapling).</span></div>
            <div className="field"><label htmlFor="web-tags">Tags</label>
              <input id="web-tags" className="input" value={web.tags} onChange={(e) => setWeb({ ...web, tags: e.target.value })} placeholder="owasp, référence" /></div>
          </div>
          <label className="checkbox">
            <input type="checkbox" checked={web.crawl} onChange={(e) => setWeb({ ...web, crawl: e.target.checked })} />
            <span>Explorer aussi les pages liées <b>du même site</b></span>
          </label>
          {web.crawl && (
            <div className="form-grid">
              <div className="field"><label htmlFor="web-pages">Pages maximum</label>
                <input id="web-pages" className="input" type="number" min={1} max={25} value={web.maxPages} onChange={(e) => setWeb({ ...web, maxPages: Number(e.target.value) })} /></div>
              <div className="field"><label htmlFor="web-depth">Profondeur (0 à 2)</label>
                <input id="web-depth" className="input" type="number" min={0} max={2} value={web.depth} onChange={(e) => setWeb({ ...web, depth: Number(e.target.value) })} /></div>
            </div>
          )}
          <div className="row wrap" style={{ gap: 8 }}>
            {!web.crawl && <button className="btn" onClick={readPage} disabled={busy || !web.url.trim()}>Lire (aperçu)</button>}
            <button className="btn primary" onClick={addWeb} disabled={busy || !web.url.trim()}>{running ? 'Exploration…' : 'Ajouter à la base'}</button>
            {running && job && <button className="btn sm" onClick={() => api.post(`/api/web/jobs/${job.id}/cancel`)}>Annuler</button>}
          </div>
          <span className="tiny faint">Sites publics uniquement (réseau local et adresses internes refusés), robots.txt respecté, contenu importé étiqueté « web-import » et non vérifié.</span>

          {job && (
            <div className="stack" style={{ gap: 6 }}>
              <Progress value={job.progress.max_pages ? 100 * (job.progress.pages ?? 0) / job.progress.max_pages : 0} />
              <span className="small">
                {running ? `Page ${job.progress.pages ?? 0}/${job.progress.max_pages ?? '?'} · ${job.progress.current ?? ''}`
                  : `${job.status === 'completed' ? 'Terminé' : job.status === 'cancelled' ? 'Annulé' : 'Échec'} : ${job.result.created ?? 0} ajoutée(s), ${job.result.updated ?? 0} mise(s) à jour, ${job.result.unchanged ?? 0} inchangée(s), ${job.result.failed ?? 0} en échec`}
              </span>
              {job.result.errors?.map((e) => <span key={e} className="tiny" style={{ color: 'var(--high)' }}>{e}</span>)}
            </div>
          )}
          {preview && (
            <div className="card" style={{ padding: 12 }}>
              <b className="small">{preview.title}</b>
              <div className="tiny faint">{preview.url} · {preview.chars.toLocaleString('fr-FR')} caractères · {preview.links.length}+ liens{preview.saved ? ` · fiche ${STATUS_TEXT[preview.saved.status] ?? preview.saved.status}` : ''}</div>
              <div className="small mt-1" style={{ whiteSpace: 'pre-wrap', maxHeight: 180, overflow: 'auto', color: 'var(--text-soft)' }}>{preview.text.slice(0, 1500)}{preview.text.length > 1500 ? '…' : ''}</div>
            </div>
          )}
        </div>
      )}

      {tab === 'bulk' && (
        <div className="stack" style={{ gap: 10 }}>
          <textarea className="textarea mono" style={{ minHeight: 220 }} value={bulk} onChange={(e) => setBulk(e.target.value)}
            placeholder={'[{"title": "Titre", "content": "Texte de la fiche", "category": "PHP", "tags": ["sessions", "cookies"]}]'} />
          <span className="tiny faint">Tableau JSON, JSONL (une fiche par ligne) ou CSV (colonnes title, content, category, source, tags). Les champs summary, category_slug et technologies sont reconnus.
            Une fiche de même titre et même catégorie n’est pas dupliquée. 500 fiches maximum.</span>
          <div><button className="btn primary" onClick={sendBulk} disabled={busy || bulk.trim().length < 2}>{busy ? 'Import…' : 'Importer les fiches'}</button></div>
        </div>
      )}

      {tab === 'text' && (
        <form onSubmit={saveText} className="stack" style={{ gap: 10 }}>
          <div className="form-grid">
            <div className="field full"><label htmlFor="txt-title">Titre *</label><input id="txt-title" className="input" required value={text.title} onChange={(e) => setText({ ...text, title: e.target.value })} /></div>
            <div className="field"><label htmlFor="txt-source">Source</label><input id="txt-source" className="input" value={text.source} onChange={(e) => setText({ ...text, source: e.target.value })} placeholder="OWASP, note interne…" /></div>
            <div className="field"><label htmlFor="txt-tags">Tags</label><input id="txt-tags" className="input" value={text.tags} onChange={(e) => setText({ ...text, tags: e.target.value })} placeholder="php, sessions" /></div>
            <div className="field full"><label htmlFor="txt-content">Contenu *</label><textarea id="txt-content" className="textarea" required style={{ minHeight: 200 }} value={text.content} onChange={(e) => setText({ ...text, content: e.target.value })} /></div>
          </div>
          <div><button className="btn primary" disabled={busy}>{busy ? 'Enregistrement…' : 'Ajouter la fiche'}</button></div>
        </form>
      )}
    </Modal>
  )
}
