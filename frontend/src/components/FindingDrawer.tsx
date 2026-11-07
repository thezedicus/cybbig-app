import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Bot, CheckCircle2, ExternalLink, ShieldAlert } from 'lucide-react'
import { api, engineLabel, formatDate, statusLabel } from '../api'
import type { Finding, FindingStatus } from '../types'
import AiPanel from './AiPanel'
import { Drawer, SeverityBadge, useToast } from './ui'

const STATUSES: FindingStatus[] = ['open', 'acknowledged', 'fixed', 'accepted_risk', 'false_positive']

export default function FindingDrawer({ findingId, onClose, onUpdated, initial }: {
  findingId: string | null
  onClose: () => void
  onUpdated?: (finding: Finding) => void
  initial?: Finding | null
}) {
  const [finding, setFinding] = useState<Finding | null>(initial ?? null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const toast = useToast()

  useEffect(() => {
    if (!findingId) { setFinding(null); return }
    setLoading(true); setError('')
    api.get<Finding>(`/api/findings/${findingId}`)
      .then((data) => setFinding(data))
      .catch((e) => setError((e as Error).message))
      .finally(() => setLoading(false))
  }, [findingId])

  const changeStatus = async (status: FindingStatus) => {
    if (!finding) return
    try {
      const updated = await api.patch<Finding>(`/api/findings/${finding.id}`, { status })
      setFinding(updated)
      onUpdated?.(updated)
      toast.push(`Statut mis à jour : ${statusLabel(status)}.`, 'success')
    } catch (err) {
      toast.push((err as Error).message, 'error')
    }
  }

  return (
    <Drawer
      open={Boolean(findingId)}
      onClose={onClose}
      title={finding?.title ?? 'Résultat'}
      subtitle={finding ? `${engineLabel(finding.engine)} · ${finding.rule_id} · ${formatDate(finding.created_at)}` : undefined}
    >
      {loading && !finding ? <div className="loading-block"><div className="spinner" /></div> : error ? <div className="alert-banner error">{error}</div> : finding ? (
        <>
          <div className="detail-meta">
            <SeverityBadge severity={finding.severity} />
            <span className="pill">{finding.category || 'Sans catégorie'}</span>
            <span className="pill">Confiance : {finding.confidence}</span>
            <span className="pill">{statusLabel(finding.status)}</span>
          </div>

          {finding.file_path && <div className="small"><span className="faint">Fichier : </span><span className="mono">{finding.file_path}{finding.line_start ? `:${finding.line_start}` : ''}</span></div>}
          {finding.url && <div className="small"><span className="faint">URL : </span><span className="mono" style={{ wordBreak: 'break-all' }}>{finding.url}</span></div>}

          <div className="detail-section"><h3>Description</h3><p>{finding.description || '—'}</p></div>
          {finding.evidence && <div className="detail-section"><h3>Preuve</h3><pre className="evidence">{finding.evidence}</pre></div>}
          <div className="detail-section"><h3>Remédiation</h3><p>{finding.remediation || '—'}</p></div>
          <AiPanel key={finding.id} task="finding_triage" params={{ finding_id: finding.id }} initialText={finding.ai_notes || undefined} title={finding.ai_verdict ? `Triage IA : ${finding.ai_verdict}` : "Triage IA"} label="Vrai ou faux positif ?" compact />

          <div className="row wrap" style={{ gap: 6 }}>
            {finding.cwe && <span className="tag">{finding.cwe}</span>}
            {finding.owasp && <span className="tag">{finding.owasp}</span>}
            <span className="tag">risque {finding.risk_score}</span>
          </div>

          {finding.references?.length > 0 && (
            <div className="detail-section">
              <h3>Références</h3>
              <ul className="refs">
                {finding.references.map((ref) => <li key={ref}><a href={ref} target="_blank" rel="noreferrer">{ref} <ExternalLink size={10} /></a></li>)}
              </ul>
            </div>
          )}

          <div className="detail-section">
            <h3>Cycle de traitement</h3>
            <div className="row wrap">
              {STATUSES.map((status) => (
                <button key={status} className={`btn sm ${finding.status === status ? 'primary' : ''}`} onClick={() => changeStatus(status)}>
                  {finding.status === status && <CheckCircle2 size={12} />} {statusLabel(status)}
                </button>
              ))}
            </div>
          </div>

          <div className="row between mt-2">
            <div className="row" style={{ gap: 6 }}>
              <Link className="btn sm" to={`/scans/${finding.scan_id}`}>Voir l’analyse <ExternalLink size={12} /></Link>
              <Link className="btn primary sm" to={`/assistant?finding=${encodeURIComponent(finding.id)}`}><Bot size={12} /> Demander à l’assistant</Link>
            </div>
            <span className="tiny faint"><ShieldAlert size={11} /> Résultat heuristique à valider</span>
          </div>
        </>
      ) : null}
    </Drawer>
  )
}
