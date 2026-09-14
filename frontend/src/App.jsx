import { Navigate, Route, Routes } from 'react-router-dom'
import AIChat from './components/AIChat.jsx'
import CropSuggestion from './components/CropSuggestion.jsx'
import Dashboard from './components/Dashboard.jsx'
import HealthUpdates from './components/HealthUpdates.jsx'
import IoTSimulation from './components/IoTSimulation.jsx'
import NDVIAnalysis from './components/NDVIAnalysis.jsx'
import DashboardLayout from './layouts/DashboardLayout.jsx'
import DiseaseDetectionPage from './pages/DiseaseDetectionPage.jsx'
import LandingPage from './LandingPage.jsx'
import { AuthProvider, useAuth } from './contexts/AuthContext.jsx'
import './App.css'

function ProtectedRoute({ children }) {
  const { currentUser, loading } = useAuth()
  
  if (loading) {
    return <div className="flex h-screen items-center justify-center bg-myanglow-navy"><div className="text-white">Loading...</div></div>
  }
  
  if (!currentUser) {
    return <Navigate to="/?auth=signin" replace />
  }
  
  return children
}

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        }>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/ndvi-analysis" element={<NDVIAnalysis />} />
          <Route path="/crop-suggestion" element={<CropSuggestion />} />
          <Route path="/disease-detection" element={<DiseaseDetectionPage />} />
          <Route path="/ai-chat" element={<AIChat />} />
          <Route path="/health-updates" element={<HealthUpdates />} />
          <Route path="/iot-simulation" element={<IoTSimulation />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AuthProvider>
  )
}

export default App
