<template>
  <div class="page">
    <div class="hero">
      <div class="hero-card card">
        <div class="hero-pad">
          <div class="hero-badge badge">
            <span class="dot online"></span>
            Premium Academy LMS
          </div>

          <h1 class="hero-title">O‘qish, vazifa, baholash va chat — bitta joyda.</h1>
          <p class="hero-sub">
            Ustoz va o‘quvchi uchun soddalashtirilgan panel: guruhlar, uy ishi, fayl almashish va guruh chat.
          </p>

          <div class="hero-actions">
            <button v-if="!role" class="btn btn-primary" @click="$router.push('/login')">Kirish</button>
            <button v-if="role" class="btn btn-primary" disabled>Yo‘naltirilmoqda...</button>

            <button class="btn btn-ghost" @click="$router.push('/chat')">Chat</button>
          </div>

          <div v-if="role" class="hero-meta">
            Sizning role: <b>{{ role }}</b>
          </div>
        </div>
      </div>

      <div class="hero-grid">
        <div class="panel">
          <div class="panel-title">
            <div class="panel-icon">📚</div>
            <div>
              <div class="panel-head">Vazifa & fayllar</div>
              <div class="panel-sub">Teacher attachment → Student download, Student submission → Teacher download.</div>
            </div>
          </div>
        </div>

        <div class="panel">
          <div class="panel-title">
            <div class="panel-icon">💬</div>
            <div>
              <div class="panel-head">Chat & guruhlar</div>
              <div class="panel-sub">Ustoz guruh ochadi, o‘quvchilarni qo‘shadi va birga yozishadi.</div>
            </div>
          </div>
        </div>

        <div class="panel">
          <div class="panel-title">
            <div class="panel-icon">🟢</div>
            <div>
              <div class="panel-head">Online status</div>
              <div class="panel-sub">O‘quvchi oxirgi ko‘ringan vaqti va online holati ko‘rinadi.</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, watchEffect } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()

const role = computed(() => auth.user?.role || '')
const fallbackPath = computed(() => {
  if (role.value === 'TEACHER') return '/teacher'
  if (role.value === 'STUDENT') return '/student'
  return ''
})

watchEffect(() => {
  if (role.value === 'TEACHER') router.replace('/teacher')
  else if (role.value === 'STUDENT') router.replace('/student')
})
</script>
