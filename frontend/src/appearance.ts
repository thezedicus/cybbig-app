// Personnalisation de l'interface par le propriétaire : couleur, taille du texte, arrondis, menu, CSS libre.
// Les valeurs vivent dans les réglages (ui_*) ; une copie dans localStorage évite le « flash » au chargement.

export interface Appearance {
  ui_accent: string
  ui_font_size: string
  ui_radius: string
  ui_hidden_nav: string
  ui_custom_css: string
}

export const APPEARANCE_DEFAULTS: Appearance = { ui_accent: '#35d6f0', ui_font_size: '14', ui_radius: '14', ui_hidden_nav: '', ui_custom_css: '' }
export const APPEARANCE_KEYS = Object.keys(APPEARANCE_DEFAULTS) as Array<keyof Appearance>
// Ces pages restent toujours accessibles : le propriétaire ne peut pas se verrouiller hors des réglages.
export const ALWAYS_VISIBLE = ['/settings', '/admin']
const CACHE_KEY = 'cybbig.appearance'
const HEX = /^#[0-9a-fA-F]{6}$/

function shade(hex: string, factor: number): string {
  const channel = (i: number) => Math.max(0, Math.min(255, Math.round(parseInt(hex.slice(1 + i * 2, 3 + i * 2), 16) * factor)))
  return `#${[0, 1, 2].map((i) => channel(i).toString(16).padStart(2, '0')).join('')}`
}

export function applyAppearance(values: Partial<Appearance>): void {
  const merged = { ...APPEARANCE_DEFAULTS, ...values }
  const root = document.documentElement
  const accent = HEX.test(merged.ui_accent) ? merged.ui_accent : APPEARANCE_DEFAULTS.ui_accent
  const rgb = [1, 3, 5].map((i) => parseInt(accent.slice(i, i + 2), 16)).join(', ')
  root.style.setProperty('--accent', accent)
  root.style.setProperty('--accent-strong', shade(accent, 0.7))
  root.style.setProperty('--accent-soft', `rgba(${rgb}, 0.12)`)
  const size = Number(merged.ui_font_size)
  document.body.style.fontSize = `${size >= 12 && size <= 20 ? size : 14}px`
  const radius = Number(merged.ui_radius)
  root.style.setProperty('--radius', `${radius >= 2 && radius <= 24 ? radius : 14}px`)
  let style = document.getElementById('cybbig-custom-css') as HTMLStyleElement | null
  if (!style) {
    style = document.createElement('style')
    style.id = 'cybbig-custom-css'
    document.head.appendChild(style)
  }
  // Adresse avec ?safe=1 : démarrage sans CSS personnalisé (secours si une règle rend l'interface inutilisable).
  style.textContent = new URLSearchParams(window.location.search).has('safe') ? '' : merged.ui_custom_css || ''
}

export function readCachedAppearance(): Partial<Appearance> {
  try { return JSON.parse(localStorage.getItem(CACHE_KEY) || '{}') as Partial<Appearance> } catch { return {} }
}

export function cacheAppearance(values: Partial<Appearance>): void {
  try { localStorage.setItem(CACHE_KEY, JSON.stringify(values)) } catch { /* stockage indisponible : sans conséquence */ }
}

export function hiddenNav(values: Partial<Appearance>): string[] {
  return (values.ui_hidden_nav || '').split(',').map((s) => s.trim()).filter((p) => p && !ALWAYS_VISIBLE.includes(p))
}
