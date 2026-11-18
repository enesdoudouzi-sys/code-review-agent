import { useState } from 'react'
import { CodeInput } from './components/CodeInput'
import { ReviewResult } from './components/ReviewResult'

interface ReviewResponse {
  dateiname: string
  report: string
  status: string
}

export default function App() {
  const [code, setCode] = useState('')
  const [dateiname, setDateiname] = useState('main.py')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<ReviewResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function handleReview() {
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const res = await fetch('/review', {
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

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      {/* Header */}
      <header className="border-b border-gray-800 px-6 py-4 flex items-center gap-3">
        <span className="text-2xl">🤖</span>
        <div>
          <h1 className="text-lg font-bold text-white">Code Review Agent</h1>
          <p className="text-xs text-gray-400">Powered by Claude · Anthropic</p>
        </div>
        <div className="ml-auto flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-green-400"></span>
          <span className="text-xs text-gray-400">API online</span>
        </div>
      </header>

      {/* Main */}
      <main className="max-w-5xl mx-auto px-6 py-8 grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left: Input */}
        <section>
          <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Code eingeben</h2>
          <CodeInput
            code={code}
            dateiname={dateiname}
            loading={loading}
            onChange={setCode}
            onDateinameChange={setDateiname}
            onSubmit={handleReview}
          />
        </section>

        {/* Right: Result */}
        <section>
          <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Review Report</h2>
          {error && (
            <div className="bg-red-900/40 border border-red-700 rounded-lg p-4 text-sm text-red-300">
              ⚠️ {error}
            </div>
          )}
          {loading && (
            <div className="flex flex-col items-center justify-center h-64 text-gray-500 gap-3">
              <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
              <p className="text-sm">Agent analysiert deinen Code...</p>
            </div>
          )}
          {result && !loading && (
            <ReviewResult report={result.report} dateiname={result.dateiname} />
          )}
          {!result && !loading && !error && (
            <div className="flex flex-col items-center justify-center h-64 text-gray-600 gap-2">
              <span className="text-4xl">📋</span>
              <p className="text-sm">Report erscheint hier nach dem Review</p>
            </div>
          )}
        </section>
      </main>
    </div>
  )
}
