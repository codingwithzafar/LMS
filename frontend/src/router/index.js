import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import HomeView from '../views/HomeView.vue'
import TeacherDashboard from '../views/TeacherDashboard.vue'
import StudentDashboard from '../views/StudentDashboard.vue'
import ChatView from '../views/ChatView.vue'
import { useAuthStore } from '../stores/auth'

const routes = [
  { path: '/login', name: 'login', component: LoginView },
  { path: '/', name: 'home', component: HomeView, meta: { auth: true } },
  { path: '/teacher', name: 'teacher', component: TeacherDashboard, meta: { auth: true, role: 'TEACHER' } },
  { path: '/student', name: 'student', component: StudentDashboard, meta: { auth: true, role: 'STUDENT' } },
  { path: '/chat', name: 'chat', component: ChatView, meta: { auth: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  if (!auth.ready) await auth.bootstrap()

  if (to.meta?.auth && !auth.isAuthenticated) return { name: 'login' }
  // ✅ role mos kelmasa, o'z paneliga yuboramiz
  if (to.meta?.role && auth.user?.role !== to.meta.role) {
    if (auth.user?.role === 'TEACHER') return { name: 'teacher' }
    if (auth.user?.role === 'STUDENT') return { name: 'student' }
    return { name: 'home' }
  }
  return true
})

export default router
