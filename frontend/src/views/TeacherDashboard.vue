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
            <span class="muted">Yuklangan topshiriqlar</span>
            <span class="pill">✅</span>
          </div>
          <div class="stat-num">
            {{ totalLoadedSubmissions }}
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
              <div>
                <h3 style="margin:0">{{ g.group_number }} — {{ g.name }}</h3>
                <div class="small muted">ID: {{ g.id }}</div>
              </div>

              <div class="row">
                <span class="pill">👥 {{ g.students_count }} o‘quvchi</span>
                <button class="btn btn-primary" @click="openGroup(g.group_number)">
                  Vazifalarni ko‘rish
                </button>
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
          <span>Group number</span>
          <input class="input" v-model.number="st.group_number" type="number" placeholder="101" />
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

        <!-- ✅ Endi group_number input emas, SELECT -->
        <div class="field">
          <span>Guruh</span>
          <select class="input" v-model.number="hw.group_number">
            <option :value="null">— Guruh tanlang —</option>
            <option v-for="g in (data?.groups || [])" :key="g.id" :value="g.group_number">
              {{ g.group_number }} — {{ g.name }}
            </option>
          </select>
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
          <button class="btn btn-primary" :disabled="hwCreating">
            {{ hwCreating ? 'Saqlanmoqda...' : 'Create homework' }}
          </button>
        </div>
      </form>

      <p v-if="createdHw" class="ok" style="margin:12px 0 0">✅ Vazifa yaratildi (HW #{{ createdHw.id }})</p>
      <p v-if="hwErr" class="error" style="margin:12px 0 0">{{ hwErr }}</p>
    </div>

    <!-- ✅ HOMEWORKS BY GROUP (NEW CLEAN UI) -->
    <div class="panel">
      <div class="panel-bar">
        <div>
          <h3 class="panel-h">Vazifalar — Guruhlar bo‘yicha</h3>
          <div class="panel-sub">
            Avval guruh tanlaysiz → ichida vazifalar → ichida submissionlar va baholash.
          </div>
        </div>

        <div class="row">
          <button class="btn btn-ghost" @click="loadHomeworks">Reload</button>
        </div>
      </div>

      <!-- Group selector row -->
      <div v-if="data?.groups?.length" class="row" style="gap:10px; flex-wrap:wrap; margin-bottom: 12px;">
        <button v-for="g in data.groups" :key="'tab-' + g.id" class="btn"
          :class="selectedGroupNumber === g.group_number ? 'btn-primary' : 'btn-ghost'"
          @click="openGroup(g.group_number)">
          {{ g.group_number }} — {{ g.name }}
          <span class="badge" style="margin-left:8px">
            <span class="dot"></span>
            {{ (homeworksByGroup[g.group_number] || []).length }} ta
          </span>
        </button>
      </div>

      <div v-else class="muted">Guruhlar yo‘q.</div>

      <!-- Selected group content -->
      <div v-if="selectedGroupNumber" class="card">
        <div class="card-pad">
          <div class="card-head">
            <div>
              <div style="font-weight:900; font-size:16px">
                Guruh: {{ selectedGroupNumber }} —
                {{ groupName(selectedGroupNumber) }}
              </div>
              <div class="small muted">
                Vazifalar soni: {{ (homeworksByGroup[selectedGroupNumber] || []).length }}
              </div>
            </div>

            <div class="row">
              <button class="btn btn-ghost" @click="selectedGroupNumber = null">
                Guruhlarga qaytish
              </button>
            </div>
          </div>

          <div class="divider"></div>

          <!-- Homeworks list for group -->
          <div v-if="(homeworksByGroup[selectedGroupNumber] || []).length" class="stack">
            <div v-for="h in homeworksByGroup[selectedGroupNumber]" :key="'hw-' + h.id" class="card"
              style="box-shadow:none">
              <div class="card-pad">
                <div class="card-head">
                  <div>
                    <div style="font-weight:900">{{ h.title }}</div>

                    <div class="small muted">
                      HW #{{ h.id }}
                      <span v-if="h.created_at"> • Yaratilgan: {{ fmtDT(h.created_at) }}</span>
                      <span v-if="h.due_date"> • Deadline: {{ fmtDT(h.due_date) }}</span>
                    </div>

                    <div v-if="h.description" class="muted" style="margin-top:8px">
                      {{ h.description }}
                    </div>
                  </div>

                  <div class="row">
                    <button v-if="h.has_attachment" class="btn btn-ghost" @click="downloadHomeworkAttachment(h)">
                      Download file
                    </button>
                    <a v-if="h.link" class="btn btn-ghost" :href="h.link" target="_blank">Open link</a>
                  </div>
                </div>

                <div class="divider"></div>

                <div class="row" style="justify-content:space-between; align-items:center">
                  <div>
                    <b>Submissionlar</b>
                    <span class="small muted" style="margin-left:8px">
                      ({{ (submissionsByHomework[h.id] || []).length }} ta yuklangan)
                    </span>
                  </div>
                  <button class="btn btn-ghost" @click="loadSubmissions(h.id)">Load</button>
                </div>

                <!-- submissions -->
                <div v-if="(submissionsByHomework[h.id] || []).length" class="stack" style="margin-top: 12px;">
                  <div v-for="s in submissionsByHomework[h.id]" :key="'sub-' + s.id" class="card" style="box-shadow:none">
                    <div class="card-pad">
                      <div class="card-head">
                        <div>
                          <div style="font-weight:900">
                            {{ s.student_full_name || s.student_username }}
                          </div>
                          <div class="small muted">
                            @{{ s.student_username }} • Submission #{{ s.id }}
                            <span v-if="s.submitted_at"> • {{ fmtDT(s.submitted_at) }}</span>
                          </div>
                        </div>

                        <div class="row">
                          <button v-if="s.file" class="btn btn-ghost"
                            @click="downloadSubmissionFile(s)">Download</button>
                        </div>
                      </div>

                      <div v-if="s.text_answer" class="muted" style="margin-top:10px">
                        📝 {{ s.text_answer }}
                      </div>

                      <div class="divider"></div>

                      <div v-if="gradeForm[s.id]" class="row"
                        style="gap:10px; flex-wrap:wrap; justify-content:flex-end">
                        <input class="input" style="width:90px" type="number" v-model.number="gradeForm[s.id].grade"
                          placeholder="Baho" />
                        <input class="input" style="min-width:220px" v-model="gradeForm[s.id].teacher_comment"
                          placeholder="Tavsif..." />
                        <button class="btn btn-primary" @click="saveGrade(s.id, h.id)">
                          Save
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                <div v-else class="muted" style="margin-top:10px">
                  Hali submission yo‘q.
                </div>
              </div>
            </div>
          </div>

          <div v-else class="muted">
            Bu guruhda hali vazifa yo‘q.
          </div>
        </div>
      </div>

      <div v-else class="muted">
        Guruhni tanlang (yuqoridagi tugmalardan).
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue'
import api from '../lib/api'
import { downloadFile } from '../lib/download'

const data = ref(null)
const loading = ref(false)
const error = ref('')

const creating = ref(false)
const createdStudent = ref(null)
const st = ref({ username: '', password: '', full_name: '', group_number: null })

const hwCreating = ref(false)
const createdHw = ref(null)
const hwErr = ref('')

const homeworks = ref([])
const submissionsByHomework = ref({}) // homeworkId -> submissions[]
const gradeForm = ref({}) // submissionId -> {grade, teacher_comment}

const hwFile = ref(null)
const hw = ref({ title: '', description: '', link: '', group_number: null })

const selectedGroupNumber = ref(null)

function dayName(d) {
  return ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][d] ?? d
}

function onHwFile(e) {
  hwFile.value = (e.target.files && e.target.files[0]) ? e.target.files[0] : null
}

function fmtDT(v) {
  if (!v) return ''
  try {
    const d = new Date(v)
    return d.toLocaleString()
  } catch {
    return String(v)
  }
}

function groupName(groupNumber) {
  const g = (data.value?.groups || []).find(x => x.group_number === groupNumber)
  return g?.name || ''
}

const homeworksByGroup = computed(() => {
  const map = {}
  for (const h of (homeworks.value || [])) {
    const gn = h?.group_info?.group_number
      ?? h?.group_number
      ?? null

    if (!gn) continue
    if (!map[gn]) map[gn] = []
    map[gn].push(h)
  }
  return map
})

const totalLoadedSubmissions = computed(() => {
  const obj = submissionsByHomework.value || {}
  return Object.values(obj).reduce((a, arr) => a + (arr?.length || 0), 0)
})

function openGroup(groupNumber) {
  selectedGroupNumber.value = groupNumber
}

async function downloadHomeworkAttachment(h) {
  try {
    await downloadFile(`/api/files/homeworks/${h.id}/attachment/`, `homework_${h.id}`)
  } catch (e) {
    hwErr.value = 'Attachment download qilishda xatolik.'
  }
}

async function downloadSubmissionFile(s) {
  try {
    await downloadFile(`/api/files/submissions/${s.id}/file/`, `submission_${s.id}`)
  } catch (e) {
    hwErr.value = 'Submission faylini download qilishda xatolik.'
  }
}

async function loadDashboard() {
  const res = await api.get('/api/teacher/dashboard/')
  data.value = res.data

  // default selected group (agar tanlanmagan bo‘lsa)
  if (!selectedGroupNumber.value && res.data?.groups?.length) {
    selectedGroupNumber.value = res.data.groups[0].group_number
  }
}

async function loadHomeworks() {
  hwErr.value = ''
  const res = await api.get('/api/teacher/homeworks/')
  homeworks.value = res.data || []
}

async function refreshAll() {
  error.value = ''
  loading.value = true
  try {
    await loadDashboard()
    await loadHomeworks()
  } catch (e) {
    error.value = "Dashboardni olishda xatolik."
  } finally {
    loading.value = false
  }
}

async function createStudent() {
  createdStudent.value = null
  creating.value = true
  error.value = ''
  try {
    const res = await api.post('/api/teacher/students/', { ...st.value })
    createdStudent.value = res.data
    st.value = { username: '', password: '', full_name: '', group_number: null }
  } catch (e) {
    error.value = (e?.response?.data?.detail) || "Student yaratishda xatolik."
  } finally {
    creating.value = false
  }
}

async function createHomework() {
  createdHw.value = null
  hwCreating.value = true
  hwErr.value = ''
  try {
    if (!hw.value.group_number) {
      hwErr.value = "Guruh tanlang."
      return
    }

    const fd = new FormData()
    fd.append('group_number', String(hw.value.group_number || ''))
    fd.append('title', hw.value.title || '')
    fd.append('description', hw.value.description || '')
    fd.append('link', hw.value.link || '')
    if (hwFile.value) fd.append('attachment', hwFile.value)

    const res = await api.post('/api/teacher/homeworks/create/', fd)
    createdHw.value = res.data

    hw.value = { title: '', description: '', link: '', group_number: null }
    hwFile.value = null

    await loadHomeworks()

    // agar hozir tanlangan guruh bo‘lsa, o‘shanga “drop” bo‘lib ko‘rinsin
    if (selectedGroupNumber.value === null && data.value?.groups?.length) {
      selectedGroupNumber.value = data.value.groups[0].group_number
    }
  } catch (e) {
    hwErr.value = (e?.response?.data?.detail) || "Vazifa yaratishda xatolik."
  } finally {
    hwCreating.value = false
  }
}

async function loadSubmissions(homeworkId) {
  try {
    const res = await api.get(`/api/teacher/homeworks/${homeworkId}/submissions/`)
    submissionsByHomework.value[homeworkId] = res.data || []

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
  } catch (e) {
    hwErr.value = "Submissions olishda xatolik."
  }
}

async function saveGrade(submissionId, homeworkId) {
  try {
    const body = {
      grade: gradeForm.value[submissionId]?.grade,
      teacher_comment: gradeForm.value[submissionId]?.teacher_comment || ''
    }
    await api.patch(`/api/teacher/submissions/${submissionId}/grade/`, body)
    await loadSubmissions(homeworkId)
  } catch (e) {
    hwErr.value = (e?.response?.data?.detail) || 'Baho saqlashda xatolik.'
  }
}

onMounted(refreshAll)
</script>
