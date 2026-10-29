import { useState, useEffect } from 'react'
import { fetchTrends } from '../api/trends'

export function usePriceTrends(productId, weeks = 12) {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!productId) return

    let cancelled = false
    setLoading(true)
    setError(null)

    fetchTrends(productId, weeks)
      .then((result) => {
        if (!cancelled) setData(result)
      })
      .catch((err) => {
        if (!cancelled) setError(err.message)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [productId, weeks])

  return { data, loading, error }
}
