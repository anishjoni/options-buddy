import { useState, useEffect } from "react"
import { api } from "../api/client"

export function useAnalytics(endpoint) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    setLoading(true)
    api.get(`/analytics/${endpoint}`)
      .then(setData)
      .catch(setError)
      .finally(() => setLoading(false))
  }, [endpoint])

  return { data, loading, error }
}
