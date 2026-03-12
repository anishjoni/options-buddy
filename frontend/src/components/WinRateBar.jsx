function Bar({ label, winRate, tradeCount }) {
  const pct = Math.round(winRate * 100)
  const color = pct >= 70 ? "bg-emerald-500" : pct >= 50 ? "bg-amber-400" : "bg-red-500"
  const textColor = pct >= 70 ? "text-emerald-400" : pct >= 50 ? "text-amber-400" : "text-red-400"
  return (
    <div>
      <div className="flex justify-between text-xs text-slate-400 mb-1">
        <span>{label}</span>
        <span className={textColor}>{pct}% <span className="text-slate-500">({tradeCount})</span></span>
      </div>
      <div className="bg-base rounded-full h-2">
        <div className={`${color} h-2 rounded-full transition-all`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  )
}

export default function WinRateBar({ data, title }) {
  if (!data?.length) return null
  return (
    <div className="bg-surface rounded-lg p-4">
      <div className="text-slate-400 text-xs font-semibold uppercase tracking-wide mb-3">{title}</div>
      <div className="flex flex-col gap-3">
        {data.map(row => (
          <Bar key={row.label} label={row.label} winRate={row.win_rate} tradeCount={row.trade_count} />
        ))}
      </div>
    </div>
  )
}
