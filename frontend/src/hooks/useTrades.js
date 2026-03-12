import { useState, useEffect } from "react"
import { api } from "../api/client"

export function useTrades(filters = {}) {
  const [trades, setTrades] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const params = new URLSearchParams(
    Object.fromEntries(Object.entries(filters).filter(([, v]) => v != null))
  ).toString()

  useEffect(() => {
    setLoading(true)
    api.get(`/trades${params ? "?" + params : ""}`)
      .then(setTrades)
      .catch(setError)
      .finally(() => setLoading(false))
  }, [params])

  return { trades, loading, error }
}
