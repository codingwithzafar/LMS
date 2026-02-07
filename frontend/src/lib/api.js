import axios from 'axios'
import { useAuthStore } from '../stores/auth'

const api = axios.create({
  baseURL: (import.meta.env.VITE_API_BASE || import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"),
})

api.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.access) config.headers.Authorization = `Bearer ${auth.access}`

  // ✅ FormData yuborilganda Content-Type ni qo'ymaymiz (browser o'zi boundary bilan qo'yadi)
  if (config.data instanceof FormData) {
    delete config.headers['Content-Type']
  } else {
    config.headers['Content-Type'] = 'application/json'
  }
  return config
})

export default api
