<!--
  OperateTasks.vue - Operational to-dos grouped by status, with one-click
  status advancement (todo -> in progress -> done).
-->
<template>
  <div>
    <!-- Toolbar -->
    <div class="flex flex-col sm:flex-row sm:items-center gap-3 mb-6">
      <div class="flex items-center gap-1.5 flex-1 overflow-x-auto">
        <button
          v-for="option in filterOptions"
          :key="option.value"
          type="button"
          class="px-3.5 py-2 rounded-xl text-sm font-medium whitespace-nowrap border transition-colors duration-200"
          :class="statusFilter === option.value
            ? 'border-amber-300 dark:border-amber-400/40 bg-amber-50 dark:bg-amber-400/10 text-amber-700 dark:text-amber-300'
            : 'border-transparent text-blue-950/60 dark:text-blue-100/60 hover:text-blue-950 dark:hover:text-white'"
          @click="setFilter(option.value)"
        >
          {{ option.label }}
          <span v-if="option.count !== null" class="ml-1 text-xs opacity-70 tabular-nums">{{ option.count }}</span>
        </button>
      </div>
      <button type="button" :class="ui.primaryBtn" @click="openCreate">
        <i class="fas fa-plus text-xs"></i>
        Add task
      </button>
    </div>

    <div v-if="loadError" :class="ui.errorBox" class="mb-6">{{ loadError }}</div>
    <div v-if="actionError" :class="ui.errorBox" class="mb-6">{{ actionError }}</div>

    <!-- Loading -->
    <div v-if="store.tasksLoading && !store.tasks.length" class="flex justify-center py-16">
      <div class="w-6 h-6 border-2 border-amber-200 dark:border-amber-300/30 border-t-amber-600 dark:border-t-amber-300 rounded-full animate-spin"></div>
    </div>

    <!-- Task list -->
    <section v-else-if="store.tasks.length" :class="ui.card" class="divide-y divide-blue-200/60 dark:divide-white/[0.08]">
      <div
        v-for="task in store.tasks"
        :key="task.id"
        class="flex items-center gap-4 px-5 py-4"
      >
        <!-- Complete toggle -->
        <button
          type="button"
          class="w-6 h-6 shrink-0 rounded-full border-2 flex items-center justify-center transition-colors duration-200"
          :class="task.status === 'done'
            ? 'border-emerald-500 bg-emerald-500 text-white'
            : 'border-blue-950/25 dark:border-white/25 text-transparent hover:border-emerald-500'"
          :disabled="busyId === task.id"
          :aria-label="task.status === 'done' ? 'Reopen task' : 'Mark task done'"
          @click="toggleDone(task)"
        >
          <i class="fas fa-check text-[10px]"></i>
        </button>

        <div class="flex-1 min-w-0">
          <p
            class="text-sm font-medium truncate transition-colors duration-200"
            :class="task.status === 'done' ? 'text-blue-950/40 dark:text-white/40 line-through' : 'text-blue-950 dark:text-white'"
          >
            {{ task.title }}
          </p>
          <p class="text-xs" :class="task.is_overdue ? 'text-red-600 dark:text-red-300' : 'text-blue-950/50 dark:text-blue-100/50'">
            <span :class="priorityClass(task.priority)">{{ task.priority }} priority</span>
            <template v-if="task.due_date"> · {{ task.is_overdue ? 'overdue — ' : 'due ' }}{{ formatDate(task.due_date) }}</template>
            <template v-if="task.notes"> · {{ task.notes }}</template>
          </p>
        </div>

        <StatusBadge :status="task.status" />

        <!-- Advance status -->
        <button
          v-if="task.status === 'todo'"
          type="button"
          :class="ui.secondaryBtn"
          class="!px-3 !py-2"
          :disabled="busyId === task.id"
          @click="setStatus(task, 'in_progress')"
        >
          <i class="fas fa-play text-[10px]"></i>
          Start
        </button>

        <div class="flex items-center gap-1">
          <button
            type="button"
            class="w-8 h-8 rounded-lg flex items-center justify-center text-blue-950/40 dark:text-white/40 hover:text-blue-950 dark:hover:text-white hover:bg-blue-50 dark:hover:bg-white/[0.08] transition-colors duration-200"
            aria-label="Edit task"
            @click="openEdit(task)"
          >
            <i class="fas fa-pen text-xs"></i>
          </button>
          <button
            type="button"
            class="w-8 h-8 rounded-lg flex items-center justify-center text-blue-950/40 dark:text-white/40 hover:text-red-600 dark:hover:text-red-300 hover:bg-red-50 dark:hover:bg-red-500/10 transition-colors duration-200"
            aria-label="Delete task"
            @click="confirmDelete(task)"
          >
            <i class="fas fa-trash-can text-xs"></i>
          </button>
        </div>
      </div>
    </section>

    <!-- Empty -->
    <section v-else class="py-16 text-center" :class="ui.card">
      <div class="w-14 h-14 mx-auto mb-4 text-xl" :class="ui.iconTile">
        <i class="fas fa-list-check"></i>
      </div>
      <h3 class="text-lg font-semibold text-blue-950 dark:text-white mb-2">
        {{ statusFilter ? 'Nothing here' : 'No tasks yet' }}
      </h3>
      <p class="text-sm text-blue-950/60 dark:text-blue-100/60 mb-6 max-w-sm mx-auto">
        {{ statusFilter ? 'No tasks match this filter.' : 'Keep track of the work that keeps your business running — fulfillment, follow-ups, admin.' }}
      </p>
      <button v-if="!statusFilter" type="button" :class="ui.primaryBtn" @click="openCreate">
        <i class="fas fa-plus text-xs"></i>
        Add your first task
      </button>
    </section>

    <!-- Create/edit modal -->
    <OperateModal
      v-if="showForm"
      :title="editing ? 'Edit task' : 'Add task'"
      @close="closeForm"
    >
      <TaskForm :task="editing" @close="closeForm" @saved="onSaved" />
    </OperateModal>

    <!-- Delete confirm -->
    <OperateModal v-if="deleting" title="Delete task" @close="deleting = null">
      <p class="text-sm text-blue-950/70 dark:text-blue-100/70 mb-6">
        Delete "{{ deleting.title }}"? This can't be undone.
      </p>
      <div v-if="deleteError" :class="ui.errorBox" class="mb-4">{{ deleteError }}</div>
      <div class="flex justify-end gap-3">
        <button type="button" :class="ui.secondaryBtn" @click="deleting = null">Cancel</button>
        <button type="button" :class="ui.dangerBtn" :disabled="deleteBusy" @click="doDelete">
          <i v-if="deleteBusy" class="fas fa-circle-notch fa-spin text-xs"></i>
          Delete
        </button>
      </div>
    </OperateModal>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import OperateModal from '../components/OperateModal.vue'
import StatusBadge from '../components/StatusBadge.vue'
import TaskForm from '../components/TaskForm.vue'
import { extractError } from '../services/operateService'
import { useOperateStore } from '../stores/operate'
import type { OperationsTask, TaskPriority, TaskStatus } from '../types'
import { formatDate, ui } from '../utils/ui'

const route = useRoute()
const router = useRouter()
const store = useOperateStore()

const statusFilter = ref('open')
const loadError = ref('')
const actionError = ref('')
const busyId = ref<number | null>(null)
const showForm = ref(false)
const editing = ref<OperationsTask | null>(null)
const deleting = ref<OperationsTask | null>(null)
const deleteBusy = ref(false)
const deleteError = ref('')

const filterOptions = computed(() => {
  const counts = store.taskCounts
  return [
    { value: 'open', label: 'Open', count: counts ? counts.todo + counts.in_progress : null },
    { value: 'in_progress', label: 'In progress', count: counts?.in_progress ?? null },
    { value: 'done', label: 'Done', count: counts?.done ?? null },
    { value: '', label: 'All', count: counts ? counts.todo + counts.in_progress + counts.done : null },
  ]
})

function priorityClass(priority: TaskPriority): string {
  if (priority === 'high') return 'text-red-600 dark:text-red-300 font-medium'
  if (priority === 'low') return 'text-blue-950/40 dark:text-blue-100/40'
  return ''
}

function setFilter(value: string) {
  statusFilter.value = value
  reload()
}

async function reload() {
  loadError.value = ''
  try {
    await store.fetchTasks({ status: statusFilter.value || undefined })
  } catch (error) {
    loadError.value = extractError(error, 'Could not load tasks.')
  }
}

async function setStatus(task: OperationsTask, status: TaskStatus) {
  actionError.value = ''
  busyId.value = task.id
  try {
    await store.updateTask(task.id, { status })
    await reload()
  } catch (error) {
    actionError.value = extractError(error, 'Could not update the task.')
  } finally {
    busyId.value = null
  }
}

function toggleDone(task: OperationsTask) {
  setStatus(task, task.status === 'done' ? 'todo' : 'done')
}

function openCreate() {
  editing.value = null
  showForm.value = true
}

function openEdit(task: OperationsTask) {
  editing.value = task
  showForm.value = true
}

function closeForm() {
  showForm.value = false
  editing.value = null
}

async function onSaved() {
  closeForm()
  await reload()
}

function confirmDelete(task: OperationsTask) {
  deleteError.value = ''
  deleting.value = task
}

async function doDelete() {
  if (!deleting.value) return
  deleteBusy.value = true
  deleteError.value = ''
  try {
    await store.deleteTask(deleting.value.id)
    deleting.value = null
    await reload()
  } catch (error) {
    deleteError.value = extractError(error, 'Could not delete the task.')
  } finally {
    deleteBusy.value = false
  }
}

onMounted(async () => {
  await reload()
  // ?new=1 (from the dashboard quick action) opens the create form.
  if (route.query.new === '1') {
    openCreate()
    router.replace({ query: { ...route.query, new: undefined } })
  }
})
</script>
