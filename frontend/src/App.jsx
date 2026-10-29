import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import PriceTrendChart from './components/PriceTrendChart'
import StoreComparisonTable from './components/StoreComparisonTable'
import InflationHeatmap from './components/InflationHeatmap'
import BasketOptimizer from './components/BasketOptimizer'

export default function App() {
  return (
    <div className="min-h-screen bg-sand">
      <Navbar />
      <main className="mx-auto max-w-5xl px-6 py-10">
        <Routes>
          <Route path="/" element={<PriceTrendChart />} />
          <Route path="/compare" element={<StoreComparisonTable />} />
          <Route path="/inflation" element={<InflationHeatmap />} />
          <Route path="/basket" element={<BasketOptimizer />} />
        </Routes>
      </main>
    </div>
  )
}
