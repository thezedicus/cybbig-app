import { useState } from 'react'
import { ArrowRight, CheckCircle2, ShieldCheck } from 'lucide-react'
import logo from '../assets/logo.png'
import { api } from '../api'
import { AlertBox } from '../components/ui'
import type { ConsentStatus } from '../types'

export default function Consent({ status, onAccepted }: { status: ConsentStatus; onAccepted: () => void }) {
  const [accepted, setAccepted] = useState(false)
  const [name, setName] = useState('')
  const [organization, setOrganization] = useState('')
  const [purpose, setPurpose] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const submit = async (event: React.FormEvent) => {
    event.preventDefault()
    if (!accepted) { setError('Vous devez cocher la case pour continuer.'); return }
    setBusy(true); setError('')
    try {
      await api.post('/api/consent', { accepted: true, user_name: name, organization, purpose })
      onAccepted()
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="consent-shell">
      <div className="consent-card">
        <div className="consent-head">
          <img className="brand-logo" src={logo} alt="" style={{ width: 54, height: 54 }} />
          <div>
            <div className="brand-sub">Cybbig · poste local de cybersécurité défensive</div>
            <h1 style={{ fontSize: 23, marginTop: 3 }}>Cadre d’utilisation</h1>
          </div>
          <span className="tag" style={{ marginLeft: 'auto' }}>v{status.version}</span>
        </div>

        <div className="consent-text">{status.text}</div>

        <form className="consent-form" onSubmit={submit}>
          <div className="form-grid">
            <div className="field">
              <label htmlFor="consent-name">Nom (facultatif)</label>
              <input id="consent-name" className="input" value={name} maxLength={200} onChange={(e) => setName(e.target.value)} placeholder="Votre nom" />
            </div>
            <div className="field">
              <label htmlFor="consent-org">Organisation (facultatif)</label>
              <input id="consent-org" className="input" value={organization} maxLength={200} onChange={(e) => setOrganization(e.target.value)} placeholder="Équipe, société, laboratoire" />
            </div>
            <div className="field full">
              <label htmlFor="consent-purpose">Usage prévu (facultatif)</label>
              <input id="consent-purpose" className="input" value={purpose} maxLength={1000} onChange={(e) => setPurpose(e.target.value)} placeholder="Audit de mes propres projets, formation, laboratoire isolé…" />
            </div>
          </div>

          <label className="checkbox mt-3">
            <input type="checkbox" checked={accepted} onChange={(e) => setAccepted(e.target.checked)} />
            <span>J’ai lu et j’accepte le cadre d’utilisation. Je n’auditerai que des systèmes que je possède ou pour lesquels je dispose d’une autorisation écrite.</span>
          </label>

          {error && <div className="mt-2"><AlertBox kind="error">{error}</AlertBox></div>}

          <div className="form-actions" style={{ alignItems: 'center' }}>
            <div className="row tiny faint" style={{ marginRight: 'auto' }}>
              <CheckCircle2 size={13} /> Données conservées localement · aucune télémétrie
            </div>
            <button className="btn primary" type="submit" disabled={busy}>
              {busy ? 'Enregistrement…' : 'Accepter et ouvrir Cybbig'} <ArrowRight size={15} />
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
