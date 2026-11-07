import { Link } from 'react-router-dom'
import { Code2, Database, Palette, RotateCcw, Sparkles, Terminal } from 'lucide-react'
import { ALWAYS_VISIBLE, APPEARANCE_DEFAULTS, applyAppearance, hiddenNav, type Appearance } from '../appearance'

// Pages que le propriétaire peut masquer du menu (les réglages et l'administration restent toujours visibles).
export const NAV_CHOICES: Array<[string, string]> = [
  ['/', 'Tableau de bord'], ['/scans', 'Analyses'], ['/findings', 'Résultats'], ['/income', 'Opportunités'], ['/projects', 'Projets'], ['/intel', 'Threat Intel'],
  ['/knowledge', 'Connaissances'], ['/assistant', 'Assistant IA'], ['/training', 'Entraînement IA'], ['/reports', 'Rapports'],
  ['/automations', 'Automatisations'], ['/lab', 'Laboratoire'], ['/terminal', 'Terminal'], ['/privacy', 'Confidentialité'],
]

const OWNER_LINKS = [
  { tab: 'atelier', label: 'Atelier IA', text: 'Un modèle Ollama propose des modifications du code, vous validez chaque différence.', icon: Sparkles },
  { tab: 'code', label: 'Éditeur de code', text: 'Tout le code du logiciel : sauvegarde avant chaque écriture, retour arrière.', icon: Code2 },
  { tab: 'database', label: 'Base de données', text: 'Requêtes SQL libres, sauvegardes et restauration.', icon: Database },
  { tab: 'terminal', label: 'Terminal', text: 'Commandes PowerShell, cmd ou Python depuis le logiciel.', icon: Terminal },
]

// Cartes « Accès propriétaire » et « Personnalisation » des Paramètres. Les valeurs ui_* passent par le formulaire commun.
export default function AppearanceSettings({ values, setValue }: { values: Record<string, string>; setValue: (key: string, value: string) => void }) {
  const current: Appearance = {
    ui_accent: values.ui_accent || APPEARANCE_DEFAULTS.ui_accent, ui_font_size: values.ui_font_size || APPEARANCE_DEFAULTS.ui_font_size,
    ui_radius: values.ui_radius || APPEARANCE_DEFAULTS.ui_radius, ui_hidden_nav: values.ui_hidden_nav || '', ui_custom_css: values.ui_custom_css || '',
  }
  const change = (key: keyof Appearance, value: string) => { setValue(key, value); applyAppearance({ ...current, [key]: value }) }  // aperçu immédiat
  const hidden = hiddenNav(current)
  const toggle = (path: string) => change('ui_hidden_nav', (hidden.includes(path) ? hidden.filter((p) => p !== path) : [...hidden, path]).join(','))
  const reset = () => { for (const [k, v] of Object.entries(APPEARANCE_DEFAULTS)) setValue(k, v); applyAppearance(APPEARANCE_DEFAULTS) }

  return (
    <>
      <section className="card">
        <div className="card-header">
          <div><h2>Accès propriétaire</h2><div className="sub">Modifier le logiciel lui-même : code, base, terminal, IA</div></div>
        </div>
        <div className="card-pad stack" style={{ gap: 8 }}>
          {OWNER_LINKS.map(({ tab, label, text, icon: Icon }) => (
            <Link key={tab} to={`/admin?tab=${tab}`} className="row" style={{ gap: 10, padding: '8px 10px', borderRadius: 9, border: '1px solid var(--line-soft)', alignItems: 'flex-start' }}>
              <Icon size={16} style={{ marginTop: 2, color: 'var(--accent)', flex: '0 0 auto' }} />
              <span><b className="small">{label}</b><br /><span className="tiny faint">{text}</span></span>
            </Link>
          ))}
          <span className="tiny faint">Connexion propriétaire requise (identifiants modifiables dans Administration &gt; Sécurité). Chaque action est journalisée.</span>
        </div>
      </section>

      <section className="card">
        <div className="card-header">
          <div><h2>Personnalisation</h2><div className="sub">Apparence et menu : l’aperçu est immédiat, « Enregistrer » le conserve</div></div>
          <Palette size={16} style={{ marginLeft: 'auto', color: 'var(--accent)' }} />
        </div>
        <div className="card-pad stack" style={{ gap: 14 }}>
          <div className="form-grid">
            <div className="field"><label htmlFor="ui-accent">Couleur d’accent</label>
              <input id="ui-accent" type="color" className="input" style={{ padding: 2, height: 38 }} value={current.ui_accent} onChange={(e) => change('ui_accent', e.target.value)} /></div>
            <div className="field"><label htmlFor="ui-font">Taille du texte : {current.ui_font_size} px</label>
              <input id="ui-font" type="range" min={12} max={18} value={current.ui_font_size} onChange={(e) => change('ui_font_size', e.target.value)} /></div>
            <div className="field"><label htmlFor="ui-radius">Arrondi des cartes : {current.ui_radius} px</label>
              <input id="ui-radius" type="range" min={2} max={24} value={current.ui_radius} onChange={(e) => change('ui_radius', e.target.value)} /></div>
          </div>
          <div className="field">
            <label>Pages affichées dans le menu</label>
            <div className="row wrap" style={{ gap: 14 }}>
              {NAV_CHOICES.map(([path, label]) => (
                <label key={path} className="checkbox"><input type="checkbox" checked={!hidden.includes(path)} onChange={() => toggle(path)} /><span>{label}</span></label>
              ))}
            </div>
            <span className="hint">Paramètres et Administration ({ALWAYS_VISIBLE.join(', ')}) restent toujours accessibles. Une page masquée reste joignable par son adresse.</span>
          </div>
          <div className="field">
            <label htmlFor="ui-css">CSS personnalisé (avancé)</label>
            <textarea id="ui-css" className="textarea mono" style={{ minHeight: 110 }} value={current.ui_custom_css} onChange={(e) => change('ui_custom_css', e.target.value)}
              placeholder={'.card { border-radius: 4px; }\n.sidebar { width: 220px; }'} />
            <span className="hint">Appliqué à toute l’interface. En cas d’erreur, ajoutez ?safe=1 à l’adresse pour démarrer sans ce CSS, puis videz ce champ.</span>
          </div>
          <div><button type="button" className="btn sm" onClick={reset}><RotateCcw size={13} /> Réinitialiser l’apparence</button></div>
        </div>
      </section>
    </>
  )
}
