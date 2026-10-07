<!--
  IdeaPrompt — the home page's call to action, shaped like the product.

  Instead of a "Start building" button, the visitor types the business they
  want straight away. Submitting carries the text to the "Start a project" form
  (see utils/pendingIdea), sending signed-out visitors through sign-in first.
  An empty submit still goes to the projects page, like the old button did.

  Enter submits; Shift+Enter adds a line. The textarea grows with its content.

  Two looks. On the editorial pages (About, Terms, Privacy) it is paper lifted
  off the page. Inside the home page's .spotlight it becomes a glassy command
  bar with a glowing gradient edge — those rules are the .spotlight
  block at the bottom.
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

.dark .idea {
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

/* --- Spotlight (home page) ----------------------------------------------- */

/* The gradient edge is a second background clipped to the border box, so the
   panel keeps one element and one radius. */
.spotlight .idea {
  gap: 14px;
  padding: 18px;
  border: 1px solid transparent;
  border-radius: 22px;
  background:
    var(--sl-prompt-bg) padding-box,
    var(--sl-prompt-edge) border-box;
  box-shadow: var(--sl-prompt-shadow);
  backdrop-filter: blur(14px);
}

.spotlight .idea--focused {
  box-shadow: var(--sl-prompt-shadow-focus);
}

.spotlight .idea__input {
  min-height: 84px;
  padding: 4px 4px 0;
  color: var(--sl-text);
  font-family: var(--sl-font-body);
  font-size: 19px;
}

.spotlight .idea--md .idea__input {
  min-height: 56px;
  font-size: 17px;
}

.spotlight .idea__input::placeholder {
  color: var(--sl-placeholder);
}

.spotlight .idea--md .idea__input::placeholder {
  color: var(--sl-faint);
}

.spotlight .idea__foot {
  gap: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--sl-line);
}

.spotlight .idea--md .idea__foot {
  padding-top: 0;
  border-top: 0;
}

.spotlight .idea__chips {
  gap: 8px;
}

.spotlight .idea__chip {
  padding: 9px 13px;
  font-size: 13.5px;
  font-weight: 500;
  color: var(--sl-muted);
  border: 1px solid var(--sl-line);
  background: var(--sl-chip-bg);
}

.spotlight .idea__chip:hover {
  color: var(--sl-text);
  border-color: var(--sl-line-strong);
  background: var(--sl-chip-bg-hover);
}

.spotlight .idea__chip:focus-visible {
  outline-color: var(--sl-focus);
}

.spotlight .idea__submit {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 13px 18px 13px 22px;
  border: 0;
  border-radius: 999px;
  background: var(--sl-grad);
  color: var(--sl-on-accent);
  font-size: 15px;
  font-weight: 700;
  white-space: nowrap;
  cursor: pointer;
  box-shadow: var(--sl-btn-shadow);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.spotlight .idea__submit:hover {
  transform: translateY(-1px);
  box-shadow: var(--sl-btn-shadow-hover);
}

.spotlight .idea__submit:focus-visible {
  outline-offset: 4px;
  border-radius: 999px;
}

@media (max-width: 560px) {
  .spotlight .idea {
    padding: 14px;
  }

  .spotlight .idea__input {
    font-size: 17px;
    min-height: 92px;
  }

  .spotlight .idea__submit {
    width: 100%;
    padding-block: 15px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .spotlight .idea__submit {
    transition: none;
  }

  .spotlight .idea__submit:hover {
    transform: none;
  }
}
</style>
