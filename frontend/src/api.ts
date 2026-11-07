export class ApiError extends Error {
  status: number
  detail: string

  constructor(status: number, detail: string) {
    super(detail)
    this.status = status
    this.detail = detail
  }
}

type RequestOptions = {
  method?: string
  body?: unknown
  headers?: Record<string, string>
  signal?: AbortSignal
}

const API_BASE = (import.meta.env.VITE_API_BASE as string | undefined) ?? ''

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const init: RequestInit = {
    method: options.method ?? 'GET',
    headers: { Accept: 'application/json', ...(options.headers ?? {}) },
    signal: options.signal,
  }
  if (options.body instanceof FormData) {
    init.body = options.body
  } else if (options.body !== undefined) {
    init.headers = { ...init.headers, 'Content-Type': 'application/json' }
    init.body = JSON.stringify(options.body)
  }
  let response: Response
  try {
    response = await fetch(`${API_BASE}${path}`, init)
  } catch (error) {
    throw new ApiError(0, `Backend injoignable. Vérifiez que le service Cybbig est démarré. (${(error as Error).message})`)
  }
  const contentType = response.headers.get('content-type') ?? ''
  const payload = contentType.includes('application/json') ? await response.json() : await response.text()
  if (!response.ok) {
    const detail = typeof payload === 'object' && payload && 'detail' in payload
      ? String((payload as { detail: unknown }).detail)
      : String(payload || response.statusText)
    throw new ApiError(response.status, detail)
  }
  return payload as T
}

export const api = {
  get: <T>(path: string, signal?: AbortSignal) => request<T>(path, { signal }),
  post: <T>(path: string, body?: unknown) => request<T>(path, { method: 'POST', body }),
  put: <T>(path: string, body?: unknown) => request<T>(path, { method: 'PUT', body }),
  patch: <T>(path: string, body?: unknown) => request<T>(path, { method: 'PATCH', body }),
  del: <T>(path: string) => request<T>(path, { method: 'DELETE' }),
  upload: <T>(path: string, file: File, fields: Record<string, string> = {}) => {
    const form = new FormData()
    form.append('file', file)
    for (const [key, value] of Object.entries(fields)) form.append(key, value)
    return request<T>(path, { method: 'POST', body: form })
  },
}

// Lit une réponse NDJSON (une ligne JSON par événement) au fil de l'eau.
export async function streamNdjson<T>(
  path: string, body: unknown, onEvent: (event: T) => void, signal?: AbortSignal, headers: Record<string, string> = {},
): Promise<void> {
  let response: Response
  try {
    response = await fetch(`${API_BASE}${path}`, {
      method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/x-ndjson', ...headers },
      body: JSON.stringify(body), signal,
    })
  } catch (error) {
    if ((error as Error).name === 'AbortError') throw error
    throw new ApiError(0, `Backend injoignable. (${(error as Error).message})`)
  }
  if (!response.ok || !response.body) {
    const text = await response.text()
    let detail = text || response.statusText
    try { detail = String(JSON.parse(text).detail ?? detail) } catch { /* texte brut */ }
    throw new ApiError(response.status, detail)
  }
  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  for (;;) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() ?? ''
    for (const line of lines) if (line.trim()) onEvent(JSON.parse(line) as T)
  }
  if (buffer.trim()) onEvent(JSON.parse(buffer) as T)
}

export function adminApi(token: string) {
  const headers = { 'X-Admin-Token': token }
  return {
    get: <T>(path: string) => request<T>(path, { headers }),
    post: <T>(path: string, body?: unknown) => request<T>(path, { method: 'POST', body, headers }),
    put: <T>(path: string, body?: unknown) => request<T>(path, { method: 'PUT', body, headers }),
    del: <T>(path: string) => request<T>(path, { method: 'DELETE', headers }),
    download: async (path: string, filename: string) => {
      const response = await fetch(`${API_BASE}${path}`, { headers })
      if (!response.ok) throw new ApiError(response.status, response.statusText)
      const url = URL.createObjectURL(await response.blob())
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      link.click()
      URL.revokeObjectURL(url)
    },
  }
}

export function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} o`
  const units = ['Ko', 'Mo', 'Go']
  let value = bytes / 1024
  let unit = 0
  while (value >= 1024 && unit < units.length - 1) { value /= 1024; unit += 1 }
  return `${value.toFixed(1)} ${units[unit]}`
}

export function formatDate(value?: string | null, withTime = true): string {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return new Intl.DateTimeFormat('fr-FR', {
    day: '2-digit', month: 'short', year: 'numeric',
    ...(withTime ? { hour: '2-digit', minute: '2-digit' } : {}),
  }).format(date)
}

export function relativeDate(value?: string | null): string {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  const diff = date.getTime() - Date.now()
  const minutes = Math.round(diff / 60000)
  const rtf = new Intl.RelativeTimeFormat('fr-FR', { numeric: 'auto' })
  if (Math.abs(minutes) < 60) return rtf.format(minutes, 'minute')
  const hours = Math.round(minutes / 60)
  if (Math.abs(hours) < 24) return rtf.format(hours, 'hour')
  const days = Math.round(hours / 24)
  if (Math.abs(days) < 30) return rtf.format(days, 'day')
  return formatDate(value, false)
}

export function percent(value: number, total: number): number {
  if (!total) return 0
  return Math.round((value / total) * 100)
}

export function scanLabel(kind: string): string {
  return ({ php: 'PHP', web: 'Web', api: 'API', checkout: 'Checkout', reverse: 'Reverse' } as Record<string, string>)[kind] ?? kind
}

export function engineLabel(engine: string): string {
  return ({ php: 'PHP', web: 'Web', api: 'API', checkout: 'Checkout', reverse: 'Reverse', intel: 'Veille' } as Record<string, string>)[engine] ?? engine
}

export function statusLabel(status: string): string {
  return ({
    queued: 'En attente', running: 'En cours', completed: 'Terminé', failed: 'Échec',
    blocked: 'Bloqué', cancelled: 'Annulé', open: 'Ouvert', acknowledged: 'Pris en compte',
    fixed: 'Corrigé', accepted_risk: 'Risque accepté', false_positive: 'Faux positif',
  } as Record<string, string>)[status] ?? status
}
