import { useState, useEffect } from 'react'
import { fetchComparison } from '../api/compare'
import { KNOWN_CATEGORIES } from '../data/knownProducts'
import LoadingSpinner from './LoadingSpinner'
import ErrorMessage from './ErrorMessage'

export default function StoreComparisonTable() {
  const [category, setCategory] = useState(KNOWN_CATEGORIES[0])
  const [rankings, setRankings] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)

    fetchComparison(category)
      .then((data) => {
        if (!cancelled) setRankings(data)
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
  }, [category])

  return (
    <section>
      <h1 className="font-display text-2xl font-semibold text-forest-900">
        Who's cheapest for {category.toLowerCase()}?
      </h1>
      <p className="mt-1 max-w-md text-sm text-forest-600">
        Average price across every product in this category, ranked
        cheapest first.
      </p>

      <label className="mt-6 flex max-w-xs flex-col gap-1 text-sm">
        <span className="font-medium text-ink">Category</span>
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="rounded border border-forest-100 bg-white px-3 py-2 text-sm"
        >
          {KNOWN_CATEGORIES.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
      </label>

      <div className="mt-8">
        {loading && <LoadingSpinner label="Loading store rankings" />}
        {error && <ErrorMessage message={error} />}
        {!loading && !error && rankings.length === 0 && (
          <p className="py-8 text-sm text-forest-600">
            No price data for this category yet.
          </p>
        )}
        {!loading && !error && rankings.length > 0 && (
          <table className="w-full max-w-xl border-collapse text-sm">
            <thead>
              <tr className="border-b border-forest-100 text-left text-forest-600">
                <th className="py-2 pr-4 font-medium">Rank</th>
                <th className="py-2 pr-4 font-medium">Store</th>
                <th className="py-2 pr-4 font-medium">Avg price</th>
                <th className="py-2 font-medium">Products compared</th>
              </tr>
            </thead>
            <tbody>
              {rankings.map((r) => (
                <tr
                  key={r.store_name}
                  className="border-b border-forest-50 last:border-0"
                >
                  <td className="py-3 pr-4 font-display font-semibold text-forest-900">
                    {r.rank}
                  </td>
                  <td className="py-3 pr-4">{r.store_name}</td>
                  <td className="py-3 pr-4 font-medium">
                    R{r.avg_price_zar.toFixed(2)}
                  </td>
                  <td className="py-3 text-forest-600">{r.product_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </section>
  )
}
