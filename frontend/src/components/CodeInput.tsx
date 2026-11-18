interface Props {
  code: string
  dateiname: string
  loading: boolean
  onChange: (code: string) => void
  onDateinameChange: (name: string) => void
  onSubmit: () => void
}

export function CodeInput({ code, dateiname, loading, onChange, onDateinameChange, onSubmit }: Props) {
  return (
    <div className="flex flex-col gap-4">
      <div className="flex gap-3 items-center">
        <label className="text-sm font-medium text-gray-300 whitespace-nowrap">Dateiname</label>
        <input
          type="text"
          value={dateiname}
          onChange={e => onDateinameChange(e.target.value)}
          className="flex-1 bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-sm text-gray-100 focus:outline-none focus:border-indigo-500 transition-colors"
          placeholder="main.py"
        />
      </div>

      <textarea
        value={code}
        onChange={e => onChange(e.target.value)}
        className="w-full h-72 bg-gray-900 border border-gray-700 rounded-lg p-4 text-sm font-mono text-green-300 focus:outline-none focus:border-indigo-500 transition-colors resize-none placeholder-gray-600"
        placeholder="# Füge deinen Code hier ein..."
        spellCheck={false}
      />

      <button
        onClick={onSubmit}
        disabled={loading || !code.trim()}
        className="w-full py-3 rounded-lg font-semibold text-white bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
      >
        {loading ? '⏳ Analysiere...' : '🔍 Code reviewen'}
      </button>
    </div>
  )
}
