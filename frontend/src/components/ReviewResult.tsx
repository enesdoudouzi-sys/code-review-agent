import { useState } from 'react'

interface Props {
  report: string
  dateiname: string
  mode?: 'review' | 'security'
}

interface Section {
  title: string
  body: string
  icon: string
  color: string
  border: string
}

const SECTION_STYLES: Record<string, { icon: string; color: string; border: string }> = {
  sicherheit:   { icon: '🔒', color: 'text-rose-400',    border: 'border-rose-900/60' },
  security:     { icon: '🔒', color: 'text-rose-400',    border: 'border-rose-900/60' },
  schwachstelle:{ icon: '⚠️', color: 'text-orange-400',  border: 'border-orange-900/60' },
  vulnerability:{ icon: '⚠️', color: 'text-orange-400',  border: 'border-orange-900/60' },
  stil:         { icon: '🎨', color: 'text-sky-400',     border: 'border-sky-900/60' },
  style:        { icon: '🎨', color: 'text-sky-400',     border: 'border-sky-900/60' },
  logik:        { icon: '🔧', color: 'text-amber-400',   border: 'border-amber-900/60' },
  logic:        { icon: '🔧', color: 'text-amber-400',   border: 'border-amber-900/60' },
  zusammenfassung: { icon: '✅', color: 'text-emerald-400', border: 'border-emerald-900/60' },
  summary:      { icon: '✅', color: 'text-emerald-400', border: 'border-emerald-900/60' },
  empfehlung:   { icon: '💡', color: 'text-violet-400',  border: 'border-violet-900/60' },
  performance:  { icon: '⚡', color: 'text-yellow-400',  border: 'border-yellow-900/60' },
}

function getSectionStyle(title: string) {
  const key = Object.keys(SECTION_STYLES).find(k =>
    title.toLowerCase().includes(k)
  )
  return key ? SECTION_STYLES[key] : { icon: '📝', color: 'text-gray-300', border: 'border-[#1e1e30]' }
}

function parseReport(report: string): Section[] {
  const lines = report.split('\n')
  const sections: Section[] = []
  let current: { title: string; lines: string[] } | null = null

  for (const line of lines) {
    if (line.match(/^#{1,3} /)) {
      if (current) {
        const style = getSectionStyle(current.title)
        sections.push({ title: current.title, body: current.lines.join('\n').trim(), ...style })
      }
      current = { title: line.replace(/^#{1,3} /, ''), lines: [] }
    } else if (current) {
      current.lines.push(line)
    }
  }
  if (current) {
    const style = getSectionStyle(current.title)
    sections.push({ title: current.title, body: current.lines.join('\n').trim(), ...style })
  }

  return sections.length > 0 ? sections : [{
    title: 'Analyse',
    body: report,
    icon: '📝',
    color: 'text-gray-300',
    border: 'border-[#1e1e30]',
  }]
}

export function ReviewResult({ report, dateiname, mode = 'review' }: Props) {
  const [copied, setCopied] = useState(false)
  const sections = parseReport(report)

  function copyReport() {
    try {
      navigator.clipboard.writeText(report).then(() => {
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
      }).catch(() => {})
    } catch {}
  }

  return (
    <div className="flex flex-col gap-3">
      {/* Result header */}
      <div className="flex items-center gap-2 px-3 py-2 bg-[#111120] rounded-xl border border-[#1e1e30]">
        <span className="text-xs font-mono text-gray-400 truncate flex-1">{dateiname}</span>
        <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${mode === 'security' ? 'bg-rose-950 text-rose-400' : 'bg-emerald-950 text-emerald-400'}`}>
          {mode === 'security' ? '🛡 Security Scan' : '✓ Review'}
        </span>
        <button
          onClick={copyReport}
          className="text-[10px] text-gray-600 hover:text-gray-300 transition-colors ml-1"
          title="Report kopieren"
        >
          {copied ? '✓ Kopiert' : '⎘ Kopieren'}
        </button>
      </div>

      {/* Sections */}
      <div className="flex flex-col gap-2 max-h-[600px] overflow-y-auto pr-1">
        {sections.map((section, i) => (
          <div
            key={i}
            className={`bg-[#0d0d14] rounded-xl p-4 border ${section.border}`}
          >
            <div className="flex items-center gap-2 mb-2">
              <span className="text-base leading-none">{section.icon}</span>
              <h3 className={`text-sm font-semibold ${section.color}`}>{section.title}</h3>
            </div>
            <div className="text-sm text-gray-400 leading-relaxed whitespace-pre-wrap font-mono text-xs">
              {section.body}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
