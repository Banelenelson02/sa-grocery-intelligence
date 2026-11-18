import { useState, useEffect } from 'react'
import { fetchComparison } from '../api/compare'
import { useProducts } from '../hooks/useProducts'
import LoadingSpinner from './LoadingSpinner'
import ErrorMessage from './ErrorMessage'

export default function StoreComparisonTable() {
  const { products, loading: productsLoading, error: productsError } = useProducts()
  const categories = [...new Set(products.map((product) => product.category).filter(Boolean))]
  const [category, setCategory] = useState('')
  const [rankings, setRankings] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!category && categories.length > 0) {
      setCategory(categories[0])
      return
    }
    if (!category) return

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
  }, [category, products])

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
          disabled={productsLoading || categories.length === 0}
        >
          {categories.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
      </label>

      <div className="mt-8">
        {(productsLoading || loading) && <LoadingSpinner label="Loading store rankings" />}
        {productsError && <ErrorMessage message={productsError} />}
        {error && <ErrorMessage message={error} />}
        {!productsLoading && !loading && !productsError && !error && rankings.length === 0 && (
          <p className="py-8 text-sm text-forest-600">
            No price data for this category yet.
          </p>
        )}
        {!productsLoading && !loading && !productsError && !error && rankings.length > 0 && (
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
