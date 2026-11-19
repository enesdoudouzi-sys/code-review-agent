interface Props {
  code: string
  dateiname: string
  loading: boolean
  mode?: 'review' | 'security'
  onChange: (code: string) => void
  onDateinameChange: (name: string) => void
  onSubmit: () => void
}

function getLanguageLabel(filename: string): string {
  const ext = filename.split('.').pop()?.toLowerCase() ?? ''
  const map: Record<string, string> = {
    py: 'Python', ts: 'TypeScript', tsx: 'TSX', js: 'JavaScript',
    jsx: 'JSX', java: 'Java', cs: 'C#', cpp: 'C++', c: 'C',
    go: 'Go', rs: 'Rust', rb: 'Ruby', php: 'PHP', sh: 'Shell',
    sql: 'SQL', html: 'HTML', css: 'CSS',
  }
  return map[ext] ?? 'Code'
}

export function CodeInput({ code, dateiname, loading, mode = 'review', onChange, onDateinameChange, onSubmit }: Props) {
  const lang = getLanguageLabel(dateiname)
  const lineCount = code ? code.split('\n').length : 0
  const isSecurityMode = mode === 'security'
  const buttonColor = isSecurityMode
    ? 'bg-rose-600 hover:bg-rose-500 shadow-rose-900/40'
    : 'bg-violet-600 hover:bg-violet-500 shadow-violet-900/40'

  return (
    <div className="flex flex-col gap-0 rounded-xl border border-[#1e1e30] overflow-hidden bg-[#0d0d14]">
      {/* Editor top bar */}
      <div className="flex items-center gap-2 px-3 py-2 bg-[#111120] border-b border-[#1e1e30]">
        <div className="flex gap-1.5">
          <div className="w-2.5 h-2.5 rounded-full bg-[#ff5f57]"></div>
          <div className="w-2.5 h-2.5 rounded-full bg-[#febc2e]"></div>
          <div className="w-2.5 h-2.5 rounded-full bg-[#28c840]"></div>
        </div>
        <input
          type="text"
          value={dateiname}
          onChange={e => onDateinameChange(e.target.value)}
          className="flex-1 bg-transparent text-xs font-mono text-gray-300 focus:outline-none placeholder-gray-700 ml-2"
          placeholder="dateiname.py"
        />
        <span className="text-[10px] text-gray-600 bg-[#0d0d14] px-2 py-0.5 rounded font-mono">
          {lang}
        </span>
      </div>

      {/* Code textarea */}
      <textarea
        value={code}
        onChange={e => onChange(e.target.value)}
        className="w-full h-72 bg-[#0d0d14] px-4 py-3 text-sm font-mono text-emerald-300 focus:outline-none transition-colors resize-none placeholder-gray-700 border-0"
        placeholder={isSecurityMode
          ? '# Füge den zu prüfenden Code hier ein...\n# Der KI-Agent scannt auf Sicherheitslücken'
          : '# Füge deinen Code hier ein...\n# z.B. eine Funktion oder Klasse'}
        spellCheck={false}
      />

      {/* Editor bottom bar */}
      <div className="flex items-center gap-3 px-3 py-2 bg-[#111120] border-t border-[#1e1e30]">
        <span className="text-[10px] text-gray-600 font-mono">
          {lineCount > 0 ? `${lineCount} Zeilen` : '0 Zeilen'}
        </span>
        <span className="text-[10px] text-gray-700">·</span>
        <span className="text-[10px] text-gray-600 font-mono">
          {code.length > 0 ? `${code.length} Zeichen` : '0 Zeichen'}
        </span>
        <button
          onClick={onSubmit}
          disabled={loading || !code.trim()}
          className={`ml-auto px-4 py-1.5 rounded-lg text-xs font-semibold text-white transition-all shadow-lg disabled:opacity-30 disabled:cursor-not-allowed ${buttonColor}`}
        >
          {loading
            ? '⏳ Analysiere…'
            : isSecurityMode
              ? '🛡 Security Scan'
              : '🔍 Code reviewen'}
        </button>
      </div>
    </div>
  )
}
