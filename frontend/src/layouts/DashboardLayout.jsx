import { useState } from 'react'
import { NavLink, Outlet } from 'react-router-dom'
import {
  LayoutDashboard,
  PackageSearch,
  ArrowLeftRight,
  ChartLine,
  ShoppingBasket,
  Menu,
  X,
  Sprout,
  ChevronRight,
} from 'lucide-react'

const navigation = [
  { label: 'Overview', path: '/', icon: LayoutDashboard },
  { label: 'Products', path: '/products', icon: PackageSearch },
  { label: 'Price Trends', path: '/trends', icon: ChartLine },
  { label: 'Store Comparison', path: '/compare', icon: ArrowLeftRight },
  { label: 'Inflation', path: '/inflation', icon: ChartLine },
  { label: 'Basket Optimiser', path: '/basket', icon: ShoppingBasket },
]

function Sidebar({ closeMenu }) {
  return (
    <aside className="flex h-full w-72 flex-col bg-forest-900 text-white">
      <div className="flex h-20 items-center gap-3 border-b border-white/10 px-6">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-marigold-400 text-forest-900">
          <Sprout size={23} />
        </div>
        <div>
          <h1 className="font-display text-base font-bold tracking-tight">
            SA Grocery
          </h1>
          <p className="text-xs text-white/60">Intelligence Platform</p>
        </div>
      </div>

      <div className="px-5 pt-8">
        <p className="mb-3 px-3 text-[10px] font-semibold uppercase tracking-[0.18em] text-white/40">
          Workspace
        </p>

        <nav className="space-y-1">
          {navigation.map(({ label, path, icon: Icon }) => (
            <NavLink
              key={path}
              to={path}
              end={path === '/'}
              onClick={closeMenu}
              className={({ isActive }) =>
                `group flex items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium transition ${
                  isActive
                    ? 'bg-white text-forest-900 shadow-sm'
                    : 'text-white/70 hover:bg-white/10 hover:text-white'
                }`
              }
            >
              <Icon size={19} />
              <span>{label}</span>
              <ChevronRight
                size={15}
                className="ml-auto opacity-0 transition group-[.active]:opacity-100"
              />
            </NavLink>
          ))}
        </nav>
      </div>

      <div className="mt-auto border-t border-white/10 p-5">
        <div className="rounded-xl bg-white/10 p-4">
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-emerald-400" />
            <span className="text-xs font-medium text-white">Data platform</span>
          </div>
          <p className="mt-2 text-xs leading-relaxed text-white/50">
            Grocery price analytics and retail intelligence for South Africa.
          </p>
        </div>
        <p className="mt-5 text-center text-[10px] text-white/35">
          SA Grocery Intelligence · 2026
        </p>
      </div>
    </aside>
  )
}

export default function DashboardLayout() {
  const [menuOpen, setMenuOpen] = useState(false)

  return (
    <div className="min-h-screen bg-[#F5F5F0] lg:flex">
      <div className="hidden lg:block">
        <div className="fixed inset-y-0 left-0 z-30">
          <Sidebar />
        </div>
      </div>

      {menuOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <button
            aria-label="Close navigation"
            className="absolute inset-0 bg-black/40"
            onClick={() => setMenuOpen(false)}
          />
          <div className="relative h-full w-72">
            <button
              onClick={() => setMenuOpen(false)}
              className="absolute right-3 top-5 z-10 rounded-lg p-2 text-white hover:bg-white/10"
              aria-label="Close menu"
            >
              <X size={20} />
            </button>
            <Sidebar closeMenu={() => setMenuOpen(false)} />
          </div>
        </div>
      )}

      <div className="min-w-0 flex-1 lg:ml-72">
        <header className="sticky top-0 z-20 flex h-20 items-center justify-between border-b border-[#E7E8DF] bg-white/95 px-5 backdrop-blur sm:px-8">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setMenuOpen(true)}
              className="rounded-lg p-2 text-forest-900 hover:bg-forest-50 lg:hidden"
              aria-label="Open navigation"
            >
              <Menu size={22} />
            </button>
            <div>
              <p className="text-xs text-gray-400">SA / Grocery Intelligence</p>
              <p className="font-display text-sm font-semibold text-forest-900">
                Retail insights workspace
              </p>
            </div>
          </div>

          <div className="hidden items-center gap-3 sm:flex">
            <div className="flex items-center gap-2 rounded-full border border-[#E7E8DF] bg-[#F8F8F4] px-3 py-2">
              <span className="h-2 w-2 rounded-full bg-emerald-500" />
              <span className="text-xs font-medium text-forest-700">
                Analytics available
              </span>
            </div>
          </div>
        </header>

        <main className="mx-auto max-w-[1500px] px-5 py-8 sm:px-8 sm:py-10">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
