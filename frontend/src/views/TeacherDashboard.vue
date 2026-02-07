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
          <div class="stat-num">{{ data?.groups?.length || 0 }}</div>
        </div>
      </div>

      <div class="stat card">
        <div class="stat-pad">
          <div class="stat-top">
            <span class="muted">Vazifalar</span>
            <span class="pill">📌</span>
          </div>
          <div class="stat-num">{{ homeworks?.length || 0 }}</div>
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
        <span v-if="data" class="pill">Jami: {{ data.groups?.length || 0 }}</span>
      </div>

      <div v-if="data" class="grid grid-2">
        <div v-for="g in data.groups" :key="g.id" class="card">
          <div class="card-pad">
            <div class="card-head">
              <h3 style="margin:0">{{ g.group_number }} — {{ g.name }}</h3>
              <span class="pill">👥 {{ g.students_count }} o‘quvchi</span>
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
          <span>Group number</span>
          <input class="input" v-model.number="st.group_number" type="number" placeholder="101" />
        </div>

        <div class="row" style="grid-column:1/-1; justify-content:flex-end">
          <button class="btn btn-primary" :disabled="creating">{{ creating ? 'Yaratilmoqda...' : 'Create student' }}</button>
        </div>
      </form>

      <p v-if="createdStudent" class="ok" style="margin:12px 0 0">
        ✅ Yaratildi: <b>{{ createdStudent.username }}</b> (id: {{ createdStudent.id }})
      </p>
    </div>

    <!-- Create homework -->
    <div class="panel">
      <div class="panel-bar">
        <div>
          <h3 class="panel-h">Vazifa berish</h3>
          <div class="panel-sub">Link va fayl (pdf/doc/zip) biriktirib yuboring.</div>
        </div>
        <span class="pill">📎 attachment</span>
      </div>

      <form class="grid grid-2" @submit.prevent="createHomework">
        <div class="field">
          <span>Title</span>
          <input class="input" v-model="hw.title" placeholder="Masalan: Unit 3 homework" />
        </div>
        <div class="field">
          <span>Group number</span>
          <input class="input" v-model.number="hw.group_number" type="number" placeholder="101" />
        </div>

        <div class="field" style="grid-column:1/-1">
          <span>Link</span>
          <input class="input" v-model="hw.link" placeholder="ixtiyoriy" />
        </div>

        <div class="field" style="grid-column:1/-1">
          <span>Attachment (zip/pdf/doc)</span>
          <input class="input" type="file" @change="onHwFile" />
        </div>

        <div class="field" style="grid-column:1/-1">
          <span>Description</span>
          <textarea class="input" v-model="hw.description" placeholder="ixtiyoriy" rows="3" />
        </div>

        <div class="row" style="grid-column:1/-1; justify-content:flex-end">
          <button class="btn btn-primary" :disabled="hwCreating">{{ hwCreating ? 'Saqlanmoqda...' : 'Create homework' }}</button>
        </div>
      </form>

      <p v-if="createdHw" class="ok" style="margin:12px 0 0">✅ Vazifa yaratildi (HW #{{ createdHw.id }})</p>
      <p v-if="hwErr" class="error" style="margin:12px 0 0">{{ hwErr }}</p>
    </div>

    <!-- Homeworks list -->
    <div class="panel">
      <div class="panel-bar">
        <div>
          <h3 class="panel-h">Vazifalar</h3>
          <div class="panel-sub">Attachment download, submissionlar va baholash.</div>
        </div>
        <button class="btn btn-ghost" @click="loadHomeworks">Reload</button>
      </div>

      <div v-if="homeworks && homeworks.length" class="stack">
        <div v-for="h in homeworks" :key="h.id" class="card">
          <div class="card-pad">
            <div class="card-head">
              <div>
                <div style="font-weight:800">{{ h.title }}</div>
                <div class="small">Group: <b>{{ h.group_number }}</b> • HW #{{ h.id }}</div>
              </div>
              <div class="row">
                <button v-if="h.has_attachment" class="btn btn-ghost" @click="downloadHomeworkAttachment(h)">Download file</button>
                <a v-if="h.link" class="btn btn-ghost" :href="h.link" target="_blank">Open link</a>
              </div>
            </div>

            <div v-if="h.description" class="muted" style="margin-top:8px">{{ h.description }}</div>

            <div class="divider"></div>

            <div class="section-title" style="margin-top:8px">
              <h4 style="margin:0">Submissionlar</h4>
              <button class="btn btn-ghost" @click="loadSubmissions(h.id)">Load</button>
            </div>

            <div v-if="submissions && submissions[h.id] && submissions[h.id].length" class="stack">
              <div v-for="s in submissions[h.id]" :key="s.id" class="sub">
                <div class="sub-left">
                  <div style="font-weight:700">{{ s.student_full_name || s.student_username }}</div>
                  <div class="small">#{{ s.id }} • {{ s.created_at }}</div>
                </div>
                <div class="sub-actions">
                  <button class="btn btn-ghost" @click="downloadSubmissionFile(s)">Download</button>
                  <div class="grade">
                    <input class="input" style="width:90px" type="number" v-model.number="gradeForm[s.id].grade" placeholder="Baho" />
                    <input class="input" style="min-width:220px" v-model="gradeForm[s.id].teacher_comment" placeholder="Tavsif..." />
                    <button class="btn btn-primary" @click="saveGrade(s.id)">Save</button>
                  </div>
                </div>
              </div>
            </div>

            <div v-else class="muted">Hali submission yo‘q.</div>
          </div>
        </div>
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

function dayName(d){
  return ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][d] ?? d
}

function onHwFile(e){
  hwFile.value = (e.target.files && e.target.files[0]) ? e.target.files[0] : null
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
}

async function loadHomeworks(){
  hwErr.value = ''
  const res = await api.get('/api/teacher/homeworks/')
  homeworks.value = res.data
}

async function refreshAll(){
  error.value = ''
  loading.value = true
  try{
    await loadDashboard()
    await loadHomeworks()
  }catch(e){
    error.value = "Dashboardni olishda xatolik."
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
    error.value = (e?.response?.data?.detail) || "Student yaratishda xatolik."
  }finally{
    creating.value = false
  }
}

async function createHomework(){
  createdHw.value = null
  hwCreating.value = true
  hwErr.value = ''
  try{
    const fd = new FormData()
    fd.append('group_number', String(hw.value.group_number || ''))
    fd.append('title', hw.value.title || '')
    fd.append('description', hw.value.description || '')
    fd.append('link', hw.value.link || '')
    if (hwFile.value) fd.append('attachment', hwFile.value)

    const res = await api.post('/api/teacher/homeworks/create/', fd)
    createdHw.value = res.data
    hw.value = { title:'', description:'', link:'', group_number: null }
    hwFile.value = null
    await loadHomeworks()
  }catch(e){
    hwErr.value = (e?.response?.data?.detail) || "Vazifa yaratishda xatolik."
  }finally{
    hwCreating.value = false
  }
}

async function loadSubmissions(homeworkId){
  try{
    const res = await api.get(`/api/teacher/homeworks/${homeworkId}/submissions/`)
    submissions.value[homeworkId] = res.data
    // forma uchun default values
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
    hwErr.value = "Submissions olishda xatolik."
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

onMounted(refreshAll)
</script>
