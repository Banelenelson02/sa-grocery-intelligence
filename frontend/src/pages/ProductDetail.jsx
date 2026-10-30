
import { useEffect, useMemo, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  ArrowLeft,
  Package,
  Store,
  TrendingUp,
  CalendarDays,
  ShoppingBasket,
} from 'lucide-react'
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

import { getProducts } from '../api/products'
import { fetchTrends } from '../api/trends'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'

const currency = new Intl.NumberFormat('en-ZA', {
  style: 'currency',
  currency: 'ZAR',
})

const STORE_COLORS = {
  'Pick n Pay': '#315C42',
  Woolworths: '#26352C',
  Checkers: '#D99A35',
  Shoprite: '#B85B45',
}

export default function ProductDetail() {
  const { productId } = useParams()

  const [product, setProduct] = useState(null)
  const [prices, setPrices] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true

    async function loadProduct() {
      try {
        setLoading(true)
        setError('')

        const products = await getProducts()
        const selected = products.find(
          (item) => item.id === Number(productId)
        )

        if (!selected) {
          throw new Error('Product not found.')
        }

        const history = await fetchTrends(selected.id, 52)

        if (active) {
          setProduct(selected)
          setPrices(history)
        }
      } catch (err) {
        if (active) setError(err.message)
      } finally {
        if (active) setLoading(false)
      }
    }

    loadProduct()

    return () => {
      active = false
    }
  }, [productId])

  const latestPrices = useMemo(() => {
    const latest = new Map()

    for (const item of prices) {
      const existing = latest.get(item.store_name)

      if (
        !existing ||
        new Date(item.recorded_at) > new Date(existing.recorded_at)
      ) {
        latest.set(item.store_name, item)
      }
    }

    return [...latest.values()].sort(
      (a, b) => a.price_zar - b.price_zar
    )
  }, [prices])

  const chartData = useMemo(() => {
    const dates = new Map()

    for (const item of prices) {
      const date = item.recorded_at.slice(0, 10)

      if (!dates.has(date)) {
        dates.set(date, { date })
      }

      dates.get(date)[item.store_name] = Number(item.price_zar)
    }

    return [...dates.values()].sort(
      (a, b) => a.date.localeCompare(b.date)
    )
  }, [prices])

  if (loading) {
    return <LoadingSpinner label="Loading product intelligence..." />
  }

  if (error) {
    return (
      <div className="space-y-5">
        <Link to="/products" className="text-sm text-forest-700">
          <ArrowLeft size={16} className="inline mr-2" />
          Back to products
        </Link>
        <ErrorMessage message={error} />
      </div>
    )
  }

  if (!product) return null

  const cheapest = latestPrices[0]

  return (
    <div className="space-y-7">

      <Link
        to="/products"
        className="inline-flex items-center gap-2 text-sm font-medium text-forest-600 hover:text-forest-900"
      >
        <ArrowLeft size={17} />
        Back to products
      </Link>

      <section>
        <p className="text-xs font-semibold uppercase tracking-widest text-forest-600">
          Product Intelligence / {product.category || 'Uncategorised'}
        </p>

        <div className="mt-3 flex flex-wrap items-start justify-between gap-4">
          <div>
            <h1 className="font-display text-3xl font-bold text-forest-900">
              {product.name}
            </h1>

            <p className="mt-2 text-sm text-gray-500">
              {product.unit || 'Grocery product'} · Product #{product.id}
            </p>
          </div>

          <span className="rounded-full bg-forest-50 px-4 py-2 text-xs font-semibold text-forest-700">
            {product.category || 'Uncategorised'}
          </span>
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">

        <StatCard
          label="Lowest latest price"
          value={
            cheapest
              ? currency.format(cheapest.price_zar)
              : product.lowest_price_zar != null
                ? currency.format(product.lowest_price_zar)
                : 'N/A'
          }
          description={cheapest?.store_name || product.lowest_price_store || 'No price data'}
          icon={ShoppingBasket}
        />

        <StatCard
          label="Retailers"
          value={product.store_count}
          description="Retailers with recorded prices"
          icon={Store}
        />

        <StatCard
          label="Price records"
          value={product.price_records}
          description="Historical observations"
          icon={CalendarDays}
        />

        <StatCard
          label="Price observations"
          value={prices.length}
          description="Last 52 weeks"
          icon={TrendingUp}
        />

      </section>

      <section className="rounded-2xl border border-[#E7E8DF] bg-white p-6">
        <div className="mb-6">
          <h2 className="font-display text-xl font-bold text-forest-900">
            Historical price movement
          </h2>

          <p className="mt-1 text-sm text-gray-500">
            Track how retailers have priced this product over time.
          </p>
        </div>

        {chartData.length > 0 ? (
          <ResponsiveContainer width="100%" height={340}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E9EEE8" />

              <XAxis
                dataKey="date"
                tick={{ fontSize: 11 }}
                tickMargin={10}
              />

              <YAxis
                tickFormatter={(value) => `R${value}`}
                tick={{ fontSize: 11 }}
                width={65}
              />

              <Tooltip
                formatter={(value) => [
                  currency.format(Number(value)),
                  'Price',
                ]}
              />

              <Legend />

              {latestPrices.map((item) => (
                <Line
                  key={item.store_name}
                  type="monotone"
                  dataKey={item.store_name}
                  name={item.store_name}
                  stroke={
                    STORE_COLORS[item.store_name] || '#64856C'
                  }
                  strokeWidth={2.5}
                  dot={false}
                  connectNulls
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <p className="py-12 text-center text-sm text-gray-500">
            No historical price data available for this product.
          </p>
        )}
      </section>

      <section className="rounded-2xl border border-[#E7E8DF] bg-white p-6">
        <div className="mb-5">
          <h2 className="font-display text-xl font-bold text-forest-900">
            Retailer price comparison
          </h2>

          <p className="mt-1 text-sm text-gray-500">
            Latest recorded price at each retailer.
          </p>
        </div>

        {latestPrices.length > 0 ? (
          <div className="space-y-3">
            {latestPrices.map((item, index) => (
              <div
                key={item.store_name}
                className="flex items-center justify-between rounded-xl bg-[#F7F8F4] p-4"
              >
                <div className="flex items-center gap-3">
                  <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-white text-forest-700">
                    <Store size={17} />
                  </div>

                  <div>
                    <p className="font-semibold text-forest-900">
                      {item.store_name}
                    </p>

                    {index === 0 && (
                      <p className="text-xs font-medium text-green-700">
                        Lowest recorded price
                      </p>
                    )}
                  </div>
                </div>

                <p className="font-display text-lg font-bold text-forest-900">
                  {currency.format(Number(item.price_zar))}
                </p>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-gray-500">
            No retailer price history available.
          </p>
        )}
      </section>

    </div>
  )
}

function StatCard({ label, value, description, icon: Icon }) {
  return (
    <div className="rounded-2xl border border-[#E7E8DF] bg-white p-5">
      <div className="flex items-center justify-between">
        <p className="text-xs font-medium text-gray-500">
          {label}
        </p>

        <div className="rounded-lg bg-forest-50 p-2 text-forest-700">
          <Icon size={18} />
        </div>
      </div>

      <p className="mt-4 font-display text-2xl font-bold text-forest-900">
        {value}
      </p>

      <p className="mt-1 text-xs text-gray-500">
        {description}
      </p>
    </div>
  )
}
