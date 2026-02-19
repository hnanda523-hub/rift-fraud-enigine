export default function FraudTable({ fraudRings }) {
  if (!fraudRings?.length) return (
    <div className="glass p-5">
      <div className="stitle">⚠ Fraud Rings</div>
      <p className="mono text-slate-500 text-sm text-center py-6">No fraud rings detected</p>
    </div>
  )

  // Sort by risk_score descending
  const sorted = [...fraudRings].sort((a, b) => b.risk_score - a.risk_score)

  function riskStyle(score) {
    if (score >= 71) return { bg:'rgba(239,68,68,0.12)',  color:'#f87171', border:'rgba(239,68,68,0.35)'  }
    if (score >= 41) return { bg:'rgba(234,179,8,0.12)',  color:'#fbbf24', border:'rgba(234,179,8,0.35)'  }
    return               { bg:'rgba(34,197,94,0.12)',  color:'#4ade80', border:'rgba(34,197,94,0.35)'  }
  }

  function patternIcon(p) {
    return { cycle:'↺', smurfing:'⇉', fan_out:'⇉', fan_in:'⇇', shell_chain:'⛓' }[p] || '◈'
  }

  return (
    <div className="glass p-5 fade-up">
      <div className="stitle">
        ⚠ Fraud Rings Detected
        <span className="badge ml-auto normal-case tracking-normal text-xs"
          style={{ background:'rgba(239,68,68,0.12)', color:'#f87171', border:'1px solid rgba(239,68,68,0.25)' }}>
          {sorted.length} ring{sorted.length !== 1 ? 's' : ''} found
        </span>
      </div>

      <div style={{ overflowX:'auto' }}>
        <table className="data-table">
          <thead>
            <tr>
              <th>Ring ID</th>
              <th>Pattern</th>
              <th>Members</th>
              <th>Account IDs</th>
              <th>Risk Score</th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((ring, i) => {
              const s = riskStyle(ring.risk_score)
              return (
                <tr key={ring.ring_id} className="fade-up" style={{ animationDelay:`${i*0.04}s` }}>
                  <td className="mono text-xs text-slate-300">{ring.ring_id}</td>
                  <td>
                    <span className="mono text-xs px-2 py-0.5 rounded"
                      style={{ background:'rgba(0,255,200,0.07)', color:'#00ffc8', border:'1px solid rgba(0,255,200,0.2)' }}>
                      {patternIcon(ring.pattern_type)} {ring.pattern_type}
                    </span>
                  </td>
                  <td className="mono text-slate-400 text-sm">{ring.member_accounts?.length || 0}</td>
                  <td>
                    <div className="flex flex-wrap gap-1">
                      {ring.member_accounts?.slice(0,6).map(acc => (
                        <span key={acc} className="mono text-xs px-1.5 py-0.5 rounded"
                          style={{ background:'rgba(255,255,255,0.05)', color:'#94a3b8' }}>
                          {acc}
                        </span>
                      ))}
                      {ring.member_accounts?.length > 6 && (
                        <span className="mono text-xs text-slate-500">+{ring.member_accounts.length - 6} more</span>
                      )}
                    </div>
                  </td>
                  <td>
                    <span className="badge"
                      style={{ background:s.bg, color:s.color, border:`1px solid ${s.border}` }}>
                      {ring.risk_score}
                    </span>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}