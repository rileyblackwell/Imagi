<!--
  IdeaPrompt — the home page's call to action, shaped like the product.

  Instead of a "Start building" button, the visitor types the business they
  want straight away. Submitting carries the text to the "Start a project" form
  (see utils/pendingIdea), sending signed-out visitors through sign-in first.
  An empty submit still goes to the projects page, like the old button did.

  Enter submits; Shift+Enter adds a line. The textarea grows with its content.
-->
<template>
  <form
    class="idea"
    :class="[`idea--${size}`, { 'idea--focused': focused }]"
    @submit.prevent="submit"
  >
    <label :for="inputId" class="sr-only">Describe the business you want to start</label>
    <textarea
      :id="inputId"
      ref="input"
      v-model="text"
      class="idea__input"
      rows="2"
      :placeholder="placeholder"
      @focus="onFocus"
      @blur="focused = false"
      @input="onInput"
      @keydown.enter.exact.prevent="submit"
    ></textarea>

    <div class="idea__foot">
      <div v-if="suggestions.length" class="idea__chips" role="group" aria-label="Start from an example">
        <button
          v-for="s in suggestions"
          :key="s.label"
          type="button"
          class="idea__chip"
          @click="useSuggestion(s.text)"
        >
          {{ s.label }}
        </button>
      </div>

      <button type="submit" class="btn-primary group idea__submit">
        <span>{{ submitLabel }}</span>
        <svg class="w-4 h-4 transition-transform duration-300 group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
        </svg>
      </button>
    </div>
  </form>
</template>

<script>
import { defineComponent, ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/shared/stores/auth'
import { savePendingIdea, peekPendingIdea } from '@/apps/home/utils/pendingIdea'

export default defineComponent({
  name: 'IdeaPrompt',
  props: {
    inputId: { type: String, default: 'idea-prompt' },
    placeholder: { type: String, default: 'Describe the business you want to start…' },
    // [{ label: 'Online store', text: 'An online store that sells ' }]
    suggestions: { type: Array, default: () => [] },
    submitLabel: { type: String, default: 'Start building' },
    size: { type: String, default: 'lg', validator: (v) => ['lg', 'md'].includes(v) },
    // Refill with an idea the visitor typed earlier this session — e.g. after
    // registering, which lands back on the home page rather than the form.
    restore: { type: Boolean, default: false }
  },
  emits: ['engage'],
  setup(props, { emit }) {
    const router = useRouter()
    const authStore = useAuthStore()
    const text = ref('')
    const focused = ref(false)
    const input = ref(null)

    const grow = () => {
      const el = input.value
      if (!el) return
      el.style.height = 'auto'
      el.style.height = `${el.scrollHeight}px`
    }

    const onFocus = () => {
      focused.value = true
      emit('engage')
    }

    const onInput = () => {
      grow()
      emit('engage')
    }

    const useSuggestion = async (starter) => {
      text.value = starter
      emit('engage')
      await nextTick()
      grow()
      const el = input.value
      if (el) {
        el.focus()
        el.setSelectionRange(starter.length, starter.length)
      }
    }

    const submit = () => {
      savePendingIdea(text.value)
      router.push(
        authStore.isAuthenticated
          ? { name: 'projects' }
          : { name: 'login', query: { redirect: '/imagi/projects' } }
      )
    }

    onMounted(async () => {
      if (!props.restore) return
      const saved = peekPendingIdea()
      if (!saved) return
      text.value = saved
      emit('engage')
      await nextTick()
      grow()
    })

    return { text, focused, input, onFocus, onInput, useSuggestion, submit }
  }
})
</script>

<style scoped>
.idea {
  display: grid;
  gap: 0.9rem;
  padding: 1.15rem 1.15rem 1rem 1.35rem;
  background: var(--paper-raised);
  border: 1px solid var(--rule-strong);
  border-radius: 1.4rem;
  box-shadow:
    0 1px 0 rgba(19, 26, 44, 0.03),
    0 28px 60px -34px rgba(19, 26, 44, 0.32);
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.idea--focused {
  border-color: var(--ink-40);
  box-shadow:
    0 0 0 4px var(--accent-soft),
    0 28px 60px -34px rgba(19, 26, 44, 0.32);
}

:global(.dark) .idea {
  box-shadow: 0 28px 60px -30px rgba(0, 0, 0, 0.7);
}

.idea__input {
  display: block;
  width: 100%;
  min-height: 3.4em;
  max-height: 14rem;
  resize: none;
  border: 0;
  outline: none;
  background: transparent;
  color: var(--ink);
  font: inherit;
  font-size: 1.125rem;
  line-height: 1.5;
  padding: 0.2rem 0 0;
}

.idea--md .idea__input {
  font-size: 1.02rem;
  min-height: 3em;
}

.idea__input::placeholder {
  color: var(--ink-40);
}

.idea__foot {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.idea__chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  min-width: 0;
}

.idea__chip {
  font-size: 0.8rem;
  line-height: 1;
  padding: 0.5rem 0.8rem;
  border-radius: 999px;
  border: 1px solid var(--rule);
  color: var(--ink-70);
  background: transparent;
  transition: border-color 0.18s ease, color 0.18s ease, background 0.18s ease;
}

.idea__chip:hover {
  border-color: var(--rule-strong);
  color: var(--ink);
  background: var(--accent-soft);
}

.idea__chip:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

.idea__submit {
  margin-left: auto;
  padding: 0.75rem 1.35rem;
  font-size: 0.95rem;
}

@media (max-width: 480px) {
  .idea__submit {
    width: 100%;
  }
}
</style>
