import { useEffect, useMemo, useState } from 'react'
import {
  BookOpen, ChevronDown, ChevronRight, Database, FolderOpen, Pencil, Plus, Search, Tag, Trash2,
} from 'lucide-react'
import { api, formatDate } from '../api'
import AddDataModal from '../components/AddDataModal'
import {
  AlertBox, Drawer, EmptyState, Loading, Modal, PageHeader, useToast,
} from '../components/ui'
import type { KnowledgeDoc } from '../types'

const EMPTY = { title: '', category: 'Général', content: '', source: '', tags: '' }
const VOLUMES = [
  { title: 'Algorithmes avancés', category: 'Algorithmes avancés', desc: 'Complexité, graphes, programmation dynamique et validation.' },
  { title: 'Programmation système', category: 'Programmation système', desc: 'Processus, mémoire, fichiers et concurrence maîtrisée.' },
  { title: 'Développement web', category: 'Développement web', desc: 'Contrats HTTP, sessions, autorisations et accessibilité.' },
  { title: 'Bases de données', category: 'Bases de données', desc: 'Modèles, transactions, migrations et restauration.' },
  { title: 'IA et apprentissage', category: 'IA et apprentissage automatique', desc: 'Évaluation, données, RAG et limites des modèles.' },
  { title: 'Mathématiques', category: 'Mathématiques appliquées', desc: 'Logique, probabilités, calcul numérique et optimisation.' },
  { title: 'Administration', category: 'Administration système', desc: 'Scripts contrôlés, réversibles et auditables.' },
  { title: 'Automatisation', category: 'Automatisation', desc: 'Workflows, reprises, idempotence et observabilité.' },
  { title: 'Compilateurs', category: 'Compilateurs', desc: 'Analyse, représentations intermédiaires et génération.' },
  { title: 'Architecture logicielle', category: 'Architectures logicielles', desc: 'Frontières, contrats et évolution du logiciel.' },
]

export default function Knowledge() {
  const [items, setItems] = useState<KnowledgeDoc[] | null>(null)
  const [categories, setCategories] = useState<Array<{ category: string; count: number }>>([])
  const [error, setError] = useState('')
  const [query, setQuery] = useState('')
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState('')
  const [selected, setSelected] = useState<KnowledgeDoc | null>(null)
  const [modal, setModal] = useState<{ open: boolean; doc?: KnowledgeDoc }>({ open: false })
  const [form, setForm] = useState(EMPTY)
  const [saving, setSaving] = useState(false)
  const [addOpen, setAddOpen] = useState(false)
  const [openGroups, setOpenGroups] = useState<Record<string, boolean>>({})
  const toast = useToast()

  const load = () => {
    const qs = new URLSearchParams({ limit: '300' })
    if (search) qs.set('q', search)
    if (category) qs.set('category', category)
    api.get<{ items: KnowledgeDoc[]; categories: Array<{ category: string; count: number }> }>(`/api/knowledge?${qs}`)
      .then((d) => { setItems(d.items); setCategories(d.categories); setError('') })
      .catch((e) => setError((e as Error).message))
  }

  useEffect(load, [search, category])

  useEffect(() => {
    const timer = window.setTimeout(() => setSearch(query.trim()), 300)
    return () => window.clearTimeout(timer)
  }, [query])

  const openDoc = async (doc: KnowledgeDoc) => {
    try { setSelected(await api.get<KnowledgeDoc>(`/api/knowledge/${doc.id}`)) }
    catch (err) { toast.push((err as Error).message, 'error') }
  }

  const openCreate = () => { setForm(EMPTY); setModal({ open: true }) }
  const openEdit = (doc: KnowledgeDoc) => {
    setForm({ title: doc.title, category: doc.category, content: doc.content, source: doc.source, tags: doc.tags })
    setModal({ open: true, doc })
  }

  const save = async (event: React.FormEvent) => {
    event.preventDefault()
    setSaving(true)
    try {
      if (modal.doc) {
        await api.put(`/api/knowledge/${modal.doc.id}`, form)
        toast.push('Document mis à jour.', 'success')
      } else {
        await api.post('/api/knowledge', form)
        toast.push('Document créé.', 'success')
      }
      setModal({ open: false }); load()
      if (selected) setSelected(null)
    } catch (err) {
      toast.push((err as Error).message, 'error')
    } finally {
      setSaving(false)
    }
  }

  const remove = async (doc: KnowledgeDoc) => {
    if (!window.confirm(`Supprimer « ${doc.title} » ?`)) return
    try {
      await api.del(`/api/knowledge/${doc.id}`)
      toast.push('Document supprimé.', 'success')
      setSelected(null); load()
    } catch (err) {
      toast.push((err as Error).message, 'error')
    }
  }

  // Catégories regroupées par préfixe (« Cyber · PHP sécurisé » -> groupe « Cyber »).
  const groups = useMemo(() => {
    const map = new Map<string, Array<{ category: string; count: number; label: string }>>()
    for (const c of categories) {
      const [head, ...rest] = c.category.split(' · ')
      const key = rest.length ? head : ''
      map.set(key, [...(map.get(key) ?? []), { ...c, label: rest.length ? rest.join(' · ') : c.category }])
    }
    return [...map.entries()].sort(([a], [b]) => (a === '' ? 1 : b === '' ? -1 : a.localeCompare(b, 'fr')))
  }, [categories])

  return (
    <>
      <PageHeader
        title="Base de connaissances"
        description="Fiches méthodologiques, durcissement PHP, OWASP, PCI DSS et procédures. Alimente aussi le contexte de l’assistant local."
        actions={
          <>
            <button className="btn" onClick={openCreate}><Plus size={14} /> Nouveau document</button>
            <button className="btn primary" onClick={() => setAddOpen(true)}><Database size={14} /> Ajouter des données</button>
          </>
        }
      />

      {error && <AlertBox kind="error">{error}</AlertBox>}

      <section className="knowledge-library" aria-label="Volumes thématiques Cybbig">
        <div className="knowledge-library-heading">
          <div><span className="knowledge-eyebrow"><BookOpen size={13} /> PARCOURS THÉMATIQUES</span><h2>Volumes Cybbig</h2><p>Dix repères pratiques, reliés à la recherche et au contexte de l’assistant.</p></div>
          <span className="knowledge-library-total">{categories.reduce((sum, item) => sum + item.count, 0)} fiches indexées</span>
        </div>
        <div className="knowledge-volume-grid">
          {VOLUMES.map((volume, index) => {
            const count = categories.find((item) => item.category === `Volumes techniques · ${volume.category}`)?.count ?? 0
            return <button key={volume.category} className={`knowledge-volume${category === `Volumes techniques · ${volume.category}` ? ' selected' : ''}`} onClick={() => setCategory(`Volumes techniques · ${volume.category}`)}>
              <span className="knowledge-volume-number">{String(index + 1).padStart(2, '0')}</span><span className="knowledge-volume-count">{count} fiche{count > 1 ? 's' : ''}</span>
              <strong>{volume.title}</strong><span className="knowledge-volume-desc">{volume.desc}</span><span className="knowledge-volume-action">Explorer <ChevronRight size={13} /></span>
            </button>
          })}
        </div>
      </section>

      <div className="grid" style={{ gridTemplateColumns: '230px minmax(0, 1fr)', alignItems: 'start' }}>
        <div className="card">
          <div className="card-header"><h2>Catégories</h2></div>
          <div className="card-pad" style={{ padding: '8px 10px 12px', display: 'grid', gap: 3 }}>
            <button className={`nav-link cat-link${category === '' ? ' active' : ''}`} onClick={() => setCategory('')}><FolderOpen size={14} /><span>Toutes</span><span className="tag" style={{ marginLeft: 'auto' }}>{categories.reduce((a, c) => a + c.count, 0)}</span></button>
            {groups.map(([group, items]) => group === '' ? items.map((c) => (
              <button key={c.category} className={`nav-link cat-link${category === c.category ? ' active' : ''}`} onClick={() => setCategory(c.category)}><BookOpen size={14} /><span className="truncate">{c.label}</span><span className="tag" style={{ marginLeft: 'auto' }}>{c.count}</span></button>
            )) : (
              <div key={group} style={{ display: 'grid', gap: 3 }}>
                <div className="row" style={{ gap: 2 }}>
                  <button className="cat-toggle" aria-label={openGroups[group] ? `Replier ${group}` : `Déplier ${group}`} onClick={() => setOpenGroups({ ...openGroups, [group]: !openGroups[group] })}>
                    {openGroups[group] ? <ChevronDown size={13} /> : <ChevronRight size={13} />}
                  </button>
                  <button className={`nav-link cat-link${category === `${group} · *` ? ' active' : ''}`} style={{ flex: 1 }} onClick={() => setCategory(`${group} · *`)}>
                    <FolderOpen size={14} /><span className="truncate">{group}</span><span className="tag" style={{ marginLeft: 'auto' }}>{items.reduce((a, c) => a + c.count, 0)}</span>
                  </button>
                </div>
                {openGroups[group] && items.map((c) => (
                  <button key={c.category} className={`nav-link cat-link${category === c.category ? ' active' : ''}`} style={{ marginLeft: 22 }} onClick={() => setCategory(c.category)}><span className="truncate">{c.label}</span><span className="tag" style={{ marginLeft: 'auto' }}>{c.count}</span></button>
                ))}
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <div className="searchbar" style={{ flex: 1 }}>
              <Search size={15} />
              <input className="input" placeholder="Rechercher dans la base (FTS5)…" value={query} onChange={(e) => setQuery(e.target.value)} />
            </div>
            <div className="right"><span className="tag">{items?.length ?? 0} document(s)</span></div>
          </div>
          {!items ? <Loading /> : items.length === 0 ? (
            <EmptyState icon={<BookOpen size={30} />} title="Aucun document" description="Créez une fiche, importez des fichiers ou ajoutez un site web." action={<button className="btn primary sm" onClick={() => setAddOpen(true)}><Database size={14} /> Ajouter des données</button>} />
          ) : (
            <div className="grid auto" style={{ padding: 16 }}>
              {items.map((doc) => (
                <article key={doc.id} className="card scenario-card" role="button" tabIndex={0} onClick={() => openDoc(doc)} onKeyDown={(event) => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); openDoc(doc) } }}>
                  <div className="row" style={{ gap: 6 }}>
                    <span className="tag">{doc.category}</span>
                    <span className="tiny faint" style={{ marginLeft: 'auto' }}>{formatDate(doc.updated_at, false)}</span>
                  </div>
                  <h3>{doc.title}</h3>
                  <p className="clamp-3">{doc.excerpt || doc.content.slice(0, 200)}</p>
                  <div className="row" style={{ gap: 6 }}>
                    <Tag size={11} color="var(--faint)" />
                    <span className="tiny faint truncate">{doc.tags || 'sans tag'}</span>
                  </div>
                </article>
              ))}
            </div>
          )}
        </div>
      </div>

      <Drawer open={Boolean(selected)} onClose={() => setSelected(null)} title={selected?.title ?? ''} subtitle={selected ? `${selected.category} · ${selected.source || 'source locale'}` : undefined}>
        {selected && (
          <>
            <div className="row wrap">
              <span className="tag">{selected.category}</span>
              {selected.tags.split(',').filter(Boolean).map((t) => <span className="tag" key={t}>{t.trim()}</span>)}
            </div>
            <div style={{ whiteSpace: 'pre-wrap', fontSize: 13, lineHeight: 1.7, color: 'var(--text-soft)' }}>{selected.content}</div>
            <div className="row between mt-2" style={{ borderTop: '1px solid var(--line-soft)', paddingTop: 14 }}>
              <span className="tiny faint">Créé {formatDate(selected.created_at)} · maj {formatDate(selected.updated_at)}</span>
              <div className="row" style={{ gap: 6 }}>
                <button className="btn sm" onClick={() => openEdit(selected)}><Pencil size={12} /> Modifier</button>
                <button className="btn danger sm" onClick={() => remove(selected)}><Trash2 size={12} /> Supprimer</button>
              </div>
            </div>
          </>
        )}
      </Drawer>

      <AddDataModal open={addOpen} onClose={() => setAddOpen(false)} onDone={load} category={category} />

      <Modal open={modal.open} onClose={() => setModal({ open: false })} title={modal.doc ? 'Modifier le document' : 'Nouveau document'} subtitle="Markdown ou texte brut" size="wide">
        <form onSubmit={save}>
          <div className="form-grid">
            <div className="field full"><label>Titre *</label><input className="input" required value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} /></div>
            <div className="field"><label>Catégorie</label><input className="input" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} /></div>
            <div className="field"><label>Source</label><input className="input" value={form.source} onChange={(e) => setForm({ ...form, source: e.target.value })} placeholder="OWASP, éditeur, note interne…" /></div>
            <div className="field full"><label>Tags</label><input className="input" value={form.tags} onChange={(e) => setForm({ ...form, tags: e.target.value })} placeholder="php, sessions, uploads" /></div>
            <div className="field full"><label>Contenu *</label><textarea className="textarea" required style={{ minHeight: 260 }} value={form.content} onChange={(e) => setForm({ ...form, content: e.target.value })} /></div>
          </div>
          <div className="form-actions"><button type="button" className="btn" onClick={() => setModal({ open: false })}>Annuler</button><button className="btn primary" disabled={saving}>{saving ? 'Enregistrement…' : 'Enregistrer'}</button></div>
        </form>
      </Modal>
    </>
  )
}
