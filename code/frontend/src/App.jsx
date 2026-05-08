import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import PhotoUpload from './pages/PhotoUpload'
import AnalysisResults from './pages/AnalysisResults'
import Recommendations from './pages/Recommendations'
import ProgressTracker from './pages/ProgressTracker'
import SkincareRoutine from './pages/SkincareRoutine'
import VideoLearning from './pages/VideoLearning'
import EventMode from './pages/EventMode'
import ConfidencePresence from './pages/ConfidencePresence'
import Experiments from './pages/Experiments'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<PhotoUpload />} />
        <Route path="analysis" element={<AnalysisResults />} />
        <Route path="recommendations" element={<Recommendations />} />
        <Route path="progress" element={<ProgressTracker />} />
        <Route path="skincare" element={<SkincareRoutine />} />
        <Route path="videos" element={<VideoLearning />} />
        <Route path="event" element={<EventMode />} />
        <Route path="confidence" element={<ConfidencePresence />} />
        <Route path="experiments" element={<Experiments />} />
      </Route>
    </Routes>
  )
}

export default App