<template>
  <div class="chat-page">
    <!-- TOP: Contacts/Threads/Groups -->
    <section class="top card">
      <header class="top-head">
        <div class="title">
          <div class="h">Chat</div>
          <div class="small">Kontaktlar • Direct • Guruh</div>
        </div>

        <div class="actions">
          <div class="search">
            <input class="input" v-model="q" placeholder="Qidirish (ism, chat, guruh)…" />
          </div>

          <button v-if="isTeacher" class="btn btn-primary" @click="openCreateGroup">
            + Guruh
          </button>
        </div>
      </header>

      <div class="tabs">
        <button class="tab" :class="{ active: tab === 'contacts' }" @click="tab = 'contacts'">Kontaktlar</button>
        <button class="tab" :class="{ active: tab === 'direct' }" @click="tab = 'direct'">Chatlar</button>
        <button class="tab" :class="{ active: tab === 'groups' }" @click="tab = 'groups'">Guruhlar</button>

        <div class="tabs-right">
          <button class="btn btn-ghost mini" @click="refreshAll">Yangilash</button>
        </div>
      </div>

      <div class="list" v-if="tab === 'contacts'">
        <div v-if="!isTeacher" class="hint">
          O‘quvchi uchun kontaktlar shaxsiy chat orqali ko‘rinadi.
        </div>

        <template v-else>
          <div v-if="contactsLoading" class="hint">Yuklanmoqda...</div>
          <div v-else-if="filteredContacts.length === 0" class="hint">
            Teacher guruhlariga biriktirilgan o‘quvchilar bu yerda chiqadi.
          </div>

          <div v-for="c in filteredContacts" :key="c.id" class="item"
            :class="{ active: selected?.type === 'thread' && selected?.otherId === c.id }" @click="startDirectFromContact(c)">
            <div class="left">
              <div class="avatar">
                <span>{{ initials(c.full_name || c.username) }}</span>
              </div>

              <div class="meta">
                <div class="name">{{ c.full_name || c.username }}</div>
                <div class="sub">
                  <span class="dot" :class="c.is_online ? 'online' : 'offline'"></span>
                  <span>{{ c.is_online ? 'online' : 'offline' }}</span>
                </div>
              </div>
            </div>

            <span class="badge">Student</span>
          </div>
        </template>
      </div>

      <div class="list" v-else-if="tab === 'direct'">
        <div v-if="threadsLoading" class="hint">Yuklanmoqda...</div>
        <div v-else-if="filteredThreads.length === 0" class="hint">
          Hali direct chat yo‘q. Teacher: kontaktni bosib boshlang.
        </div>

        <div v-for="t in filteredThreads" :key="t.id" class="item"
          :class="{ active: selected?.type === 'thread' && selected?.id === t.id }" @click="selectThread(t)">
          <div class="left">
            <div class="avatar">
              <span>{{ initials(otherName(t)) }}</span>
            </div>
            <div class="meta">
              <div class="name">{{ otherName(t) }}</div>
              <div class="sub">{{ t.last_message?.text || '—' }}</div>
            </div>
          </div>
          <span class="badge">Direct</span>
        </div>
      </div>

      <div class="list" v-else>
        <div v-if="groupsLoading" class="hint">Yuklanmoqda...</div>
        <div v-else-if="filteredGroups.length === 0" class="hint">
          Hali guruh yo‘q. Teacher: “+ Guruh” bosib yarating.
        </div>

        <div v-for="g in filteredGroups" :key="g.id" class="item"
          :class="{ active: selected?.type === 'group' && selected?.id === g.id }" @click="selectGroup(g)">
          <div class="left">
            <div class="avatar hash">
              <span>#</span>
            </div>
            <div class="meta">
              <div class="name">{{ g.name }}</div>
              <div class="sub">{{ g.last_message?.text || '—' }}</div>
            </div>
          </div>
          <span class="badge">{{ g.members_count }} a'zo</span>
        </div>
      </div>
    </section>

    <!-- BOTTOM: Messages -->
    <section class="bottom card">
      <header class="chat-head">
        <div class="who">
          <div class="who-title">{{ headerTitle }}</div>
          <div class="small">{{ headerSub }}</div>
        </div>

        <div class="chat-actions">
          <button v-if="selected?.type === 'group' && isTeacher && selectedGroupOwner" class="btn mini"
            @click="openAddMembers">
            + A'zo
          </button>
        </div>
      </header>

      <div class="chat-body" ref="msgBox">
          <div class="hint" v-if="(selected?.type === 'thread' && threadNext) || (selected?.type === 'group' && groupNext)">
            <button class="btn btn-ghost" style="width:100%" @click="loadMoreMessages" :disabled="loadingMore">
              {{ loadingMore ? 'Yuklanmoqda...' : 'Load older messages' }}
            </button>
          </div>
        <div v-if="!selected" class="empty">
          Chap tomondan kontakt/chat tanlang.
        </div>

        <template v-else>
          <div v-if="messagesLoading" class="hint">Yuklanmoqda...</div>

          <div v-for="m in messages" :key="m.id" class="bubble" :class="{ me: m.sender === auth.user?.id }">
            <div class="txt">{{ m.text }}</div>
            <div class="time">{{ formatTime(m.created_at) }}</div>
          </div>

          <div v-if="!messagesLoading && messages.length === 0" class="hint">Hali xabar yo‘q.</div>
        </template>
      </div>

      <footer class="chat-input" v-if="selected">
        <textarea v-model="draft" class="input" placeholder="Xabar yozing…" @keydown.enter.exact.prevent="send" />
        <button class="btn btn-primary" @click="send" :disabled="sending || !draft.trim()">
          {{ sending ? '...' : 'Yuborish' }}
        </button>
      </footer>
    </section>

    <!-- Create Group Modal -->
    <div v-if="showCreateGroup" class="modal">
      <div class="backdrop" @click="closeCreateGroup"></div>
      <div class="modal-card card">
        <div class="modal-head">
          <div>
            <div class="modal-title">Yangi guruh</div>
            <div class="small">Nom bering va o‘quvchilarni qo‘shing</div>
          </div>
          <button class="btn btn-ghost" @click="closeCreateGroup">Yopish</button>
        </div>

        <div class="gap"></div>
        <input class="input" v-model="groupForm.name" placeholder="Guruh nomi" />

        <div class="gap"></div>
        <div class="small">A'zolar</div>
        <div class="pick-list">
          <label v-for="c in contacts" :key="c.id" class="pick">
            <input type="checkbox" :value="c.id" v-model="groupForm.member_ids" />
            <span>{{ c.full_name || c.username }}</span>
            <span class="small right">{{ c.is_online ? 'online' : 'offline' }}</span>
          </label>
        </div>

        <div class="modal-actions">
          <button class="btn btn-ghost" @click="closeCreateGroup">Bekor</button>
          <button class="btn btn-primary" @click="createGroup" :disabled="creatingGroup || !groupForm.name.trim()">
            {{ creatingGroup ? '...' : 'Yaratish' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Add Members Modal -->
    <div v-if="showAddMembers" class="modal">
      <div class="backdrop" @click="closeAddMembers"></div>
      <div class="modal-card card">
        <div class="modal-head">
          <div>
            <div class="modal-title">A'zo qo‘shish</div>
            <div class="small">{{ selectedGroup?.name }}</div>
          </div>
          <button class="btn btn-ghost" @click="closeAddMembers">Yopish</button>
        </div>

        <div class="gap"></div>
        <div class="pick-list">
          <label v-for="c in contacts" :key="c.id" class="pick">
            <input type="checkbox" :value="c.id" v-model="addMembersIds" />
            <span>{{ c.full_name || c.username }}</span>
          </label>
        </div>

        <div class="modal-actions">
          <button class="btn btn-ghost" @click="closeAddMembers">Bekor</button>
          <button class="btn btn-primary" @click="addMembers" :disabled="addingMembers || addMembersIds.length === 0">
            {{ addingMembers ? '...' : 'Qo‘shish' }}
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, reactive, ref, nextTick } from 'vue'
import api from '../lib/api'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const isTeacher = computed(() => auth.user?.role === 'TEACHER')

const tab = ref('contacts')
const q = ref('')

const contacts = ref([])
const contactsLoading = ref(false)
const threads = ref([])
const threadsLoading = ref(false)
const groups = ref([])
const groupsLoading = ref(false)

const selected = ref(null) // {type, id, payload, otherId?}
const messages = ref([])
const threadNext = ref(null)
const groupNext = ref(null)
const loadingMore = ref(false)
const threadNext = ref(null)
const groupNext = ref(null)
const loadingMore = ref(false)
const messagesLoading = ref(false)

const draft = ref('')
const sending = ref(false)
const msgBox = ref(null)
let poll = null

const selectedGroup = computed(() => selected.value?.type === 'group' ? selected.value.payload : null)
const selectedGroupOwner = computed(() => selectedGroup.value?.owner === auth.user?.id)

const headerTitle = computed(() => {
  if (!selected.value) return 'Chat'
  if (selected.value.type === 'thread') return otherName(selected.value.payload)
  if (selected.value.type === 'group') return selected.value.payload.name
  return 'Chat'
})
const headerSub = computed(() => {
  if (!selected.value) return 'Kontaktlar va guruhlar yuqorida'
  return selected.value.type === 'group' ? 'Guruh chat' : 'Shaxsiy chat'
})

function initials(name = '') {
  const p = String(name).trim().split(' ').filter(Boolean)
  const a = (p[0] || '').slice(0, 1)
  const b = (p[1] || '').slice(0, 1)
  return (a + b).toUpperCase() || 'U'
}
function otherName(t) {
  if (!t) return ''
  if (auth.user?.role === 'TEACHER') return t.student_info?.full_name || t.student_info?.username || 'Student'
  return t.teacher_info?.full_name || t.teacher_info?.username || 'Teacher'
}
function formatTime(iso) {
  try { return new Date(iso).toLocaleString() } catch { return iso }
}
async function scrollBottom() {
  await nextTick()
  if (msgBox.value) msgBox.value.scrollTop = msgBox.value.scrollHeight
}

const filteredContacts = computed(() => {
  const s = q.value.trim().toLowerCase()
  if (!s) return contacts.value
  return contacts.value.filter(x => String(x.full_name || x.username || '').toLowerCase().includes(s))
})
const filteredThreads = computed(() => {
  const s = q.value.trim().toLowerCase()
  if (!s) return threads.value
  return threads.value.filter(t => otherName(t).toLowerCase().includes(s) || String(t.last_message?.text || '').toLowerCase().includes(s))
})
const filteredGroups = computed(() => {
  const s = q.value.trim().toLowerCase()
  if (!s) return groups.value
  return groups.value.filter(g => String(g.name || '').toLowerCase().includes(s) || String(g.last_message?.text || '').toLowerCase().includes(s))
})

async function loadContacts() {
  if (!isTeacher.value) return
  contactsLoading.value = true
  try {
    const { data } = await api.get('/api/contacts/')
    contacts.value = data
  } finally { contactsLoading.value = false }
}

function unwrapPage(data){
  // Supports both paginated and old array responses
  if (Array.isArray(data)) return { results: data, next: null }
  return { results: data?.results || [], next: data?.next || null }
}

function mergeMessages(existing, incoming){
  const map = new Map()
  for (const m of (existing || [])) map.set(m.id, m)
  for (const m of (incoming || [])) map.set(m.id, m)
  const out = Array.from(map.values())
  out.sort((a,b)=> new Date(a.created_at) - new Date(b.created_at))
  return out
}

async function keepScrollAfterPrepend(prependCount){
  // Keep scroll position when we prepend older messages
  const el = msgBox.value
  if (!el || prependCount <= 0) return
  const prevScrollFromBottom = el.scrollHeight - el.scrollTop
  await nextTick()
  el.scrollTop = el.scrollHeight - prevScrollFromBottom
}

async function loadThreads() {
  threadsLoading.value = true
  try {
    const { data } = await api.get('/api/threads/')
    threads.value = data
  } finally { threadsLoading.value = false }
}
async function loadGroups() {
  groupsLoading.value = true
  try {
    const { data } = await api.get('/api/groups/')
    groups.value = data
  } finally { groupsLoading.value = false }
}

async function refreshAll() {
  await Promise.all([loadContacts(), loadThreads(), loadGroups()])
  if (selected.value?.type === 'thread') await loadThreadMessages(selected.value.payload.id, { silent: true, reset: false })
  if (selected.value?.type === 'group') await loadGroupMessages(selected.value.payload.id, { silent: true, reset: false })
}

async function selectThread(t) {
  selected.value = { type: 'thread', id: t.id, payload: t }
  tab.value = 'direct'
  messages.value = []
  threadNext.value = null
  groupNext.value = null
  await loadThreadMessages(t.id, { reset: true })
}
async function selectGroup(g) {
  selected.value = { type: 'group', id: g.id, payload: g }
  tab.value = 'groups'
  messages.value = []
  threadNext.value = null
  groupNext.value = null
  await loadGroupMessages(g.id, { reset: true })
}

async function startDirectFromContact(c) {
  const { data } = await api.post('/api/threads/start/', { other_user_id: c.id })
  await loadThreads()
  selected.value = { type: 'thread', id: data.id, payload: data, otherId: c.id }
  tab.value = 'direct'
  threadNext.value = null
  groupNext.value = null
  await loadThreadMessages(data.id, { reset: true })
}

async function loadThreadMessages(id, { silent = false, reset = false } = {}) {
  if (!silent) messagesLoading.value = true
  try {
    const { data } = await api.get(`/api/threads/${id}/messages/`, { params: { page: 1 } })
    const page = unwrapPage(data)
    threadNext.value = page.next
    const incoming = (page.results || []).slice().reverse() // oldest -> newest
    messages.value = reset ? incoming : mergeMessages(messages.value, incoming)
    await scrollBottom()
  } catch (e) {
    if (!silent) messagesErr.value = 'Messages olishda xatolik.'
  } finally {
    if (!silent) messagesLoading.value = false
  }
}

async function loadGroupMessages(id, { silent = false, reset = false } = {}) {
  if (!silent) messagesLoading.value = true
  try {
    const { data } = await api.get(`/api/groups/${id}/messages/`, { params: { page: 1 } })
    const page = unwrapPage(data)
    groupNext.value = page.next
    const incoming = (page.results || []).slice().reverse()
    messages.value = reset ? incoming : mergeMessages(messages.value, incoming)
    await scrollBottom()
  } catch (e) {
    if (!silent) messagesErr.value = 'Messages olishda xatolik.'
  } finally {
    if (!silent) messagesLoading.value = false
  }
}

async function loadMoreMessages() {
  if (loadingMore.value) return
  if (!selected.value) return

  const nextUrl = selected.value.type === 'thread' ? threadNext.value : groupNext.value
  if (!nextUrl) return

  loadingMore.value = true
  try {
    const before = msgBox.value ? msgBox.value.scrollHeight : 0
    const { data } = await api.get(nextUrl)
    const page = unwrapPage(data)

    if (selected.value.type === 'thread') threadNext.value = page.next
    else groupNext.value = page.next

    const incoming = (page.results || []).slice().reverse()
    messages.value = [...incoming, ...messages.value]

    // keep scroll position (so UI doesn't jump)
    await keepScrollAfterPrepend(before)
  } finally {
    loadingMore.value = false
  }
}

async function send() {
  const text = draft.value.trim()
  if (!text || !selected.value) return
  sending.value = true
  try {
    if (selected.value.type === 'thread') {
      await api.post(`/api/threads/${selected.value.payload.id}/messages/`, { text })
      await loadThreadMessages(selected.value.payload.id, { silent: true, reset: false })
      await loadThreads()
    } else if (selected.value.type === 'group') {
      await api.post(`/api/groups/${selected.value.payload.id}/messages/`, { text })
      await loadGroupMessages(selected.value.payload.id, { silent: true, reset: false })
      await loadGroups()
    }
    draft.value = ''
  } finally { sending.value = false }
}

/* Group modals */
const showCreateGroup = ref(false)
const creatingGroup = ref(false)
const groupForm = reactive({ name: '', member_ids: [] })

function openCreateGroup() {
  showCreateGroup.value = true
  loadContacts()
}
function closeCreateGroup() {
  showCreateGroup.value = false
  groupForm.name = ''
  groupForm.member_ids = []
}
async function createGroup() {
  creatingGroup.value = true
  try {
    const { data } = await api.post('/api/groups/', { name: groupForm.name, member_ids: groupForm.member_ids })
    showCreateGroup.value = false
    await loadGroups()
    selectGroup(data)
  } finally { creatingGroup.value = false }
}

const showAddMembers = ref(false)
const addMembersIds = ref([])
const addingMembers = ref(false)

function openAddMembers() {
  showAddMembers.value = true
  addMembersIds.value = []
  loadContacts()
}
function closeAddMembers() {
  showAddMembers.value = false
  addMembersIds.value = []
}
async function addMembers() {
  if (!selectedGroup.value) return
  addingMembers.value = true
  try {
    await api.post(`/api/groups/${selectedGroup.value.id}/members/`, { member_ids: addMembersIds.value })
    showAddMembers.value = false
    await loadGroups()
  } finally { addingMembers.value = false }
}

function startPoll() {
  stopPoll()
  poll = setInterval(async () => {
    try {
      if (selected.value?.type === 'thread') await loadThreadMessages(selected.value.payload.id, { silent: true, reset: false })
      if (selected.value?.type === 'group') await loadGroupMessages(selected.value.payload.id, { silent: true, reset: false })
      await loadContacts()
    } catch { }
  }, 8000)
}
function stopPoll() { if (poll) clearInterval(poll); poll = null }

onMounted(async () => {
  await refreshAll()
  startPoll()
})
onUnmounted(() => stopPoll())
</script>

<style scoped>
/* page layout: ALWAYS stacked (tagma-tag) */
.chat-page {
  height: calc(100vh - 64px);
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

/* top list area */
.top{
  flex: 0 0 clamp(220px, 30vh, 360px); /* 220px dan kichik emas, 360px dan katta emas */
  min-height: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.bottom{
  flex: 1 1 auto;
  min-height: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.top-head {
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, .08);
}

.title .h {
  font-weight: 900;
  font-size: 18px
}

.actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.search {
  width: 360px
}

@media (max-width: 820px) {
  .search {
    width: 100%
  }

  .actions {
    width: 100%
  }

  .top-head {
    flex-direction: column;
    align-items: stretch
  }
}

.tabs {
  display: flex;
  gap: 10px;
  padding: 12px 16px;
  align-items: center;
  border-bottom: 1px solid rgba(255, 255, 255, .08);
}

.tab {
  flex: 0 0 auto;
  padding: 10px 12px;
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, .12);
  background: rgba(255, 255, 255, .04);
  color: var(--muted);
  cursor: pointer;
  transition: .12s ease;
  font-size: 13px;
}

.tab:hover {
  background: rgba(255, 255, 255, .06)
}

.tab.active {
  color: var(--text);
  background: rgba(255, 255, 255, .07);
  border-color: rgba(255, 255, 255, .16);
}

.tabs-right {
  margin-left: auto
}

.mini {
  padding: 9px 11px;
  border-radius: 13px
}

.list {
  flex: 1;
  overflow: auto;
  padding: 10px 10px 14px;
}

/* items (premium list row) */
.item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 12px;
  margin: 10px 6px;
  border-radius: 18px;
  border: 1px solid rgba(255, 255, 255, .10);
  background: rgba(255, 255, 255, .04);
  cursor: pointer;
  transition: .12s ease;
}

.item:hover {
  background: rgba(255, 255, 255, .06);
  transform: translateY(-1px);
}

.item.active {
  border-color: rgba(6, 182, 212, .55);
  box-shadow: 0 0 0 4px rgba(6, 182, 212, .12);
}

.left {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0
}

.meta {
  min-width: 0
}

.name {
  font-weight: 800;
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis
}

.sub {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis
}

.avatar {
  width: 42px;
  height: 42px;
  border-radius: 16px;
  background: rgba(255, 255, 255, .08);
  border: 1px solid rgba(255, 255, 255, .10);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 900;
}

.avatar.hash {
  background: rgba(124, 58, 237, .18);
  border-color: rgba(124, 58, 237, .25)
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: rgba(255, 255, 255, .35)
}

.dot.online {
  background: var(--a3);
  box-shadow: 0 0 0 6px rgba(34, 197, 94, .14)
}

.dot.offline {
  background: rgba(255, 255, 255, .25)
}

.hint {
  padding: 12px 12px;
  margin: 10px 6px;
  border-radius: 16px;
  border: 1px dashed rgba(255, 255, 255, .14);
  background: rgba(0, 0, 0, .18);
  color: var(--muted);
  font-size: 13px;
}

/* chat */
.chat-head {
  padding: 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, .08);
}

.who {
  min-width: 0
}

.who-title {
  font-weight: 900;
  font-size: 16px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chat-body {
  flex: 1;
  overflow: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-height: 0;
}

.empty {
  margin: auto;
  color: var(--muted);
  font-size: 13px;
}

.bubble {
  max-width: 78%;
  padding: 12px 12px;
  border-radius: 18px;
  border: 1px solid rgba(255, 255, 255, .10);
  background: rgba(255, 255, 255, .045);
}

.bubble.me {
  margin-left: auto;
  border: none;
  background: linear-gradient(135deg, rgba(124, 58, 237, .95), rgba(6, 182, 212, .70));
}

.txt {
  white-space: pre-wrap
}

.time {
  margin-top: 6px;
  font-size: 11px;
  color: rgba(255, 255, 255, .75)
}

.chat-input {
  padding: 14px;
  border-top: 1px solid rgba(255, 255, 255, .08);
  display: flex;
  gap: 10px;
  align-items: flex-end;
}

.chat-input textarea {
  resize: none;
  min-height: 44px;
  max-height: 140px;
}

/* modals */
.modal {
  position: fixed;
  inset: 0;
  z-index: 80;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 18px
}

.backdrop {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, .55);
  backdrop-filter: blur(6px)
}

.modal-card {
  position: relative;
  width: min(720px, 100%);
  padding: 16px;
  border-radius: 22px
}

.modal-head {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: center
}

.modal-title {
  font-weight: 900
}

.gap {
  height: 12px
}

.pick-list {
  margin-top: 10px;
  max-height: 340px;
  overflow: auto;
  border: 1px solid rgba(255, 255, 255, .10);
  border-radius: 16px;
  background: rgba(255, 255, 255, .03)
}

.pick {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 12px;
  border-bottom: 1px solid rgba(255, 255, 255, .08)
}

.pick:last-child {
  border-bottom: none
}

.right {
  margin-left: auto
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 12px
}

/* small screens: give more space to messages */
@media (max-width: 820px) {
  .chat-page {
    padding: 10px
  }

  .top {
    flex: 0 0 48%
  }
}
</style>
// deploy-test
