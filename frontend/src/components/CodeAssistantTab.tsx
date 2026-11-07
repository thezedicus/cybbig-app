import { useEffect, useRef, useState } from 'react'
import { Check, FilePlus, Send, Sparkles, Square, X } from 'lucide-react'
import { adminApi, streamNdjson } from '../api'
import { AlertBox, useToast } from './ui'
import Markdown from './Markdown'

type Client = ReturnType<typeof adminApi>
type Guard = <T>(promise: Promise<T>) => Promise<T>
interface Edit { index: number; path: string; search: string; replace: string; status: 'ok' | 'error'; message: string; diff: string; new_file: boolean }
interface Turn { id: number; instruction: string; text: string; model: string; provider: string; files: Array<{ path: string; chars: number; truncated: boolean }>; autoContext: boolean; edits: Edit[]; picked: Set<number>; applied: boolean; done: boolean; error: string }
type Event =
  | { type: 'meta'; model: string; provider: string; files: Turn['files'] }
  | { type: 'token'; content: string }
  | { type: 'error'; message: string }
  | { type: 'done'; edits: Edit[]; empty: boolean }

const NEEDS: Record<string, string> = {
  restart: 'Backend modifié : redémarrez le service (onglet Vue d’ensemble) pour appliquer.',
  rebuild: 'Interface modifiée : recompilez l’interface pour appliquer.',
  reload: 'Fichier compilé modifié : rechargez la fenêtre.',
  relaunch: 'Moteur de bureau modifié : fermez et relancez Cybbig.',
  none: 'Modifications appliquées.',
}
const MARK = '<<<<<<< SEARCH'

function Diff({ text }: { text: string }) {
  return (
    <pre className="mono" style={{ margin: 0, fontSize: 11.5, overflow: 'auto', maxHeight: 260, background: 'var(--bg-soft)', borderRadius: 8, padding: 8 }}>
      {text.split('\n').map((line, i) => (
        <div key={i} style={{ color: line.startsWith('+') && !line.startsWith('+++') ? 'var(--green)' : line.startsWith('-') && !line.startsWith('---') ? 'var(--critical)' : line.startsWith('@@') ? 'var(--accent)' : 'var(--text-soft)' }}>{line || ' '}</div>
      ))}
    </pre>
  )
}

// Atelier IA (Administration) : un modèle Ollama propose des modifications du code ; chaque différence est validée ici,
// l'écriture se fait par l'éditeur du propriétaire (sauvegarde avant chaque modification, contrôle de syntaxe Python).
export default function CodeAssistantTab({ client, guard, token }: { client: Client; guard: Guard; token: string }) {
  const [paths, setPaths] = useState<string[]>([])
  const [query, setQuery] = useState('')
  const [suggestions, setSuggestions] = useState<string[]>([])
  const [instruction, setInstruction] = useState('')
  const [turns, setTurns] = useState<Turn[]>([])
  const [busy, setBusy] = useState(false)
  const abortRef = useRef<AbortController | null>(null)
  const bottomRef = useRef<HTMLDivElement>(null)
  const toast = useToast()

  useEffect(() => {
    if (query.trim().length < 2) { setSuggestions([]); return }
    const timer = window.setTimeout(() => {
      guard(client.get<{ items: string[] }>(`/api/admin/code/search?q=${encodeURIComponent(query.trim())}`)).then((d) => setSuggestions(d.items)).catch(() => undefined)
    }, 250)
    return () => window.clearTimeout(timer)
  }, [query])
  useEffect(() => { bottomRef.current?.scrollIntoView({ block: 'end' }) }, [turns])

  const addPath = (path: string) => {
    const clean = path.trim()
    if (!clean) return
    if (paths.length >= 6) { toast.push('6 fichiers au maximum par demande.', 'info'); return }
    if (!paths.includes(clean)) setPaths([...paths, clean])
    setQuery('')
  }
  const patch = (id: number, change: Partial<Turn> | ((t: Turn) => Partial<Turn>)) =>
    setTurns((current) => current.map((t) => (t.id === id ? { ...t, ...(typeof change === 'function' ? change(t) : change) } : t)))

  const send = async () => {
    const text = instruction.trim()
    if (!text || busy) return
    const id = Date.now()
    const history = turns.filter((t) => t.done && t.text).slice(-4).flatMap((t) => [{ role: 'user', content: t.instruction }, { role: 'assistant', content: t.text.split(MARK)[0].trim() || t.text }])
    setTurns((current) => [...current, { id, instruction: text, text: '', model: '', provider: '', files: [], autoContext: paths.length === 0, edits: [], picked: new Set(), applied: false, done: false, error: '' }])
    setInstruction(''); setBusy(true)
    const controller = new AbortController()
    abortRef.current = controller
    let acc = ''
    try {
      await streamNdjson<Event>('/api/admin/code/assist', { instruction: text, paths, history }, (event) => {
        if (event.type === 'meta') patch(id, { model: event.model, provider: event.provider, files: event.files })
        else if (event.type === 'token') { acc += event.content; patch(id, { text: acc }) }
        else if (event.type === 'error') patch(id, { error: event.message })
        else if (event.type === 'done') patch(id, { edits: event.edits, picked: new Set(event.edits.filter((e) => e.status === 'ok').map((e) => e.index)), done: true })
      }, controller.signal, { 'X-Admin-Token': token })
    } catch (err) {
      if ((err as Error).name !== 'AbortError') patch(id, { error: (err as Error).message, done: true })
      else patch(id, { done: true })
    } finally { setBusy(false); abortRef.current = null }
  }

  const apply = async (turn: Turn) => {
    const chosen = turn.edits.filter((e) => turn.picked.has(e.index))
    if (!chosen.length) return
    try {
      const result = await guard(client.post<{ files: Array<{ path: string; backup: string | null }>; needs: string }>('/api/admin/code/assist/apply', {
        edits: chosen.map(({ path, search, replace }) => ({ path, search, replace })),
      }))
      patch(turn.id, { applied: true })
      toast.push(`${result.files.length} fichier(s) modifié(s). ${NEEDS[result.needs] ?? ''}`, 'success')
    } catch (err) { toast.push((err as Error).message, 'error') }
  }

  const toggle = (turn: Turn, index: number) => {
    const picked = new Set(turn.picked)
    if (picked.has(index)) picked.delete(index); else picked.add(index)
    patch(turn.id, { picked })
  }

  return (
    <div className="stack" style={{ gap: 12 }}>
      <AlertBox kind="info">
        L’IA peut explorer le code source du logiciel pour repérer les fichiers pertinents. Sans sélection ci-dessous, elle les choisit automatiquement d’après votre demande. Elle propose un diff, puis <b>vous validez</b> chaque modification; une sauvegarde précède toute écriture. Avec un modèle en ligne, seuls les extraits retenus sont transmis (secrets connus masqués).
      </AlertBox>

      <div className="card card-pad stack" style={{ gap: 8 }}>
        <label className="tiny faint" htmlFor="atelier-file">Fichiers à joindre (facultatif, 6 maximum — sans sélection, Cybbig repère automatiquement les sources)</label>
        <div className="row wrap" style={{ gap: 6 }}>
          {paths.map((p) => (
            <span key={p} className="tag mono">{p} <button type="button" className="link-btn" aria-label={`Retirer ${p}`} onClick={() => setPaths(paths.filter((x) => x !== p))}><X size={11} /></button></span>
          ))}
          <input id="atelier-file" className="input mono" style={{ flex: 1, minWidth: 240 }} value={query} placeholder="Chercher un fichier : ai.py, Settings.tsx…" autoComplete="off"
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); if (suggestions[0]) addPath(suggestions[0]); else if (query.includes('.')) addPath(query) } }} />
        </div>
        {suggestions.length > 0 && (
          <div className="stack" role="listbox" aria-label="Fichiers trouvés" style={{ gap: 2, maxHeight: 190, overflow: 'auto' }}>
            {suggestions.slice(0, 12).map((path) => (
              <button key={path} type="button" role="option" aria-selected={false} className="nav-link cat-link mono" style={{ fontSize: 12, padding: '5px 9px' }} onClick={() => { addPath(path); setSuggestions([]) }}>
                <FilePlus size={12} /> <span className="truncate">{path}</span>
              </button>
            ))}
          </div>
        )}
        {query.trim().length >= 2 && suggestions.length === 0 && <span className="tiny faint">Aucun fichier ne correspond.</span>}
      </div>

      <div className="stack" style={{ gap: 12 }}>
        {turns.length === 0 && <div className="tiny faint" style={{ padding: 6 }}><Sparkles size={13} /> Exemple : « Améliore l’affichage des résultats de recherche et vérifie les appels API associés » — l’atelier peut retrouver les fichiers nécessaires à partir de la demande.</div>}
        {turns.map((turn) => {
          const explanation = turn.text.split(MARK)[0].trim()
          return (
            <div key={turn.id} className="card card-pad stack" style={{ gap: 10 }}>
              <div><b className="small">Vous</b><div className="small" style={{ whiteSpace: 'pre-wrap' }}>{turn.instruction}</div></div>
              <div className="tiny faint">{turn.model ? `${turn.model} · ${turn.provider === 'cloud' ? 'en ligne' : 'local'} · ${turn.autoContext ? 'analyse automatique du projet' : 'fichiers choisis'}` : 'Connexion au modèle…'}{turn.files.some((f) => f.truncated) ? ' · fichier(s) tronqué(s) : seul le début est visible du modèle' : ''}</div>
              {turn.files.length > 0 && <div className="tiny mono faint">Sources lues : {turn.files.map((file) => `${file.path} (${file.chars.toLocaleString('fr-FR')} caractères)`).join(' · ')}</div>}
              {explanation ? <Markdown text={explanation} /> : !turn.done && <span className="faint small">Réflexion…</span>}
              {turn.error && <AlertBox kind="error">{turn.error}</AlertBox>}
              {turn.done && !turn.error && turn.edits.length === 0 && <span className="small faint">Aucune modification proposée (le modèle a répondu sans bloc valide).</span>}
              {turn.edits.map((edit) => (
                <div key={edit.index} className="card" style={{ padding: 10, borderColor: edit.status === 'ok' ? undefined : 'rgba(251,77,109,.35)' }}>
                  <label className="checkbox" style={{ alignItems: 'center' }}>
                    <input type="checkbox" disabled={edit.status !== 'ok' || turn.applied} checked={turn.picked.has(edit.index)} onChange={() => toggle(turn, edit.index)} />
                    <span className="mono small">{edit.path}</span>
                    {edit.new_file && <span className="tag">nouveau fichier</span>}
                    {edit.status !== 'ok' && <span className="tag" style={{ color: 'var(--critical)' }}>refusé</span>}
                  </label>
                  {edit.status === 'ok' ? <Diff text={edit.diff} /> : <div className="tiny" style={{ color: 'var(--critical)', marginTop: 4 }}>{edit.message}</div>}
                </div>
              ))}
              {turn.edits.some((e) => e.status === 'ok') && (
                <div className="row" style={{ gap: 8 }}>
                  <button className="btn primary sm" disabled={turn.applied || turn.picked.size === 0} onClick={() => apply(turn)}><Check size={13} /> {turn.applied ? 'Appliqué' : `Appliquer la sélection (${turn.picked.size})`}</button>
                  {turn.applied && <span className="tiny faint">Sauvegardes dans Administration &gt; Code &gt; Historique.</span>}
                </div>
              )}
            </div>
          )
        })}
        <div ref={bottomRef} />
      </div>

      <div className="card card-pad row" style={{ gap: 8, alignItems: 'flex-end' }}>
        <textarea className="textarea" style={{ flex: 1, minHeight: 64 }} value={instruction} placeholder="Décrivez la modification souhaitée (Ctrl+Entrée pour envoyer)"
          onChange={(e) => setInstruction(e.target.value)} onKeyDown={(e) => { if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) { e.preventDefault(); send() } }} />
        {busy
          ? <button className="btn danger" onClick={() => abortRef.current?.abort()}><Square size={14} /> Arrêter</button>
          : <button className="btn primary" disabled={!instruction.trim()} onClick={send}><Send size={14} /> Envoyer</button>}
      </div>
      <span className="tiny faint">Modèle utilisé : un modèle « coder » s’il est installé (ex. qwen2.5-coder), sinon le modèle actif. Avec un 7B sur processeur, comptez plusieurs minutes ; le modèle en ligne répond en secondes.</span>
    </div>
  )
}
