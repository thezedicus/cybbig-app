import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import {
  ArrowLeft, Activity, AlertTriangle, Boxes, CalendarClock, CheckCircle2, ClipboardList,
  FileText, FolderOpen, Globe2, KeyRound, Play, ShieldCheck, ShieldX, UserCheck,
} from 'lucide-react'
import { api, formatDate, scanLabel } from '../api'
import { AlertBox, EmptyState, Loading, PageHeader, RiskGauge, SeverityBadge, SeverityBar, StatusPill } from '../components/ui'
import type { Project } from '../types'

export default function ProjectDetail() {
  const { id = '' } = useParams()
  const [project, setProject] = useState<Project | null>(null)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    api.get<Project>(`/api/projects/${id}`)
      .then(setProject)
      .catch((e) => setError((e as Error).message))
  }, [id])

  if (error) return <AlertBox kind="error">{error}</AlertBox>
  if (!project) return <Loading label="Chargement du projet…" />

  const domains = Array.isArray(project.scope_domains) ? project.scope_domains : []
  const confirmed = Boolean(project.authorization_confirmed)

  return (
    <>
      <PageHeader
        title={project.name}
        description={`${project.client || 'Sans client'} · ${project.environment} · niveau d’activité ${project.activity_level}`}
        actions={
          <>
            <button className="btn ghost" onClick={() => navigate('/projects')}><ArrowLeft size={14} /> Projets</button>
            <Link className="btn" to={`/reports?project=${project.id}`}><FileText size={14} /> Rapports</Link>
            <Link className="btn primary" to={`/scans?launch=1&project=${project.id}`}><Play size={14} /> Lancer une analyse</Link>
          </>
        }
      />

      <div className="detail-layout">
        <div className="stack" style={{ gap: 14 }}>
          <div className="card card-pad">
            <div className="row wrap" style={{ gap: 22 }}>
              <RiskGauge value={project.risk_score} size={118} />
              <div style={{ flex: 1, minWidth: 250 }}>
                <div className="row" style={{ gap: 7 }}>
                  {confirmed ? <><CheckCircle2 size={15} color="var(--green)" /><span className="tiny" style={{ color: 'var(--green)', fontWeight: 700 }}>PÉRIMÈTRE CONFIRMÉ</span></>
                    : <><ShieldX size={15} color="var(--critical)" /><span className="tiny" style={{ color: 'var(--critical)', fontWeight: 700 }}>AUTORISATION NON CONFIRMÉE</span></>}
                  <span className="tag" style={{ marginLeft: 'auto' }}>{project.findings_count} résultat(s)</span>
                </div>
                <p className="small muted mt-1" style={{ marginBottom: 8 }}>{project.description || 'Aucune description.'}</p>
                <div className="row wrap" style={{ gap: 14 }}>
                  <span className="row small" style={{ gap: 5 }}><ClipboardList size={13} /> {project.open_findings} ouvert(s)</span>
                  <span className="row small" style={{ gap: 5 }}><Activity size={13} /> {project.scans_count} analyse(s)</span>
                  <span className="row small" style={{ gap: 5 }}><CalendarClock size={13} /> {formatDate(project.updated_at)}</span>
                </div>
              </div>
            </div>
            <div className="mt-3"><SeverityBar counts={project.severity} /></div>
          </div>

          <div className="card">
            <div className="card-header"><div><h2>Analyses récentes</h2><div className="sub">10 dernières exécutions</div></div><div className="right"><Link className="btn ghost sm" to={`/scans?project=${project.id}`}>Toutes</Link></div></div>
            {!project.recent_scans?.length ? (
              <EmptyState icon={<Activity size={26} />} title="Aucune analyse" description="Ce projet n’a pas encore été analysé." action={<Link className="btn primary sm" to={`/scans?launch=1&project=${project.id}`}>Lancer la première analyse</Link>} />
            ) : (
              <div className="table-wrap">
                <table className="data">
                  <thead><tr><th>Type</th><th>Cible</th><th>Statut</th><th>Résultats</th><th>Date</th></tr></thead>
                  <tbody>
                    {project.recent_scans.map((s) => (
                      <tr key={s.id} className="clickable" onClick={() => navigate(`/scans/${s.id}`)}>
                        <td><span className="tag">{scanLabel(s.kind)}</span></td>
                        <td className="cell-mono truncate" style={{ maxWidth: 280 }}>{s.target || '—'}</td>
                        <td><StatusPill status={s.status} /></td>
                        <td className="mono">{s.summary?.findings ?? '—'}</td>
                        <td className="tiny faint">{formatDate(s.created_at)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          <div className="card">
            <div className="card-header"><div><h2>Résultats prioritaires</h2><div className="sub">Principaux écarts détectés</div></div><div className="right"><Link className="btn ghost sm" to={`/findings?project=${project.id}`}>Tout voir</Link></div></div>
            {!project.top_findings?.length ? (
              <EmptyState icon={<ShieldCheck size={26} />} title="Aucun résultat" description="Aucun écart n’a été enregistré pour ce projet." />
            ) : (
              <div className="table-wrap">
                <table className="data">
                  <thead><tr><th>Gravité</th><th>Résultat</th><th>Emplacement</th><th>Statut</th></tr></thead>
                  <tbody>
                    {project.top_findings.map((f) => (
                      <tr key={f.id} className="clickable" onClick={() => navigate(`/findings?focus=${f.id}`)}>
                        <td><SeverityBadge severity={f.severity} /></td>
                        <td><div className="cell-title clamp-2">{f.title}</div><div className="cell-sub">{f.category}</div></td>
                        <td className="cell-mono truncate" style={{ maxWidth: 260 }}>{f.file_path || f.url}</td>
                        <td><StatusPill status={f.status} /></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>

        <div className="stack" style={{ gap: 14 }}>
          <div className="card">
            <div className="card-header"><h2>Périmètre autorisé</h2></div>
            <div className="card-pad" style={{ paddingTop: 4 }}>
              <div className="kv-list">
                <div className="kv-item"><span><Globe2 size={12} /> URL de base</span><b>{project.base_url || '—'}</b></div>
                <div className="kv-item"><span><FolderOpen size={12} /> Dossier</span><b>{project.path || '—'}</b></div>
                <div className="kv-item"><span><Boxes size={12} /> Environnement</span><b>{project.environment}</b></div>
                <div className="kv-item"><span><ShieldCheck size={12} /> Niveau</span><b>{project.activity_level} — autorisé</b></div>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="card-header"><h2>Autorisation</h2></div>
            <div className="card-pad" style={{ paddingTop: 4 }}>
              <div className="kv-list">
                <div className="kv-item"><span><KeyRound size={12} /> Référence</span><b>{project.authorization_ref || 'Non renseignée'}</b></div>
                <div className="kv-item"><span><UserCheck size={12} /> Autorisé par</span><b>{project.authorized_by || '—'}</b></div>
                <div className="kv-item"><span><CalendarClock size={12} /> Confirmé le</span><b>{project.authorized_at ? formatDate(project.authorized_at) : '—'}</b></div>
              </div>
              {!confirmed && <div className="mt-2"><div className="alert-banner error"><AlertTriangle size={15} /><div>Les scans seront refusés tant que l’autorisation n’est pas confirmée.</div></div></div>}
            </div>
          </div>

          <div className="card">
            <div className="card-header"><h2>Domaines</h2><div className="right"><span className="tag">{domains.length}</span></div></div>
            <div className="card-pad" style={{ paddingTop: 10 }}>
              {domains.length === 0 ? <span className="small faint">Aucun domaine autorisé pour les cibles distantes.</span> : (
                <div className="row wrap">{domains.map((d) => <span key={d} className="tag">{d}</span>)}</div>
              )}
              <div className="small faint mt-2">Les cibles locales (localhost, IP privée) sont autorisées dans le laboratoire.</div>
            </div>
          </div>

          <div className="card card-pad">
            <div className="row" style={{ gap: 8 }}><ShieldCheck size={15} color="var(--accent)" /><b className="small">Analyse passive uniquement</b></div>
            <p className="tiny faint mt-1" style={{ marginBottom: 0 }}>
              Aucune charge d’exploitation, aucun contournement d’authentification. Les fichiers exposés sont détectés par GET tronqué, sans collecte de contenu.
            </p>
          </div>
        </div>
      </div>
    </>
  )
}
