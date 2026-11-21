import { useState } from 'react'
import { CodeInput } from './components/CodeInput'
import { ReviewResult } from './components/ReviewResult'

interface StreamEvent {
  type: 'start' | 'thinking' | 'tool_call' | 'tool_result' | 'report' | 'done' | 'error'
  name?: string
  input?: Record<string, unknown>
  result?: Record<string, unknown>
  content?: string
  iteration?: number
  message?: string
  dateiname?: string
}

interface AgentStep {
  type: 'thinking' | 'tool_call' | 'tool_result'
  label: string
  detail?: string
}

const API_BASE = import.meta.env.VITE_API_URL ? `https://${import.meta.env.VITE_API_URL}` : ''

const TOOL_LABELS: Record<string, string> = {
  code_analysieren: 'Code analysieren',
  muster_suchen: 'Muster suchen',
  komplexitaet_messen: 'Komplexität messen',
  abhaengigkeiten_pruefen: 'Abhängigkeiten prüfen',
  testabdeckung_pruefen: 'Testabdeckung prüfen',
}

export default function App() {
  const [code, setCode] = useState('')
  const [dateiname, setDateiname] = useState('main.py')
  const [loading, setLoading] = useState(false)
  const [report, setReport] = useState<string | null>(null)
  const [steps, setSteps] = useState<AgentStep[]>([])
  const [error, setError] = useState<string | null>(null)

  async function handleReview() {
    setLoading(true)
    setError(null)
    setReport(null)
    setSteps([])

    try {
      const res = await fetch(`${API_BASE}/review/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, dateiname }),
      })

      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.detail ?? 'Unbekannter Fehler')
      }

      const reader = res.body!.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() ?? ''

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          try {
            const event: StreamEvent = JSON.parse(line.slice(6))
            handleEvent(event)
          } catch {
            // ignore malformed lines
          }
        }
      }
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Fehler beim Review')
    } finally {
      setLoading(false)
    }
  }

  function handleEvent(event: StreamEvent) {
    switch (event.type) {
      case 'thinking':
        setSteps(prev => [...prev, {
          type: 'thinking',
          label: `Iteration ${event.iteration} — Agent denkt...`,
        }])
        break
      case 'tool_call':
        setSteps(prev => [...prev, {
          type: 'tool_call',
          label: `🔧 ${TOOL_LABELS[event.name!] ?? event.name}`,
          detail: event.name === 'muster_suchen'
            ? `Muster: ${(event.input as { muster?: string })?.muster}`
            : undefined,
        }])
        break
      case 'tool_result':
        setSteps(prev => {
          const result = event.result as Record<string, unknown>
          let detail = ''
          if (result.zeilen_gesamt) detail = `${result.zeilen_gesamt} Zeilen`
          else if (result.anzahl !== undefined) detail = `${result.anzahl} Treffer`
          else if (result.abdeckung_prozent !== undefined) detail = `${result.abdeckung_prozent}% abgedeckt`
          else if (result.sicher !== undefined) detail = result.sicher ? 'Keine Probleme' : `${(result.warnungen as unknown[])?.length} Warnungen`
          return [...prev, { type: 'tool_result', label: `✅ Ergebnis`, detail }]
        })
        break
      case 'report':
        setReport(event.content ?? '')
        break
      case 'error':
        setError(event.message ?? 'Unbekannter Fehler')
        break
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

          {/* Agent Live-Steps */}
          {(loading || steps.length > 0) && !report && (
            <div className="bg-gray-900 border border-gray-700 rounded-lg p-4 mb-4">
              <p className="text-xs text-gray-500 uppercase tracking-wider mb-3">Agent-Loop live</p>
              <div className="flex flex-col gap-2">
                {steps.map((step, i) => (
                  <div key={i} className="flex items-start gap-2 text-sm">
                    <span className={`mt-0.5 w-2 h-2 rounded-full flex-shrink-0 ${
                      step.type === 'thinking' ? 'bg-indigo-400' :
                      step.type === 'tool_call' ? 'bg-yellow-400' : 'bg-green-400'
                    }`}></span>
                    <div>
                      <span className="text-gray-300">{step.label}</span>
                      {step.detail && <span className="text-gray-500 ml-2 text-xs">{step.detail}</span>}
                    </div>
                  </div>
                ))}
                {loading && (
                  <div className="flex items-center gap-2 text-sm text-gray-500">
                    <div className="w-2 h-2 rounded-full bg-indigo-400 animate-pulse"></div>
                    <span>Warte auf Antwort...</span>
                  </div>
                )}
              </div>
            </div>
          )}

          {report && (
            <ReviewResult report={report} dateiname={dateiname} steps={steps.length} />
          )}

          {!report && !loading && !error && steps.length === 0 && (
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
