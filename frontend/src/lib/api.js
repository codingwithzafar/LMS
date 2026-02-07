import axios from "axios";
import { useAuthStore } from "../stores/auth";

const API_BASE =
  import.meta.env.VITE_API_BASE || import.meta.env.VITE_API_URL;

if (!API_BASE) {
  throw new Error("VITE_API_BASE (or VITE_API_URL) is missing in production build");
}

const api = axios.create({ baseURL: API_BASE });

api.interceptors.request.use((config) => {
  const auth = useAuthStore();

  if (auth?.access) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${auth.access}`;
  }

  if (config.data instanceof FormData) {
    if (config.headers) delete config.headers["Content-Type"];
  } else {
    config.headers = config.headers || {};
    config.headers["Content-Type"] = "application/json";
  }

  return config;
});

export default api;
