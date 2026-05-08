import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8003",
  timeout: 60000,
});

api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error("API Error:", error);
    return Promise.reject(error);
  }
);

export const getUserId = () => {
  let id = localStorage.getItem("lookcoach_user_id");
  if (!id) {
    id = Date.now().toString();
    localStorage.setItem("lookcoach_user_id", id);
  }
  return parseInt(id);
};

export const uploadPhoto = (file, photoType) => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("photo_type", photoType);
  formData.append("user_id", getUserId());
  return api.post("/api/photos/upload", formData).then(r => r);
};

export const getPhotos = () =>
  api.get(`/api/photos/?user_id=${getUserId()}`);

export const deletePhoto = (id) =>
  api.delete(`/api/photos/${id}`);

export const getAnalysis = () =>
  api.get(`/api/analysis/latest?user_id=${getUserId()}`);

export const analyzePhoto = (photoId) =>
  api.post(`/api/analysis/analyze/${photoId}`);

export const getRecommendations = (limit = 10) =>
  api.get(`/api/recommendations/?limit=${limit}`);

export const getTimeline = () =>
  api.get(`/api/progress/timeline?user_id=${getUserId()}`);

export const comparePhotos = (beforeId, afterId) =>
  api.post(`/api/progress/compare`, {
    photo_before_id: parseInt(beforeId),
    photo_after_id: parseInt(afterId),
  });

export const getProfile = () =>
  api.get(`/api/profile/?user_id=${getUserId()}`);

export const updateProfile = (data) =>
  api.put(`/api/profile/?user_id=${getUserId()}`, data);

export const getSkincareRoutine = () =>
  api.get(`/api/skincare/routine?user_id=${getUserId()}`);

export const getRecommendedVideos = () =>
  api.get(`/api/video-learning/videos/recommended?user_id=${getUserId()}`);

export const searchVideos = (query) =>
  api.get(`/api/video-learning/videos?query=${encodeURIComponent(query)}`);

export const generateEventPlan = (eventDate, eventType) =>
  api.post(`/api/event-mode/plan`, {
    event_date: eventDate,
    event_type: eventType,
  });

export const getEventTips = (eventType) =>
  api.get(`/api/event-mode/tips/${eventType}`);

export const getConfidenceAnalysis = () =>
  api.get(`/api/confidence/analyze?user_id=${getUserId()}`);

export const getActionPlan = () =>
  api.get(`/api/confidence/action-plan`);

export const getAttractivenessImpact = (confidenceScore = 70, presenceScore = 70) =>
  api.get(`/api/confidence/attractiveness-impact?confidence_score=${confidenceScore}&presence_score=${presenceScore}`);

// Experiments
export const getExperimentTemplates = () =>
  api.get(`/api/experiments/templates`);

export const startExperiment = (templateId, customName) =>
  api.post(`/api/experiments/start`, {
    template_id: templateId,
    custom_name: customName,
    user_id: getUserId(),
  });

export const getExperiment = (experimentId) =>
  api.get(`/api/experiments/${experimentId}`);

export const logDaily = (experimentId, day, rating, notes) =>
  api.post(`/api/experiments/log`, {
    experiment_id: experimentId,
    day,
    rating,
    notes,
  });

export const getResults = (experimentId) =>
  api.get(`/api/experiments/${experimentId}/results`);

export const getActiveExperiments = () =>
  api.get(`/api/experiments/active?user_id=${getUserId()}`);

export const finishExperiment = (experimentId) =>
  api.post(`/api/experiments/${experimentId}/finish`);

// Aesthetic Training
export const getAvailablePlans = () =>
  api.get(`/api/aesthetic-training/plans`);

export const generateTrainingPlan = (goal = "v_taper") =>
  api.post(`/api/aesthetic-training/plan`, { goal });

export const analyzePhysique = (measurements) =>
  api.post(`/api/aesthetic-training/analyze`, { measurements });

// Posture Correction
export const getPostureIssues = () =>
  api.get(`/api/posture/issues`);

export const detectPostureIssues = (analysis) =>
  api.post(`/api/posture/detect`, { analysis });

export const getCorrectionPlan = (issueId) =>
  api.get(`/api/posture/correction/${issueId}`);

export const fullPostureAssessment = (analysis) =>
  api.post(`/api/posture/assess`, { analysis });

// Nutrition for Looks
export const getNutritionFactors = () =>
  api.get(`/api/nutrition/factors`);

export const getNutritionRecommendations = () =>
  api.get(`/api/nutrition/recommendations`);

export const getMealPlan = (planType = "pre_event") =>
  api.get(`/api/nutrition/meal-plan/${planType}`);

export const analyzeDiet = (dietLog) =>
  api.post(`/api/nutrition/analyze`, { diet_log: dietLog });

// Sleep Optimization
export const getSleepFactors = () =>
  api.get(`/api/sleep/factors`);

export const analyzeSleep = (sleepData) =>
  api.post(`/api/sleep/analyze`, { sleep_data: sleepData });

export const getPreEventSleepTips = (eventType = "general") =>
  api.get(`/api/sleep/pre-event/${eventType}`);

// Stress Management
export const getStressEffects = () =>
  api.get(`/api/stress/effects`);

export const getRelaxationTechniques = () =>
  api.get(`/api/stress/techniques`);

export const analyzeStress = (stressData) =>
  api.post(`/api/stress/analyze`, { stress_data: stressData });

export default api;
