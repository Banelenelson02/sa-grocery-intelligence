import { Navigate, Route, Routes } from 'react-router-dom'
import DashboardLayout from './layouts/DashboardLayout'
import Overview from './pages/Overview'
import Products from './pages/Products'
import ProductDetail from './pages/ProductDetail'
import PriceTrendChart from './components/PriceTrendChart'
import StoreComparisonTable from './components/StoreComparisonTable'
import InflationHeatmap from './components/InflationHeatmap'
import BasketOptimizer from './components/BasketOptimizer'

export default function App() {
  return (
    <Routes>
      <Route element={<DashboardLayout />}>
        <Route path="/" element={<Overview />} />
        <Route path="/products" element={<Products />} />
        <Route path="/products/:productId" element={<ProductDetail />} />
        <Route path="/trends" element={<PriceTrendChart />} />
        <Route path="/compare" element={<StoreComparisonTable />} />
        <Route path="/inflation" element={<InflationHeatmap />} />
        <Route path="/basket" element={<BasketOptimizer />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  )
}
