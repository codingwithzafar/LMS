<template>
  <div class="page">
    <div class="page-head">
      <div>
        <div class="kicker">TEACHER</div>
        <h2 class="page-h">Ustoz paneli</h2>
        <p class="subtitle">Guruhlar, o‘quvchilar, vazifalar va baholash.</p>
      </div>

      <div class="page-actions">
        <button class="btn btn-ghost" @click="$router.push('/chat')">Chat</button>
        <button class="btn btn-primary" @click="refreshAll" :disabled="loading">
          {{ loading ? 'Yuklanmoqda...' : 'Yangilash' }}
        </button>
      </div>
    </div>

    <div v-if="error" class="error">{{ error }}</div>

    <!-- Quick stats -->
    <div class="stats">
      <div class="stat card">
        <div class="stat-pad">
          <div class="stat-top">
            <span class="muted">Guruhlar</span>
            <span class="pill">👥</span>
          </div>
          <div class="stat-num">{{ groups.length }}</div>
        </div>
      </div>

      <div class="stat card">
        <div class="stat-pad">
          <div class="stat-top">
            <span class="muted">Vazifalar</span>
            <span class="pill">📌</span>
          </div>
          <div class="stat-num">{{ homeworks.length }}</div>
        </div>
      </div>

      <div class="stat card">
        <div class="stat-pad">
          <div class="stat-top">
            <span class="muted">Topshiriqlar</span>
            <span class="pill">✅</span>
          </div>
          <div class="stat-num">
            {{ Object.values(submissions || {}).reduce((a,arr)=>a + (arr?.length||0), 0) }}
          </div>
        </div>
      </div>
    </div>

    <!-- Groups -->
    <div class="panel">
      <div class="panel-bar">
        <div>
          <h3 class="panel-h">Guruhlar</h3>
          <div class="panel-sub">Jadval, xonalar va studentlar soni.</div>
        </div>
        <span v-if="data" class="pill">Jami: {{ groups.length }}</span>
      </div>

      <div v-if="data" class="grid grid-2">
        <div v-for="g in groups" :key="g.id" class="card">
          <div class="card-pad">
            <div class="card-head">
              <div>
                <h3 style="margin:0">{{ g.group_number }} — {{ g.name }}</h3>
                <div class="small muted">Guruh ID: {{ g.id }}</div>
              </div>
              <div class="row">
                <span class="pill">👥 {{ g.students_count }} o‘quvchi</span>
                <span class="pill">📌 {{ groupHomeworkCount(g) }} vazifa</span>
                <span class="pill">✅ {{ groupSubmissionCount(g) }} topshiriq</span>
                <button class="btn btn-ghost" @click="openGroupHomeworks(g.group_number)">Vazifalar</button>
              </div>
            </div>

            <div v-if="g.schedules && g.schedules.length" class="sched">
              <div v-for="s in g.schedules" :key="s.id" class="sched-row">
                <span>📅 {{ dayName(s.day_of_week) }}</span>
                <span>⏰ {{ s.start_time }} - {{ s.end_time }}</span>
                <span v-if="s.room">🏫 {{ s.room }}</span>
              </div>
            </div>
            <div v-else class="muted">Schedule yo‘q</div>
          </div>
        </div>
      </div>
      <div v-else class="muted">Ma’lumot yuklanmoqda...</div>
    </div>

    <!-- Create student -->
    <div class="panel">
      <div class="panel-bar">
        <div>
          <h3 class="panel-h">O‘quvchi yaratish</h3>
          <div class="panel-sub">Yangi student login/parol va guruh raqami bilan.</div>
        </div>
        <span class="pill">TEACHER → STUDENT</span>
      </div>

      <form class="grid grid-2" @submit.prevent="createStudent">
        <div class="field">
          <span>Username</span>
          <input class="input" v-model="st.username" placeholder="username" />
        </div>
        <div class="field">
          <span>Password</span>
          <input class="input" v-model="st.password" placeholder="password" />
        </div>
        <div class="field">
          <span>Full name</span>
          <input class="input" v-model="st.full_name" placeholder="ixtiyoriy" />
        </div>

        <div class="field">
          <span>Group</span>
          <select class="input" v-model.number="st.group_number">
            <option :value="null">Guruhni tanlang</option>
            <option v-for="g in groups" :key="g.id" :value="g.group_number">
              {{ g.group_number }} — {{ g.name }}
            </option>
          </select>
        </div>

        <div class="row" style="grid-column:1/-1; justify-content:flex-end">
          <button class="btn btn-primary" :disabled="creating">
            {{ creating ? 'Yaratilmoqda...' : 'Create student' }}
          </button>
        </div>
      </form>

      <p v-if="createdStudent" class="ok" style="margin:12px 0 0">
        ✅ Yaratildi: <b>{{ createdStudent.username }}</b> (id: {{ createdStudent.id }})
      </p>
    </div>

    <!-- Create homework -->
    <div class="panel" ref="createHwPanel">
      <div class="panel-bar">
        <div>
          <h3 class="panel-h">Vazifa berish</h3>
          <div class="panel-sub">Guruhni tanlang, link va fayl (pdf/doc/zip) biriktiring.</div>
        </div>
        <span class="pill">📎 attachment</span>
      </div>

      <form class="grid grid-2" @submit.prevent="createHomework">
        <div class="field">
          <span>Title</span>
          <input class="input" v-model="hw.title" placeholder="Masalan: Unit 3 homework" />
        </div>

        <div class="field">
          <span>Group</span>

          <div class="select-wrap">
            <select class="input" v-model.number="hw.group_number">
              <option :value="null">Guruhni tanlang</option>
              <option v-for="g in groups" :key="g.id" :value="g.group_number">
                {{ g.group_number }} — {{ g.name }}
              </option>
            </select>
          </div>

          <div v-if="selectedCreateGroup" class="preview-box">
            <div style="font-weight:850">
              Tanlandi: {{ selectedCreateGroup.group_number }} — {{ selectedCreateGroup.name }}
            </div>
            <div class="small" style="margin-top:4px">👥 {{ selectedCreateGroup.students_count }} o‘quvchi</div>

            <div v-if="selectedCreateGroup.schedules && selectedCreateGroup.schedules.length" class="sched" style="margin-top:10px">
              <div v-for="s in selectedCreateGroup.schedules" :key="s.id" class="sched-row">
                <span>📅 {{ dayName(s.day_of_week) }}</span>
                <span>⏰ {{ s.start_time }} - {{ s.end_time }}</span>
                <span v-if="s.room">🏫 {{ s.room }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="field" style="grid-column:1/-1">
          <span>Link</span>
          <input class="input" v-model="hw.link" placeholder="ixtiyoriy" />
        </div>

        <div class="field" style="grid-column:1/-1">
          <span>Attachment (zip/pdf/doc) — max 20MB</span>
          <input class="input" type="file" @change="onHwFile" />
          <div v-if="hwFile" class="small muted" style="margin-top:6px">
            Tanlangan: <b>{{ hwFile.name }}</b> ({{ prettySize(hwFile.size) }})
          </div>
        </div>

        <div class="field" style="grid-column:1/-1">
          <span>Description</span>
          <textarea class="input" v-model="hw.description" placeholder="ixtiyoriy" rows="3" />
        </div>

        <div class="row" style="grid-column:1/-1; justify-content:flex-end">
          <button class="btn btn-primary" :disabled="hwCreating">
            {{ hwCreating ? 'Saqlanmoqda...' : 'Create homework' }}
          </button>
        </div>
      </form>

      <p v-if="createdHw" class="ok" style="margin:12px 0 0">
        ✅ Vazifa yaratildi (HW #{{ createdHw.id }})
      </p>
      <p v-if="hwErr" class="error" style="margin:12px 0 0">{{ hwErr }}</p>
    </div>

    <!-- Homeworks by group -->
    <div class="panel" ref="homeworksPanel">
      <div class="panel-bar">
        <div>
          <h3 class="panel-h">Vazifalar</h3>
          <div class="panel-sub">
            Avval guruhni tanlang — keyin o‘sha guruhga berilgan vazifalar va topshiriqlar chiqadi.
          </div>
        </div>

        <div class="row">
          <select class="input" style="width:260px" v-model.number="selectedGroupNumber" @change="loadHomeworks">
            <option :value="null">Barcha guruhlar</option>
            <option v-for="g in groups" :key="g.id" :value="g.group_number">
              {{ g.group_number }} — {{ g.name }}
            </option>
          </select>
          <button class="btn btn-ghost" @click="loadHomeworks">Reload</button>
        </div>
      </div>

      <div v-if="homeworks.length" class="stack">
        <div v-for="h in homeworks" :key="h.id" class="card">
          <div class="card-pad">
            <div class="card-head">
              <div>
                <div style="font-weight:900">{{ h.title }}</div>
                <div class="small">
                  Guruh:
                  <b>{{ h.group_info?.group_number ?? h.group }}</b>
                  <span v-if="h.group_info?.name">— {{ h.group_info.name }}</span>
                  • HW #{{ h.id }}
                </div>
                <div class="small muted" style="margin-top:4px">
                  🕒 {{ fmtDateTime(h.created_at) }}
                  <span v-if="h.due_date"> • ⏳ Deadline: {{ fmtDateTime(h.due_date) }}</span>
                  <span v-if="typeof h.submissions_count === 'number'"> • ✅ {{ h.submissions_count }} topshiriq</span>
                </div>
              </div>

              <div class="row">
                <button v-if="h.attachment" class="btn btn-ghost" @click="downloadHomeworkAttachment(h)">Download file</button>
                <a v-if="h.link" class="btn btn-ghost" :href="h.link" target="_blank">Open link</a>
              </div>
            </div>

            <div v-if="h.description" class="muted" style="margin-top:8px">{{ h.description }}</div>

            <div class="divider"></div>

            <div class="row" style="justify-content:space-between; align-items:center">
              <h4 style="margin:0">Topshiriqlar (submissionlar)</h4>
              <button class="btn btn-ghost" @click="loadSubmissions(h.id)">
                {{ submissions[h.id]?.length ? 'Yangilash' : 'Ko‘rish' }}
              </button>
            </div>

            <div v-if="submissions[h.id] && submissions[h.id].length" class="stack" style="margin-top:10px">
              <div v-for="s in submissions[h.id]" :key="s.id" class="sub">
                <div class="sub-left">
                  <div style="font-weight:800">
                    {{ s.student_username }}
                    <span v-if="s.student_full_name" class="muted">— {{ s.student_full_name }}</span>
                  </div>
                  <div class="small muted">
                    #{{ s.id }} • {{ fmtDateTime(s.submitted_at) }}
                  </div>
                  <div v-if="s.text_answer" class="small" style="margin-top:6px">
                    📝 {{ s.text_answer }}
                  </div>
                </div>

                <div class="sub-actions">
                  <button v-if="s.file" class="btn btn-ghost" @click="downloadSubmissionFile(s)">Download</button>

                  <div class="grade">
                    <input
                      class="input"
                      style="width:90px"
                      type="number"
                      min="1"
                      max="5"
                      v-model.number="gradeForm[s.id].grade"
                      placeholder="Baho"
                    />
                    <input
                      class="input"
                      style="min-width:220px"
                      v-model="gradeForm[s.id].teacher_comment"
                      placeholder="Izoh..."
                    />
                    <button class="btn btn-primary" @click="saveGrade(s.id, h.id)">Save</button>
                  </div>
                </div>
              </div>
            </div>

            <div v-else class="muted" style="margin-top:10px">Hali topshiriq yo‘q.</div>
          </div>
        </div>
      </div>

      <div v-else class="muted">Hali vazifa yo‘q.</div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import api from '../lib/api'
import { downloadFile } from '../lib/download'

const data = ref(null)
const loading = ref(false)
const error = ref('')

const creating = ref(false)
const createdStudent = ref(null)
const st = ref({ username:'', password:'', full_name:'', group_number: null })

const hwCreating = ref(false)
const createdHw = ref(null)
const hwErr = ref('')
const homeworks = ref([])
const submissions = ref({})
const gradeForm = ref({}) // submission_id -> {grade, teacher_comment}
const hwFile = ref(null)
const hw = ref({ title:'', description:'', link:'', group_number: null })

const selectedGroupNumber = ref(null)

const groups = computed(() => data.value?.groups || [])

// ✅ Group badge stats (vazifalar / topshiriqlar)
// homeworks endpointdan kelgan submissions_count bilan hisoblaymiz
const groupStats = computed(() => {
  const map = {}
  for (const h of (homeworks.value || [])) {
    const gn = h?.group_info?.group_number ?? h?.group_number
    if (gn === undefined || gn === null) continue
    if (!map[gn]) map[gn] = { homeworks: 0, submissions: 0 }
    map[gn].homeworks += 1
    map[gn].submissions += Number(h?.submissions_count || 0)
  }
  return map
})

function groupHomeworkCount(g){
  const gn = g?.group_number
  return (groupStats.value?.[gn]?.homeworks) || 0
}

function groupSubmissionCount(g){
  const gn = g?.group_number
  return (groupStats.value?.[gn]?.submissions) || 0
}


const homeworksPanel = ref(null)
const createHwPanel = ref(null)

function dayName(d){
  return ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][d] ?? d
}

function fmtDateTime(v){
  if (!v) return ''
  const d = new Date(v)
  if (Number.isNaN(d.getTime())) return String(v)
  return d.toLocaleString()
}

function prettySize(bytes){
  if (!bytes && bytes !== 0) return ''
  const mb = bytes / (1024*1024)
  if (mb >= 1) return `${mb.toFixed(2)} MB`
  const kb = bytes / 1024
  return `${kb.toFixed(1)} KB`
}

function onHwFile(e){
  const f = (e.target.files && e.target.files[0]) ? e.target.files[0] : null
  if (f && f.size > 20 * 1024 * 1024) {
    hwErr.value = 'Fayl 20MB dan katta. Iltimos kichikroq fayl yuklang.'
    e.target.value = ''
    hwFile.value = null
    return
  }
  hwErr.value = ''
  hwFile.value = f
}

async function downloadHomeworkAttachment(h){
  try{
    await downloadFile(`/api/files/homeworks/${h.id}/attachment/`, `homework_${h.id}`)
  }catch(e){
    hwErr.value = 'Attachment download qilishda xatolik.'
  }
}

async function downloadSubmissionFile(s){
  try{
    await downloadFile(`/api/files/submissions/${s.id}/file/`, `submission_${s.id}`)
  }catch(e){
    hwErr.value = 'Submission faylini download qilishda xatolik.'
  }
}

async function loadDashboard(){
  const res = await api.get('/api/teacher/dashboard/')
  data.value = res.data

  // default group selection
  if (selectedGroupNumber.value == null && (res.data?.groups?.length || 0) > 0) {
    selectedGroupNumber.value = res.data.groups[0].group_number
  }
}

async function loadHomeworks(){
  hwErr.value = ''
  const params = {}
  if (selectedGroupNumber.value != null) params.group_number = selectedGroupNumber.value
  const res = await api.get('/api/teacher/homeworks/', { params })
  homeworks.value = res.data
}

async function refreshAll(){
  error.value = ''
  loading.value = true
  try{
    await loadDashboard()
    await loadHomeworks()
  }catch(e){
    error.value = 'Dashboardni olishda xatolik.'
  }finally{
    loading.value = false
  }
}

async function createStudent(){
  createdStudent.value = null
  creating.value = true
  error.value = ''
  try{
    const res = await api.post('/api/teacher/students/', { ...st.value })
    createdStudent.value = res.data
    st.value = { username:'', password:'', full_name:'', group_number: null }
  }catch(e){
    error.value = (e?.response?.data?.detail) || 'Student yaratishda xatolik.'
  }finally{
    creating.value = false
  }
}

async function createHomework(){
  createdHw.value = null
  hwCreating.value = true
  hwErr.value = ''
  try{
    if (!hw.value.group_number) {
      throw new Error('Guruh tanlanmagan')
    }
    const fd = new FormData()
    fd.append('group_number', String(hw.value.group_number || ''))
    fd.append('title', hw.value.title || '')
    fd.append('description', hw.value.description || '')
    fd.append('link', hw.value.link || '')
    if (hwFile.value) fd.append('attachment', hwFile.value)

    const res = await api.post('/api/teacher/homeworks/create/', fd)
    createdHw.value = res.data

    // reset
    hw.value = { title:'', description:'', link:'', group_number: hw.value.group_number }
    hwFile.value = null

    // show in list immediately
    selectedGroupNumber.value = hw.value.group_number
    await loadHomeworks()
  }catch(e){
    const detail = e?.response?.data?.detail
    hwErr.value = detail || e?.message || 'Vazifa yaratishda xatolik.'
  }finally{
    hwCreating.value = false
  }
}

async function loadSubmissions(homeworkId){
  try{
    const res = await api.get(`/api/teacher/homeworks/${homeworkId}/submissions/`)
    submissions.value[homeworkId] = res.data

    for (const s of (res.data || [])) {
      if (!gradeForm.value[s.id]) {
        gradeForm.value[s.id] = {
          grade: s.grade ?? null,
          teacher_comment: s.teacher_comment ?? ''
        }
      } else {
        gradeForm.value[s.id].grade = s.grade ?? null
        gradeForm.value[s.id].teacher_comment = s.teacher_comment ?? ''
      }
    }
  }catch(e){
    hwErr.value = 'Submissions olishda xatolik.'
  }
}

async function saveGrade(submissionId, homeworkId){
  try{
    const body = {
      grade: gradeForm.value[submissionId]?.grade,
      teacher_comment: gradeForm.value[submissionId]?.teacher_comment || ''
    }
    await api.patch(`/api/teacher/submissions/${submissionId}/grade/`, body)
    await loadSubmissions(homeworkId)
  }catch(e){
    hwErr.value = (e?.response?.data?.detail) || 'Baho saqlashda xatolik.'
  }
}

function openGroupHomeworks(groupNumber){
  selectedGroupNumber.value = groupNumber
  loadHomeworks()
  // smooth scroll to homeworks panel
  try{
    homeworksPanel.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }catch(_e){
    // ignore
  }
}

onMounted(refreshAll)
</script>

<style scoped>
.select-wrap{
  position: relative;
}
.select-wrap::after{
  content: "▾";
  position: absolute;
  right: 14px;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
  color: rgba(255,255,255,.65);
  font-size: 14px;
}
.select-wrap select{
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  padding-right: 40px;
}

.preview-box{
  margin-top: 10px;
  padding: 12px;
  border-radius: 16px;
  border: 1px solid rgba(255,255,255,.10);
  background: rgba(0,0,0,.18);
}
</style>
