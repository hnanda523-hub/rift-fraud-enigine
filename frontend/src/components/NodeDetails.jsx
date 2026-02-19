export default function NodeDetails({ node }) {
  function riskInfo(score) {
    if (score >= 71) return { label: 'HIGH RISK',    color: '#ef4444', bg: 'rgba(239,68,68,0.1)',   border: 'rgba(239,68,68,0.3)'  }
    if (score >= 41) return { label: 'MEDIUM RISK',  color: '#eab308', bg: 'rgba(234,179,8,0.1)',   border: 'rgba(234,179,8,0.3)'  }
    return               { label: 'LOW RISK',      color: '#22c55e', bg: 'rgba(34,197,94,0.1)',   border: 'rgba(34,197,94,0.3)'  }
  }

  function flagColor(f) {
    return { cycle_length_3:'#f87171', cycle_length_4:'#f87171', cycle_length_5:'#f87171',
             fan_out:'#fb923c', fan_in:'#a78bfa', shell_account:'#60a5fa',
             high_velocity:'#facc15', high_volume_merchant:'#94a3b8' }[f] || '#94a3b8'
  }

  if (!node) return (
    <div className="glass p-5" style={{ minHeight: '170px' }}>
      <div className="stitle">◉ Node Details</div>
      <div className="flex flex-col items-center justify-center py-6 gap-2">
        <div className="text-3xl opacity-20">◎</div>
        <p className="mono text-slate-500 text-sm">Click any node to inspect</p>
      </div>
    </div>
  )

  const risk = riskInfo(node.suspicion_score)

  return (
    <div className="glass p-5 fade-up" style={{ minHeight: '170px' }}>
      <div className="stitle">◉ Node Details</div>

      {/* Header row */}
      <div className="flex items-start justify-between mb-4">
        <div>
          <p className="mono text-xs text-slate-500 uppercase tracking-widest mb-1">Account ID</p>
          <p className="mono text-xl font-bold text-white">{node.id}</p>
          {node.inRing && (
            <span className="mono text-xs px-2 py-0.5 rounded mt-1 inline-block"
              style={{ background:'rgba(255,68,68,0.12)', color:'#f87171', border:'1px solid rgba(255,68,68,0.3)' }}>
              ⚠ In Fraud Ring
            </span>
          )}
        </div>
        <span className="badge text-xs"
          style={{ background: risk.bg, color: risk.color, border: `1px solid ${risk.border}` }}>
          {risk.label}
        </span>
      </div>

      {/* Score bar */}
      <div className="mb-4">
        <div className="flex justify-between mb-1">
          <span className="mono text-xs text-slate-400 uppercase tracking-wider">Suspicion Score</span>
          <span className="mono text-sm font-bold" style={{ color: risk.color }}>{node.suspicion_score}/100</span>
        </div>
        <div className="w-full h-2 rounded-full" style={{ background: 'rgba(255,255,255,0.07)' }}>
          <div className="h-2 rounded-full transition-all duration-700"
            style={{
              width:     `${node.suspicion_score}%`,
              background:`linear-gradient(90deg, ${risk.color}77, ${risk.color})`,
              boxShadow: `0 0 8px ${risk.color}66`,
            }} />
        </div>
      </div>

      {/* Flags */}
      <div>
        <p className="mono text-xs text-slate-400 uppercase tracking-wider mb-2">Detected Patterns</p>
        {node.flags?.length > 0 ? (
          <div className="flex flex-wrap gap-1.5">
            {node.flags.map(f => (
              <span key={f} className="mono text-xs px-2 py-0.5 rounded"
                style={{ background:`${flagColor(f)}15`, color:flagColor(f), border:`1px solid ${flagColor(f)}40` }}>
                ⚑ {f}
              </span>
            ))}
          </div>
        ) : (
          <span className="mono text-slate-500 text-sm">No patterns</span>
        )}
      </div>
    </div>
  )
}