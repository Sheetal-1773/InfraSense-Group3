import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Layout } from './components/Layout'
import { Dashboard } from './pages/Dashboard'
import { Components } from './pages/Components'
import { Alerts } from './pages/Alerts'
import { AlertDetail } from './pages/AlertDetail'
import { Predictions } from './pages/Predictions'
import { Correlations } from './pages/Correlations'
import { Settings } from './pages/Settings'
import './index.css'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,
      retry: 1,
    },
  },
})

function App() {
  return (
    <BrowserRouter>
      <QueryClientProvider client={queryClient}>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/components" element={<Components />} />
            <Route path="/alerts" element={<Alerts />} />
            <Route path="/alerts/:id" element={<AlertDetail />} />
            <Route path="/predictions" element={<Predictions />} />
            <Route path="/correlations" element={<Correlations />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </Layout>
      </QueryClientProvider>
    </BrowserRouter>
  )
}

export default App