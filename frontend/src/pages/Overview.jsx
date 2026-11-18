import { Link } from 'react-router-dom'
import {
  ArrowRight,
  ArrowLeftRight,
  ChartLine,
  ShoppingBasket,
  PackageSearch,
  ChartNoAxesCombined,
  Sprout,
} from 'lucide-react'

const features = [
  {
    title: 'Product Intelligence',
    description:
      'Explore grocery products and access their available historical price information.',
    path: '/products',
    icon: PackageSearch,
    number: '01',
  },
  {
    title: 'Price Trends',
    description:
      'Track historical price movements and compare changes across retailers.',
    path: '/trends',
    icon: ChartLine,
    number: '02',
  },
  {
    title: 'Store Comparison',
    description:
      'Compare average grocery prices across supermarkets and product categories.',
    path: '/compare',
    icon: ArrowLeftRight,
    number: '03',
  },
  {
    title: 'Inflation Analysis',
    description:
      'Explore monthly price changes across different grocery categories.',
    path: '/inflation',
    icon: ChartNoAxesCombined,
    number: '04',
  },
  {
    title: 'Basket Optimiser',
    description:
      'Compare single-store and split-store shopping options against your budget.',
    path: '/basket',
    icon: ShoppingBasket,
    number: '05',
  },
]

export default function Overview() {
  return (
    <div className="space-y-10">
      <section className="relative overflow-hidden rounded-2xl bg-forest-900 px-7 py-10 text-white sm:px-10 sm:py-12">
        <div className="relative z-10 max-w-2xl">
          <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-3 py-1.5 text-xs text-white/80">
            <Sprout size={14} />
            South African retail intelligence
          </div>

          <h1 className="font-display text-3xl font-bold leading-tight sm:text-4xl">
            Understand grocery prices.
            <span className="block text-[#E8B95D]">
              Make informed decisions.
            </span>
          </h1>

          <p className="mt-5 max-w-xl text-sm leading-7 text-white/65 sm:text-base">
            Explore historical grocery prices, compare supermarket costs,
            monitor category-level price movements and optimise your shopping
            basket.
          </p>

          <div className="mt-8 flex flex-wrap gap-3">
            <Link
              to="/products"
              className="inline-flex items-center gap-2 rounded-lg bg-marigold-400 px-5 py-3 text-sm font-semibold text-forest-900 transition hover:bg-marigold-500"
            >
              Explore products
              <ArrowRight size={17} />
            </Link>

            <Link
              to="/compare"
              className="inline-flex items-center gap-2 rounded-lg border border-white/25 px-5 py-3 text-sm font-medium text-white transition hover:bg-white/10"
            >
              Compare retailers
            </Link>
          </div>
        </div>

        <div className="pointer-events-none absolute -right-16 -top-24 h-80 w-80 rounded-full border border-white/10" />
        <div className="pointer-events-none absolute -right-4 -top-12 h-64 w-64 rounded-full border border-white/10" />
        <div className="pointer-events-none absolute -bottom-40 right-36 h-80 w-80 rounded-full border border-white/10" />
      </section>

      <section>
        <div className="mb-6 flex flex-wrap items-end justify-between gap-3">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-forest-600">
              Explore the platform
            </p>
            <h2 className="mt-2 font-display text-2xl font-bold text-forest-900">
              Your grocery intelligence workspace
            </h2>
            <p className="mt-2 text-sm text-gray-500">
              Choose an area to explore the available data and analytics.
            </p>
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {features.map((feature) => {
            const Icon = feature.icon

            return (
              <Link
                key={feature.number}
                to={feature.path}
                className="group rounded-2xl border border-[#E7E8DF] bg-white p-6 transition duration-200 hover:-translate-y-1 hover:border-forest-100 hover:shadow-lg hover:shadow-forest-900/5"
              >
                <div className="flex items-center justify-between">
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-forest-50 text-forest-900 transition group-hover:bg-forest-900 group-hover:text-white">
                    <Icon size={22} />
                  </div>
                  <span className="font-display text-xs font-semibold text-gray-300">
                    {feature.number}
                  </span>
                </div>

                <h3 className="mt-6 font-display text-lg font-bold text-forest-900">
                  {feature.title}
                </h3>

                <p className="mt-2 min-h-12 text-sm leading-6 text-gray-500">
                  {feature.description}
                </p>

                <div className="mt-5 flex items-center gap-2 text-sm font-semibold text-forest-700">
                  Explore
                  <ArrowRight
                    size={16}
                    className="transition group-hover:translate-x-1"
                  />
                </div>
              </Link>
            )
          })}
        </div>
      </section>

      <section className="rounded-2xl border border-[#E7E8DF] bg-white p-6 sm:p-8">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-[#F8F1DE] text-[#A77A25]">
            <ChartNoAxesCombined size={23} />
          </div>
          <div>
            <h2 className="font-display text-lg font-bold text-forest-900">
              Built around real price intelligence
            </h2>
            <p className="mt-1 text-sm leading-6 text-gray-500">
              The platform uses a Python ETL pipeline, PostgreSQL and a FastAPI
              backend to collect, validate, store and expose grocery price data
              for analysis.
            </p>
          </div>
        </div>
      </section>
    </div>
  )
}
