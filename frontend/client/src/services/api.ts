// src/services/api.ts
import axios from "axios";

/**
 * Shared Axios instance for all API calls.
 * Uses VITE_API_BASE_URL if defined, otherwise falls back to local dev URL.
 */
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api",
});

export default api;
