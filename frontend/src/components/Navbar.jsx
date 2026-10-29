import { NavLink } from 'react-router-dom'

const links = [
  { to: '/', label: 'Trends' },
  { to: '/compare', label: 'Compare' },
  { to: '/inflation', label: 'Inflation' },
  { to: '/basket', label: 'Basket' },
]

export default function Navbar() {
  return (
    <header className="border-b border-forest-100 bg-sand">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-5">
        <span className="font-display text-lg font-semibold text-forest-900">
          SA Grocery Intelligence
        </span>
        <nav className="flex gap-6">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.to === '/'}
              className={({ isActive }) =>
                `font-body text-sm font-medium transition-colors ${
                  isActive
                    ? 'text-forest-900'
                    : 'text-forest-400 hover:text-forest-900'
                }`
              }
            >
              {link.label}
            </NavLink>
          ))}
        </nav>
      </div>
    </header>
  )
}
