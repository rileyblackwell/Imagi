<!--
  IdeaPrompt — the home page's call to action, shaped like the product.

  Instead of a "Start building" button, the visitor types the business they
  want straight away. Submitting carries the text to the "Start a project" form
  (see utils/pendingIdea), sending signed-out visitors through sign-in first.
  An empty submit still goes to the projects page, like the old button did.

  Enter submits; Shift+Enter adds a line. The textarea grows with its content.

  It only renders on Spotlight pages (Home, About, Terms, Privacy), as a glassy
  command bar with a glowing gradient edge.
-->
<template>
  <form
    class="grid gap-[14px] rounded-[22px] border border-transparent p-[18px] backdrop-blur-[14px]
      [background:var(--sl-prompt-bg)_padding-box,var(--sl-prompt-edge)_border-box]
      [transition:border-color_0.2s_ease,box-shadow_0.2s_ease] max-[560px]:p-[14px]"
    :class="focused ? 'shadow-sl-prompt-focus' : 'shadow-sl-prompt'"
    @submit.prevent="submit"
  >
    <!-- The gradient edge is a second background clipped to the border box, so
         the panel keeps one element and one radius. -->
    <label :for="inputId" class="sr-only">Describe the business you want to start</label>
    <textarea
      :id="inputId"
      ref="input"
      v-model="text"
      class="block max-h-[14rem] w-full resize-none [border:0] bg-transparent px-1 pb-0 pt-1 font-sl-body
        leading-[1.5] text-sl-text [outline:none]"
      :class="size === 'md'
        ? 'min-h-[56px] text-[17px] placeholder:text-sl-faint'
        : 'min-h-[84px] text-[19px] placeholder:text-sl-placeholder max-[560px]:min-h-[92px] max-[560px]:text-[17px]'"
      rows="2"
      :placeholder="placeholder"
      @focus="onFocus"
      @blur="focused = false"
      @input="onInput"
      @keydown.enter.exact.prevent="submit"
    ></textarea>

    <div
      class="flex flex-wrap items-center justify-between gap-3"
      :class="size === 'md' ? 'pt-0 [border-top:0]' : 'border-t border-t-sl-line pt-3'"
    >
      <div v-if="suggestions.length" class="flex min-w-0 flex-wrap gap-2" role="group" aria-label="Start from an example">
        <!-- No focus ring, as before: the old rule's outline read var(--accent),
             which is undefined outside .editorial, so the whole outline dropped. -->
        <button
          v-for="s in suggestions"
          :key="s.label"
          type="button"
          class="idea__chip rounded-[999px] border border-sl-line bg-sl-chip-bg px-[13px] py-[9px] text-[13.5px]
            font-medium leading-none text-sl-muted
            [transition:border-color_0.18s_ease,color_0.18s_ease,background_0.18s_ease]
            hover:border-sl-line-strong hover:bg-sl-chip-bg-hover hover:text-sl-text
            focus-visible:![outline:medium_none_var(--sl-focus)] focus-visible:!outline-offset-2"
          @click="useSuggestion(s.text)"
        >
          {{ s.label }}
        </button>
      </div>

      <!-- .btn-primary (spotlight.css, and editorial.css on the legal pages)
           supplies the lit pill and its hover lift; the ! utilities are the
           properties this button sets differently from it. -->
      <button
        type="submit"
        class="btn-primary group ml-auto inline-flex cursor-pointer items-center justify-center whitespace-nowrap
          rounded-[999px] !gap-[10px] !py-[13px] !pl-[22px] !pr-[18px] !text-[15px] !font-bold
          ![transition:transform_0.2s_ease,box-shadow_0.2s_ease] focus-visible:!outline-offset-4
          max-[560px]:w-full max-[560px]:!py-[15px] motion-reduce:![transition:none]"
      >
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
