import { useState, useEffect } from "react"
import { api } from "../api/client"

export function useCampaigns() {
  const [campaigns, setCampaigns] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const refresh = () => {
    setLoading(true)
    api.get("/campaigns")
      .then(setCampaigns)
      .catch(setError)
      .finally(() => setLoading(false))
  }

  useEffect(() => { refresh() }, [])
  return { campaigns, loading, error, refresh }
}
