import { Routes, Route, Navigate } from 'react-router-dom'
import Navbar from './components/Navbar'
import Chatbot from './components/Chatbot'
import Dashboard from './pages/Dashboard'
import RoutePlanner from './pages/RoutePlanner'
import DelayPrediction from './pages/DelayPrediction'
import LiveTrain from './pages/LiveTrain'
import Megablock from './pages/Megablock'
import SOS from './pages/SOS'
import { Login, Signup } from './pages/Auth'
import MultiRoute from './pages/MultiRoute'

export default function App() {
  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900 transition-colors duration-300">
      <Navbar />
      <main className="max-w-6xl mx-auto px-4 py-6">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/route" element={<RoutePlanner />} />
          <Route path="/multi" element={<MultiRoute />} />
          <Route path="/delay" element={<DelayPrediction />} />
          <Route path="/live" element={<LiveTrain />} />
          <Route path="/megablock" element={<Megablock />} />
          <Route path="/sos" element={<SOS />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
      <Chatbot />
    </div>
  )
}
