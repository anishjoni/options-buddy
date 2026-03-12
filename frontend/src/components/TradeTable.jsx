import { useState } from "react"

const STRATEGY_COLORS = {
  csp: "text-emerald-400", covered_call: "text-blue-400",
  credit_spread: "text-amber-400", long_call: "text-purple-400",
  long_put: "text-pink-400", debit_spread: "text-orange-400",
}

export default function TradeTable({ trades }) {
  const [sortField, setSortField] = useState("opened_at")
  const [sortDir, setSortDir] = useState("desc")

  const toggleSort = (field) => {
    if (sortField === field) setSortDir(d => d === "asc" ? "desc" : "asc")
    else { setSortField(field); setSortDir("desc") }
  }

  const sorted = [...trades].sort((a, b) => {
    const va = a[sortField], vb = b[sortField]
    if (va == null) return 1
    if (vb == null) return -1
    return sortDir === "asc" ? (va > vb ? 1 : -1) : (va < vb ? 1 : -1)
  })

  const cols = [
    { key: "opened_at", label: "Date" },
    { key: "symbol", label: "Symbol" },
    { key: "strategy", label: "Strategy" },
    { key: "dte_entry", label: "DTE" },
    { key: "premium_collected", label: "Premium" },
    { key: "pnl", label: "P&L" },
    { key: "status", label: "Status" },
  ]

  return (
    <div className="bg-surface rounded-lg overflow-hidden">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border">
            {cols.map(c => (
              <th key={c.key}
                className="px-4 py-3 text-left text-xs text-slate-400 uppercase tracking-wide cursor-pointer hover:text-white"
                onClick={() => toggleSort(c.key)}>
                {c.label} {sortField === c.key ? (sortDir === "asc" ? "↑" : "↓") : ""}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sorted.map(t => (
            <tr key={t.id} className="border-b border-border/50 hover:bg-slate-800 transition-colors">
              <td className="px-4 py-3 text-slate-400 text-xs">
                {new Date(t.opened_at).toLocaleDateString("en-CA")}
              </td>
              <td className="px-4 py-3 font-semibold">{t.symbol}</td>
              <td className={`px-4 py-3 text-xs ${STRATEGY_COLORS[t.strategy] || "text-slate-300"}`}>
                {t.strategy.replace("_", " ")}
              </td>
              <td className="px-4 py-3 text-slate-400">{t.dte_entry ?? "—"}</td>
              <td className="px-4 py-3 text-slate-300">
                {t.premium_collected != null ? `$${t.premium_collected.toFixed(0)}` : "—"}
              </td>
              <td className={`px-4 py-3 font-semibold ${t.pnl == null ? "text-slate-500" : t.pnl >= 0 ? "text-emerald-400" : "text-red-400"}`}>
                {t.pnl == null ? "Open" : `${t.pnl >= 0 ? "+" : ""}$${t.pnl.toFixed(0)}`}
              </td>
              <td className="px-4 py-3">
                <span className={`text-xs px-2 py-0.5 rounded-full ${
                  t.status === "closed" ? "bg-slate-700 text-slate-300" :
                  t.status === "open" ? "bg-blue-900 text-blue-300" : "bg-slate-600 text-slate-400"
                }`}>{t.status}</span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {sorted.length === 0 && (
        <div className="p-8 text-center text-slate-500 text-sm">No trades found</div>
      )}
    </div>
  )
}
