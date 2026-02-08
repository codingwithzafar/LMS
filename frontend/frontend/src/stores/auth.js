import { defineStore } from 'pinia'
import api from '../lib/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    access: localStorage.getItem('access') || '',
    refresh: localStorage.getItem('refresh') || '',
    user: null,
    ready: false,
  }),
  getters: {
    isAuthenticated: (s) => !!s.access,
  },
  actions: {
    async bootstrap() {
      try {
        if (this.access) {
          const { data } = await api.get('/api/auth/me/')
          this.user = data
        }
      } catch (e) {
        this.access = ''
        this.refresh = ''
        this.user = null
        localStorage.removeItem('access')
        localStorage.removeItem('refresh')
      } finally {
        this.ready = true
      }
    },
    async login(username, password) {
      const { data } = await api.post('/api/auth/login/', { username, password })
      this.access = data.access
      this.refresh = data.refresh
      localStorage.setItem('access', this.access)
      localStorage.setItem('refresh', this.refresh)
      const me = await api.get('/api/auth/me/')
      this.user = me.data
    },
    logout() {
      this.access = ''
      this.refresh = ''
      this.user = null
      localStorage.removeItem('access')
      localStorage.removeItem('refresh')
      window.location.href = '/login'
    }
  }
})
