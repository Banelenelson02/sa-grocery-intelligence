import { Navigate, Route, Routes } from 'react-router-dom'
import DashboardLayout from './layouts/DashboardLayout'
import Overview from './pages/Overview'
import PriceTrendChart from './components/PriceTrendChart'
import StoreComparisonTable from './components/StoreComparisonTable'
import InflationHeatmap from './components/InflationHeatmap'
import BasketOptimizer from './components/BasketOptimizer'
import ProductDetail from './pages/ProductDetail'
import Products from './pages/Products'

function ProductsPlaceholder() {
  return (
    <section className="rounded-2xl border border-[#E7E8DF] bg-white p-8">
      <h1 className="font-display text-2xl font-bold text-forest-900">
        Product Intelligence
      </h1>
      <p className="mt-3 text-sm text-gray-500">
        The searchable product catalogue is the next feature we're building.
      </p>
    </section>
  )
}

export default function App() {
  return (
    <Routes>
      <Route element={<DashboardLayout />}>
        <Route path="/" element={<Overview />} />
        <Route path="/products" element={<Products />} />
        <Route path="/trends" element={<PriceTrendChart />} />
        <Route path="/compare" element={<StoreComparisonTable />} />
        <Route path="/inflation" element={<InflationHeatmap />} />
        <Route path="/basket" element={<BasketOptimizer />} />
        <Route path="*" element={<Navigate to="/" replace />} />
	<Route path="/products/:productId" element={<ProductDetail />} />
      </Route>
    </Routes>
  )
}
