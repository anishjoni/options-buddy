import { useAnalytics } from "../hooks/useAnalytics"
import { useTrades } from "../hooks/useTrades"
import MetricCard from "../components/MetricCard"
import PnLChart from "../components/PnLChart"
import TradeTable from "../components/TradeTable"
import CSVUpload from "../components/CSVUpload"
import { useState } from "react"

export default function Dashboard() {
  const { data: overview } = useAnalytics("overview")
  const { trades, loading, error } = useTrades()
  const [showImport, setShowImport] = useState(false)

  const openCount = trades.filter(t => t.status === "open").length

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <button
          onClick={() => setShowImport(v => !v)}
          className="px-4 py-2 bg-blue-700 hover:bg-blue-600 rounded-lg text-sm font-medium transition-colors"
        >
          {showImport ? "Hide Import" : "Import CSV"}
        </button>
      </div>

      {showImport && (
        <CSVUpload onImportComplete={() => window.location.reload()} />
      )}

      {/* Metric cards */}
      <div className="grid grid-cols-4 gap-4">
        <MetricCard
          value={overview ? `${Math.round(overview.win_rate * 100)}%` : null}
          label="Win Rate"
          subLabel={overview ? `${overview.winning_trades} of ${overview.trade_count} trades` : null}
        />
        <MetricCard
          value={overview ? `$${overview.total_pnl?.toFixed(0)}` : null}
          label="Total P&L"
          color={overview?.total_pnl >= 0 ? "text-emerald-400" : "text-red-400"}
        />
        <MetricCard
          value={overview?.avg_premium ? `$${overview.avg_premium?.toFixed(0)}` : null}
          label="Avg Premium"
          color="text-amber-400"
        />
        <MetricCard
          value={openCount || null}
          label="Open Positions"
          color="text-blue-400"
        />
      </div>

      {/* P&L Chart */}
      {!loading && <PnLChart trades={trades} />}

      {/* Recent trades */}
      <div>
        <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wide mb-3">Recent Trades</h2>
        {loading ? (
          <div className="text-slate-500 text-sm">Loading...</div>
        ) : error ? (
          <div className="text-red-400 text-sm">Error loading trades</div>
        ) : (
          <TradeTable trades={trades.slice(0, 20)} />
        )}
      </div>
    </div>
  )
}
