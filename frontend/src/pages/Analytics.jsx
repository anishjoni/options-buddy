import { useState } from "react"
import { useAnalytics } from "../hooks/useAnalytics"
import MetricCard from "../components/MetricCard"
import WinRateBar from "../components/WinRateBar"
import EdgePanel from "../components/EdgePanel"

const TABS = [
  { key: "overview", label: "Overview" },
  { key: "by-strategy", label: "By Strategy" },
  { key: "by-symbol", label: "By Symbol" },
  { key: "by-dte", label: "By DTE" },
  { key: "by-iv-rank", label: "By IV Rank" },
]

function OverviewTab() {
  const { data: overview } = useAnalytics("overview")
  const { data: byStrategy } = useAnalytics("by-strategy")
  const { data: edge } = useAnalytics("edge")

  return (
    <div className="flex flex-col gap-4">
      <div className="grid grid-cols-4 gap-4">
        <MetricCard value={overview ? `${Math.round(overview.win_rate * 100)}%` : null} label="Win Rate"
          subLabel={overview ? `${overview.winning_trades}/${overview.trade_count}` : null} />
        <MetricCard value={overview?.profit_factor != null ? `${overview.profit_factor}x` : null}
          label="Profit Factor" color="text-amber-400" />
        <MetricCard value={overview?.avg_premium ? `$${overview.avg_premium}` : null}
          label="Avg Premium" color="text-amber-400" />
        <MetricCard value={overview ? `$${overview.total_pnl?.toFixed(0)}` : null}
          label="Total P&L" color={overview?.total_pnl >= 0 ? "text-emerald-400" : "text-red-400"} />
      </div>
      <WinRateBar data={byStrategy} title="Win Rate by Strategy" />
      <EdgePanel edge={edge} />
    </div>
  )
}

function DimensionTab({ endpoint, title }) {
  const { data, loading } = useAnalytics(endpoint)
  if (loading) return <div className="text-slate-500 text-sm">Loading...</div>
  return <WinRateBar data={data} title={title} />
}

export default function Analytics() {
  const [activeTab, setActiveTab] = useState("overview")

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-bold">Analytics</h1>

      <div className="flex gap-1 bg-base p-1 rounded-lg">
        {TABS.map(tab => (
          <button key={tab.key} onClick={() => setActiveTab(tab.key)}
            className={`px-4 py-2 rounded text-sm transition-colors ${
              activeTab === tab.key
                ? "bg-blue-700 text-white"
                : "text-slate-400 hover:text-white"
            }`}>
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === "overview" && <OverviewTab />}
      {activeTab === "by-strategy" && <DimensionTab endpoint="by-strategy" title="Win Rate by Strategy" />}
      {activeTab === "by-symbol" && <DimensionTab endpoint="by-symbol" title="Win Rate by Symbol" />}
      {activeTab === "by-dte" && <DimensionTab endpoint="by-dte" title="Win Rate by DTE at Entry" />}
      {activeTab === "by-iv-rank" && <DimensionTab endpoint="by-iv-rank" title="Win Rate by IV Rank" />}
    </div>
  )
}
