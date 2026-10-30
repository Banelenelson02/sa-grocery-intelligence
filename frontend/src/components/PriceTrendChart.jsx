import { useState, useMemo, useEffect } from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
  ResponsiveContainer,
} from 'recharts'
import { usePriceTrends } from '../hooks/usePriceTrends'
import { useProducts } from '../hooks/useProducts'
import LoadingSpinner from './LoadingSpinner'
import ErrorMessage from './ErrorMessage'

const STORE_COLORS = {
  'Pick n Pay': '#3A7359',
  Woolworths: '#20241F',
  Checkers: '#E8A33D',
  Shoprite: '#C6822A',
}

function toChartRows(points) {
  // API returns one row per (date, store). Recharts wants one row per date,
  // with each store as its own key, so a line can be drawn per store.
  const byDate = new Map()
  for (const point of points) {
    const date = point.recorded_at.slice(0, 10)
    if (!byDate.has(date)) byDate.set(date, { date })
    byDate.get(date)[point.store_name] = point.price_zar
  }
  return [...byDate.values()].sort((a, b) => a.date.localeCompare(b.date))
}

export default function PriceTrendChart() {
  const [productId, setProductId] = useState(KNOWN_PRODUCTS[0].id)
  const [weeks, setWeeks] = useState(12)
  const { data, loading, error } = usePriceTrends(productId, weeks)

  const rows = useMemo(() => toChartRows(data), [data])
  const stores = useMemo(
    () => [...new Set(data.map((p) => p.store_name))],
    [data],
  )

  return (
    <section>
      <h1 className="font-display text-2xl font-semibold text-forest-900">
        Where has this price moved?
      </h1>
      <p className="mt-1 max-w-md text-sm text-forest-600">
        Weekly price history per store, so you can see who's actually
        cheaper over time -- not just today.
      </p>

      <div className="mt-6 flex flex-wrap gap-4">
        <label className="flex flex-col gap-1 text-sm">
          <span className="font-medium text-ink">Product</span>
          <select
            value={productId}
            onChange={(e) => setProductId(Number(e.target.value))}
            className="rounded border border-forest-100 bg-white px-3 py-2 text-sm"
          >
            {products.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>
        </label>

        <label className="flex flex-col gap-1 text-sm">
          <span className="font-medium text-ink">Weeks of history</span>
          <select
            value={weeks}
            onChange={(e) => setWeeks(Number(e.target.value))}
            className="rounded border border-forest-100 bg-white px-3 py-2 text-sm"
          >
            {[4, 12, 26, 52].map((w) => (
              <option key={w} value={w}>
                {w} weeks
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="mt-8">
        {(productsLoading || loading) && <LoadingSpinner label="Loading price history" />}\n        {productsError && <ErrorMessage message={productsError} />}
        {error && <ErrorMessage message={error} />}
        {!productsLoading && !loading && !productsError && !error && rows.length === 0 && (
          <p className="py-8 text-sm text-forest-600">
            No price history for this product in the selected window.
          </p>
        )}
        {!productsLoading && !loading && !productsError && !error && rows.length > 0 && (
          <ResponsiveContainer width="100%" height={360}>
            <LineChart data={rows} margin={{ left: -10, right: 16 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#EAF1EC" />
              <XAxis dataKey="date" tick={{ fontSize: 12 }} />
              <YAxis
                tick={{ fontSize: 12 }}
                tickFormatter={(v) => `R${v}`}
                width={56}
              />
              <Tooltip
                formatter={(value) => [`R${value.toFixed(2)}`, '']}
                contentStyle={{ fontSize: 13, borderRadius: 4 }}
              />
              <Legend wrapperStyle={{ fontSize: 13 }} />
              {stores.map((store) => (
                <Line
                  key={store}
                  type="monotone"
                  dataKey={store}
                  stroke={STORE_COLORS[store] || '#3A7359'}
                  strokeWidth={2}
                  dot={false}
                  connectNulls
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
    </section>
  )
}
