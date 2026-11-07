import { useEffect, useMemo, useRef, useState } from 'react'
import { ChevronDown, ChevronRight, FilePlus, FileText, Folder, History, Power, RefreshCw, RotateCcw, Save, Trash2, Wrench } from 'lucide-react'
import { api, adminApi } from '../api'
import { AlertBox, Loading, Modal, useToast } from './ui'

type Client = ReturnType<typeof adminApi>
type Guard = <T>(promise: Promise<T>) => Promise<T>
interface Entry { name: string; path: string; dir: boolean; size: number | null }
interface FileData { path: string; size: number; binary: boolean; content: string; reason?: string }
interface Backup { backup: string; path: string; size: number }

const NEEDS: Record<string, string> = {
  restart: 'Modification du backend : redémarrez le service pour l’appliquer.',
  rebuild: 'Modification de l’interface : recompilez l’interface pour l’appliquer.',
  reload: 'Fichier compilé de l’interface : rechargez la fenêtre.',
  relaunch: 'Moteur de bureau : fermez et relancez Cybbig.',
}

// Éditeur du code complet du logiciel (onglet Administration → Code).
export default function CodeEditorTab({ client, guard }: { client: Client; guard: Guard }) {
  const [root, setRoot] = useState('')
  const [children, setChildren] = useState<Record<string, Entry[]>>({})
  const [open, setOpen] = useState<Set<string>>(new Set(['']))
  const [file, setFile] = useState<FileData | null>(null)
  const [content, setContent] = useState('')
  const [needs, setNeeds] = useState('')
  const [busy, setBusy] = useState('')
  const [filter, setFilter] = useState('')
  const [backups, setBackups] = useState<Backup[] | null>(null)
  const editorRef = useRef<HTMLTextAreaElement>(null)
  const toast = useToast()
  const dirty = file !== null && !file.binary && content !== file.content

  const loadDir = async (path: string) => {
    const data = await guard(client.get<{ root: string; entries: Entry[] }>(`/api/admin/code/tree?path=${encodeURIComponent(path)}`))
    setRoot(data.root)
    setChildren((current) => ({ ...current, [path]: data.entries }))
  }

  useEffect(() => { loadDir('').catch((e) => toast.push((e as Error).message, 'error')) }, [])

  const toggleDir = (path: string) => {
    const next = new Set(open)
    if (next.has(path)) next.delete(path)
    else { next.add(path); if (!children[path]) loadDir(path).catch(() => undefined) }
    setOpen(next)
  }

  const openFile = async (path: string) => {
    if (dirty && !window.confirm('Des modifications ne sont pas enregistrées. Les abandonner ?')) return
    try {
      const data = await guard(client.get<FileData>(`/api/admin/code/file?path=${encodeURIComponent(path)}`))
      setFile(data); setContent(data.content)
    } catch (err) { toast.push((err as Error).message, 'error') }
  }

  const save = async (force = false) => {
    if (!file || !dirty) return
    setBusy('save')
    try {
      const result = await guard(client.put<{ needs: string; backup: string | null }>('/api/admin/code/file', { path: file.path, content, force }))
      setFile({ ...file, content })
      setNeeds(result.needs)
      toast.push(`Enregistré${result.backup ? ' (ancienne version sauvegardée)' : ''}.`, 'success')
    } catch (err) {
      const message = (err as Error).message
      if (message.includes('syntaxe') && window.confirm(`${message}\n\nEnregistrer quand même ? Le service risque de ne plus démarrer (une restauration automatique vous sera proposée).`)) {
        setBusy(''); await save(true); return
      }
      toast.push(message, 'error')
    } finally { setBusy('') }
  }

  const createFile = async () => {
    const base = file ? file.path.split('/').slice(0, -1).join('/') : ''
    const path = window.prompt('Chemin du nouveau fichier (depuis la racine du logiciel) :', base ? `${base}/` : '')
    if (!path) return
    try {
      await guard(client.put('/api/admin/code/file', { path, content: '', create: true }))
      const parent = path.split('/').slice(0, -1).join('/')
      await loadDir(parent).catch(() => undefined)
      await openFile(path)
    } catch (err) { toast.push((err as Error).message, 'error') }
  }

  const removeFile = async () => {
    if (!file || !window.confirm(`Supprimer ${file.path} ? Une copie est conservée dans les sauvegardes de code.`)) return
    try {
      const result = await guard(client.del<{ needs: string }>(`/api/admin/code/file?path=${encodeURIComponent(file.path)}`))
      setNeeds(result.needs)
      await loadDir(file.path.split('/').slice(0, -1).join('/')).catch(() => undefined)
      setFile(null); setContent('')
    } catch (err) { toast.push((err as Error).message, 'error') }
  }

  const restart = async () => {
    setBusy('restart')
    try {
      await guard(client.post('/api/admin/restart'))
      toast.push('Redémarrage du service…', 'info')
      for (let i = 0; i < 60; i += 1) {
        await new Promise((resolve) => window.setTimeout(resolve, 1000))
        try { await api.get('/api/health'); setNeeds(''); toast.push('Service redémarré avec le nouveau code.', 'success'); return } catch { /* pas encore prêt */ }
      }
      toast.push('Le service ne répond pas encore : consultez la fenêtre Cybbig.', 'error')
    } catch (err) { toast.push((err as Error).message, 'error') } finally { setBusy('') }
  }

  const rebuild = async () => {
    setBusy('rebuild')
    toast.push('Recompilation de l’interface… (installation des outils de build au premier passage)', 'info')
    try {
      const result = await guard(client.post<{ exit_code: number; stdout: string; stderr: string }>('/api/admin/exec', {
        shell: 'powershell', cwd: 'frontend', timeout: 900,
        code: "if (-not (Get-Command npm.cmd -ErrorAction SilentlyContinue)) { Write-Error 'Node.js est requis pour recompiler l''interface : installez-le depuis nodejs.org.'; exit 1 }\nif (-not (Test-Path node_modules)) { npm.cmd ci --no-audit --no-fund }\nnpm.cmd run build",
      }))
      if (result.exit_code === 0) { toast.push('Interface recompilée : rechargement.', 'success'); window.setTimeout(() => window.location.reload(), 800) }
      else toast.push(`Échec de la compilation : ${(result.stderr || result.stdout).slice(-400)}`, 'error')
    } catch (err) { toast.push((err as Error).message, 'error') } finally { setBusy('') }
  }

  const showBackups = async () => {
    try { setBackups((await guard(client.get<{ items: Backup[] }>('/api/admin/code/backups'))).items) }
    catch (err) { toast.push((err as Error).message, 'error') }
  }

  const restore = async (item: Backup) => {
    if (!window.confirm(`Restaurer ${item.path} depuis la sauvegarde du ${item.backup} ?`)) return
    try {
      const result = await guard(client.post<{ needs: string }>('/api/admin/code/restore', { backup: item.backup, path: item.path }))
      setNeeds(result.needs); setBackups(null)
      if (file?.path === item.path) await openFile(item.path)
      toast.push('Version restaurée.', 'success')
    } catch (err) { toast.push((err as Error).message, 'error') }
  }

  const onKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if ((event.ctrlKey || event.metaKey) && event.key === 's') { event.preventDefault(); save(); return }
    if (event.key === 'Tab') {
      // Tabulation = 4 espaces au lieu de quitter le champ.
      event.preventDefault()
      const el = event.currentTarget
      const { selectionStart, selectionEnd } = el
      const next = content.slice(0, selectionStart) + '    ' + content.slice(selectionEnd)
      setContent(next)
      window.requestAnimationFrame(() => { el.selectionStart = el.selectionEnd = selectionStart + 4 })
    }
  }

  const lines = useMemo(() => content.split('\n').length, [content])

  const renderDir = (path: string, depth: number): React.ReactNode => {
    const entries = (children[path] ?? []).filter((e) => !filter || e.dir || e.path.toLowerCase().includes(filter.toLowerCase()))
    return entries.map((entry) => (
      <div key={entry.path}>
        <button className={`code-tree-item${file?.path === entry.path ? ' active' : ''}`} style={{ paddingLeft: 8 + depth * 14 }}
          onClick={() => (entry.dir ? toggleDir(entry.path) : openFile(entry.path))} title={entry.path}>
          {entry.dir ? (open.has(entry.path) ? <ChevronDown size={12} /> : <ChevronRight size={12} />) : <span style={{ width: 12 }} />}
          {entry.dir ? <Folder size={12} color="var(--accent)" /> : <FileText size={12} />}
          <span className="truncate">{entry.name}</span>
        </button>
        {entry.dir && open.has(entry.path) && (children[entry.path] ? renderDir(entry.path, depth + 1) : <div className="tiny faint" style={{ paddingLeft: 30 }}>…</div>)}
      </div>
    ))
  }

  return (
    <section className="card">
      <div className="card-header">
        <div><h2>Code du logiciel</h2><div className="sub mono tiny">{root || '…'}</div></div>
        <div className="right">
          <button className="btn sm" onClick={createFile}><FilePlus size={13} /> Nouveau fichier</button>
          <button className="btn sm" onClick={showBackups}><History size={13} /> Sauvegardes</button>
          <button className="btn sm" onClick={rebuild} disabled={!!busy}><Wrench size={13} /> {busy === 'rebuild' ? 'Compilation…' : 'Recompiler l’interface'}</button>
          <button className="btn sm" onClick={restart} disabled={!!busy}><Power size={13} /> {busy === 'restart' ? 'Redémarrage…' : 'Redémarrer le service'}</button>
        </div>
      </div>
      {needs && NEEDS[needs] && <div style={{ padding: '0 16px' }}><AlertBox kind="info">{NEEDS[needs]}</AlertBox></div>}
      <div className="code-layout">
        <div className="code-tree">
          <input className="input" placeholder="Filtrer les fichiers ouverts…" value={filter} onChange={(e) => setFilter(e.target.value)} style={{ margin: '0 0 8px', width: '100%' }} />
          {children[''] ? renderDir('', 0) : <Loading />}
        </div>
        <div className="code-main">
          {!file ? (
            <div className="faint small" style={{ padding: 24 }}>
              Choisissez un fichier à gauche. Tout le logiciel est modifiable : backend (backend/app), interface (frontend/src),
              moteur de bureau (desktop), scripts. Chaque enregistrement conserve l’ancienne version dans les sauvegardes.
            </div>
          ) : file.binary ? (
            <div className="faint small" style={{ padding: 24 }}>{file.reason}</div>
          ) : (
            <>
              <div className="code-bar">
                <span className="mono tiny">{file.path}{dirty && <b style={{ color: 'var(--accent)' }}> •</b>}</span>
                <span className="tiny faint">{lines} lignes</span>
                <div style={{ marginLeft: 'auto', display: 'flex', gap: 6 }}>
                  <button className="btn ghost sm" onClick={() => openFile(file.path)} title="Recharger depuis le disque"><RefreshCw size={12} /></button>
                  <button className="btn ghost sm" onClick={removeFile} title="Supprimer"><Trash2 size={12} /></button>
                  <button className="btn primary sm" onClick={() => save()} disabled={!dirty || busy === 'save'}><Save size={12} /> Enregistrer (Ctrl+S)</button>
                </div>
              </div>
              <textarea ref={editorRef} className="code-editor" value={content} spellCheck={false} wrap="off"
                onChange={(e) => setContent(e.target.value)} onKeyDown={onKeyDown} />
            </>
          )}
        </div>
      </div>

      <Modal open={backups !== null} onClose={() => setBackups(null)} title="Sauvegardes de code" subtitle="Versions conservées avant chaque modification">
        {!backups?.length ? <div className="small faint">Aucune sauvegarde pour le moment.</div> : (
          <div className="table-wrap" style={{ maxHeight: 420 }}>
            <table className="data">
              <thead><tr><th>Date</th><th>Fichier</th><th /></tr></thead>
              <tbody>
                {backups.map((b) => (
                  <tr key={`${b.backup}/${b.path}`}>
                    <td className="tiny mono">{b.backup.slice(0, 15).replace(/^(\d{4})(\d{2})(\d{2})-(\d{2})(\d{2})(\d{2})/, '$3/$2/$1 $4:$5:$6')}</td>
                    <td className="cell-mono">{b.path}</td>
                    <td><button className="btn sm" onClick={() => restore(b)}><RotateCcw size={12} /> Restaurer</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Modal>
    </section>
  )
}
