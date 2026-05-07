import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import PhotoUpload from './pages/PhotoUpload'
import AnalysisResults from './pages/AnalysisResults'
import Recommendations from './pages/Recommendations'
import ProgressTracker from './pages/ProgressTracker'
import SkincareRoutine from './pages/SkincareRoutine'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<PhotoUpload />} />
        <Route path="analysis" element={<AnalysisResults />} />
        <Route path="recommendations" element={<Recommendations />} />
        <Route path="progress" element={<ProgressTracker />} />
        <Route path="skincare" element={<SkincareRoutine />} />
      </Route>
    </Routes>
  )
}

export default App