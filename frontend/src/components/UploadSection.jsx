import { useState, useRef } from 'react'

export default function UploadSection({ onAnalyze, loading, error }) {
  const [file, setFile]         = useState(null)
  const [dragOver, setDragOver] = useState(false)
  const inputRef                = useRef(null)

  function handleFile(f) {
    if (f && f.name.endsWith('.csv')) setFile(f)
  }

  return (
    <div className="glass p-5">
      <div className="stitle">⬆ Upload CSV</div>

      {/* Drop zone */}
      <div
        onClick={() => inputRef.current.click()}
        onDrop={(e) => { e.preventDefault(); setDragOver(false); handleFile(e.dataTransfer.files[0]) }}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        className="rounded-lg border-2 border-dashed p-6 text-center cursor-pointer mb-4 transition-all duration-200"
        style={{
          borderColor: dragOver ? '#00ffc8' : 'rgba(0,255,200,0.22)',
          background:  dragOver ? 'rgba(0,255,200,0.06)' : 'rgba(0,0,0,0.25)',
        }}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".csv"
          className="hidden"
          onChange={(e) => handleFile(e.target.files[0])}
        />
        <div className="text-3xl mb-2">{file ? '📄' : '📂'}</div>
        {file ? (
          <>
            <p className="mono text-green-400 text-sm">{file.name}</p>
            <p className="text-slate-500 text-xs mt-1">{(file.size/1024).toFixed(1)} KB · click to change</p>
          </>
        ) : (
          <>
            <p className="text-slate-300 text-sm font-semibold">Drop CSV file here</p>
            <p className="text-slate-500 text-xs mt-1">or click to browse</p>
          </>
        )}
      </div>

      {/* CSV format hint */}
      <div className="mb-4 p-3 rounded-lg text-xs mono"
        style={{ background: 'rgba(0,112,243,0.08)', border: '1px solid rgba(0,112,243,0.2)', color: '#60a5fa' }}>
        Required columns: transaction_id, sender_id, receiver_id, amount, timestamp
      </div>

      {/* Error */}
      {error && (
        <div className="mb-4 p-3 rounded-lg text-sm mono"
          style={{ background: 'rgba(255,50,50,0.08)', border: '1px solid rgba(255,50,50,0.25)', color: '#f87171' }}>
          ⚠ {error}
        </div>
      )}

      {/* Button */}
      <button
        onClick={() => file && onAnalyze(file)}
        disabled={!file || loading}
        className="glow-btn flex items-center justify-center gap-3"
      >
        {loading
          ? <><span className="spinner" /> Analyzing Network...</>
          : <><span>◈</span> Run Fraud Detection</>
        }
      </button>
    </div>
  )
}