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
  bg: string
}

interface SeverityCounts {
  kritisch: number
  hoch: number
  mittel: number
  niedrig: number
}

const SECTION_STYLES: Record<string, { icon: string; color: string; border: string; bg: string }> = {
  kritisch:     { icon: '🚨', color: 'text-red-400',     border: 'border-red-900/70',     bg: 'bg-red-950/20' },
  critical:     { icon: '🚨', color: 'text-red-400',     border: 'border-red-900/70',     bg: 'bg-red-950/20' },
  sicherheit:   { icon: '🔒', color: 'text-rose-400',    border: 'border-rose-900/60',    bg: 'bg-rose-950/15' },
  security:     { icon: '🔒', color: 'text-rose-400',    border: 'border-rose-900/60',    bg: 'bg-rose-950/15' },
  schwachstelle:{ icon: '⚠️', color: 'text-orange-400',  border: 'border-orange-900/60',  bg: 'bg-orange-950/15' },
  vulnerability:{ icon: '⚠️', color: 'text-orange-400',  border: 'border-orange-900/60',  bg: 'bg-orange-950/15' },
  mittler:      { icon: '⚠️', color: 'text-orange-400',  border: 'border-orange-900/60',  bg: 'bg-orange-950/15' },
  stil:         { icon: '🎨', color: 'text-sky-400',     border: 'border-sky-900/60',     bg: 'bg-sky-950/15' },
  style:        { icon: '🎨', color: 'text-sky-400',     border: 'border-sky-900/60',     bg: 'bg-sky-950/15' },
  logik:        { icon: '🔧', color: 'text-amber-400',   border: 'border-amber-900/60',   bg: 'bg-amber-950/15' },
  logic:        { icon: '🔧', color: 'text-amber-400',   border: 'border-amber-900/60',   bg: 'bg-amber-950/15' },
  zusammenfassung: { icon: '✅', color: 'text-emerald-400', border: 'border-emerald-900/60', bg: 'bg-emerald-950/15' },
  summary:      { icon: '✅', color: 'text-emerald-400', border: 'border-emerald-900/60', bg: 'bg-emerald-950/15' },
  positiv:      { icon: '✅', color: 'text-emerald-400', border: 'border-emerald-900/60', bg: 'bg-emerald-950/15' },
  empfehlung:   { icon: '💡', color: 'text-violet-400',  border: 'border-violet-900/60',  bg: 'bg-violet-950/15' },
  performance:  { icon: '⚡', color: 'text-yellow-400',  border: 'border-yellow-900/60',  bg: 'bg-yellow-950/15' },
}

function getSectionStyle(title: string) {
  const key = Object.keys(SECTION_STYLES).find(k => title.toLowerCase().includes(k))
  return key ? SECTION_STYLES[key] : { icon: '📝', color: 'text-gray-300', border: 'border-[#1e1e30]', bg: 'bg-[#0d0d14]' }
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
    title: 'Analyse', body: report,
    icon: '📝', color: 'text-gray-300', border: 'border-[#1e1e30]', bg: 'bg-[#0d0d14]',
  }]
}

function countSeverities(report: string): SeverityCounts {
  const text = report.toLowerCase()
  const count = (terms: string[]) =>
    terms.reduce((n, t) => n + (text.split(t).length - 1), 0)
  return {
    kritisch: count(['kritisch', 'critical', 'rce', 'remote code execution']),
    hoch:     count(['hoch', 'high', 'sql injection', 'command injection', 'injection']),
    mittel:   count(['mittel', 'medium', 'path traversal', 'xss', 'csrf']),
    niedrig:  count(['niedrig', 'low', 'info', 'hinweis']),
  }
}

function exportReport(report: string, dateiname: string) {
  const content = `Security Report – ${dateiname}\nErstellt: ${new Date().toLocaleString('de-DE')}\n${'='.repeat(60)}\n\n${report}`
  const blob = new Blob([content], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `security-report-${dateiname.replace(/[^a-z0-9]/gi, '-')}.txt`
  a.click()
  URL.revokeObjectURL(url)
}

export function ReviewResult({ report, dateiname, mode = 'review' }: Props) {
  const [copied, setCopied] = useState(false)
  const sections = parseReport(report)
  const severities = mode === 'security' ? countSeverities(report) : null

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
        <button onClick={copyReport} className="text-[10px] text-gray-600 hover:text-gray-300 transition-colors">
          {copied ? '✓' : '⎘'}
        </button>
        {mode === 'security' && (
          <button onClick={() => exportReport(report, dateiname)} className="text-[10px] text-gray-600 hover:text-violet-400 transition-colors" title="Als .txt exportieren">
            ↓ Export
          </button>
        )}
      </div>

      {/* Severity bar — only in security mode */}
      {mode === 'security' && severities && (
        <div className="grid grid-cols-4 gap-2">
          {[
            { label: 'Kritisch', count: severities.kritisch, bg: 'bg-red-950/50',    text: 'text-red-400',    border: 'border-red-900/60' },
            { label: 'Hoch',     count: severities.hoch,     bg: 'bg-orange-950/50', text: 'text-orange-400', border: 'border-orange-900/60' },
            { label: 'Mittel',   count: severities.mittel,   bg: 'bg-yellow-950/50', text: 'text-yellow-400', border: 'border-yellow-900/60' },
            { label: 'Niedrig',  count: severities.niedrig,  bg: 'bg-sky-950/50',    text: 'text-sky-400',    border: 'border-sky-900/60' },
          ].map(({ label, count, bg, text, border }) => (
            <div key={label} className={`${bg} border ${border} rounded-lg px-3 py-2 text-center`}>
              <div className={`text-lg font-bold ${text}`}>{count}</div>
              <div className="text-[10px] text-gray-500">{label}</div>
            </div>
          ))}
        </div>
      )}

      {/* Sections */}
      <div className="flex flex-col gap-2 max-h-[520px] overflow-y-auto pr-1">
        {sections.map((section, i) => (
          <div key={i} className={`${section.bg} rounded-xl p-4 border ${section.border}`}>
            <div className="flex items-center gap-2 mb-2">
              <span className="text-base leading-none">{section.icon}</span>
              <h3 className={`text-sm font-semibold ${section.color}`}>{section.title}</h3>
            </div>
            <div className="text-xs text-gray-400 leading-relaxed whitespace-pre-wrap font-mono">
              {section.body}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
