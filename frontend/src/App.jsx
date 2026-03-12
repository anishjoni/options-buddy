import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom"
import Dashboard from "./pages/Dashboard"
import Analytics from "./pages/Analytics"
import TradeLog from "./pages/TradeLog"
import Campaigns from "./pages/Campaigns"

const navItems = [
  { to: "/", label: "Dashboard" },
  { to: "/analytics", label: "Analytics" },
  { to: "/trades", label: "Trade Log" },
  { to: "/campaigns", label: "Campaigns" },
]

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex min-h-screen">
        <nav className="w-48 bg-surface border-r border-border p-4 flex flex-col gap-1 shrink-0">
          <div className="text-lg font-bold text-white mb-6 px-2">Options Buddy</div>
          {navItems.map(({ to, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              className={({ isActive }) =>
                `px-3 py-2 rounded text-sm transition-colors ${
                  isActive
                    ? "bg-blue-700 text-white"
                    : "text-slate-400 hover:text-white hover:bg-slate-700"
                }`
              }
            >
              {label}
            </NavLink>
          ))}
        </nav>
        <main className="flex-1 p-6 overflow-auto">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/trades" element={<TradeLog />} />
            <Route path="/campaigns" element={<Campaigns />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
