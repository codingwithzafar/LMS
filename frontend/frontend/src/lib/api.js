import axios from "axios"
import { useAuthStore } from "../stores/auth"

const API_BASE = import.meta.env.VITE_API_BASE || import.meta.env.VITE_API_URL
if (!API_BASE) throw new Error("Missing VITE_API_BASE/VITE_API_URL")

const api = axios.create({ baseURL: API_BASE })

api.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.access) config.headers.Authorization = `Bearer ${auth.access}`

  if (config.data instanceof FormData) {
    delete config.headers["Content-Type"]
  } else {
    config.headers["Content-Type"] = "application/json"
  }
  return config
})

export default api
