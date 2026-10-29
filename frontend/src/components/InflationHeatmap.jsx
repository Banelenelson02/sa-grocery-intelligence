import { useState, useEffect, useMemo } from 'react'
import { fetchInflation } from '../api/inflation'
import LoadingSpinner from './LoadingSpinner'
import ErrorMessage from './ErrorMessage'

function cellColor(pctChange) {
  if (pctChange == null) return '#F4F4F1' // no data yet for this cell
  if (pctChange > 3) return '#C6822A' // sharp increase
  if (pctChange > 0) return '#F0B44D' // mild increase
  if (pctChange > -3) return '#CBDCD1' // mild decrease
  return '#3A7359' // sharp decrease
}

export default function InflationHeatmap() {
  const [months, setMonths] = useState(6)
  const [points, setPoints] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)

    fetchInflation(months)
      .then((data) => {
        if (!cancelled) setPoints(data)
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
  }, [months])

  const { categories, monthLabels, grid } = useMemo(() => {
    const categories = [...new Set(points.map((p) => p.category))]
    const monthLabels = [
      ...new Set(points.map((p) => p.month.slice(0, 7))),
    ].sort()

    const grid = {}
    for (const p of points) {
      grid[`${p.category}|${p.month.slice(0, 7)}`] = p.pct_change
    }

    return { categories, monthLabels, grid }
  }, [points])

  return (
    <section>
      <h1 className="font-display text-2xl font-semibold text-forest-900">
        Which categories are inflating fastest?
      </h1>
      <p className="mt-1 max-w-md text-sm text-forest-600">
        Month-over-month average price change per category, across all
        stores.
      </p>

      <label className="mt-6 flex max-w-xs flex-col gap-1 text-sm">
        <span className="font-medium text-ink">Time window</span>
        <select
          value={months}
          onChange={(e) => setMonths(Number(e.target.value))}
          className="rounded border border-forest-100 bg-white px-3 py-2 text-sm"
        >
          {[3, 6, 12, 24].map((m) => (
            <option key={m} value={m}>
              {m} months
            </option>
          ))}
        </select>
      </label>

      <div className="mt-8">
        {loading && <LoadingSpinner label="Loading inflation data" />}
        {error && <ErrorMessage message={error} />}
        {!loading && !error && categories.length === 0 && (
          <p className="py-8 text-sm text-forest-600">
            Not enough price history yet to compute inflation.
          </p>
        )}
        {!loading && !error && categories.length > 0 && (
          <div className="overflow-x-auto">
            <table className="border-collapse text-sm">
              <thead>
                <tr>
                  <th className="py-2 pr-4 text-left font-medium text-forest-600">
                    Category
                  </th>
                  {monthLabels.map((m) => (
                    <th
                      key={m}
                      className="px-2 py-2 text-center font-medium text-forest-600"
                    >
                      {m}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {categories.map((cat) => (
                  <tr key={cat}>
                    <td className="py-1 pr-4 font-medium text-ink">{cat}</td>
                    {monthLabels.map((m) => {
                      const value = grid[`${cat}|${m}`]
                      return (
                        <td key={m} className="p-1">
                          <div
                            className="flex h-12 w-16 items-center justify-center rounded text-xs font-medium text-ink"
                            style={{ backgroundColor: cellColor(value) }}
                            title={
                              value != null
                                ? `${value > 0 ? '+' : ''}${value.toFixed(1)}%`
                                : 'No data'
                            }
                          >
                            {value != null
                              ? `${value > 0 ? '+' : ''}${value.toFixed(1)}%`
                              : '–'}
                          </div>
                        </td>
                      )
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  )
}
