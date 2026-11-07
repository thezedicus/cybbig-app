import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import {
  AlertTriangle, ArrowLeft, CheckCircle2, Copy, FlaskConical, Play,
  ShieldCheck, Sparkles,
} from 'lucide-react'
import { api } from '../api'
import {
  AlertBox, CodeBlock, EmptyState, Loading, PageHeader, SeverityBadge, useToast,
} from '../components/ui'
import type { LabScenario, Severity } from '../types'

interface ValidationHit {
  line: number
  rule_id: string
  title: string
  severity: string
  evidence: string
}

interface ValidationResult {
  hits: ValidationHit[]
  count: number
  note: string
}

const CATEGORY_LABEL: Record<string, string> = {
  PHP: 'PHP', API: 'API', Finance: 'Finance', 'E-commerce': 'E-commerce',
}

export default function LabDetail() {
  const { slug = '' } = useParams()
  const [scenario, setScenario] = useState<LabScenario | null>(null)
  const [error, setError] = useState('')
  const [code, setCode] = useState('')
  const [language, setLanguage] = useState('php')
  const [result, setResult] = useState<ValidationResult | null>(null)
  const [validating, setValidating] = useState(false)
  const [validationError, setValidationError] = useState('')
  const toast = useToast()

  useEffect(() => {
    setScenario(null); setResult(null); setError('')
    api.get<LabScenario>(`/api/lab/scenarios/${encodeURIComponent(slug)}`)
      .then((data) => {
        setScenario(data)
        setCode(data.vulnerable_code)
        setLanguage(inferLanguage(data.vulnerable_code, data.category))
      })
      .catch((e) => setError((e as Error).message))
  }, [slug])

  const copy = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text)
      toast.push('Extrait copié.', 'success')
    } catch {
      toast.push('Copie impossible dans ce contexte.', 'error')
    }
  }

  const validate = async () => {
    if (!code.trim()) return
    setValidating(true); setValidationError('')
    try {
      const data = await api.post<ValidationResult>('/api/lab/validate', { code, language })
      setResult(data)
    } catch (err) {
      setValidationError((err as Error).message)
    } finally {
      setValidating(false)
    }
  }

  if (error) {
    return (
      <>
        <PageHeader title="Scénario introuvable" actions={<Link to="/lab" className="btn sm"><ArrowLeft size={13} /> Laboratoire</Link>} />
        <AlertBox kind="error">{error}</AlertBox>
      </>
    )
  }
  if (!scenario) return <Loading label="Chargement du scénario…" />

  return (
    <>
      <PageHeader
        title={scenario.title}
        description={scenario.description}
        actions={<Link to="/lab" className="btn sm"><ArrowLeft size={13} /> Tous les scénarios</Link>}
      />

      <div className="detail-meta mb-2">
        <span className="badge high">{CATEGORY_LABEL[scenario.category] ?? scenario.category}</span>
        <span className="tag">Niveau {scenario.level}</span>
        <span className="tag"><ShieldCheck size={11} /> Pédagogique</span>
      </div>

      <AlertBox kind="info">
        <b>Périmètre du laboratoire.</b> Les extraits sont inertes et ne sont jamais exécutés par Cybbig.
        Pour les tester, utilisez uniquement une machine virtuelle isolée, des données fictives et un serveur local.
      </AlertBox>

      <div className="grid cols-2 mt-3">
        <div className="card">
          <div className="card-header">
            <div><h2>Objectif pédagogique</h2><div className="sub">Ce que le scénario cherche à démontrer</div></div>
            <FlaskConical size={17} style={{ marginLeft: 'auto', color: 'var(--accent)' }} />
          </div>
          <div className="card-pad">
            <p className="small" style={{ color: 'var(--text-soft)', margin: 0, whiteSpace: 'pre-wrap' }}>{scenario.objective}</p>
          </div>
        </div>
        <div className="card">
          <div className="card-header">
            <div><h2>Détection</h2><div className="sub">Motifs à rechercher lors d’une revue</div></div>
            <Sparkles size={17} style={{ marginLeft: 'auto', color: 'var(--medium)' }} />
          </div>
          <div className="card-pad">
            <p className="small" style={{ color: 'var(--text-soft)', margin: 0, whiteSpace: 'pre-wrap' }}>{scenario.detection}</p>
          </div>
        </div>
      </div>

      <div className="two-col mt-3">
        <div className="card">
          <div className="card-header">
            <div><h2>Code vulnérable</h2><div className="sub">Extrait inerte, fourni à titre pédagogique</div></div>
            <button className="btn ghost sm" onClick={() => copy(scenario.vulnerable_code)}><Copy size={12} /> Copier</button>
          </div>
          <div className="card-pad"><CodeBlock code={scenario.vulnerable_code} label="À ne jamais déployer" /></div>
        </div>
        <div className="card">
          <div className="card-header">
            <div><h2>Correction</h2><div className="sub">Approche défensive de référence</div></div>
            <button className="btn ghost sm" onClick={() => copy(scenario.secure_code)}><Copy size={12} /> Copier</button>
          </div>
          <div className="card-pad"><CodeBlock code={scenario.secure_code} label="Bonne pratique" /></div>
        </div>
      </div>

      <div className="two-col mt-3">
        <div className="card">
          <div className="card-header">
            <div><h2>Étapes de test</h2><div className="sub">À exécuter dans un environnement isolé</div></div>
          </div>
          <div className="card-pad">
            <p className="small" style={{ color: 'var(--text-soft)', margin: 0, whiteSpace: 'pre-wrap' }}>{scenario.test_steps}</p>
          </div>
        </div>
        <div className="card">
          <div className="card-header"><div><h2>Références</h2><div className="sub">Documentation externe</div></div></div>
          <div className="card-pad">
            {scenario.references?.length ? (
              <ul className="refs">
                {scenario.references.map((ref) => (
                  <li key={ref}><a href={ref} target="_blank" rel="noreferrer noopener">{ref}</a></li>
                ))}
              </ul>
            ) : <div className="small faint">Aucune référence.</div>}
          </div>
        </div>
      </div>

      <div className="card mt-3">
        <div className="card-header">
          <div><h2>Valider un extrait</h2><div className="sub">Analyse par motifs locale, sans exécution</div></div>
          <span className="tag" style={{ marginLeft: 'auto' }}><ShieldCheck size={11} /> statique</span>
        </div>
        <div className="card-pad">
          <div className="row wrap mb-2" style={{ gap: 8 }}>
            <button className="btn sm" onClick={() => { setCode(scenario.vulnerable_code); setResult(null); setLanguage(inferLanguage(scenario.vulnerable_code, scenario.category)) }}>Charger le code vulnérable</button>
            <button className="btn sm" onClick={() => { setCode(scenario.secure_code); setResult(null); setLanguage(inferLanguage(scenario.secure_code, scenario.category)) }}>Charger la correction</button>
            <div className="spacer" />
            <select className="select" style={{ width: 150 }} value={language} onChange={(e) => setLanguage(e.target.value)}>
              <option value="php">PHP</option>
              <option value="javascript">JavaScript</option>
              <option value="text">Autre / texte</option>
            </select>
            <button className="btn primary sm" onClick={validate} disabled={validating || !code.trim()}>
              <Play size={13} /> {validating ? 'Analyse…' : 'Analyser'}
            </button>
          </div>
          <textarea
            className="textarea"
            style={{ minHeight: 210, fontFamily: 'var(--mono)', fontSize: 12.5 }}
            value={code}
            onChange={(e) => setCode(e.target.value)}
            spellCheck={false}
            aria-label="Extrait de code à analyser"
          />
          {validationError && <div className="mt-2"><AlertBox kind="error">{validationError}</AlertBox></div>}

          {result && (
            <div className="mt-3">
              <div className="row between mb-2">
                <div className="row" style={{ gap: 7 }}>
                  {result.count > 0 ? <AlertTriangle size={16} color="var(--high)" /> : <CheckCircle2 size={16} color="var(--green)" />}
                  <b>{result.count} motif(s) détecté(s)</b>
                </div>
                <span className="tiny faint">Analyse indicative</span>
              </div>
              {result.hits.length === 0 ? (
                <EmptyState title="Aucun motif connu" description="L’absence de détection ne garantit pas l’absence de vulnérabilité." />
              ) : (
                <div className="table-wrap">
                  <table className="data">
                    <thead><tr><th>Ligne</th><th>Gravité</th><th>Motif</th><th>Extrait masqué</th></tr></thead>
                    <tbody>
                      {result.hits.map((hit, index) => (
                        <tr key={`${hit.rule_id}-${hit.line}-${index}`}>
                          <td className="mono small">{hit.line}</td>
                          <td><SeverityBadge severity={hit.severity as Severity} /></td>
                          <td><div className="cell-title">{hit.title}</div><div className="cell-sub mono">{hit.rule_id}</div></td>
                          <td><code className="cell-mono">{hit.evidence}</code></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
              <p className="tiny faint mt-2" style={{ marginBottom: 0 }}>{result.note}</p>
            </div>
          )}
        </div>
      </div>
    </>
  )
}

function inferLanguage(code: string, category: string): string {
  if (code.includes('<?php') || (category === 'PHP' && /\$[A-Za-z_]/.test(code))) return 'php'
  if (category === 'API' && /^\s*(openapi|paths|components):/m.test(code)) return 'text'
  if (/\b(function|const|let|var|=>|new Function|document\.)\b/.test(code)) return 'javascript'
  return 'text'
}
