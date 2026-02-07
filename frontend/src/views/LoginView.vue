<template>
  <div class="grid" style="place-items:center; min-height: calc(100vh - 140px);">
    <div class="card" style="max-width:460px;width:100%">
      <div class="card-pad">
        <div class="page-title" style="margin:0 0 12px">
          <div>
            <h1 style="margin:0;font-size:28px">Kirish</h1>
            <p class="subtitle">Username va parol bilan tizimga kiring.</p>
          </div>
        </div>

        <form @submit.prevent="onSubmit" class="grid" style="gap:12px">
          <div class="field">
            <span>Username</span>
            <input v-model="username" autocomplete="username" placeholder="username" />
          </div>

          <div class="field">
            <span>Password</span>
            <input v-model="password" type="password" autocomplete="current-password" placeholder="••••••••" />
          </div>

          <button class="btn btn-primary" :disabled="loading">
            {{ loading ? 'Kirilmoqda...' : 'Kirish' }}
          </button>

          <p v-if="error" class="error">{{ error }}</p>
        </form>

        <div class="spacer" />
        <div class="pill" style="justify-content:space-between; width:100%">
          <span><b>Admin</b> yaratish:</span>
          <span style="font-family:ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace; font-size:12px">
            python manage.py createsuperuser
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function onSubmit() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(username.value.trim(), password.value)
    // role based redirect
    if (auth.user?.role === 'TEACHER') await router.push('/teacher')
    else if (auth.user?.role === 'STUDENT') await router.push('/student')
    else await router.push('/')
  } catch (e) {
    error.value = 'Login yoki parol xato.'
  } finally {
    loading.value = false
  }
}
</script>
