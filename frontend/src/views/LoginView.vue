<template>
  <div class="login-page">
    <!-- background blobs -->
    <div class="wrap card">
      <div class="left">
        <div class="brand">
          <div class="logo">🎓</div>
          <div>
            <h1>Academy LMS</h1>
            <p>Ustoz ↔ O‘quvchi • Homework • Chat</p>
          </div>
        </div>

        <div class="features">
          <div class="f">
            <span class="dot"></span>
            <div>
              <b>Vazifalar & fayllar</b>
              <div class="muted">Teacher attachment → Student download</div>
            </div>
          </div>
          <div class="f">
            <span class="dot"></span>
            <div>
              <b>Chat & guruhlar</b>
              <div class="muted">Direct + group chat bitta joyda</div>
            </div>
          </div>
          <div class="f">
            <span class="dot"></span>
            <div>
              <b>Tez va qulay</b>
              <div class="muted">Mobilga ham mos (responsive)</div>
            </div>
          </div>
        </div>

        <div class="hint muted">
          CODINGWITHULUGBEK
        </div>
      </div>

      <div class="right">
        <div class="head">
          <div class="badge">KIRISH</div>
          <h2>Hisobga kiring</h2>
          <p class="muted">Username va parol orqali tizimga kiring.</p>
        </div>

        <form class="form" @submit.prevent="onSubmit">
          <label class="field">
            <span>Username</span>
            <input v-model="username" class="input" autocomplete="username" placeholder="username" />
          </label>

          <label class="field">
            <span>Password</span>
            <div class="pass">
              <input v-model="password" class="input" :type="show ? 'text' : 'password'" autocomplete="current-password"
                placeholder="••••••••" />
              <button type="button" class="eye btn btn-ghost" @click="show = !show">
                {{ show ? "🙈" : "👁️" }}
              </button>
            </div>
          </label>

          <p v-if="error" class="err">{{ error }}</p>

          <button class="btn btn-primary" :disabled="loading">
            {{ loading ? "Kirilmoqda..." : "Kirish" }}
          </button>

          <div class="small muted">
            Muammo bo‘lsa: API url (VITE_API_BASE) Netlify’da to‘g‘ri qo‘yilganini tekshiring.
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue"
import { useRouter } from "vue-router"
import { useAuthStore } from "../stores/auth"

const router = useRouter()
const auth = useAuthStore()

const username = ref("")
const password = ref("")
const loading = ref(false)
const error = ref("")
const show = ref(false)

async function onSubmit() {
  error.value = ""
  loading.value = true
  try {
    await auth.login(username.value.trim(), password.value)
    // sizda role bo‘yicha redirect bor edi:
    if (auth.user?.role === "TEACHER") await router.push("/teacher")
    else if (auth.user?.role === "STUDENT") await router.push("/student")
    else await router.push("/")
  } catch (e) {
    error.value = "Login yoki parol xato."
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 26px 16px;

  /* ✅ Eng muhimi: body foni ko‘rinsin */
  background: transparent;
}

.blob {
  position: absolute;
  width: 520px;
  height: 520px;
  border-radius: 999px;
  filter: blur(45px);
  opacity: .55;
  animation: float 8s ease-in-out infinite;
  pointer-events: none;
}

.b1 {
  left: -120px;
  top: -140px;
  background: rgba(124, 92, 255, .45);
}

.b2 {
  right: -160px;
  bottom: -160px;
  background: rgba(47, 230, 255, .30);
  animation-duration: 10s;
}

@keyframes float {

  0%,
  100% {
    transform: translateY(0px)
  }

  50% {
    transform: translateY(18px)
  }
}

.wrap {
  width: min(980px, 100%);
  display: grid;
  grid-template-columns: 1.1fr .9fr;
  overflow: hidden;
}

.left {
  padding: 28px;
  border-right: 1px solid rgba(255, 255, 255, .08);
  background: transparent;
}

.right {
  padding: 28px;
}

.brand {
  display: flex;
  gap: 12px;
  align-items: center;
}

.logo {
  width: 54px;
  height: 54px;
  display: grid;
  place-items: center;
  border-radius: 16px;
  background: rgba(255, 255, 255, .08);
  border: 1px solid rgba(255, 255, 255, .10);
}

h1 {
  margin: 0;
  font-size: 22px;
  letter-spacing: .2px
}

.brand p {
  margin: 4px 0 0;
  opacity: .75;
  font-size: 13px
}

.features {
  margin-top: 22px;
  display: grid;
  gap: 12px
}

.f {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  padding: 12px;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, .08);
  background: rgba(255, 255, 255, .04);
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: rgba(47, 230, 255, .95);
  box-shadow: 0 0 0 6px rgba(47, 230, 255, .12);
  margin-top: 4px;
}

.muted {
  opacity: .72;
  font-size: 13px
}

.hint {
  margin-top: 18px
}

.head .badge {
  display: inline-flex;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(255, 255, 255, .07);
  border: 1px solid rgba(255, 255, 255, .10);
  font-size: 12px;
  letter-spacing: .6px;
}

.head h2 {
  margin: 10px 0 0;
  font-size: 26px
}

.head p {
  margin: 8px 0 0
}

.form {
  margin-top: 16px;
  display: grid;
  gap: 12px
}

.field span {
  display: block;
  font-size: 13px;
  opacity: .78;
  margin: 0 0 7px
}

.pass {
  display: flex;
  gap: 10px;
  align-items: center
}

.eye {
  padding: 10px 12px;
  border-radius: 14px;
  white-space: nowrap
}

.err {
  margin: 0;
  padding: 10px 12px;
  border-radius: 14px;
  border: 1px solid rgba(255, 90, 90, .35);
  background: rgba(255, 90, 90, .10);
}

.small {
  font-size: 12px;
  opacity: .7;
  margin-top: 6px
}

@media (max-width: 860px) {
  .wrap {
    grid-template-columns: 1fr
  }

  .left {
    display: none
  }
}
</style>
