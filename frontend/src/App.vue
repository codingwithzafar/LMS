<template>
  <div>
    <header class="topbar">
      <div class="container topbar-inner">
        <div class="brand" @click="$router.push({name:'home'})" style="cursor:pointer">
          <div class="brand-mark"></div>
          <div>
            <div style="font-weight:800; letter-spacing:.2px">Academy LMS</div>
            <div class="small">Ustoz ↔ O‘quvchi • Homework • Chat</div>
          </div>
        </div>

        <nav class="nav" v-if="auth.isAuthenticated">
          <RouterLink :to="{name:'home'}" active-class="active">Bosh sahifa</RouterLink>
          <RouterLink v-if="auth.user?.role==='TEACHER'" :to="{name:'teacher'}" active-class="active">Teacher</RouterLink>
          <RouterLink v-if="auth.user?.role==='STUDENT'" :to="{name:'student'}" active-class="active">Student</RouterLink>
          <RouterLink :to="{name:'chat'}" active-class="active">Chat</RouterLink>
        </nav>

        <div style="display:flex; gap:10px; align-items:center">
          <span v-if="auth.isAuthenticated" class="badge">
            <span class="dot online"></span>
            <span>{{ auth.user?.full_name || auth.user?.username }}</span>
            <span style="opacity:.7">•</span>
            <span style="opacity:.85">{{ auth.user?.role }}</span>
          </span>

          <button v-if="!auth.isAuthenticated" class="btn btn-primary" @click="$router.push({name:'login'})">
            Kirish
          </button>
          <button v-else class="btn btn-ghost" @click="logout">
            Chiqish
          </button>
        </div>
      </div>
    </header>

    <main class="main">
      <div class="container">
        <RouterView />
      </div>
    </main>
  </div>
</template>

<script setup>
import { RouterLink, RouterView } from 'vue-router'
import { useAuthStore } from './stores/auth'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()

function logout(){
  auth.logout()
  router.push({name:'login'})
}
</script>
