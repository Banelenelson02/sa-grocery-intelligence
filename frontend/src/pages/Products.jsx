import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Search, Package, ArrowUpRight, Store, Tags, RefreshCw,
  ShoppingBasket, Leaf, X,
} from 'lucide-react'
import { getProducts } from '../api/products'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'

const currency = new Intl.NumberFormat('en-ZA', { style: 'currency', currency: 'ZAR' })
const categoryIcons = { Staples: ShoppingBasket, Dairy: Package, Meat: Tags, Produce: Leaf }
const categoryImages = {
  Staples: '/images/staples.jpg',
  Dairy: '/images/dairy.jpg',
  Meat: '/images/meat.jpg',
  Produce: '/images/produce.jpg',
}

function ProductCard({ product }) {
  const Icon = categoryIcons[product.category] || Package
  return (
    <article className="group flex flex-col overflow-hidden rounded-2xl border border-[#E7E8DF] bg-white transition duration-300 hover:-translate-y-1 hover:border-[#CBDCD1] hover:shadow-xl hover:shadow-forest-900/5">
      <div className="relative h-48 overflow-hidden bg-[#EAF0E9]">
        {categoryImages[product.category] ? (
          <img
            src={categoryImages[product.category]}
            alt={`${product.category} groceries`}
            loading="lazy"
            className="h-full w-full object-cover transition duration-500 group-hover:scale-105"
          />
        ) : (
          <div className="flex h-full items-center justify-center bg-gradient-to-br from-[#E8EFE7] via-[#F5F5EF] to-[#DCE8DD] text-forest-700">
            <Icon size={42} strokeWidth={1.4} />
          </div>
        )}
        <span className="absolute left-4 top-4 rounded-full bg-white/90 px-3 py-1 text-[10px] font-semibold uppercase tracking-wider text-forest-700">{product.category || 'Uncategorised'}</span>
        <span className="absolute right-4 top-4 text-xs font-medium text-gray-400">#{product.id}</span>
      </div>
      <div className="flex flex-1 flex-col p-5">
        <h3 className="font-display text-base font-bold leading-snug text-forest-900">{product.name}</h3>
        <p className="mt-1 text-xs text-gray-400">{product.unit || product.subcategory || 'Grocery product'}</p>
        <div className="my-5 rounded-xl bg-[#F8F8F4] p-4">
          <p className="text-[10px] font-semibold uppercase tracking-wider text-gray-400">Lowest latest recorded price</p>
          {product.lowest_price_zar != null ? <>
            <p className="mt-1 font-display text-2xl font-bold text-forest-900">{currency.format(Number(product.lowest_price_zar))}</p>
            <p className="mt-1 flex items-center gap-1.5 text-xs text-forest-600"><Store size={13} />{product.lowest_price_store}</p>
          </> : <p className="mt-2 text-sm text-gray-400">No price data available</p>}
        </div>
        <div className="mt-auto flex items-center justify-between border-t border-[#F0F0EA] pt-4">
          <div>
            <p className="text-xs font-semibold text-forest-900">{product.store_count} {product.store_count === 1 ? 'retailer' : 'retailers'}</p>
            <p className="mt-1 text-[10px] text-gray-400">{product.price_records} historical records</p>
          </div>
          <Link to={`/products/${product.id}`} aria-label={`View ${product.name}`} className="flex h-9 w-9 items-center justify-center rounded-full bg-forest-50 text-forest-900 transition hover:bg-forest-900 hover:text-white">
            <ArrowUpRight size={18} />
          </Link>
        </div>
      </div>
    </article>
  )
}

export default function Products() {
  const [products, setProducts] = useState([])
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState('All')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    const timer = setTimeout(async () => {
      setLoading(true)
      setError('')
      try {
        const data = await getProducts()
        if (active) setProducts(data)
      } catch (err) {
        if (active) setError(err.message || 'Unable to load products.')
      } finally {
        if (active) setLoading(false)
      }
    }, search ? 200 : 0)
    return () => { active = false; clearTimeout(timer) }
  }, [search])

  const categories = useMemo(() => [
    'All',
    ...new Set(products.map((p) => p.category).filter(Boolean)),
    ...(products.some((p) => !p.category) ? ['Uncategorised'] : []),
  ], [products])

  const visibleProducts = products.filter((product) => {
    const matchesSearch = product.name.toLowerCase().includes(search.trim().toLowerCase())
    const matchesCategory = category === 'All' ||
      (category === 'Uncategorised' ? !product.category : product.category === category)
    return matchesSearch && matchesCategory
  })

  return (
    <div className="space-y-8">
      <section className="relative isolate overflow-hidden rounded-2xl bg-forest-900 px-7 py-9 text-white sm:px-10 sm:py-11">
        <img src="/images/grocery-hero.jpg" alt="" aria-hidden="true" className="absolute inset-0 -z-10 h-full w-full object-cover opacity-30" />
        <div className="absolute inset-0 -z-10 bg-gradient-to-r from-[#173D2B] via-[#173D2B]/90 to-[#173D2B]/35" />
        <div className="relative z-10 max-w-2xl">
          <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/10 px-3 py-1.5 text-xs text-white/75"><Leaf size={14} />Product intelligence</div>
          <h1 className="font-display text-3xl font-bold tracking-tight sm:text-4xl">Know what your groceries cost.</h1>
          <p className="mt-4 max-w-xl text-sm leading-7 text-white/65 sm:text-base">Explore grocery products, compare the latest available retailer prices and understand how everyday shopping costs change.</p>
          <div className="mt-7 flex flex-wrap gap-6">
            <div><p className="font-display text-2xl font-bold">{products.length}</p><p className="mt-1 text-xs text-white/55">Products found</p></div>
            <div><p className="font-display text-2xl font-bold">{products.reduce((sum, p) => sum + Number(p.price_records || 0), 0)}</p><p className="mt-1 text-xs text-white/55">Price records</p></div>
          </div>
        </div>
        <div className="pointer-events-none absolute -right-20 -top-28 h-80 w-80 rounded-full border border-white/10" />
        <div className="pointer-events-none absolute -right-8 -top-12 h-64 w-64 rounded-full border border-white/10" />
      </section>

      <section className="space-y-5">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-forest-600">Explore the catalogue</p>
          <h2 className="mt-2 font-display text-2xl font-bold text-forest-900">Find your products</h2>
          <p className="mt-2 text-sm text-gray-500">Search and explore products using the latest available price data.</p>
        </div>
        <div className="relative">
          <Search size={19} className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" />
          <input type="search" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search bread, milk, rice..." className="w-full rounded-xl border border-[#E7E8DF] bg-white py-4 pl-12 pr-12 text-sm text-forest-900 shadow-sm outline-none transition placeholder:text-gray-400 focus:border-forest-400 focus:ring-4 focus:ring-forest-50" />
          {search && <button type="button" onClick={() => setSearch('')} aria-label="Clear search" className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-forest-900"><X size={18} /></button>}
        </div>
        <div className="flex flex-wrap gap-2">
          {categories.map((item) => <button key={item} type="button" onClick={() => setCategory(item)} className={`rounded-full px-4 py-2 text-xs font-semibold transition ${category === item ? 'bg-forest-900 text-white shadow-sm' : 'border border-[#E7E8DF] bg-white text-gray-500 hover:border-forest-200 hover:text-forest-900'}`}>{item}</button>)}
        </div>
        <div className="flex items-center justify-between border-b border-[#E7E8DF] pb-4">
          <p className="text-sm text-gray-500">Showing <span className="font-semibold text-forest-900">{visibleProducts.length}</span> products</p>
          <button type="button" onClick={() => { setSearch(''); setCategory('All') }} className="flex items-center gap-1.5 text-xs font-semibold text-forest-600 hover:text-forest-900"><RefreshCw size={13} />Reset filters</button>
        </div>
        {loading ? <div className="flex min-h-56 items-center justify-center"><LoadingSpinner /></div>
          : error ? <ErrorMessage message={error} />
          : visibleProducts.length === 0 ? <div className="rounded-2xl border border-dashed border-[#D8DED5] bg-white px-6 py-16 text-center"><Package size={35} className="mx-auto text-forest-400" /><h3 className="mt-4 font-display text-lg font-bold text-forest-900">No products found</h3><p className="mt-2 text-sm text-gray-500">Try another search term or select a different category.</p></div>
          : <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-3">{visibleProducts.map((product) => <ProductCard key={product.id} product={product} />)}</div>}
      </section>
    </div>
  )
}
