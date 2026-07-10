<!--
  TaskForm.vue - Create/edit an operational task.
-->
<template>
  <form class="space-y-4" @submit.prevent="submit">
    <div v-if="error" :class="ui.errorBox">{{ error }}</div>

    <div>
      <label :class="ui.label" for="task-title">Task</label>
      <input
        id="task-title"
        v-model="form.title"
        type="text"
        required
        maxlength="255"
        placeholder="e.g. Restock inventory"
        :class="ui.input"
      />
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <div>
        <label :class="ui.label" for="task-status">Status</label>
        <select id="task-status" v-model="form.status" :class="ui.input">
          <option value="todo">To do</option>
          <option value="in_progress">In progress</option>
          <option value="done">Done</option>
        </select>
      </div>
      <div>
        <label :class="ui.label" for="task-priority">Priority</label>
        <select id="task-priority" v-model="form.priority" :class="ui.input">
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
      </div>
      <div>
        <label :class="ui.label" for="task-due">Due date <span class="normal-case tracking-normal font-normal">(optional)</span></label>
        <input id="task-due" v-model="form.due_date" type="date" :class="ui.input" />
      </div>
    </div>

    <div>
      <label :class="ui.label" for="task-notes">Notes <span class="normal-case tracking-normal font-normal">(optional)</span></label>
      <textarea id="task-notes" v-model="form.notes" rows="2" :class="ui.input"></textarea>
    </div>

    <div class="flex justify-end gap-3 pt-2">
      <button type="button" :class="ui.secondaryBtn" @click="$emit('close')">Cancel</button>
      <button type="submit" :disabled="saving" :class="ui.primaryBtn">
        <i v-if="saving" class="fas fa-circle-notch fa-spin text-xs"></i>
        {{ task ? 'Save changes' : 'Add task' }}
      </button>
    </div>
  </form>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { extractError } from '../services/operateService'
import { useOperateStore } from '../stores/operate'
import type { OperationsTask, TaskPriority, TaskStatus } from '../types'
import { ui } from '../utils/ui'

const props = defineProps<{
  /** When set, the form edits this task; otherwise it creates one. */
  task?: OperationsTask | null
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'saved'): void
}>()

const store = useOperateStore()
const saving = ref(false)
const error = ref('')

const form = reactive({
  title: props.task?.title ?? '',
  status: (props.task?.status ?? 'todo') as TaskStatus,
  priority: (props.task?.priority ?? 'medium') as TaskPriority,
  due_date: props.task?.due_date ?? '',
  notes: props.task?.notes ?? '',
})

async function submit() {
  saving.value = true
  error.value = ''
  try {
    const payload = {
      title: form.title.trim(),
      status: form.status,
      priority: form.priority,
      due_date: form.due_date || null,
      notes: form.notes.trim(),
    }
    if (props.task) {
      await store.updateTask(props.task.id, payload)
    } else {
      await store.createTask(payload)
    }
    emit('saved')
  } catch (err) {
    error.value = extractError(err, 'Could not save the task.')
  } finally {
    saving.value = false
  }
}
</script>
