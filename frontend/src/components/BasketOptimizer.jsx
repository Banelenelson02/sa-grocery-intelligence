import { useState } from 'react'
import { useBasketOptimizer } from '../hooks/useBasketOptimizer'
import { KNOWN_PRODUCTS } from '../data/knownProducts'
import LoadingSpinner from './LoadingSpinner'
import ErrorMessage from './ErrorMessage'

export default function BasketOptimizer() {
  const [quantities, setQuantities] = useState({})
  const [budget, setBudget] = useState(500)
  const { result, loading, error, optimize } = useBasketOptimizer()

  function setQty(productId, qty) {
    setQuantities((prev) => ({ ...prev, [productId]: qty }))
  }

  function handleSubmit(e) {
    e.preventDefault()
    const items = Object.entries(quantities)
      .filter(([, qty]) => qty > 0)
      .map(([productId, qty]) => ({
        product_id: Number(productId),
        qty: Number(qty),
      }))
    if (items.length === 0) return
    optimize(items, Number(budget))
  }

  const selectedCount = Object.values(quantities).filter((q) => q > 0).length

  return (
    <section>
      <h1 className="font-display text-2xl font-semibold text-forest-900">
        Where should you actually shop for this basket?
      </h1>
      <p className="mt-1 max-w-md text-sm text-forest-600">
        Compares one store covering everything against buying each item
        wherever it's cheapest.
      </p>

      <form onSubmit={handleSubmit} className="mt-6 max-w-xl">
        <ul className="divide-y divide-forest-50 rounded border border-forest-100 bg-white">
          {KNOWN_PRODUCTS.map((p) => (
            <li key={p.id} className="flex items-center justify-between px-4 py-3">
              <span className="text-sm text-ink">{p.name}</span>
              <input
                type="number"
                min="0"
                value={quantities[p.id] || ''}
                onChange={(e) => setQty(p.id, e.target.value)}
                placeholder="0"
                className="w-16 rounded border border-forest-100 px-2 py-1 text-right text-sm"
              />
            </li>
          ))}
        </ul>

        <div className="mt-4 flex items-end gap-4">
          <label className="flex flex-col gap-1 text-sm">
            <span className="font-medium text-ink">Budget (ZAR)</span>
            <input
              type="number"
              min="0"
              step="0.01"
              value={budget}
              onChange={(e) => setBudget(e.target.value)}
              className="w-32 rounded border border-forest-100 px-3 py-2 text-sm"
            />
          </label>
          <button
            type="submit"
            disabled={selectedCount === 0 || loading}
            className="rounded bg-forest-900 px-5 py-2 text-sm font-medium text-sand hover:bg-forest-600 disabled:cursor-not-allowed disabled:opacity-40"
          >
            Optimize basket
          </button>
        </div>
      </form>

      <div className="mt-8">
        {loading && <LoadingSpinner label="Comparing stores" />}
        {error && <ErrorMessage message={error} />}
        {!loading && !error && result && (
          <div className="grid max-w-xl gap-4 sm:grid-cols-2">
            <div className="rounded border border-forest-100 bg-white p-4">
              <p className="text-xs font-medium uppercase tracking-wide text-forest-400">
                One store
              </p>
              <p className="mt-1 font-display text-lg font-semibold text-forest-900">
                {result.single_store.store_name}
              </p>
              <p className="mt-1 text-2xl font-semibold text-ink">
                R{result.single_store.total_zar.toFixed(2)}
              </p>
            </div>

            <div className="rounded border border-forest-100 bg-white p-4">
              <p className="text-xs font-medium uppercase tracking-wide text-forest-400">
                Split across stores
              </p>
              <p className="mt-1 font-display text-lg font-semibold text-forest-900">
                {new Set((result.split_stores?.items ?? []).map((item) => item.store_name)).size} stores
              </p>
              <p className="mt-1 text-2xl font-semibold text-ink">
                R{(result.split_stores?.total_zar ?? 0).toFixed(2)}
              </p>
            </div>

            {result.saving_zar != null && (
              <div
                className={`sm:col-span-2 rounded px-4 py-3 text-sm font-medium ${
                  result.saving_zar > 0
                    ? 'bg-marigold-400/20 text-forest-900'
                    : 'bg-sage/60 text-forest-900'
                }`}
              >
                {result.saving_zar > 0
                  ? `Splitting saves R${result.saving_zar.toFixed(2)} over one store.`
                  : 'One store is already the cheapest option -- no splitting needed.'}
              </div>
            )}
          </div>
        )}
      </div>
    </section>
  )
}
