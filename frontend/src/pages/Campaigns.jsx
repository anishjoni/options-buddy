import { useState } from "react"
import { useCampaigns } from "../hooks/useCampaigns"
import CampaignCard from "../components/CampaignCard"
import { api } from "../api/client"

export default function Campaigns() {
  const { campaigns, loading, refresh } = useCampaigns()
  const [showCreate, setShowCreate] = useState(false)
  const [form, setForm] = useState({ name: "", symbol: "", type: "wheel" })

  const handleCreate = async (e) => {
    e.preventDefault()
    await api.post("/campaigns", form)
    setShowCreate(false)
    setForm({ name: "", symbol: "", type: "wheel" })
    refresh()
  }

  const active = campaigns.filter(c => c.status === "active")
  const completed = campaigns.filter(c => c.status === "completed")

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Campaigns</h1>
        <button onClick={() => setShowCreate(v => !v)}
          className="px-4 py-2 bg-blue-700 hover:bg-blue-600 rounded-lg text-sm font-medium transition-colors">
          New Campaign
        </button>
      </div>

      {showCreate && (
        <form onSubmit={handleCreate} className="bg-surface rounded-lg p-4 flex gap-3 items-end">
          <div className="flex flex-col gap-1">
            <label className="text-xs text-slate-400">Name</label>
            <input value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
              placeholder="TSLA Wheel Q2 2026" required
              className="bg-base border border-border rounded px-3 py-2 text-sm text-white placeholder-slate-600" />
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs text-slate-400">Symbol</label>
            <input value={form.symbol} onChange={e => setForm(f => ({ ...f, symbol: e.target.value.toUpperCase() }))}
              placeholder="TSLA" required
              className="bg-base border border-border rounded px-3 py-2 text-sm text-white placeholder-slate-600 w-24" />
          </div>
          <button type="submit" className="px-4 py-2 bg-emerald-700 hover:bg-emerald-600 rounded text-sm font-medium">
            Create
          </button>
        </form>
      )}

      {loading ? (
        <div className="text-slate-500 text-sm">Loading...</div>
      ) : (
        <>
          {active.length > 0 && (
            <div>
              <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wide mb-3">Active</h2>
              <div className="grid grid-cols-3 gap-4">
                {active.map(c => <CampaignCard key={c.id} campaign={c} onUpdate={refresh} />)}
              </div>
            </div>
          )}
          {completed.length > 0 && (
            <div>
              <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wide mb-3">Completed</h2>
              <div className="grid grid-cols-3 gap-4">
                {completed.map(c => <CampaignCard key={c.id} campaign={c} onUpdate={refresh} />)}
              </div>
            </div>
          )}
          {campaigns.length === 0 && (
            <div className="text-slate-500 text-sm text-center py-12">
              No campaigns yet. Import trades and link Wheel sequences, or create one manually.
            </div>
          )}
        </>
      )}
    </div>
  )
}
