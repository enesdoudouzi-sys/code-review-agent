interface Props {
  report: string
  dateiname: string
  steps?: number
}

export function ReviewResult({ report, dateiname, steps = 0 }: Props) {
  const sections = parseReport(report)

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center gap-2 text-sm text-gray-400 border-b border-gray-700 pb-3">
        <span>📄</span>
        <span className="font-mono text-gray-200">{dateiname}</span>
        {steps > 0 && <span className="text-xs text-gray-500">{steps} Schritte</span>}
        <span className="ml-auto text-green-400 font-medium">✓ Review abgeschlossen</span>
      </div>

      {sections.map((section, i) => (
        <div key={i} className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h3 className="text-base font-semibold text-white mb-3">{section.title}</h3>
          <div className="text-sm text-gray-300 leading-relaxed whitespace-pre-wrap">{section.body}</div>
        </div>
      ))}
    </div>
  )
}

function parseReport(report: string) {
  const lines = report.split('\n')
  const sections: { title: string; body: string }[] = []
  let current: { title: string; lines: string[] } | null = null

  for (const line of lines) {
    if (line.startsWith('## ')) {
      if (current) sections.push({ title: current.title, body: current.lines.join('\n').trim() })
      current = { title: line.replace('## ', ''), lines: [] }
    } else if (current) {
      current.lines.push(line)
    }
  }
  if (current) sections.push({ title: current.title, body: current.lines.join('\n').trim() })

  return sections.length > 0 ? sections : [{ title: 'Review', body: report }]
}
