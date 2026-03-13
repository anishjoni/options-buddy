import { api } from "../api/client"

export default function CampaignCard({ campaign, onUpdate }) {
  const handleComplete = async () => {
    await api.patch(`/campaigns/${campaign.id}/complete`, {})
    if (onUpdate) onUpdate()
  }

  return (
    <div className="bg-surface rounded-lg p-4 border border-border">
      <div className="flex justify-between items-start mb-3">
        <div>
          <div className="font-semibold">{campaign.name}</div>
          <div className="text-slate-400 text-xs mt-0.5">{campaign.symbol} • {campaign.type}</div>
        </div>
        <span className={`text-xs px-2 py-0.5 rounded-full ${
          campaign.status === "active" ? "bg-blue-900 text-blue-300" : "bg-slate-700 text-slate-400"
        }`}>{campaign.status}</span>
      </div>
      <div className="grid grid-cols-3 gap-3 mb-3">
        <div className="text-center">
          <div className={`font-bold ${campaign.total_pnl >= 0 ? "text-emerald-400" : "text-red-400"}`}>
            {campaign.total_pnl != null ? `$${campaign.total_pnl.toFixed(0)}` : "—"}
          </div>
          <div className="text-slate-500 text-xs">Cycle P&L</div>
        </div>
        <div className="text-center">
          <div className="font-bold text-slate-300">{campaign.trade_count}</div>
          <div className="text-slate-500 text-xs">Trades</div>
        </div>
        <div className="text-center">
          <div className="text-slate-300 text-xs">{new Date(campaign.started_at).toLocaleDateString("en-CA")}</div>
          <div className="text-slate-500 text-xs">Started</div>
        </div>
      </div>
      {campaign.status === "active" && (
        <button onClick={handleComplete}
          className="w-full text-xs text-slate-400 hover:text-white py-1 border border-slate-700 hover:border-slate-500 rounded transition-colors">
          Mark Complete
        </button>
      )}
    </div>
  )
}
