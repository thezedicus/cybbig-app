import { api } from './api'

// Lecture vocale automatique des réponses IA (synthèse vocale locale du module Confidentialité).
const KEY = 'cybbig-auto-read'
const listeners = new Set<(on: boolean) => void>()

export function isAutoRead(): boolean {
  try { return localStorage.getItem(KEY) === '1' } catch { return false }
}

export function setAutoRead(on: boolean) {
  try { localStorage.setItem(KEY, on ? '1' : '0') } catch { /* stockage indisponible */ }
  if (!on) stopSpeaking()
  listeners.forEach((listener) => listener(on))
}

export function onAutoReadChange(listener: (on: boolean) => void): () => void {
  listeners.add(listener)
  return () => { listeners.delete(listener) }
}

function plainText(markdown: string): string {
  return markdown
    .replace(/```[\s\S]*?```/g, ' (bloc de code) ')
    .replace(/`([^`]+)`/g, '$1')
    .replace(/[*_#>]+/g, '')
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
    .replace(/\n{2,}/g, '. ')
    .trim()
}

export function speak(markdown: string) {
  const text = plainText(markdown).slice(0, 8000)
  if (text) api.post('/api/privacy/tts/speak', { text }).catch(() => undefined)
}

export function speakIfEnabled(markdown: string) {
  if (isAutoRead()) speak(markdown)
}

export function stopSpeaking() {
  api.post('/api/privacy/tts/stop').catch(() => undefined)
}
