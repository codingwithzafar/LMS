import axios from "axios";
import { useAuthStore } from "../stores/auth";

// ✅ API base URL: production’da majburiy, dev’da fallback bor
const API_BASE =
  import.meta.env.VITE_API_BASE ||
  import.meta.env.VITE_API_URL ||
  (import.meta.env.DEV ? "http://127.0.0.1:8000" : "");

if (!API_BASE) {
  // production’da env yo‘q bo‘lsa, darrov ko‘rinadigan xato
  throw new Error(
    "API base URL is missing. Set VITE_API_BASE (or VITE_API_URL) in Netlify env."
  );
}

const api = axios.create({
  baseURL: API_BASE,
  // timeout: 20000, // xohlasangiz
});

api.interceptors.request.use((config) => {
  const auth = useAuthStore();

  // ✅ token bo‘lsa yuboramiz
  if (auth?.access) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${auth.access}`;
  }

  // ✅ FormData bo‘lsa Content-Type qo‘ymaymiz
  if (config.data instanceof FormData) {
    if (config.headers) delete config.headers["Content-Type"];
  } else {
    config.headers = config.headers || {};
    config.headers["Content-Type"] = "application/json";
  }

  return config;
});

export default api;
