import { useState } from 'react'
import { optimizeBasket } from '../api/basket'

export function useBasketOptimizer() {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function optimize(items, budget) {
    setLoading(true)
    setError(null)
    try {
      const data = await optimizeBasket(items, budget)
      setResult(data)
      return data
    } catch (err) {
      setError(err.message)
      throw err
    } finally {
      setLoading(false)
    }
  }

  return { result, loading, error, optimize }
}
