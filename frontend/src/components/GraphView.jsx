import { useEffect, useRef } from 'react'
import cytoscape from 'cytoscape'

// Node color based on suspicion score
function nodeColor(score) {
  if (score >= 71) return '#ef4444'   // red   = high risk
  if (score >= 41) return '#eab308'   // yellow = medium risk
  return '#22c55e'                     // green  = low risk
}

export default function GraphView({ nodes, edges, fraudRings, onNodeClick }) {
  const containerRef = useRef(null)
  const cyRef        = useRef(null)

  useEffect(() => {
    if (!containerRef.current || !nodes?.length) return

    // Build a set of accounts that are IN a fraud ring
    const ringMembers = new Set()
    ;(fraudRings || []).forEach(r => r.member_accounts?.forEach(a => ringMembers.add(a)))

    // Build Cytoscape elements
    const elements = [
      ...nodes.map(n => ({
        data: {
          id:              n.id,
          label:           n.id,
          suspicion_score: n.suspicion_score,
          flags:           n.flags,
          color:           nodeColor(n.suspicion_score),
          inRing:          ringMembers.has(n.id),
        }
      })),
      ...edges.map((e, i) => ({
        data: {
          id:     `e${i}`,
          source: e.source,
          target: e.target,
          label:  `$${e.amount}`,
        }
      })),
    ]

    if (cyRef.current) cyRef.current.destroy()

    const cy = cytoscape({
      container: containerRef.current,
      elements,
      style: [
        // Normal node
        {
          selector: 'node',
          style: {
            'background-color':   'data(color)',
            'label':              'data(label)',
            'color':              '#fff',
            'font-size':          '10px',
            'font-family':        'Share Tech Mono, monospace',
            'text-valign':        'center',
            'text-halign':        'center',
            'width':              '42px',
            'height':             '42px',
            'border-width':       '2px',
            'border-color':       'data(color)',
            'border-opacity':     0.8,
          }
        },
        // Ring member — glowing border
        {
          selector: 'node[?inRing]',
          style: {
            'border-width':   '3px',
            'border-color':   '#ff4444',
            'border-opacity': 1,
            'width':          '50px',
            'height':         '50px',
          }
        },
        // Selected node
        {
          selector: 'node:selected',
          style: {
            'border-width': '3px',
            'border-color': '#00ffc8',
            'width':        '54px',
            'height':       '54px',
          }
        },
        // Edge
        {
          selector: 'edge',
          style: {
            'width':                1.5,
            'line-color':           'rgba(0,255,200,0.3)',
            'target-arrow-color':   'rgba(0,255,200,0.6)',
            'target-arrow-shape':   'triangle',
            'curve-style':          'bezier',
            'label':                'data(label)',
            'font-size':            '8px',
            'font-family':          'Share Tech Mono, monospace',
            'color':                'rgba(200,230,255,0.65)',
            'text-background-color':'#020b18',
            'text-background-opacity': 0.85,
            'text-background-padding': '2px',
          }
        },
        // Edge hover
        {
          selector: 'edge:hover',
          style: { 'line-color': 'rgba(0,255,200,0.8)', 'width': 2.5 }
        },
      ],
      layout: {
        name:              'cose',
        idealEdgeLength:   120,
        nodeRepulsion:     8000,
        padding:           40,
        animate:           true,
        animationDuration: 700,
        randomize:         false,
      },
    })

    // Node click → show details panel
    cy.on('tap', 'node', e => {
      const n = e.target
      onNodeClick({
        id:              n.data('id'),
        suspicion_score: n.data('suspicion_score'),
        flags:           n.data('flags'),
        inRing:          n.data('inRing'),
      })
    })

    // Background click → clear panel
    cy.on('tap', e => { if (e.target === cy) onNodeClick(null) })

    cyRef.current = cy
    return () => { if (cyRef.current) { cyRef.current.destroy(); cyRef.current = null } }
  }, [nodes, edges, fraudRings])

  return (
    <div className="glass p-4 fade-up" style={{ height: '520px' }}>
      <div className="stitle">
        ◈ Transaction Network Graph
        <span className="mono text-slate-400 text-xs ml-auto normal-case tracking-normal">
          {nodes?.length || 0} accounts · {edges?.length || 0} transactions
        </span>
      </div>

      {/* Legend strip */}
      <div className="flex gap-4 mb-3">
        {[
          { color: '#22c55e', label: 'Low Risk (0-40)'    },
          { color: '#eab308', label: 'Medium Risk (41-70)' },
          { color: '#ef4444', label: 'High Risk (71-100)' },
          { color: '#ff4444', label: 'In Fraud Ring',  border: true },
        ].map(({ color, label, border }) => (
          <div key={label} className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-full flex-shrink-0"
              style={{
                background:  color,
                border:      border ? '2px solid #ff4444' : 'none',
                boxShadow:   `0 0 6px ${color}88`,
              }} />
            <span className="text-slate-400" style={{ fontSize: '0.65rem' }}>{label}</span>
          </div>
        ))}
      </div>

      {/* Cytoscape container */}
      <div ref={containerRef} style={{
        height:       'calc(100% - 70px)',
        borderRadius: '8px',
        background:   'rgba(0,0,0,0.4)',
        border:       '1px solid rgba(0,255,200,0.07)',
      }} />
    </div>
  )
}