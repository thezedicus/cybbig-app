import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  ArrowUpRight, FlaskConical, Layers, ShieldCheck, Terminal,
} from 'lucide-react'
import { api } from '../api'
import { AlertBox, EmptyState, Loading, PageHeader } from '../components/ui'
import type { LabScenario } from '../types'

const LEVEL_LABEL: Record<string, string> = {
  A: 'Niveau A', B: 'Niveau B', C: 'Niveau C', intro: 'Initiation', beginner: 'Initiation',
  intermediate: 'Intermédiaire', advanced: 'Avancé', expert: 'Expert',
}

const CATEGORY_LABEL: Record<string, string> = {
  PHP: 'PHP', API: 'API', Finance: 'Finance', 'E-commerce': 'E-commerce',
  injection: 'Injection', auth: 'Authentification', xss: 'XSS', crypto: 'Cryptographie',
  upload: 'Téléversement', session: 'Session', payment: 'Paiement', headers: 'En-têtes',
  configuration: 'Configuration',
}

const CATEGORY_TONE: Record<string, string> = {
  PHP: 'high', API: 'medium', Finance: 'critical', 'E-commerce': 'critical',
  injection: 'critical', auth: 'high', xss: 'high', crypto: 'medium', upload: 'critical',
  session: 'medium', payment: 'high', headers: 'low', configuration: 'low',
}

export default function Lab() {
  const [items, setItems] = useState<LabScenario[] | null>(null)
  const [categories, setCategories] = useState<string[]>([])
  const [category, setCategory] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    const qs = category ? `?category=${encodeURIComponent(category)}` : ''
    api.get<{ items: LabScenario[]; categories: string[] }>(`/api/lab/scenarios${qs}`)
      .then((d) => { setItems(d.items); setCategories(d.categories); setError('') })
      .catch((e) => setError((e as Error).message))
  }, [category])

  const stats = useMemo(() => {
    const levels = new Set((items ?? []).map((s) => s.level))
    return {
      total: items?.length ?? 0,
      categories: categories.length,
      levels: levels.size,
    }
  }, [items, categories])

  return (
    <>
      <PageHeader
        title="Laboratoire"
        description="Scénarios pédagogiques de vulnérabilités Web et PHP. Le code fourni est analysé par motifs, jamais exécuté. Utilisez un environnement isolé et des données fictives."
        actions={<span className="tag"><ShieldCheck size={12} /> Analyse statique uniquement</span>}
      />

      {error && <AlertBox kind="error">{error}</AlertBox>}

      <div className="grid cols-3 mb-2">
        <div className="card stat-card">
          <div className="stat-label"><FlaskConical size={13} /> Scénarios</div>
          <div className="stat-value">{stats.total}</div>
          <div className="stat-foot">disponibles hors ligne</div>
        </div>
        <div className="card stat-card">
          <div className="stat-label"><Layers size={13} /> Catégories</div>
          <div className="stat-value">{stats.categories}</div>
          <div className="stat-foot">API, PHP, finance, e-commerce</div>
        </div>
        <div className="card stat-card">
          <div className="stat-label"><Terminal size={13} /> Validation</div>
          <div className="stat-value" style={{ fontSize: 20, paddingTop: 5 }}>Locale</div>
          <div className="stat-foot">motifs, taint heuristique, secrets</div>
        </div>
      </div>

      <div className="filters mb-2">
        <button className={`btn sm${category ? '' : ' primary'}`} onClick={() => setCategory('')}>Toutes</button>
        {categories.map((value) => (
          <button
            key={value}
            className={`btn sm${category === value ? ' primary' : ''}`}
            onClick={() => setCategory(value)}
          >
            {CATEGORY_LABEL[value] ?? value}
          </button>
        ))}
      </div>

      {!items ? <Loading label="Chargement des scénarios…" /> : items.length === 0 ? (
        <div className="card">
          <EmptyState
            icon={<FlaskConical size={30} />}
            title="Aucun scénario dans cette catégorie"
            description="Choisissez une autre catégorie ou réinitialisez le filtre."
            action={<button className="btn sm" onClick={() => setCategory('')}>Toutes les catégories</button>}
          />
        </div>
      ) : (
        <div className="grid auto">
          {items.map((scenario) => {
            const tone = CATEGORY_TONE[scenario.category] ?? 'info'
            return (
              <Link key={scenario.id} to={`/lab/${encodeURIComponent(scenario.slug)}`} className="card scenario-card" style={{ color: 'inherit' }}>
                <div className="row wrap" style={{ gap: 5 }}>
                  <span className={`badge ${tone}`}>{CATEGORY_LABEL[scenario.category] ?? scenario.category}</span>
                  <span className="tag">{LEVEL_LABEL[scenario.level] ?? scenario.level}</span>
                  <ArrowUpRight size={14} style={{ marginLeft: 'auto', color: 'var(--faint)' }} />
                </div>
                <h3>{scenario.title}</h3>
                <p className="clamp-3">{scenario.description}</p>
                <div className="row between" style={{ marginTop: 'auto', paddingTop: 4 }}>
                  <span className="tiny faint">Objectif pédagogique</span>
                  <span className="tiny" style={{ color: 'var(--accent)' }}>Ouvrir le scénario</span>
                </div>
              </Link>
            )
          })}
        </div>
      )}
    </>
  )
}
