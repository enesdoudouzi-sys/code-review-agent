import { useState } from 'react'
import { CodeInput } from './components/CodeInput'
import { HistoryPanel } from './components/HistoryPanel'
import { ReviewResult } from './components/ReviewResult'

interface ReviewResponse {
  dateiname: string
  report: string
  status: string
}

type Mode = 'review' | 'security'

export default function App() {
  const [mode, setMode] = useState<Mode>('review')
  const [code, setCode] = useState('')
  const [dateiname, setDateiname] = useState('main.py')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<ReviewResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const apiBase = import.meta.env.VITE_API_URL ?? ''

  async function handleSubmit() {
    setLoading(true)
    setError(null)
    setResult(null)
    const endpoint = mode === 'security' ? '/security-scan' : '/review'
    try {
      const res = await fetch(`${apiBase}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, dateiname }),
      })
      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.detail ?? 'Unbekannter Fehler')
      }
      setResult(await res.json())
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Fehler beim Review')
    } finally {
      setLoading(false)
    }
  }

  function switchMode(m: Mode) {
    setMode(m)
    setResult(null)
    setError(null)
  }

  return (
    <div className="min-h-screen bg-[#0d0d14] text-gray-100 flex flex-col">
      {/* Header */}
      <header className="border-b border-[#1e1e30] bg-[#0d0d14]/95 backdrop-blur sticky top-0 z-10 px-6 py-3 flex items-center gap-4">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-600 to-indigo-600 flex items-center justify-center text-xs font-bold shadow-lg shadow-violet-900/40">
            AI
          </div>
          <div>
            <h1 className="text-sm font-bold text-white leading-none">Code Review Agent</h1>
            <p className="text-[10px] text-gray-500 mt-0.5">KI-Agent · Anthropic LLM API</p>
          </div>
        </div>

        {/* Mode tabs */}
        <div className="flex gap-1 ml-6 bg-[#111120] rounded-lg p-1 border border-[#1e1e30]">
          <button
            onClick={() => switchMode('review')}
            className={`px-3 py-1 rounded-md text-xs font-medium transition-all ${
              mode === 'review'
                ? 'bg-violet-600 text-white shadow'
                : 'text-gray-500 hover:text-gray-300'
            }`}
          >
            🔍 Code Review
          </button>
          <button
            onClick={() => switchMode('security')}
            className={`px-3 py-1 rounded-md text-xs font-medium transition-all ${
              mode === 'security'
                ? 'bg-rose-600 text-white shadow'
                : 'text-gray-500 hover:text-gray-300'
            }`}
          >
            🛡 Security Scan
          </button>
        </div>

        <div className="flex items-center gap-6 ml-auto">
          <a
            href={`${apiBase}/docs`}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs text-gray-500 hover:text-violet-400 transition-colors hidden sm:block"
          >
            API Docs ↗
          </a>
          <HistoryPanel apiBase={apiBase} />
          <div className="flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
            <span className="text-xs text-gray-500">API online</span>
          </div>
        </div>
      </header>

      {/* Mode banner */}
      {mode === 'security' && (
        <div className="bg-rose-950/30 border-b border-rose-900/40 px-6 py-2 flex items-center gap-2">
          <span className="text-rose-400 text-xs">🛡</span>
          <p className="text-xs text-rose-300/80">
            Security Scan aktiv — analysiert OWASP Top 10, Injektionen, Path Traversal und weitere Schwachstellen
          </p>
        </div>
      )}
      {mode === 'review' && (
        <div className="bg-gradient-to-r from-violet-950/30 via-indigo-950/20 to-[#0d0d14] border-b border-[#1e1e30] px-6 py-2">
          <p className="text-xs text-gray-500">
            Automatisierte Code-Analyse — erkennt Style-Issues, Logikfehler und Verbesserungspotenzial
          </p>
        </div>
      )}

      {/* Main layout */}
      <main className="flex-1 max-w-7xl mx-auto w-full px-4 py-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Input */}
        <div className="flex flex-col gap-3">
          <div className="flex items-center justify-between">
            <h2 className="text-xs font-semibold text-gray-600 uppercase tracking-widest">Eingabe</h2>
            {code && (
              <button
                onClick={() => { setCode(''); setResult(null); setError(null) }}
                className="text-xs text-gray-700 hover:text-gray-400 transition-colors"
              >
                Leeren
              </button>
            )}
          </div>
          <CodeInput
            code={code}
            dateiname={dateiname}
            loading={loading}
            mode={mode}
            onChange={setCode}
            onDateinameChange={setDateiname}
            onSubmit={handleSubmit}
          />
        </div>

        {/* Right: Result */}
        <div className="flex flex-col gap-3">
          <div className="flex items-center justify-between">
            <h2 className="text-xs font-semibold text-gray-600 uppercase tracking-widest">
              {mode === 'security' ? 'Sicherheitsanalyse' : 'Analyse'}
            </h2>
            {result && (
              <span className="text-xs text-emerald-400 font-medium flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 inline-block"></span>
                Abgeschlossen
              </span>
            )}
          </div>

          {error && (
            <div className="bg-red-950/40 border border-red-800/60 rounded-xl p-4 text-sm text-red-300 flex gap-3 items-start">
              <span className="text-lg leading-none mt-0.5">⚠</span>
              <span>{error}</span>
            </div>
          )}

          {loading && (
            <div className="flex flex-col items-center justify-center h-80 text-gray-600 gap-4">
              <div className="relative">
                <div className={`w-10 h-10 border-2 rounded-full animate-spin ${mode === 'security' ? 'border-rose-700 border-t-rose-400' : 'border-violet-700 border-t-violet-400'}`}></div>
                <div className={`absolute inset-0 flex items-center justify-center`}>
                  <div className={`w-4 h-4 border-2 rounded-full animate-spin [animation-direction:reverse] ${mode === 'security' ? 'border-orange-700 border-t-orange-400' : 'border-indigo-700 border-t-indigo-400'}`}></div>
                </div>
              </div>
              <p className="text-sm text-gray-500">
                {mode === 'security' ? 'Scanne auf Sicherheitslücken…' : 'KI-Agent analysiert deinen Code…'}
              </p>
            </div>
          )}

          {result && !loading && (
            <ReviewResult report={result.report} dateiname={result.dateiname} mode={mode} />
          )}

          {!result && !loading && !error && (
            <div className="flex flex-col items-center justify-center h-80 border border-dashed border-[#1e1e30] rounded-xl text-gray-700 gap-3">
              <div className={`w-12 h-12 rounded-xl flex items-center justify-center text-2xl ${mode === 'security' ? 'bg-rose-950/30' : 'bg-[#111120]'}`}>
                {mode === 'security' ? '🛡' : '🔍'}
              </div>
              <p className="text-sm text-gray-600">
                {mode === 'security' ? 'Security-Report erscheint hier' : 'Review-Report erscheint hier'}
              </p>
            </div>
          )}
        </div>
      </main>

      <footer className="border-t border-[#1e1e30] px-6 py-3 text-center">
        <p className="text-[10px] text-gray-700">
          KI Code Review Agent · FastAPI + React + Anthropic LLM API
        </p>
      </footer>
    </div>
  )
}
