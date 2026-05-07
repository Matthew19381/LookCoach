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

export default api;
