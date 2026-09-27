import axios from "axios";

const api = axios.create({
  // relative by default: works through the Vite proxy on desktop AND from a phone on the LAN
  // ("http://localhost:8010" pointed a phone at itself)
  baseURL: import.meta.env.VITE_API_URL ?? "",
  timeout: 60000,
});

api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error("API Error:", error);
    return Promise.reject(error);
  }
);

// Single-user ecosystem: 1 = PRIMARY_USER_ID of the System-Glowny hub. The old
// default Date.now() id made hub events and directives refer to a different person.
export const getUserId = () => {
  let id = localStorage.getItem("lookcoach_user_id");
  if (!id || parseInt(id) > 1e9) {
    id = "1";
    localStorage.setItem("lookcoach_user_id", id);
  }
  return parseInt(id);
};

export const uploadPhoto = (file, photoType) => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("photo_type", photoType);
  formData.append("user_id", getUserId());
  return api.post("/api/v1/photos/upload", formData).then(r => r);
};

export const getPhotos = () =>
  api.get(`/api/v1/photos/?user_id=${getUserId()}`);

export const deletePhoto = (id) =>
  api.delete(`/api/v1/photos/${id}`);

export const getAnalysis = () =>
  api.get(`/api/v1/analysis/latest?user_id=${getUserId()}`);

export const analyzePhoto = (photoId) =>
  api.post(`/api/v1/analysis/analyze/${photoId}`);

export const getRecommendations = (limit = 10) =>
  api.get(`/api/v1/recommendations/?limit=${limit}`);

export const getTimeline = () =>
  api.get(`/api/v1/progress/timeline?user_id=${getUserId()}`);

export const comparePhotos = (beforeId, afterId) =>
  api.post(`/api/v1/progress/compare`, {
    photo_before_id: parseInt(beforeId),
    photo_after_id: parseInt(afterId),
  });

export const getProfile = () =>
  api.get(`/api/v1/profile/?user_id=${getUserId()}`);

export const updateProfile = (data) =>
  api.put(`/api/v1/profile/?user_id=${getUserId()}`, data);

export const getSkincareRoutine = () =>
  api.get(`/api/v1/skincare/routine?user_id=${getUserId()}`);

export const getRecommendedVideos = () =>
  api.get(`/api/v1/video-learning/videos/recommended?user_id=${getUserId()}`);

export const searchVideos = (query) =>
  api.get(`/api/v1/video-learning/videos?query=${encodeURIComponent(query)}`);

export const generateEventPlan = (eventDate, eventType) =>
  api.post(`/api/v1/event-mode/plan`, {
    event_date: eventDate,
    event_type: eventType,
  });

export const getEventTips = (eventType) =>
  api.get(`/api/v1/event-mode/tips/${eventType}`);

export const getConfidenceAnalysis = () =>
  api.get(`/api/v1/confidence/analyze?user_id=${getUserId()}`);

export const getActionPlan = () =>
  api.get(`/api/v1/confidence/action-plan`);

export const getAttractivenessImpact = (confidenceScore = 70, presenceScore = 70) =>
  api.get(`/api/v1/confidence/attractiveness-impact?confidence_score=${confidenceScore}&presence_score=${presenceScore}`);

// Experiments
export const getExperimentTemplates = () =>
  api.get(`/api/v1/experiments/templates`);

export const startExperiment = (templateId, customName) =>
  api.post(`/api/v1/experiments/start`, {
    template_id: templateId,
    custom_name: customName,
    user_id: getUserId(),
  });

export const getExperiment = (experimentId) =>
  api.get(`/api/v1/experiments/${experimentId}`);

export const logDaily = (experimentId, day, rating, notes) =>
  api.post(`/api/v1/experiments/log`, {
    experiment_id: experimentId,
    day,
    rating,
    notes,
  });

export const getResults = (experimentId) =>
  api.get(`/api/v1/experiments/${experimentId}/results`);

export const getActiveExperiments = () =>
  api.get(`/api/v1/experiments/active?user_id=${getUserId()}`);

export const finishExperiment = (experimentId) =>
  api.post(`/api/v1/experiments/${experimentId}/finish`);

// Aesthetic Training
export const getAvailablePlans = () =>
  api.get(`/api/v1/aesthetic-training/plans`);

export const generateTrainingPlan = (goal = "v_taper") =>
  api.post(`/api/v1/aesthetic-training/plan`, { goal });

export const analyzePhysique = (measurements) =>
  api.post(`/api/v1/aesthetic-training/analyze`, { measurements });

// Posture Correction
export const getPostureIssues = () =>
  api.get(`/api/v1/posture/issues`);

export const detectPostureIssues = (analysis) =>
  api.post(`/api/v1/posture/detect`, { analysis });

export const getCorrectionPlan = (issueId) =>
  api.get(`/api/v1/posture/correction/${issueId}`);

export const fullPostureAssessment = (analysis) =>
  api.post(`/api/v1/posture/assess`, { analysis });

// Nutrition for Looks
export const getNutritionFactors = () =>
  api.get(`/api/v1/nutrition/factors`);

export const getNutritionRecommendations = () =>
  api.get(`/api/v1/nutrition/recommendations`);

export const getMealPlan = (planType = "pre_event") =>
  api.get(`/api/v1/nutrition/meal-plan/${planType}`);

export const analyzeDiet = (dietLog) =>
  api.post(`/api/v1/nutrition/analyze`, { diet_log: dietLog });

// Sleep Optimization
export const getSleepFactors = () =>
  api.get(`/api/v1/sleep/factors`);

export const analyzeSleep = (sleepData) =>
  api.post(`/api/v1/sleep/analyze`, { sleep_data: sleepData });

export const getPreEventSleepTips = (eventType = "general") =>
  api.get(`/api/v1/sleep/pre-event/${eventType}`);

// Stress Management
export const getStressEffects = () =>
  api.get(`/api/v1/stress/effects`);

export const getRelaxationTechniques = () =>
  api.get(`/api/v1/stress/techniques`);

export const analyzeStress = (stressData) =>
  api.post(`/api/v1/stress/analyze`, { stress_data: stressData });

export default api;

// ── My skincare products (label scan / pasted INCI), usage, reactions, rotation ──
const uid = () => `user_id=${getUserId()}`;
export const scanProductLabel = (file) => {
  const fd = new FormData();
  fd.append("file", file);
  return api.post(`/api/v1/skincare/products/scan?${uid()}`, fd);
};
export const parseProductText = (text, name = "") =>
  api.post(`/api/v1/skincare/products/parse?${uid()}`, { text, name });
export const saveProduct = (product) => api.post(`/api/v1/skincare/products?${uid()}`, product);
export const getProducts = () => api.get(`/api/v1/skincare/products?${uid()}`);
export const deleteProduct = (id) => api.delete(`/api/v1/skincare/products/${id}?${uid()}`);
export const logProductUsage = (productIds) =>
  api.post(`/api/v1/skincare/usage/log?${uid()}`, { product_ids: productIds });
export const getMyRotation = () => api.get(`/api/v1/skincare/rotation/mine?${uid()}`);
export const logSkinReaction = (ingredient, reaction, severity) =>
  api.post(`/api/v1/skincare/reaction/log?${uid()}&ingredient=${encodeURIComponent(ingredient)}&reaction=${encodeURIComponent(reaction)}&severity=${severity}`);

// ── Consistency Tracker (LC-7) - the page imported these, but they never existed ──
const q = (params) => new URLSearchParams(
  Object.fromEntries(Object.entries({ ...params, user_id: getUserId() }).filter(([, v]) => v !== undefined && v !== null && v !== ""))
).toString();
export const logAdherence = ({ protocol_type, completed, date, difficulty_level, notes }) =>
  api.post(`/api/v1/consistency/adherence/log?${q({ protocol_type, completed, date, difficulty_level, notes })}`);
export const getAdherenceHistory = (protocol_type, days = 28) =>
  api.get(`/api/v1/consistency/adherence/history?${q({ protocol_type, days })}`);
export const getAdherenceRate = (protocol_type, days = 28) =>
  api.get(`/api/v1/consistency/adherence/rate?${q({ protocol_type, days })}`);
export const getRecommendedDifficulty = (protocol_type, current_difficulty = "full") =>
  api.get(`/api/v1/consistency/difficulty/recommended?${q({ protocol_type, current_difficulty })}`);
export const getAllProtocolsStatus = () => api.get(`/api/v1/consistency/protocols/status?${q({})}`);
export const getConsistencySummary = (days = 28) => api.get(`/api/v1/consistency/summary?${q({ days })}`);
export const getMinimumEffectiveProtocol = (protocol_type, difficulty = "full") =>
  api.get(`/api/v1/consistency/minimum-effective/${protocol_type}?${q({ difficulty })}`);
export const recalculateMetrics = (days = 28) => api.post(`/api/v1/consistency/recalculate?${q({ days })}`);
export const getPatternAlert = () => api.get(`/api/v1/consistency/pattern-alert?${q({})}`);
