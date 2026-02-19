// Shows the 4 key stats across the top after analysis

export default function SummaryBar({ summary }) {
  if (!summary) return null

  const stats = [
    {
      label: 'Accounts Analyzed',
      value: summary.total_accounts_analyzed,
      color: '#00ffc8',
      icon:  '◉',
    },
    {
      label: 'Suspicious Flagged',
      value: summary.suspicious_accounts_flagged,
      color: '#f87171',
      icon:  '⚑',
    },
    {
      label: 'Fraud Rings Found',
      value: summary.fraud_rings_detected,
      color: '#fb923c',
      icon:  '↺',
    },
    {
      label: 'Processing Time',
      value: `${summary.processing_time_seconds}s`,
      color: '#a78bfa',
      icon:  '⚡',
    },
  ]

  return (
    <div className="grid grid-cols-4 gap-3 mb-4 fade-up">
      {stats.map(({ label, value, color, icon }) => (
        <div key={label} className="glass p-4 text-center">
          <div className="text-xl mb-1" style={{ color }}>{icon}</div>
          <div className="mono font-bold text-2xl" style={{ color }}>{value}</div>
          <div className="text-xs text-slate-400 mt-1 uppercase tracking-wider"
            style={{ fontSize: '0.65rem' }}>{label}</div>
        </div>
      ))}
    </div>
  )
}