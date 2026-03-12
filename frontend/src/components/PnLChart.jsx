import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceDot } from "recharts"

export default function PnLChart({ trades }) {
  // Build cumulative P&L series from closed trades sorted by close date
  const sorted = [...trades]
    .filter(t => t.status === "closed" && t.pnl != null && t.closed_at)
    .sort((a, b) => new Date(a.closed_at) - new Date(b.closed_at))

  let cumulative = 0
  const data = sorted.map(t => {
    cumulative += t.pnl
    return {
      date: new Date(t.closed_at).toLocaleDateString("en-CA"),
      pnl: Math.round(cumulative * 100) / 100,
      loss: t.pnl < 0,
    }
  })

  const lossDots = data
    .map((d, i) => ({ ...d, index: i }))
    .filter(d => d.loss)

  if (data.length === 0) {
    return <div className="bg-surface rounded-lg p-6 text-slate-500 text-sm text-center">No closed trades yet</div>
  }

  return (
    <div className="bg-surface rounded-lg p-4">
      <div className="text-slate-400 text-xs font-semibold uppercase tracking-wide mb-3">Cumulative P&L</div>
      <ResponsiveContainer width="100%" height={180}>
        <LineChart data={data}>
          <XAxis dataKey="date" tick={{ fontSize: 10, fill: "#64748b" }} tickLine={false} />
          <YAxis tick={{ fontSize: 10, fill: "#64748b" }} tickLine={false} axisLine={false}
            tickFormatter={v => `$${v}`} />
          <Tooltip
            contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 6 }}
            labelStyle={{ color: "#94a3b8" }}
            formatter={v => [`$${v}`, "Cumulative P&L"]}
          />
          <Line type="monotone" dataKey="pnl" stroke="#10b981" strokeWidth={2} dot={false} />
          {lossDots.map((d) => (
            <ReferenceDot key={d.index} x={d.date} y={d.pnl} r={4} fill="#ef4444" stroke="none" />
          ))}
        </LineChart>
      </ResponsiveContainer>
      <div className="text-slate-500 text-xs mt-1 text-right">Red dots = losing trades</div>
    </div>
  )
}
