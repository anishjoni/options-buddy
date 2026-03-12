export default function EdgePanel({ edge }) {
  if (!edge) return null
  const { best, worst } = edge
  if (!best?.length && !worst?.length) {
    return (
      <div className="bg-surface border border-slate-700 rounded-lg p-4 text-slate-500 text-sm">
        Import more trades to surface your edge patterns.
      </div>
    )
  }
  return (
    <div className="bg-surface border border-blue-900 rounded-lg p-4">
      <div className="text-blue-400 text-sm font-bold mb-3">⚡ Your Edge</div>
      <div className="grid grid-cols-2 gap-3">
        <div className="bg-base border-l-2 border-emerald-500 rounded p-3">
          <div className="text-emerald-400 text-xs font-semibold mb-2">Best Conditions</div>
          {best.map(p => (
            <div key={p.condition} className="text-slate-300 text-xs leading-relaxed">
              • {p.condition}: <strong className="text-emerald-400">{Math.round(p.win_rate * 100)}% win</strong>
              <span className="text-slate-500"> ({p.trade_count} trades)</span>
            </div>
          ))}
        </div>
        <div className="bg-base border-l-2 border-red-500 rounded p-3">
          <div className="text-red-400 text-xs font-semibold mb-2">Where You Lose</div>
          {worst.map(p => (
            <div key={p.condition} className="text-slate-300 text-xs leading-relaxed">
              • {p.condition}: <strong className="text-red-400">{Math.round(p.win_rate * 100)}% win</strong>
              <span className="text-slate-500"> ({p.trade_count} trades)</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
