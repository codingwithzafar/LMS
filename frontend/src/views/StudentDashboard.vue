<template>
  <div class="page student">
    <!-- HEADER -->
    <div class="page-head">
      <div>
        <div class="kicker">STUDENT</div>
        <h2 class="page-h">O‘quvchi paneli</h2>
        <p class="subtitle">Vazifalar, topshirish va chat.</p>
      </div>

      <div class="page-actions actions-row">
        <button class="btn btn-ghost" @click="$router.push('/chat')">Chat</button>
        <button class="btn btn-primary" @click="refreshAll" :disabled="loading">
          {{ loading ? 'Yuklanmoqda...' : 'Yangilash' }}
        </button>
      </div>
    </div>

    <div v-if="error" class="error">{{ error }}</div>

    <!-- STATS -->
    <div class="stats">
      <div class="stat card statx">
        <div class="stat-pad">
          <div class="stat-top">
            <span class="muted">Guruhlar</span>
            <span class="pill">👥</span>
          </div>
          <div class="stat-num">{{ data?.groups?.length || 0 }}</div>
          <div class="small muted">Biriktirilgan guruhlar soni</div>
        </div>
      </div>

      <div class="stat card statx">
        <div class="stat-pad">
          <div class="stat-top">
            <span class="muted">Vazifalar</span>
            <span class="pill">📌</span>
          </div>
          <div class="stat-num">{{ homeworks?.length || 0 }}</div>
          <div class="small muted">Aktiv vazifalar</div>
        </div>
      </div>

      <div class="stat card statx">
        <div class="stat-pad">
          <div class="stat-top">
            <span class="muted">Topshirganlarim</span>
            <span class="pill">✅</span>
          </div>
          <div class="stat-num">{{ Object.keys(mySubs || {}).length }}</div>
          <div class="small muted">Yuborilgan javoblar</div>
        </div>
      </div>
    </div>

    <!-- GROUPS -->
    <div class="panel">
      <div class="panel-bar">
        <div>
          <h3 class="panel-h">Mening guruhlarim</h3>
          <div class="panel-sub">Jadval va xona.</div>
        </div>
        <span class="pill">Jami: {{ data?.groups?.length || 0 }}</span>
      </div>

      <div v-if="data?.groups?.length" class="grid grid-2">
        <div v-for="g in data.groups" :key="g.id" class="card group-card">
          <div class="card-pad">
            <div class="card-head">
              <div style="min-width:0">
                <h3 class="card-title">{{ g.group_number }} — {{ g.name }}</h3>
                <div class="small muted">Guruh ID: #{{ g.id }}</div>
              </div>
              <span class="pill">🏫 {{ g.room || '—' }}</span>
            </div>

            <div class="divider soft"></div>

            <div v-if="g.schedules?.length" class="sched">
              <div v-for="s in g.schedules" :key="s.id" class="sched-row">
                <span>📅 {{ dayName(s.day_of_week) }}</span>
                <span>⏰ {{ s.start_time }} - {{ s.end_time }}</span>
              </div>
            </div>

            <div v-else class="muted small">Schedule yo‘q</div>
          </div>
        </div>
      </div>

      <div v-else class="muted">Siz hali guruhga biriktirilmagansiz.</div>
    </div>

    <!-- HOMEWORKS -->
    <div class="panel">
      <div class="panel-bar">
        <div>
          <h3 class="panel-h">Vazifalar</h3>
          <div class="panel-sub">Faylni download qiling, javob yuboring.</div>
        </div>

        <div class="row">
          <button class="btn btn-ghost" @click="loadHomeworks" :disabled="loading">
            Reload
          </button>
        </div>
      </div>

      <p v-if="hwErr" class="error" style="margin:12px 0">{{ hwErr }}</p>

      <div v-if="homeworks?.length" class="stack">
        <div v-for="h in homeworks" :key="h.id" class="card hw-card" :class="{ done: submitted[h.id] }">
          <div class="card-pad">
            <!-- HW HEAD -->
            <div class="hw-head">
              <div class="hw-left">
                <div class="hw-title">{{ h.title }}</div>
                <div class="small muted">
                  Group: <b>{{ h.group_number }}</b> • HW #{{ h.id }}
                </div>
              </div>

              <div class="hw-actions">
                <span class="pill ok-pill" v-if="submitted[h.id]">✅ yuborilgan</span>

                <button v-if="h.has_attachment" class="btn btn-ghost" @click="downloadHomeworkAttachment(h)">
                  📥 Download file
                </button>

                <a v-if="h.link" class="btn btn-ghost" :href="h.link" target="_blank">
                  🔗 Open link
                </a>
              </div>
            </div>

            <div v-if="h.description" class="muted hw-desc">{{ h.description }}</div>

            <div class="divider"></div>

            <!-- FORM GRID -->
            <div class="grid grid-2 hw-form">
              <!-- TEXT -->
              <div class="field full">
                <span>Text answer (ixtiyoriy)</span>
                <textarea class="input" rows="4" v-model="answers[h.id]" placeholder="Javobingiz..." />
              </div>

              <!-- FILE -->
              <div class="field">
                <span>File</span>

                <label class="filebox">
                  <input class="file-native" type="file" @change="(e) => onFile(e, h.id)" />
                  <div class="file-ui">
                    <div class="file-ico">📎</div>

                    <div class="file-meta">
                      <div class="file-title">
                        {{ files[h.id]?.name ? 'Tanlandi' : 'Fayl tanlash' }}
                      </div>
                      <div class="file-sub">
                        {{ files[h.id]?.name || 'PDF, DOCX, PNG… (ixtiyoriy)' }}
                      </div>
                    </div>

                    <div class="file-cta">Browse</div>
                  </div>
                </label>

                <div v-if="files[h.id]?.name" class="small muted" style="margin-top:8px">
                  Tanlangan fayl: <b>{{ files[h.id].name }}</b>
                </div>
              </div>

              <!-- STATUS -->
              <div class="field">
                <span>Status</span>
                <div class="badge status-badge">
                  <span class="dot" :class="submitted[h.id] ? 'online' : 'offline'"></span>
                  {{ submitted[h.id] ? 'Submitted' : 'Not submitted' }}
                </div>

                <div class="small muted" style="margin-top:8px">
                  Yuborgandan keyin ustoz baho qo‘yadi.
                </div>
              </div>

              <!-- SUBMIT -->
              <div class="submit-row full">
                <button class="btn btn-primary" @click="submitHomework(h.id)" :disabled="submitted[h.id]">
                  {{ submitted[h.id] ? 'Yuborilgan' : 'Yuborish' }}
                </button>
              </div>
            </div>

            <!-- SUBMISSION INFO -->
            <div v-if="mySubs[h.id]" class="sub-note">
              <div class="sub-top">
                <div class="badge">
                  <span class="dot online"></span>
                  Baho: <b>{{ mySubs[h.id].grade ?? '—' }}</b>
                </div>

                <button class="btn btn-ghost" @click="downloadMySubmissionFile(mySubs[h.id])">
                  ⬇️ Mening faylimni download
                </button>
              </div>

              <div class="small muted" v-if="mySubs[h.id].teacher_comment" style="margin-top:10px">
                Tavsif: {{ mySubs[h.id].teacher_comment }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="homeworksNext" class="row" style="justify-content:center; margin-top:12px">
        <button class="btn btn-ghost" @click="loadMoreHomeworks">Load more</button>
      </div>

      <div v-else class="muted">Hali vazifa yo‘q.</div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api from '../lib/api'
import { downloadFile } from '../lib/download'

const data = ref(null)
const loading = ref(false)
const error = ref('')

const homeworks = ref([])
const homeworksNext = ref(null)
const hwErr = ref('')
const answers = ref({})
const files = ref({})
const submitted = ref({})
const mySubs = ref({}) // homework_id -> submission

function dayName(d) {
  return ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][d] ?? d
}


function unwrapList(data){
  if (Array.isArray(data)) return { results: data, next: null }
  return { results: data?.results || [], next: data?.next || null }
}

function onFile(e, id) {
  const f = e.target.files && e.target.files[0]
  if (f) files.value[id] = f
}

async function downloadHomeworkAttachment(h) {
  try {
    await downloadFile(`/api/files/homeworks/${h.id}/attachment/`, `homework_${h.id}`)
  } catch (e) {
    hwErr.value = 'Attachment download qilishda xatolik.'
  }
}

async function downloadMySubmissionFile(s) {
  try {
    await downloadFile(`/api/files/submissions/${s.id}/file/`, `submission_${s.id}`)
  } catch (e) {
    hwErr.value = 'Faylni download qilishda xatolik.'
  }
}

async function loadDashboard() {
  error.value = ''
  const res = await api.get('/api/student/dashboard/')
  data.value = res.data
}

async function loadHomeworks(reset = true, url = null) {
  hwErr.value = ''
  const res = url ? await api.get(url) : await api.get('/api/student/homeworks/', { params: { page: 1 } })
  const page = unwrapList(res.data)
  homeworksNext.value = page.next
  if (reset) {
    homeworks.value = page.results
  } else {
    homeworks.value = [...homeworks.value, ...page.results]
  }
}

async function loadMoreHomeworks(){
  if (!homeworksNext.value) return
  await loadHomeworks(false, homeworksNext.value)
}

async function loadMySubmissions() {
  const res = await api.get('/api/student/submissions/')
  const map = {}
  for (const s of res.data || []) {
    if (s.homework) map[s.homework] = s
  }
  mySubs.value = map
  Object.keys(map).forEach((k) => { submitted.value[k] = true })
}

async function refreshAll() {
  loading.value = true
  try {
    await loadDashboard()
    await loadHomeworks()
    await loadMySubmissions()
  } catch (e) {
    error.value = "Dashboardni olishda xatolik."
  } finally {
    loading.value = false
  }
}

async function submitHomework(id) {
  hwErr.value = ''
  try {
    const fd = new FormData()
    fd.append('text_answer', answers.value[id] || '')
    if (files.value[id]) fd.append('file', files.value[id])

    await api.post(`/api/student/homeworks/${id}/submit/`, fd)
    submitted.value[id] = true
    await loadMySubmissions()
  } catch (e) {
    hwErr.value = "Topshirishda xatolik (allaqachon topshirgan bo‘lishing mumkin)."
  }
}

onMounted(refreshAll)
</script>

<style scoped>
/* layout tweaks */
.actions-row {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  align-items: center
}

.student .page-h {
  letter-spacing: .2px
}

/* stats premium glow */
.statx {
  position: relative;
  overflow: hidden
}

.statx::before {
  content: "";
  position: absolute;
  inset: -1px;
  background:
    radial-gradient(620px 160px at 10% 0%, rgba(124, 58, 237, .22), transparent 62%),
    radial-gradient(620px 160px at 92% 10%, rgba(6, 182, 212, .18), transparent 60%);
  opacity: .9;
  pointer-events: none;
}

.statx .stat-pad {
  position: relative
}

/* group card */
.group-card {
  transition: .14s ease
}

.group-card:hover {
  transform: translateY(-2px);
  background: rgba(255, 255, 255, .05)
}

.card-title {
  margin: 0;
  font-size: 16px;
  font-weight: 900;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* homework card */
.hw-card {
  position: relative;
  overflow: hidden;
  transition: .14s ease
}

.hw-card:hover {
  transform: translateY(-2px)
}

.hw-card::after {
  content: "";
  position: absolute;
  inset: -2px;
  background:
    radial-gradient(640px 260px at 12% 0%, rgba(124, 58, 237, .18), transparent 66%),
    radial-gradient(640px 260px at 92% 10%, rgba(6, 182, 212, .14), transparent 62%);
  opacity: .55;
  pointer-events: none;
}

.hw-card .card-pad {
  position: relative
}

.hw-card.done {
  border-color: rgba(34, 197, 94, .35);
  box-shadow: 0 0 0 5px rgba(34, 197, 94, .10), var(--shadow);
}

.hw-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.hw-left {
  min-width: 0
}

.hw-title {
  font-weight: 950;
  font-size: 16px;
  line-height: 1.2
}

.hw-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: flex-end
}

.hw-desc {
  margin-top: 10px
}

/* form panels inside hw */
.hw-form {
  margin-top: 10px
}

.field {
  background: rgba(0, 0, 0, .16);
  border: 1px solid rgba(255, 255, 255, .10);
  border-radius: 16px;
  padding: 12px;
}

.field>span {
  font-size: 12px;
  color: var(--muted)
}

.field.full {
  grid-column: 1/-1
}

textarea.input {
  min-height: 120px
}

.status-badge {
  justify-content: flex-start
}

.submit-row {
  display: flex;
  justify-content: flex-end;
  gap: 10px
}

.submit-row.full {
  grid-column: 1/-1
}

@media (max-width:860px) {
  .hw-head {
    flex-direction: column;
    align-items: flex-start
  }

  .hw-actions {
    justify-content: flex-start
  }

  .submit-row {
    justify-content: stretch
  }

  .submit-row .btn {
    width: 100%
  }
}

/* ok pill */
.ok-pill {
  border-color: rgba(34, 197, 94, .35) !important;
  background: rgba(34, 197, 94, .10) !important;
}

/* file input (premium) */
.filebox {
  display: block;
  margin-top: 8px
}

.file-native {
  position: absolute;
  width: 1px;
  height: 1px;
  opacity: 0;
  pointer-events: none;
}

.file-ui {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 16px;
  border: 1px dashed rgba(255, 255, 255, .18);
  background: rgba(255, 255, 255, .03);
  cursor: pointer;
  transition: .12s ease;
}

.file-ui:hover {
  background: rgba(255, 255, 255, .05);
  border-color: rgba(6, 182, 212, .35);
}

.file-ico {
  width: 42px;
  height: 42px;
  border-radius: 16px;
  display: grid;
  place-items: center;
  background: rgba(255, 255, 255, .06);
  border: 1px solid rgba(255, 255, 255, .10);
  font-size: 18px;
}

.file-meta {
  min-width: 0;
  flex: 1
}

.file-title {
  font-weight: 950;
  font-size: 14px
}

.file-sub {
  font-size: 12px;
  color: var(--muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-cta {
  padding: 9px 12px;
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, .14);
  background: rgba(255, 255, 255, .06);
  font-size: 12px;
  font-weight: 900;
}

/* submission note */
.sub-note {
  margin-top: 14px;
  border-top: 1px solid rgba(255, 255, 255, .08);
  padding-top: 12px;
}

.sub-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.divider.soft {
  opacity: .65
}
</style>
