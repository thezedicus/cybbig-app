import { Fragment, useState, type ReactNode } from 'react'
import { Check, Copy } from 'lucide-react'

// Rendu Markdown minimal et sûr (aucun HTML injecté) : titres, listes, citations,
// blocs de code, code en ligne, gras, italique et liens http(s).

function inline(text: string, key = 0): ReactNode[] {
  const out: ReactNode[] = []
  const pattern = /(`[^`]+`)|(\*\*[^*]+\*\*)|(\*[^*\s][^*]*\*|_[^_\s][^_]*_)|(\[[^\]]+\]\(https?:\/\/[^)\s]+\))/g
  let last = 0
  let match: RegExpExecArray | null
  let i = 0
  while ((match = pattern.exec(text))) {
    if (match.index > last) out.push(text.slice(last, match.index))
    const token = match[0]
    const k = `${key}-${i++}`
    if (match[1]) out.push(<code key={k} className="md-code">{token.slice(1, -1)}</code>)
    else if (match[2]) out.push(<strong key={k}>{inline(token.slice(2, -2), i)}</strong>)
    else if (match[3]) out.push(<em key={k}>{inline(token.slice(1, -1), i)}</em>)
    else {
      const [, label, href] = /^\[([^\]]+)\]\(([^)]+)\)$/.exec(token) ?? []
      out.push(<a key={k} href={href} target="_blank" rel="noreferrer noopener">{label}</a>)
    }
    last = match.index + token.length
  }
  if (last < text.length) out.push(text.slice(last))
  return out
}

function CodeFence({ code, lang }: { code: string; lang: string }) {
  const [copied, setCopied] = useState(false)
  const copy = async () => {
    try { await navigator.clipboard.writeText(code); setCopied(true); window.setTimeout(() => setCopied(false), 1500) } catch { /* presse-papiers refusé */ }
  }
  return (
    <div className="md-pre">
      <div className="md-pre-bar">
        <span>{lang || 'code'}</span>
        <button type="button" onClick={copy} title="Copier">{copied ? <Check size={12} /> : <Copy size={12} />}</button>
      </div>
      <pre><code>{code}</code></pre>
    </div>
  )
}

export default function Markdown({ text }: { text: string }) {
  const lines = text.replace(/\r\n/g, '\n').split('\n')
  const blocks: ReactNode[] = []
  let i = 0
  while (i < lines.length) {
    const line = lines[i]
    const fence = /^\s*```\s*([\w+#.-]*)/.exec(line)
    if (fence) {
      const body: string[] = []
      i += 1
      while (i < lines.length && !/^\s*```/.test(lines[i])) { body.push(lines[i]); i += 1 }
      i += 1 // ligne de fermeture (absente pendant le streaming)
      blocks.push(<CodeFence key={blocks.length} code={body.join('\n')} lang={fence[1]} />)
      continue
    }
    const heading = /^\s*(#{1,4})\s+(.*)$/.exec(line)
    if (heading) {
      const level = Math.min(4, heading[1].length + 2)
      const Tag = `h${level}` as 'h3' | 'h4' | 'h5' | 'h6'
      blocks.push(<Tag key={blocks.length} className="md-h">{inline(heading[2])}</Tag>)
      i += 1
      continue
    }
    if (/^\s*([-*+]|\d+[.)])\s+/.test(line)) {
      const ordered = /^\s*\d+[.)]/.test(line)
      const items: string[] = []
      while (i < lines.length && /^\s*([-*+]|\d+[.)])\s+/.test(lines[i])) {
        items.push(lines[i].replace(/^\s*([-*+]|\d+[.)])\s+/, ''))
        i += 1
      }
      const List = ordered ? 'ol' : 'ul'
      blocks.push(<List key={blocks.length} className="md-list">{items.map((item, n) => <li key={n}>{inline(item, n)}</li>)}</List>)
      continue
    }
    if (/^\s*>/.test(line)) {
      const quote: string[] = []
      while (i < lines.length && /^\s*>/.test(lines[i])) { quote.push(lines[i].replace(/^\s*>\s?/, '')); i += 1 }
      blocks.push(<blockquote key={blocks.length} className="md-quote">{inline(quote.join(' '))}</blockquote>)
      continue
    }
    if (!line.trim()) { i += 1; continue }
    const para: string[] = []
    while (i < lines.length && lines[i].trim() && !/^\s*(```|#{1,4}\s|[-*+]\s|\d+[.)]\s|>)/.test(lines[i])) { para.push(lines[i]); i += 1 }
    blocks.push(
      <p key={blocks.length} className="md-p">
        {para.map((p, n) => <Fragment key={n}>{n > 0 && <br />}{inline(p, n)}</Fragment>)}
      </p>,
    )
  }
  return <div className="md">{blocks}</div>
}
