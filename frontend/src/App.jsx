import { useState } from 'react'
import { analyzeCSV } from './utils/api'
import UploadSection from './components/UploadSection'
import GraphView     from './components/GraphView'
import FraudTable    from './components/FraudTable'
import NodeDetails   from './components/NodeDetails'
import SummaryBar    from './components/SummaryBar'

export default function App() {
  const [loading,      setLoading]      = useState(false)
  const [error,        setError]        = useState(null)
  const [data,         setData]         = useState(null)
  const [selectedNode, setSelectedNode] = useState(null)

  async function handleAnalyze(file) {
    setLoading(true)
    setError(null)
    setSelectedNode(null)
    setData(null)
    try {
      const result = await analyzeCSV(file)
      setData(result)
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        err.message ||
        'Cannot connect to backend. Make sure FastAPI is running on port 8000.'
      )
    } finally {
      setLoading(false)
    }
  }

  // Download exact judge-required JSON format
  function handleDownload() {
    if (!data) return
    const judgeOutput = {
      suspicious_accounts: data.suspicious_accounts,
      fraud_rings:         data.fraud_rings,
      summary:             data.summary,
    }
    const blob = new Blob([JSON.stringify(judgeOutput, null, 2)], { type: 'application/json' })
    const url  = URL.createObjectURL(blob)
    const a    = document.createElement('a')
    a.href     = url
    a.download = 'fraud_analysis.json'
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="min-h-screen relative" style={{ zIndex: 1 }}>

      {/* ── Header ─────────────────────────────────────────────────── */}
      <header className="border-b" style={{ borderColor:'rgba(0,255,200,0.1)' }}>
        <div className="max-w-screen-xl mx-auto px-6 py-4 flex items-center justify-between">

          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="w-9 h-9 rounded-lg flex items-center justify-center"
                style={{ background:'linear-gradient(135deg,#00ffc8,#0070f3)', boxShadow:'0 0 18px rgba(0,255,200,0.35)' }}>
                <span className="text-black font-black">⬡</span>
              </div>
              <div className="pulse absolute -top-0.5 -right-0.5 w-2.5 h-2.5 rounded-full"
                style={{ background:'#00ffc8', boxShadow:'0 0 6px #00ffc8' }} />
            </div>
            <div>
              <h1 className="font-black text-lg leading-none">
                FinCrime<span style={{ color:'#00ffc8' }}>Graph</span>
              </h1>
              <p className="mono text-xs" style={{ color:'rgba(0,255,200,0.45)', fontSize:'0.65rem' }}>
                RIFT 2026 · Money Mule Detection Engine
              </p>
            </div>
          </div>

          {/* Right side */}
          <div className="flex items-center gap-3">
            {data && (
              <>
                <div className="flex items-center gap-2">
                  <div className="pulse w-2 h-2 rounded-full" style={{ background:'#00ffc8' }} />
                  <span className="mono text-xs text-slate-400">Analysis Complete</span>
                </div>
                <button onClick={handleDownload} className="sec-btn">
                  ↓ Download JSON
                </button>
              </>
            )}
          </div>
        </div>
      </header>

      {/* ── Main ───────────────────────────────────────────────────── */}
      <main className="max-w-screen-xl mx-auto px-6 py-5">

        {/* Summary stats bar (only shows after analysis) */}
        <SummaryBar summary={data?.summary} />

        {/* Two-column layout */}
        <div className="grid gap-4 mb-4" style={{ gridTemplateColumns:'320px 1fr' }}>

          {/* Left sidebar */}
          <div className="flex flex-col gap-4">
            <UploadSection onAnalyze={handleAnalyze} loading={loading} error={error} />
            <NodeDetails node={selectedNode} />
          </div>

          {/* Graph or placeholder */}
          {data ? (
            <GraphView
              nodes={data.nodes}
              edges={data.edges}
              fraudRings={data.fraud_rings}
              onNodeClick={setSelectedNode}
            />
          ) : (
            <div className="glass flex flex-col items-center justify-center"
              style={{ minHeight:'420px' }}>
              <div className="text-5xl opacity-10 mb-4">⬡</div>
              <p className="mono text-slate-500 text-sm">Upload a CSV to visualize the transaction network</p>
              <p className="mono text-slate-600 text-xs mt-2">Supports up to 10,000 transactions</p>
            </div>
          )}
        </div>

        {/* Fraud rings table */}
        {data && <FraudTable fraudRings={data.fraud_rings} />}

        {/* Footer */}
        <footer className="mt-6 text-center">
          <p className="mono text-slate-700" style={{ fontSize:'0.65rem' }}>
            RIFT 2026 Hackathon · Graph-Based Financial Crime Detection · Money Muling Detection Engine
          </p>
        </footer>
      </main>
    </div>
  )
}