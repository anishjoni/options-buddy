export default function MetricCard({ value, label, subLabel, color = "text-emerald-400" }) {
  return (
    <div className="bg-surface rounded-lg p-4 text-center">
      <div className={`text-2xl font-bold ${color}`}>{value ?? "—"}</div>
      <div className="text-slate-400 text-sm mt-1">{label}</div>
      {subLabel && <div className="text-slate-500 text-xs mt-0.5">{subLabel}</div>}
    </div>
  )
}
