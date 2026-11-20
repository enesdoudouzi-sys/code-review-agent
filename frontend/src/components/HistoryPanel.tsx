import { useEffect, useState } from 'react'

interface HistoryEntry {
  id: number
  dateiname: string
  modus: string
  erstellt: string
  vorschau: string
}

interface Props {
  apiBase: string
  onSelect?: (entry: HistoryEntry) => void
}

export function HistoryPanel({ apiBase, onSelect }: Props) {
  const [entries, setEntries] = useState<HistoryEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [open, setOpen] = useState(false)

  useEffect(() => {
    if (!open) return
    setLoading(true)
    fetch(`${apiBase}/history`)
      .then(r => r.json())
      .then(data => setEntries(Array.isArray(data) ? data : []))
      .catch(() => setEntries([]))
      .finally(() => setLoading(false))
  }, [open, apiBase])

  function formatTime(iso: string) {
    try {
      return new Date(iso).toLocaleString('de-DE', { dateStyle: 'short', timeStyle: 'short' })
    } catch {
      return iso
    }
  }

  return (
    <div className="relative">
      <button
        onClick={() => setOpen(o => !o)}
        className="flex items-center gap-1.5 text-xs text-gray-500 hover:text-gray-300 transition-colors px-2 py-1 rounded-lg hover:bg-[#111120]"
      >
        🗂 Verlauf
        {open && <span className="text-gray-700">▲</span>}
        {!open && <span className="text-gray-700">▼</span>}
      </button>

      {open && (
        <div className="absolute right-0 top-8 w-80 bg-[#0d0d14] border border-[#1e1e30] rounded-xl shadow-2xl z-20 overflow-hidden">
          <div className="px-3 py-2 bg-[#111120] border-b border-[#1e1e30] flex items-center justify-between">
            <span className="text-xs font-semibold text-gray-400">Letzte Analysen</span>
            <button onClick={() => setOpen(false)} className="text-gray-600 hover:text-gray-300 text-xs">✕</button>
          </div>

          {loading && (
            <div className="p-4 text-center text-xs text-gray-600">Lade…</div>
          )}

          {!loading && entries.length === 0 && (
            <div className="p-4 text-center text-xs text-gray-600">Noch keine Analysen gespeichert.</div>
          )}

          {!loading && entries.length > 0 && (
            <div className="max-h-72 overflow-y-auto">
              {entries.map(e => (
                <button
                  key={e.id}
                  onClick={() => { onSelect?.(e); setOpen(false) }}
                  className="w-full text-left px-3 py-2.5 border-b border-[#1e1e30] last:border-0 hover:bg-[#111120] transition-colors"
                >
                  <div className="flex items-center gap-2 mb-0.5">
                    <span className={`text-[10px] px-1.5 py-0.5 rounded font-medium ${e.modus === 'security' ? 'bg-rose-950 text-rose-400' : 'bg-violet-950 text-violet-400'}`}>
                      {e.modus === 'security' ? '🛡' : '🔍'} {e.modus}
                    </span>
                    <span className="text-[10px] text-gray-600 font-mono ml-auto">{formatTime(e.erstellt)}</span>
                  </div>
                  <div className="text-xs font-mono text-gray-300 truncate">{e.dateiname}</div>
                  <div className="text-[10px] text-gray-600 truncate mt-0.5">{e.vorschau}</div>
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
