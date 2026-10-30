<!--
  AgentComposer.vue — the one text box for talking to an agent.

  The coordinator and every thread are typed to through this same composer:
  the box, the microphone button that turns into a send arrow once there are
  words, the model and reasoning chip, and the usage meter. What differs is
  where the words go, which the pane decides through `submit`: the
  coordinator's next message, or a thread's next turn (steering it).

  Model and effort are the instance's own, so changing them on a thread
  changes that thread only.
-->
<template>
<!-- Chat Input Section (fixed at bottom). Relative so the usage panel
     can anchor to the full section width — the sidebar clips overflow,
     so a panel anchored to its narrow button couldn't fit. -->
<div class="shrink-0 relative bg-canvas transition-colors duration-300">
  <!-- Model + reasoning menu (opens upward above the composer). The
       model is a short list — three tiers, each with what it is for and
       a check on the one in use — and reasoning effort is a four-bar
       meter under it, both running faster → smarter. Each is a radio
       group: one tab stop, arrows move the choice, and every change is
       one idempotent write to the workspace.

       The panels share one popover treatment: a translucent material
       that grows out of the chip that opened it (transform-origin sits
       at the bottom edge), so opening reads as the control unfolding
       rather than a card being dealt onto the pane. Closing is faster than
       opening: dismissals should feel immediate, arrivals deliberate. -->
  <Transition
    enter-active-class="origin-bottom [transition:opacity_var(--iw-dur-2)_var(--iw-ease-out),transform_var(--iw-dur-3)_var(--iw-ease-spring)]"
    enter-from-class="translate-y-2 scale-[0.96] opacity-0"
    leave-active-class="origin-bottom [transition:opacity_var(--iw-dur-1)_var(--iw-ease-out),transform_var(--iw-dur-1)_var(--iw-ease-out)]"
    leave-to-class="translate-y-1 scale-[0.98] opacity-0"
  >
  <div
    v-if="tuneOpen"
    id="tune-panel"
    ref="tunePanel"
    role="group"
    aria-label="Model and reasoning"
    :class="['absolute bottom-full left-2 right-2 mb-1.5 z-50 overflow-hidden', POPOVER]"
    @keydown.escape.stop.prevent="closeTune"
  >
    <!-- Body scrolls on short viewports so the panel never grows past the
         top of the sidebar (the usage panel's recipe). -->
    <div class="iw-scroll max-h-[min(26rem,calc(100vh-19rem))] overflow-y-auto">
      <div class="flex items-center justify-between gap-2 border-b border-b-iw-hairline px-3 py-2">
        <span id="tune-model-heading" class="text-[11px] font-semibold uppercase tracking-wider text-ink/50 dark:text-white/50">
          Model
        </span>
        <!-- Which family's models the list shows. Switching it only changes
             the list; picking a model is what changes the conversation. -->
        <div
          role="radiogroup"
          aria-label="Model family"
          class="inline-flex rounded-full bg-ink/[0.06] p-0.5 dark:bg-white/[0.07]"
          data-testid="model-family-toggle"
          @keydown="onFamilyKeydown"
        >
          <button
            v-for="f in MODEL_FAMILIES"
            :key="f.id"
            ref="familyButtons"
            type="button"
            role="radio"
            :aria-checked="f.id === family"
            :tabindex="f.id === family ? 0 : -1"
            :class="[
              'cursor-pointer rounded-full px-2.5 py-0.5 text-[0.6875rem] font-semibold leading-[1.125rem] [border:0] ![outline:none]',
              '[transition:background-color_var(--iw-dur-2)_var(--iw-ease-out),color_var(--iw-dur-2)_var(--iw-ease-out)] motion-reduce:[transition:none]',
              'hover:text-ink focus-visible:shadow-iw-focus dark:hover:text-white/[0.92] dark:focus-visible:shadow-iw-focus',
              f.id === family
                ? 'bg-white text-ink [box-shadow:0_1px_2px_rgba(19,26,44,0.12)] dark:bg-white/[0.14] dark:text-white/95 dark:[box-shadow:none]'
                : 'bg-transparent text-ink/60 dark:text-white/55',
            ]"
            :data-testid="`model-family-${f.id}`"
            @click="family = f.id"
          >{{ f.name }}</button>
        </div>
      </div>
      <div
        role="radiogroup"
        aria-labelledby="tune-model-heading"
        class="p-1"
        @keydown="onModelKeydown"
      >
        <button
          v-for="(m, i) in familyModels"
          :key="m.id"
          ref="modelRows"
          type="button"
          role="radio"
          :aria-checked="i === modelIndex"
          :tabindex="i === Math.max(modelIndex, 0) ? 0 : -1"
          :disabled="!instance"
          :class="['model-row', MENU_ROW, i === modelIndex ? MENU_ROW_ON : 'bg-transparent']"
          @click="pickModel(m.id)"
        >
          <span class="min-w-0 flex-1">
            <span :class="['model-row__name', ROW_NAME]">
              {{ modelShortName(m.id) }}
              <span :class="ROW_TIER">{{ modelTier(m.id) }}</span>
            </span>
            <span :class="['model-row__blurb', ROW_BLURB]">{{ modelBlurb(m.id) }}</span>
          </span>
          <i
            class="fas fa-check shrink-0 text-[0.6875rem] text-ink dark:text-[#f3ede2]"
            :class="{ 'opacity-0': i !== modelIndex }"
            aria-hidden="true"
          ></i>
        </button>
      </div>

      <div class="flex items-center justify-between gap-2 border-y border-y-iw-hairline px-3 py-2">
        <span id="tune-effort-heading" class="text-[11px] font-semibold uppercase tracking-wider text-ink/50 dark:text-white/50">
          Reasoning effort
        </span>
      </div>
      <div class="flex items-center gap-3 px-3 pt-3 pb-2">
        <!-- Bars rise with the rung and fill up to the chosen one, so the
             row reads as a meter. Hovering a bar previews its rung in
             the text beside it. -->
        <div
          role="radiogroup"
          aria-labelledby="tune-effort-heading"
          aria-describedby="tune-effort-note"
          class="flex shrink-0 items-end gap-[0.1875rem]"
          @mouseleave="effortPreview = null"
          @keydown="onEffortKeydown"
        >
          <button
            v-for="(o, i) in effortOptions"
            :key="o.id"
            ref="effortBars"
            type="button"
            role="radio"
            :aria-checked="i === effortIndex"
            :aria-label="`${o.name}: ${o.description}`"
            :tabindex="i === effortIndex ? 0 : -1"
            :disabled="!instance"
            class="effort-bar flex h-7 w-4 cursor-pointer items-end rounded bg-transparent px-0.5 [border:0] ![outline:none]
              focus-visible:shadow-iw-focus disabled:cursor-not-allowed disabled:opacity-50"
            :class="{
              'effort-bar--on': i <= (effortPreview ?? effortIndex),
              'effort-bar--preview': effortPreview !== null && i <= effortPreview && i > effortIndex,
            }"
            :style="{ '--rung': i }"
            @mouseenter="effortPreview = i"
            @click="pickEffort(o.id)"
          ><span :class="effortFillClass(i)" aria-hidden="true"></span></button>
        </div>
        <div class="min-w-0 flex-1" aria-hidden="true">
          <p class="effort-readout__name text-[0.8125rem] font-medium leading-5 text-ink dark:text-white/[0.92]">{{ shownEffort?.name }}</p>
          <p :class="ROW_BLURB">{{ shownEffort?.description }}</p>
        </div>
      </div>
      <!-- What more reasoning costs. The opacities here clear 4.5:1 for 10px
           text over the glass. -->
      <p id="tune-effort-note" :class="['px-3 pt-1 pb-3', TUNE_NOTE, 'text-ink/55 dark:text-white/50']">
        More reasoning helps with difficult problems but costs more per run. Medium is the default.
      </p>

      <!-- OpenAI's faster tiers. Only an OpenAI model has them, so the
           section appears once one is picked. Each says its price beside
           its name, and the note under them says what that does to usage. -->
      <template v-if="currentProvider === 'openai'">
        <div class="flex items-center justify-between gap-2 border-y border-y-iw-hairline px-3 py-2">
          <span id="tune-speed-heading" class="text-[11px] font-semibold uppercase tracking-wider text-ink/50 dark:text-white/50">
            Speed
          </span>
        </div>
        <div
          role="radiogroup"
          aria-labelledby="tune-speed-heading"
          aria-describedby="tune-speed-note"
          class="p-1"
          data-testid="speed-options"
          @keydown="onSpeedKeydown"
        >
          <button
            v-for="(t, i) in SERVICE_TIERS"
            :key="t.id || 'standard'"
            ref="speedRows"
            type="button"
            role="radio"
            :aria-checked="t.id === currentTier"
            :tabindex="t.id === currentTier ? 0 : -1"
            :disabled="!instance || !tierOffered(t.id)"
            :class="['model-row', MENU_ROW, t.id === currentTier ? MENU_ROW_ON : 'bg-transparent']"
            :data-testid="`speed-${t.id || 'standard'}`"
            @click="pickTier(t.id)"
          >
            <span class="min-w-0 flex-1">
              <span :class="['model-row__name', ROW_NAME]">
                {{ t.name }}
                <span :class="ROW_TIER">{{ t.multiplier === 1 ? 'Standard price' : `${t.multiplier}x price` }}</span>
              </span>
              <span :class="['model-row__blurb', ROW_BLURB]">
                {{ tierOffered(t.id) ? t.description : `On ${tierModelsText(t.id)}` }}
              </span>
            </span>
            <i
              class="fas fa-check shrink-0 text-[0.6875rem] text-ink dark:text-[#f3ede2]"
              :class="{ 'opacity-0': t.id !== currentTier }"
              aria-hidden="true"
            ></i>
          </button>
        </div>
        <p
          id="tune-speed-note"
          :class="[
            'px-3 pt-1 pb-3', TUNE_NOTE,
            currentTier !== '' ? 'tune-note--cost text-sl-wait' : 'text-ink/55 dark:text-white/50',
          ]"
          data-testid="speed-cost-note"
        >
          Fast costs twice the standard price and Ultrafast six times, so each run costs that much more.
        </p>
      </template>
    </div>
  </div>
  </Transition>

  <!-- Usage limits panel (opens upward above the composer) -->
  <Transition
    enter-active-class="origin-bottom [transition:opacity_var(--iw-dur-2)_var(--iw-ease-out),transform_var(--iw-dur-3)_var(--iw-ease-spring)]"
    enter-from-class="translate-y-2 scale-[0.96] opacity-0"
    leave-active-class="origin-bottom [transition:opacity_var(--iw-dur-1)_var(--iw-ease-out),transform_var(--iw-dur-1)_var(--iw-ease-out)]"
    leave-to-class="translate-y-1 scale-[0.98] opacity-0"
  >
  <div
    v-if="usageOpen"
    ref="usagePanel"
    :class="['absolute bottom-full left-2 right-2 mb-1.5 z-50 overflow-hidden', POPOVER]"
  >
    <div class="flex items-center justify-between gap-2 border-b border-b-iw-hairline px-3 py-2">
      <span class="text-[11px] font-semibold uppercase tracking-wider text-ink/50 dark:text-white/50">
        Usage
      </span>
      <span class="text-[11px] font-medium text-ink/70 dark:text-white/70 truncate">
        {{ planSummary }}
      </span>
    </div>
    <!-- Body scrolls on short viewports (like the version-history list)
         so the panel never grows past the top of the sidebar; the calc
         budget covers the navbar + composer + panel header. -->
    <div class="iw-scroll max-h-[min(20rem,calc(100vh-19rem))] overflow-y-auto">
      <div class="px-3 py-2.5 space-y-3">
        <div v-for="meter in usageMeters" :key="meter.key">
          <div class="flex items-baseline justify-between gap-2">
            <span class="text-[10px] font-semibold uppercase tracking-wider text-ink/40 dark:text-white/40">
              {{ meter.label }}
            </span>
            <!-- Unknown usage shows an em-dash and no bar — never 0% -->
            <span class="text-[11px] font-medium tabular-nums text-ink/70 dark:text-white/70">
              {{ meter.usedText }}
            </span>
          </div>
          <!-- Quiet navy ink bar (cream in dark mode, matching the primary
               button system) -->
          <div
            v-if="meter.percent !== null"
            class="relative mt-1.5 h-1 overflow-hidden rounded-full bg-ink/10 dark:bg-white/[0.12]"
          >
            <div
              class="absolute inset-y-0 left-0 rounded-full bg-blue-950 [transition:width_var(--iw-dur-4)_var(--iw-ease-out)] dark:bg-[#f3ede2]"
              :style="{ width: `${meter.percent}%` }"
            ></div>
          </div>
          <p v-if="meter.resetsAt" class="mt-1 text-[10px] text-ink/40 dark:text-white/35">
            Resets {{ meter.resetsAt }}
          </p>
        </div>
      </div>
    </div>
  </div>
  </Transition>

  <!-- Microphone picker (opens upward above the composer). The computer's
       own mic is the default; a headset is a choice, never a surprise. -->
  <Transition
    enter-active-class="origin-bottom [transition:opacity_var(--iw-dur-2)_var(--iw-ease-out),transform_var(--iw-dur-3)_var(--iw-ease-spring)]"
    enter-from-class="translate-y-2 scale-[0.96] opacity-0"
    leave-active-class="origin-bottom [transition:opacity_var(--iw-dur-1)_var(--iw-ease-out),transform_var(--iw-dur-1)_var(--iw-ease-out)]"
    leave-to-class="translate-y-1 scale-[0.98] opacity-0"
  >
  <div
    v-if="micOpen"
    ref="micPanel"
    :class="['mic-panel absolute bottom-full left-2 right-2 mb-1.5 z-50 overflow-hidden', POPOVER]"
  >
    <div class="flex items-center justify-between gap-2 border-b border-b-iw-hairline px-3 py-2">
      <span class="text-[11px] font-semibold uppercase tracking-wider text-ink/50 dark:text-white/50">
        Microphone
      </span>
      <span class="text-[11px] font-medium text-ink/70 dark:text-white/70 truncate">
        {{ micActive?.label || (micLabelsHidden ? 'Not allowed yet' : 'System default') }}
      </span>
    </div>
    <div v-if="micLabelsHidden || micInputs.length === 0" class="px-3 py-3">
      <p class="text-[11px] leading-snug text-ink/60 dark:text-white/55">
        Allow microphone access to see and choose your microphones. Until
        then, dictation records from your computer's default input.
      </p>
      <button
        type="button"
        class="mic-allow iw-press mt-2 w-full rounded-full bg-blue-950 px-3 py-1.5 text-[11px] font-semibold text-paper
          [box-shadow:var(--iw-shadow-2),inset_0_1px_0_rgba(255,255,255,0.12)]
          ![transition:background-color_var(--iw-dur-2)_var(--iw-ease-out),box-shadow_var(--iw-dur-2)_var(--iw-ease-out),transform_var(--iw-dur-1)_var(--iw-ease-out)]
          hover:bg-blue-900 focus-visible:shadow-iw-focus focus-visible:![outline:none] dark:bg-[#f3ede2] dark:text-ink dark:hover:bg-white"
        @click="unlockMicInputs"
      >
        Allow microphone access
      </button>
    </div>
    <div v-else class="py-1" role="group" aria-label="Microphone">
      <button
        v-for="input in micInputs"
        :key="input.id"
        type="button"
        role="menuitemradio"
        :aria-checked="input.id === micActive?.id"
        :class="[
          'mic-option iw-press flex w-full items-center gap-2 bg-transparent px-3 py-[0.45rem] text-left text-[0.75rem] font-medium ![outline:none]',
          '![transition:background-color_var(--iw-dur-2)_var(--iw-ease-out),color_var(--iw-dur-2)_var(--iw-ease-out)]',
          'hover:bg-blue-100/50 hover:text-ink focus-visible:bg-blue-100/50 focus-visible:text-ink',
          'dark:hover:bg-white/[0.07] dark:hover:text-white/95 dark:focus-visible:bg-white/[0.07] dark:focus-visible:text-white/95',
          input.id === micActive?.id ? 'text-ink dark:text-white/95' : 'text-ink/75 dark:text-[rgba(219,234,254,0.7)]',
        ]"
        @click="chooseMicInput(input.id)"
      >
        <i
          class="fas fa-check w-3 shrink-0 text-[0.625rem]"
          :class="input.id === micActive?.id ? 'opacity-[0.85]' : 'opacity-0'"
        ></i>
        <span class="truncate">{{ input.label || 'Microphone' }}</span>
        <span
          v-if="isBuiltInInput(input)"
          class="mic-option-tag ml-auto shrink-0 rounded-[999px] bg-blue-100/70 px-[0.4rem] py-[0.1rem] text-[0.5625rem] font-semibold uppercase tracking-[0.06em] text-ink/60
            dark:bg-white/10 dark:text-white/70"
        >Built-in</span>
      </button>
      <p class="px-3 pb-2 pt-1.5 text-[10px] leading-snug text-ink/45 dark:text-white/40">
        Your computer's built-in microphone is used unless you pick another.
      </p>
    </div>
  </div>
  </Transition>

  <div class="px-2 pt-1 pb-3">
    <!-- What the pane puts above the box: the coordinator's check-in
         queue, or a stopped thread's way to try again. -->
    <slot />

    <!-- Queued prompt: one message held while the agent works. It slides
         in above the composer and slides back out when it fires, so the
         hand-off from "held" to "sent" is something you watch happen. -->
    <!-- It opens and closes its own space (the negative margin) so the
         composer glides down and back rather than jumping. -->
    <Transition
      enter-active-class="[transition:opacity_var(--iw-dur-2)_var(--iw-ease-out),transform_var(--iw-dur-3)_var(--iw-ease-out),margin-bottom_var(--iw-dur-3)_var(--iw-ease-out)]"
      enter-from-class="translate-y-2 scale-[0.98] opacity-0 !-mb-9"
      leave-active-class="[transition:opacity_var(--iw-dur-2)_var(--iw-ease-out),transform_var(--iw-dur-3)_var(--iw-ease-out),margin-bottom_var(--iw-dur-3)_var(--iw-ease-out)]"
      leave-to-class="translate-y-2 scale-[0.98] opacity-0 !-mb-9"
    >
    <div
      v-if="instance?.queuedPrompt"
      class="flex items-center gap-2 rounded-xl border border-blue-100 dark:border-white/[0.08] bg-ink/[0.03] dark:bg-white/[0.04] px-2.5 py-1.5 mb-1.5"
    >
      <i class="fas fa-hourglass-half text-[10px] text-ink/40 dark:text-white/40 shrink-0"></i>
      <div class="flex-1 min-w-0">
        <p class="text-[11px] font-medium text-ink/75 dark:text-white/70 truncate" :title="instance.queuedPrompt">
          {{ instance.queuedPrompt }}
        </p>
        <p class="text-[10px] text-ink/40 dark:text-white/35">{{ queuedNote }}</p>
      </div>
      <button
        type="button"
        title="Cancel queued message"
        aria-label="Cancel queued message"
        class="iw-press shrink-0 inline-flex items-center justify-center w-6 h-6 rounded-full text-ink/40 dark:text-white/40 hover:bg-blue-100/70 dark:hover:bg-white/[0.08] hover:text-ink/70 dark:hover:text-white/70
          ![transition:background-color_var(--iw-dur-2)_var(--iw-ease-out),color_var(--iw-dur-2)_var(--iw-ease-out),transform_var(--iw-dur-1)_var(--iw-ease-out)]
          focus-visible:shadow-iw-focus focus-visible:![outline:none]"
        @click="cancelQueuedPrompt"
      >
        <i class="fas fa-times text-[10px]"></i>
      </button>
    </div>
    </Transition>

    <!-- Input shell: textarea on top, controls toolbar below, as one field.
         Focus adds a soft halo outside the existing edge rather than
         thickening the border, so the field never changes size as you click
         into it. -->
    <div
      class="rounded-2xl bg-ink/[0.03] dark:bg-white/[0.03] border border-ink/[0.08] dark:border-white/[0.14] shadow-sm
        [transition:border-color_var(--iw-dur-2)_var(--iw-ease-out),box-shadow_var(--iw-dur-2)_var(--iw-ease-out)]
        focus-within:border-ink/40 focus-within:[box-shadow:0_0_0_3px_rgba(var(--iw-accent),0.13)] dark:focus-within:border-white/40"
    >
      <textarea
        ref="promptTextarea"
        v-model="prompt"
        :placeholder="promptPlaceholder"
        @keydown.enter.exact.prevent="handlePrompt"
        @keydown.enter.shift.exact="() => {}"
        @input="autoResizeTextarea"
        :disabled="!instance"
        rows="4"
        class="w-full bg-transparent text-ink dark:text-white/90 placeholder-ink/40 dark:placeholder-bone/40 text-sm px-3 pt-3 pb-1 resize-none leading-relaxed
          ![border:none] ![box-shadow:none] ![outline:0_none_transparent] ![outline-offset:0] ![transition:none] ![-webkit-tap-highlight-color:transparent]"
        style="min-height: 92px; max-height: 240px;"
      ></textarea>

      <!-- What went wrong with the last dictation, for a few seconds -->
      <p
        v-if="dictationError"
        role="status"
        class="dictation-error px-3 pb-1 text-[11px] leading-snug text-red-700/90 dark:text-red-300/90"
      >
        {{ dictationError }}
      </p>

      <!-- Controls toolbar: model + reasoning as one chip and usage on the left, send pinned right -->
      <div class="flex items-center justify-between gap-2 px-2 pb-2 pt-1">
        <!-- min-w-0 + overflow-hidden lets the chips truncate rather than
             shove the send button off the edge on a narrow sidebar. -->
        <div class="flex flex-nowrap items-center gap-1 min-w-0 flex-1 overflow-hidden">
          <!-- Model + reasoning: one chip naming both ("Opus 5.5 · Medium"),
               opening the model list and the effort meter together. -->
          <div ref="tuneRoot" class="min-w-0">
            <button
              type="button"
              title="Model and reasoning"
              aria-label="Model and reasoning"
              aria-controls="tune-panel"
              :aria-expanded="tuneOpen"
              :disabled="!instance"
              :class="['control-chip iw-press', CHIP, tuneOpen ? CHIP_OPEN : CHIP_SHUT]"
              @click="toggleTune"
            >
              <i class="fas fa-microchip shrink-0 text-[0.6875rem] opacity-75"></i>
              <span class="truncate">{{ tuneLabel }}</span>
              <i
                class="fas fa-chevron-down shrink-0 text-[0.5rem] opacity-60 [transition:transform_var(--iw-dur-3)_var(--iw-ease-inout)]"
                :class="{ 'rotate-180': tuneOpen }"
              ></i>
            </button>
          </div>

          <!-- Usage limits (button + anchored panel above) -->
          <div ref="usageRoot" class="shrink-0">
            <button
              type="button"
              title="Plan usage limits"
              aria-label="Usage limits"
              :aria-expanded="usageOpen"
              :class="['control-chip iw-press', CHIP, usageOpen ? CHIP_OPEN : CHIP_SHUT]"
              @click="toggleUsage"
            >
              <i class="fas fa-gauge-high shrink-0 text-[0.6875rem] opacity-75"></i>
              <span class="truncate">Usage</span>
            </button>
          </div>
        </div>

        <!-- The one button, and it is the microphone first: hold to
             dictate, click to send (or to stop a run in flight). Once
             the box has words in it, typed or dictated, it turns into
             the red record button with a send arrow on it, so the tap
             that sends is obvious; a hold still records more onto the
             end, which is why it stays red rather than turning into a
             plain send button. Emptying the box (sending, or deleting
             the text) turns it back into the quiet mic. A run in flight
             makes it navy with the stop glyph, since a click stops the
             agent. Recording turns it red with a ring that swells with
             the voice; the click the browser fires when a hold lets go
             is swallowed, so letting go never sends. Which microphone it
             listens on lives behind the same button: a right-click (or
             the keyboard's menu key) opens the picker, so there is no
             second mic control beside it. Where the browser cannot
             record at all it is a plain send arrow. -->
        <button
          ref="sendButton"
          type="button"
          :title="sendTitle"
          :aria-label="sendTitle"
          :aria-pressed="isRecording"
          :aria-expanded="dictationSupported ? micOpen : undefined"
          :disabled="!instance || isTranscribing"
          class="btn-send iw-press relative flex shrink-0 items-center justify-center w-9 h-9 rounded-full border
            [-webkit-touch-callout:none] [transform:translateZ(0)] touch-none select-none focus-visible:![outline:none] disabled:cursor-not-allowed"
          :class="sendClass"
          :style="isRecording ? micRingStyle : undefined"
          @pointerdown="onSendPointerDown"
          @pointerup="onSendPointerUp"
          @pointercancel="onSendPointerUp"
          @contextmenu.prevent="toggleMic"
          @click="onSendClick"
        >
          <!-- One glyph at a time; a change cross-fades the old one out
               as the new one turns in, rather than snapping. -->
          <Transition
            enter-active-class="[transition:opacity_var(--iw-dur-2)_var(--iw-ease-out),transform_var(--iw-dur-3)_var(--iw-ease-spring)] motion-reduce:[transition:opacity_var(--iw-dur-1)_linear]"
            enter-from-class="translate-y-1.5 scale-[0.6] opacity-0 motion-reduce:[transform:none]"
            leave-active-class="absolute [transition:opacity_var(--iw-dur-2)_var(--iw-ease-out),transform_var(--iw-dur-3)_var(--iw-ease-spring)] motion-reduce:[transition:opacity_var(--iw-dur-1)_linear]"
            leave-to-class="scale-[0.6] opacity-0 motion-reduce:[transform:none]"
          >
            <i :key="sendGlyph" :class="sendGlyphClass" aria-hidden="true"></i>
          </Transition>
        </button>
      </div>
    </div>
  </div>
</div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted, onBeforeUnmount, onActivated, onDeactivated, watch, toRef } from 'vue'
import { useAgentStore } from '../../../stores/agentStore'
// The workspace's shared motion + material vocabulary (curves, durations,
// radii, elevation, focus ring). A var(--iw-*) with no token behind it
// resolves to nothing, which would leave the popovers transparent.
import '../../../styles/workspace.css'
import { useUsageStore, formatResetTime } from '@/shared/stores/usage'
import { isBuiltInInput, useDictation } from '../../../composables/useDictation'
import type { AIModel } from '../../../types/index'
import type { AgentInstance, ReasoningEffort, ReasoningEffortOption, ServiceTier } from '../../../types/services'
import {
  AI_MODELS,
  SERVICE_TIERS,
  modelProvider,
  reasoningEffortsForModel,
  serviceTierForModel,
  supportsServiceTier,
} from '../../../types/services'

const props = withDefaults(
  defineProps<{
    /** The coordinator or thread being typed to */
    instance: AgentInstance | null
    /** Where a message goes: the coordinator's next message, or a thread's
     *  next turn. Called mid-run too; the pane holds it behind the run. */
    submit: (text: string) => void | Promise<void>
    /** What the empty box says */
    placeholder?: string
    /** Under a message held behind a live run */
    queuedNote?: string
  }>(),
  {
    placeholder: 'Ask me to build, edit, or explain anything in your project...',
    queuedNote: 'Queued — sends when the agent finishes',
  }
)

const emit = defineEmits<{ (e: 'stop'): void }>()

const store = useAgentStore()
const instance = toRef(props, 'instance')
/* ── Panel and menu classes ──────────────────────────────────────────────
   Model, reasoning, usage and the mic picker share one surface: a
   translucent material lifted off the composer, so the transcript behind it
   stays present as colour (opaque where the browser has no backdrop blur). */
const POPOVER =
  'rounded-iw-lg border border-iw-material-border bg-iw-material-bg shadow-iw-3 [backdrop-filter:var(--iw-material-filter)] ' +
  '[@supports_not_((backdrop-filter:blur(1px))_or_(-webkit-backdrop-filter:blur(1px)))]:bg-white ' +
  'dark:[@supports_not_((backdrop-filter:blur(1px))_or_(-webkit-backdrop-filter:blur(1px)))]:bg-[#0f0f0f]'

/** Control chip: the compact model / reasoning / usage buttons. Ghost until
 *  hovered or open, so the input shell stays the focal point. */
const CHIP =
  'inline-flex max-w-full cursor-pointer items-center gap-[0.3rem] rounded-iw-sm border border-transparent px-[0.55rem] py-[0.3rem] ' +
  'text-[0.75rem] font-medium tracking-[0.01em] ![outline:none] ' +
  '![transition:background-color_var(--iw-dur-2)_var(--iw-ease-out),color_var(--iw-dur-2)_var(--iw-ease-out),box-shadow_var(--iw-dur-2)_var(--iw-ease-out),transform_var(--iw-dur-1)_var(--iw-ease-out)] ' +
  'focus-visible:shadow-iw-focus disabled:cursor-not-allowed disabled:opacity-50 ' +
  'enabled:hover:bg-blue-100/50 enabled:hover:text-ink dark:enabled:hover:bg-white/[0.07] dark:enabled:hover:text-white/95'
const CHIP_SHUT = 'bg-transparent text-ink/75 dark:text-[rgba(219,234,254,0.7)]'
const CHIP_OPEN = 'control-chip--active bg-blue-100/70 text-ink dark:bg-white/10 dark:text-white'

/** Menu rows: name, tier tag and what it is for, with a check on the one in
 *  use. Ghost rows that tint on hover, like the chip. */
const MENU_ROW =
  'flex w-full cursor-pointer items-center gap-3 rounded-iw-sm px-2.5 py-2 text-left [border:0] ![outline:none] ' +
  '[transition:background-color_var(--iw-dur-2)_var(--iw-ease-out)] motion-reduce:[transition:none] ' +
  'focus-visible:shadow-iw-focus disabled:cursor-not-allowed disabled:opacity-50 ' +
  'enabled:hover:bg-blue-100/50 dark:enabled:hover:bg-white/[0.07]'
const MENU_ROW_ON = 'model-row--on bg-blue-100/[0.35] dark:bg-white/5'
const ROW_NAME = 'flex items-baseline gap-[0.4rem] text-[0.8125rem] font-medium leading-5 text-ink dark:text-white/[0.92]'
const ROW_TIER = 'text-[0.6875rem] font-medium text-ink/55 dark:text-white/45'
const ROW_BLURB = 'block text-[0.6875rem] leading-4 text-ink/70 dark:text-white/55'
const TUNE_NOTE = 'tune-note text-[0.625rem] leading-[0.875rem]'

/**
 * One reasoning-effort bar's fill. Bars rise with the rung and fill up to the
 * chosen one in the send button's navy (cream in dark); the rest are
 * hairline outlines. A hovered rung above the chosen one previews at half
 * strength.
 */
function effortFillClass(i: number): string {
  const base =
    'block h-[calc(0.5rem+var(--rung)*0.375rem)] w-full rounded-[0.1875rem] motion-reduce:[transition:none] ' +
    '[transition:background-color_var(--iw-dur-2)_var(--iw-ease-out),box-shadow_var(--iw-dur-2)_var(--iw-ease-out)] ' +
    'dark:[box-shadow:inset_0_0_0_1px_rgba(243,237,226,0.3)]'
  const preview = effortPreview.value
  if (preview !== null && i <= preview && i > effortIndex.value) {
    return `${base} bg-ink/35 [box-shadow:none] dark:bg-[rgba(243,237,226,0.4)]`
  }
  if (i <= (preview ?? effortIndex.value)) {
    return `${base} bg-ink [box-shadow:none] dark:bg-[#f3ede2]`
  }
  return `${base} [box-shadow:inset_0_0_0_1px_rgba(19,26,44,0.25)]`
}

const prompt = ref('')
const promptTextarea = ref<HTMLTextAreaElement | null>(null)

function onDocMousedown(e: MouseEvent) {
  const target = e.target as Node
  // The toggle buttons count as "inside": closing on their mousedown would
  // make the follow-up click toggle the menu straight back open.
  if (
    usageOpen.value &&
    !usageRoot.value?.contains(target) &&
    !usagePanel.value?.contains(target)
  ) {
    usageOpen.value = false
  }
  if (
    tuneOpen.value &&
    !tuneRoot.value?.contains(target) &&
    !tunePanel.value?.contains(target)
  ) {
    tuneOpen.value = false
  }
  if (
    micOpen.value &&
    !sendButton.value?.contains(target) &&
    !micPanel.value?.contains(target)
  ) {
    micOpen.value = false
  }
}

// Escape closes the model menu from anywhere, not only while focus is
// inside it — a keyboard user who Tabs past the last control would otherwise
// have no way back to dismiss it. Inside the panel its own handler fires
// first and stops the event, so this never runs twice.
function onDocKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape' && tuneOpen.value) closeTune()
}

onMounted(() => {
  document.addEventListener('mousedown', onDocMousedown)
  document.addEventListener('keydown', onDocKeydown)
})
onBeforeUnmount(() => {
  document.removeEventListener('mousedown', onDocMousedown)
  document.removeEventListener('keydown', onDocKeydown)
})

// --- Usage limits dropdown (plan + rolling windows) ---

const usageStore = useUsageStore()
const usageOpen = ref(false)
const usageRoot = ref<HTMLElement | null>(null)
const usagePanel = ref<HTMLElement | null>(null)

// --- Model + reasoning menu (the model list and the effort meter share one panel) ---

const tuneOpen = ref(false)
const tuneRoot = ref<HTMLElement | null>(null)
const tunePanel = ref<HTMLElement | null>(null)
// The microphone picker hangs off the send button (right-click) rather than
// off a handle of its own.
const micOpen = ref(false)
const sendButton = ref<HTMLElement | null>(null)
const micPanel = ref<HTMLElement | null>(null)

// The three controls share the space above the composer, so only one panel
// opens at a time.
function closeControlPanels() {
  usageOpen.value = false
  tuneOpen.value = false
  micOpen.value = false
}

function toggleUsage() {
  const next = !usageOpen.value
  closeControlPanels()
  usageOpen.value = next
  // Windows drift as older activity ages out; refresh on open.
  if (usageOpen.value) void usageStore.fetchUsage()
}

function toggleTune() {
  const next = !tuneOpen.value
  closeControlPanels()
  tuneOpen.value = next
}

/** "Pro plan" — em-dash while the plan is unknown. The allowances belong to
 *  the weekly meter below, not here. */
const planSummary = computed(() =>
  usageStore.plan ? `${usageStore.plan.name} plan` : '—'
)

/** The rolling-window meter. A list of one: the weekly allowance is the only
 *  window, but the panel renders rows, so keeping the shape costs nothing.
 *  Missing data renders as unknown (em-dash, no bar) — never as 0%. */
const usageMeters = computed(() => {
  const rows = [
    { key: 'week', label: 'Weekly limit', win: usageStore.weekly, percent: usageStore.weeklyPercent },
  ]
  return rows.map(({ key, label, win, percent }) => {
    // Known usage with no limit is an unlimited plan (Free while the
    // server's FREE_TIER_UNLIMITED is on): nothing to fill or reset.
    const unlimited = !!win && win.usedUsd !== null && win.limitUsd === null
    return {
      key,
      label,
      percent,
      // How much of the window's allowance is gone, on a 0-100 scale — the
      // dollar figures behind it stay out of the workspace. Unknown usage
      // stays an em-dash, never 0%.
      usedText: unlimited ? 'Unlimited' : percent !== null ? `${percent}% used` : '—',
      resetsAt: unlimited ? null : formatResetTime(win?.resetsAt ?? null),
    }
  })
})

// The models offered in the composer, one per tier. SELECTABLE_MODEL_PATTERN
// admits whole families (GPT and Claude), so a new model the catalog adds
// shows up without another edit here.
const SELECTABLE_MODEL_PATTERN = /^(gpt|claude)-/
const modelOptions = computed<AIModel[]>(() => {
  const available = (store.availableModels || []).filter(model =>
    SELECTABLE_MODEL_PATTERN.test(model.id)
  )
  return available.length > 0 ? available : AI_MODELS
})

// The menu shows one family at a time, Anthropic's or OpenAI's, picked by
// the toggle in its head. It opens on the family of the model in use.
const MODEL_FAMILIES = [
  { id: 'anthropic', name: 'Anthropic' },
  { id: 'openai', name: 'OpenAI' },
] as const
type ModelFamily = (typeof MODEL_FAMILIES)[number]['id']
const currentProvider = computed<ModelFamily>(() => modelProvider(instance.value?.selectedModelId))
const family = ref<ModelFamily>(currentProvider.value)
const familyButtons = ref<HTMLButtonElement[]>([])

const effortOptions = computed<ReasoningEffortOption[]>(() =>
  reasoningEffortsForModel(instance.value?.selectedModelId)
)

// The tiers ranked faster → smarter, the order the model menu lists them
// in. Unknown ids sort last but still appear, so the menu degrades
// gracefully if the lineup changes before this table does.
const MODEL_RANK: Record<string, number> = {
  'claude-haiku-5-5': 0,
  'claude-sonnet-5-5': 1,
  'claude-opus-5-5': 2,
  'claude-fable-5-1': 3,
  'gpt-6-luna': 10,
  'gpt-6.1-terra': 11,
  'gpt-6.1-sol': 12,
  'gpt-6-astra': 13,
}
const orderedModels = computed<AIModel[]>(() =>
  [...modelOptions.value].sort(
    (a, b) => (MODEL_RANK[a.id] ?? 99) - (MODEL_RANK[b.id] ?? 99)
  )
)
const familyModels = computed<AIModel[]>(() =>
  orderedModels.value.filter(m => modelProvider(m.id) === family.value)
)
// The model in use. A conversation on a model the menu does not offer shows
// the default rather than an arbitrary end of the lineup.
const currentModel = computed<AIModel | null>(() => {
  const models = orderedModels.value
  return models.find(m => m.id === instance.value?.selectedModelId)
    ?? models.find(m => m.default)
    ?? models[0]
    ?? null
})
// Where the model in use sits in the family shown; -1 when it is in the
// other family, so nothing here is checked.
const modelIndex = computed(() =>
  familyModels.value.findIndex(m => m.id === currentModel.value?.id)
)

/** The distinctive part of the model name for the chip
 *  ("Haiku 5.5", "Opus 5.5", "Fable 5.1"), dropping the "Claude" prefix. */
function modelShortName(id?: string | null): string {
  const model = orderedModels.value.find(m => m.id === id) ?? currentModel.value
  if (!model) return 'Model'
  return model.name.replace(/^(?:GPT\s*\d+(?:\.\d+)?|Claude)\s*/i, '').trim() || model.name
}

// What each tier is for, shown under its name in the menu. Static: the models endpoint
// sends no copy, and the composer's fallback list has none either.
const MODEL_BLURBS: Record<string, string> = {
  'claude-haiku-5-5': 'Fast and inexpensive, yet capable at most tasks. Turn up effort for harder ones.',
  'claude-sonnet-5-5': 'Quick and capable, a strong everyday builder at a modest price.',
  'claude-opus-5-5': 'Thoughtful and dependable, with strong judgment on code and design. The default.',
  'claude-fable-5-1': 'Frontier intelligence for the hardest, most complex work.',
  'gpt-6-luna': 'Fast and inexpensive, capable at most everyday edits.',
  'gpt-6.1-terra': "Quick and capable at half Sol's price, strong at agent work.",
  'gpt-6.1-sol': 'Near-Astra intelligence at a fifth of the price.',
  'gpt-6-astra': "OpenAI's most capable model, for the hardest work.",
}
const modelBlurb = (id: string) =>
  MODEL_BLURBS[id] ?? orderedModels.value.find(m => m.id === id)?.description ?? ''

// effortOptions is the one ladder every model shares, ordered faster →
// smarter. The store re-seats a legacy selectedEffort onto it when the model
// changes, so the meter can't point at a rung the next request would reject —
// and changing model never moves it.
const effortIndex = computed(() => {
  const idx = effortOptions.value.findIndex(
    o => o.id === (instance.value?.selectedEffort ?? 'medium')
  )
  return idx >= 0 ? idx : 0
})

// The tier tag beside each model's name in the menu.
const MODEL_TIERS: Record<string, string> = {
  'claude-haiku-5-5': 'Fast',
  'claude-sonnet-5-5': 'Quick',
  'claude-opus-5-5': 'Balanced',
  'claude-fable-5-1': 'Frontier',
  'gpt-6-luna': 'Fast',
  'gpt-6.1-terra': 'Quick',
  'gpt-6.1-sol': 'Balanced',
  'gpt-6-astra': 'Frontier',
}
const modelTier = (id: string) => MODEL_TIERS[id] ?? ''

// --- Speed (OpenAI's service tiers) ---

/** The tier the next request carries: the one picked, if this model has it. */
const currentTier = computed<ServiceTier>(() =>
  serviceTierForModel(instance.value?.selectedModelId, instance.value?.serviceTier)
)
/** Standard always; a faster tier only on a model that offers it. */
const tierOffered = (tier: ServiceTier) =>
  tier === '' || supportsServiceTier(currentModel.value?.id, tier)
/** "Sol and Astra": the models a tier runs on, for a row the current
 *  model can't use. */
function tierModelsText(tier: ServiceTier): string {
  const names = orderedModels.value
    .filter(m => supportsServiceTier(m.id, tier))
    .map(m => modelShortName(m.id))
  return names.length > 1 ? `${names.slice(0, -1).join(', ')} and ${names[names.length - 1]}` : names[0] ?? 'other models'
}
function pickTier(tier: ServiceTier) {
  if (instance.value && tierOffered(tier)) store.setInstanceServiceTier(instance.value.id, tier)
}
const speedRows = ref<HTMLButtonElement[]>([])

/** The chip reads "Opus 5.5 · Medium": the model's short name and the
 *  reasoning rung, so both settings are legible without opening anything. */
const tuneLabel = computed(
  () => `${modelShortName(currentModel.value?.id)} · ${effortOptions.value[effortIndex.value]?.name ?? 'Reasoning'}`
    + (currentTier.value ? ` · ${SERVICE_TIERS.find(t => t.id === currentTier.value)?.name}` : '')
)

function pickModel(id: string) {
  if (id !== instance.value?.selectedModelId) void handleModelSelect(id)
}

function pickEffort(id: ReasoningEffort) {
  if (id !== instance.value?.selectedEffort) void handleEffortSelect(id)
}

// The bar under the pointer, whose rung the readout previews; null when the
// pointer is elsewhere and the readout shows the rung in use.
const effortPreview = ref<number | null>(null)
const shownEffort = computed<ReasoningEffortOption | null>(
  () => effortOptions.value[effortPreview.value ?? effortIndex.value] ?? null
)

const modelRows = ref<HTMLButtonElement[]>([])
const effortBars = ref<HTMLButtonElement[]>([])

/** Radio-group keys: arrows step one option (clamped at the ends rather than
 *  wrapping — both groups run faster → smarter, so they have a top), Home/End
 *  jump to them. `upIsMore` says which way ArrowUp goes: toward the top of
 *  the model list is faster, while the effort bars stand left to right, so
 *  there Up means more. Returns the index to move to, or null to ignore. */
function radioStep(key: string, current: number, count: number, upIsMore: boolean): number | null {
  const steps: Record<string, number> = {
    ArrowRight: current + 1,
    ArrowLeft: current - 1,
    ArrowDown: upIsMore ? current - 1 : current + 1,
    ArrowUp: upIsMore ? current + 1 : current - 1,
    Home: 0,
    End: count - 1,
  }
  if (!(key in steps) || count === 0) return null
  return Math.min(Math.max(steps[key]!, 0), count - 1)
}

// Focus follows the choice, since the chosen option is its group's one tab
// stop.
function onModelKeydown(e: KeyboardEvent) {
  const target = radioStep(e.key, modelIndex.value, familyModels.value.length, false)
  if (target === null || !instance.value) return
  e.preventDefault()
  pickModel(familyModels.value[target]!.id)
  void nextTick(() => modelRows.value[target]?.focus())
}

function onFamilyKeydown(e: KeyboardEvent) {
  const current = MODEL_FAMILIES.findIndex(f => f.id === family.value)
  const target = radioStep(e.key, current, MODEL_FAMILIES.length, false)
  if (target === null) return
  e.preventDefault()
  family.value = MODEL_FAMILIES[target]!.id
  void nextTick(() => familyButtons.value[target]?.focus())
}

function onSpeedKeydown(e: KeyboardEvent) {
  const offered = SERVICE_TIERS.filter(t => tierOffered(t.id))
  const current = offered.findIndex(t => t.id === currentTier.value)
  const target = radioStep(e.key, current, offered.length, false)
  if (target === null || !instance.value) return
  e.preventDefault()
  const tier = offered[target]!.id
  pickTier(tier)
  void nextTick(() => speedRows.value[SERVICE_TIERS.findIndex(t => t.id === tier)]?.focus())
}

function onEffortKeydown(e: KeyboardEvent) {
  const target = radioStep(e.key, effortIndex.value, effortOptions.value.length, true)
  if (target === null || !instance.value) return
  e.preventDefault()
  effortPreview.value = null
  pickEffort(effortOptions.value[target]!.id)
  void nextTick(() => effortBars.value[target]?.focus())
}

/** Escape: the panel goes and focus returns to the chip that opened it, so a
 *  keyboard user is not dropped on the page body. */
function closeTune() {
  tuneOpen.value = false
  effortPreview.value = null
  void nextTick(() => tuneRoot.value?.querySelector<HTMLButtonElement>('button')?.focus())
}

watch(tuneOpen, open => {
  // The menu opens on the model in use, in its family, with focus on it so
  // the arrows work straight away.
  if (open) {
    family.value = currentProvider.value
    void nextTick(() => modelRows.value[Math.max(modelIndex.value, 0)]?.focus())
  } else effortPreview.value = null
})

// --- Dictation (holding the send button, or holding ⌘D) ---

// ⌘ on Apple hardware, Ctrl elsewhere: the modifier the rest of the OS
// already puts its shortcuts on.
const isApplePlatform =
  typeof navigator !== 'undefined' &&
  /Mac|iPhone|iPad|iPod/i.test(navigator.platform || navigator.userAgent || '')
const dictationShortcut = isApplePlatform ? '⌘D' : 'Ctrl+D'

const {
  state: dictationState,
  error: dictationError,
  supported: dictationSupported,
  level: dictationLevel,
  inputs: micInputs,
  activeInput: micActive,
  labelsHidden: micLabelsHidden,
  start: startDictation,
  stop: stopDictation,
  cancel: cancelDictation,
  selectInput: selectMicInput,
  unlockInputs: unlockMicInputs,
  refreshInputs: refreshMicInputs,
} = useDictation({ onTranscript: insertDictation })

const isRecording = computed(() => dictationState.value === 'recording')
const isTranscribing = computed(() => dictationState.value === 'transcribing')

/** What is being held to keep the mic open — the button, or the shortcut.
 *  Written by whichever hold opened it, and read only while recording, so
 *  the composer can say which one to let go of. */
const heldBy = ref<'button' | 'key' | null>(null)

/** How a live recording ends, in the words of whatever opened it. Both are
 *  holds: nothing stops dictation by being pressed a second time. */
const releaseHint = computed(() => {
  if (heldBy.value === 'key') return `let go of ${dictationShortcut}`
  if (heldBy.value === 'button') return 'let go of the button'
  return 'let go'
})

/** The red ring around a live mic widens with the voice it hears, so "is it
 *  picking me up?" is answered by looking rather than by sending a clip. */
const micRingStyle = computed(() => ({
  '--dictate-ring': `${2 + Math.round(dictationLevel.value * 10)}px`,
}))

function toggleMic() {
  // Nothing to pick from where the browser cannot record, and a right-click
  // on a disabled button is still a right-click.
  if (!dictationSupported || !instance.value) return
  const next = !micOpen.value
  closeControlPanels()
  micOpen.value = next
  // A headset may have connected since the list was last read.
  if (micOpen.value) void refreshMicInputs()
}

function chooseMicInput(id: string) {
  selectMicInput(id)
  micOpen.value = false
}

/** What a hold, a click, and a right-click each do, in that order: the
 *  button is the microphone first, and a click is how the words leave. */
const sendTitle = computed(() => {
  if (isTranscribing.value) return 'Transcribing…'
  if (isRecording.value) return `Listening — ${releaseHint.value} when you're done`
  const running = !!instance.value?.isProcessing
  if (!dictationSupported) return running ? 'Stop agent' : 'Send (Enter)'
  const click = running ? 'click to stop the agent' : 'click to send (Enter)'
  return `Hold to dictate, or hold ${dictationShortcut} · ${click} · right-click to choose microphone`
})

/** There is something a click would send. */
const hasPromptText = computed(() => !!instance.value && !!prompt.value.trim())

/** Words in the box and nothing running: the button is the red record
 *  button with a send arrow on it. A tap sends; a hold still records more. */
const isReadyToSend = computed(
  () => dictationSupported && hasPromptText.value && !instance.value?.isProcessing
)

/** Which glyph the button wears. Keyed, so a change animates. */
const sendGlyph = computed(() => {
  if (isTranscribing.value) return 'transcribing'
  if (isRecording.value) return 'mic'
  if (instance.value?.isProcessing) return 'stop'
  if (!dictationSupported || isReadyToSend.value) return 'arrow'
  return 'mic'
})

const sendGlyphClass = computed(() => {
  switch (sendGlyph.value) {
    case 'transcribing':
      return 'send-glyph fas fa-circle-notch fa-spin text-[13px]'
    case 'stop':
      return 'send-glyph fas fa-stop text-sm'
    case 'arrow':
      return 'send-glyph fas fa-arrow-up text-sm'
    default:
      return 'send-glyph fas fa-microphone text-[13px]'
  }
})

/** Red while the mic is live, and red with an arrow once there are words to
 *  send (still the record button, since a hold adds to them); navy ink when
 *  a click stops a run, or sends where the browser cannot record; a ghost
 *  otherwise — still pressable, because a hold records into an empty box. */
/* The send button's states. Send, stop and the mic are the same button in
   different states, so the swap between them is a colour and shadow change on
   one shape rather than controls trading places. Each state carries its whole
   transition and its focus ring, since a hovered ready or recording button
   keeps its own shadow over the ring. */
const SEND_TRANSITION =
  '![transition:background-color_var(--iw-dur-2)_var(--iw-ease-out),border-color_var(--iw-dur-2)_var(--iw-ease-out),color_var(--iw-dur-2)_var(--iw-ease-out),box-shadow_var(--iw-dur-2)_var(--iw-ease-out),transform_var(--iw-dur-1)_var(--iw-ease-out)]'

/** Nothing to send yet: a quiet shape in the control chips' ghost register.
 *  Still pressable, because a hold records into an empty box. */
const SEND_IDLE = `btn-send--idle ${SEND_TRANSITION} border-blue-200/70 bg-blue-100/60 text-ink/45 shadow-iw-1 focus-visible:shadow-iw-focus
  enabled:hover:bg-blue-100/90 enabled:hover:text-ink/70 disabled:opacity-60
  dark:border-white/[0.12] dark:bg-white/5 dark:text-[rgba(219,234,254,0.5)] dark:enabled:hover:bg-white/[0.09] dark:enabled:hover:text-white/85`

/** A click stops the run (or sends, where the browser cannot record): navy
 *  ink, the site's primary button. */
const SEND_ACTIVE = `btn-send--active ${SEND_TRANSITION} border-transparent bg-blue-950 text-paper
  [box-shadow:var(--iw-shadow-2),inset_0_1px_0_rgba(255,255,255,0.12)] focus-visible:shadow-iw-focus
  hover:bg-blue-900 hover:[box-shadow:var(--iw-shadow-3),inset_0_1px_0_rgba(255,255,255,0.12)]
  hover:focus-visible:[box-shadow:var(--iw-shadow-3),inset_0_1px_0_rgba(255,255,255,0.12)]
  dark:bg-[#f3ede2] dark:text-ink dark:hover:bg-white`

/** Live: red, with a ring whose width is the voice level (set inline as
 *  --dictate-ring). It sits still on silence and swells as you speak. */
const SEND_RECORDING = `btn-send--recording border-transparent bg-red-600 text-white
  ![transition:background-color_var(--iw-dur-2)_var(--iw-ease-out),color_var(--iw-dur-2)_var(--iw-ease-out),box-shadow_80ms_linear]
  [box-shadow:0_0_0_var(--dictate-ring,2px)_rgba(220,38,38,0.35)] focus-visible:shadow-iw-focus
  enabled:hover:focus-visible:[box-shadow:0_0_0_var(--dictate-ring,2px)_rgba(220,38,38,0.35)] dark:bg-red-500`

/** Words to send: the record button, red, wearing a send arrow. Calmer than
 *  live recording — no ring — so the two never read as the same state. */
const SEND_READY = `btn-send--ready ${SEND_TRANSITION} border-transparent bg-red-600 text-white
  [box-shadow:var(--iw-shadow-2),inset_0_1px_0_rgba(255,255,255,0.18)] focus-visible:shadow-iw-focus
  enabled:hover:bg-red-700 enabled:hover:[box-shadow:var(--iw-shadow-3),inset_0_1px_0_rgba(255,255,255,0.18)]
  enabled:hover:focus-visible:[box-shadow:var(--iw-shadow-3),inset_0_1px_0_rgba(255,255,255,0.18)]
  dark:bg-red-500 dark:enabled:hover:bg-red-400`

const sendClass = computed(() => {
  if (isRecording.value) return SEND_RECORDING
  if (isReadyToSend.value) return SEND_READY
  if (instance.value && (hasPromptText.value || instance.value.isProcessing)) {
    return SEND_ACTIVE
  }
  return SEND_IDLE
})
// --- Tap versus hold on the send button ---
//
// A press that lasts HOLD_TO_TALK_MS becomes a hold: the mic opens, and
// letting go closes it and transcribes. A shorter press is a tap, and the
// click the browser fires on release does the tap's work (send, or stop the
// run) — that way a keyboard Enter or Space on the focused button sends too.
// A hold's release also fires a click, which is swallowed.

/** How long a press must last before it is a hold. Shorter reads as a click. */
const HOLD_TO_TALK_MS = 250

let holdTimer: ReturnType<typeof setTimeout> | null = null
let pointerHeld = false
// Set once a press has become a hold: the click on release is not a tap.
let holdConsumedClick = false
// The mic is still opening (permission prompt, device negotiation).
let holdOpening = false

function clearHoldTimer() {
  if (holdTimer) clearTimeout(holdTimer)
  holdTimer = null
}

function onSendPointerDown(e: PointerEvent) {
  // Only the primary button: a right-click is the context menu, not a hold.
  if (e.button !== undefined && e.button !== 0) return
  if (!instance.value || isTranscribing.value) return
  // Keep the caret (and any selection) in the textarea — a click sends what
  // is typed there, and a hold puts words there, at that caret.
  e.preventDefault()
  // A press on the button is a send or a hold, never a browse of the
  // picker it also opens: put the picker away first.
  micOpen.value = false
  pointerHeld = true
  holdConsumedClick = false
  // Follow the pointer off the button: a thumb that drifts mid-sentence
  // must still end the recording when it lifts.
  const el = e.currentTarget as HTMLElement | null
  if (el && typeof el.setPointerCapture === 'function') {
    try {
      el.setPointerCapture(e.pointerId)
    } catch {
      // jsdom, or a pointer that is already gone.
    }
  }
  clearHoldTimer()
  holdTimer = setTimeout(() => {
    holdTimer = null
    if (!pointerHeld) return
    holdConsumedClick = true
    // Already live from a ⌘D hold: the button simply takes over, and its
    // release is what stops the recording now.
    heldBy.value = 'button'
    if (isRecording.value) return
    holdOpening = true
    void startDictation().finally(() => {
      holdOpening = false
    })
  }, HOLD_TO_TALK_MS)
}

function onSendPointerUp() {
  if (!pointerHeld) return
  pointerHeld = false
  if (holdTimer) {
    // Let go before it became a hold: a tap. The click that follows does it.
    clearHoldTimer()
    return
  }
  if (isRecording.value) {
    stopDictation()
  } else if (holdOpening) {
    // Let go while the microphone was still opening (the permission prompt
    // was up): nothing was heard, so there is nothing to transcribe.
    cancelDictation()
  }
}

function onSendClick() {
  if (holdConsumedClick) {
    holdConsumedClick = false
    return
  }
  // Something else has the mic open — a ⌘D hold whose keys are still down.
  // A tap closes it rather than sending, and the next tap sends the words.
  if (isRecording.value) {
    stopDictation()
    return
  }
  if (instance.value?.isProcessing) {
    handleStopClick()
    return
  }
  void handlePrompt()
}

onBeforeUnmount(clearHoldTimer)

/** Dictated text lands where the caret is — in place of a selection, or
 *  between what is on either side, with a space added wherever it would
 *  otherwise run into a word — and the caret lands after it, so the next
 *  thing typed or dictated follows on. With the caret at the end, where
 *  each transcript leaves it, that is a plain append. Once the box has lost
 *  focus the words go on the end: a caret nobody can see is not a place to
 *  put them. Typing, selecting, and deleting are the textarea's own; nothing
 *  here takes them away, so the words can be edited between holds. The
 *  transcript is never sent by itself: the user reads it over, then clicks
 *  the button or presses Enter. */
function insertDictation(text: string) {
  const el = promptTextarea.value
  const current = prompt.value
  const caret = el && document.activeElement === el ? [el.selectionStart, el.selectionEnd] : null
  const [start, end] = caret ?? [current.length, current.length]
  const before = current.slice(0, start)
  const after = current.slice(end)
  const lead = before && !/\s$/.test(before) ? ' ' : ''
  const trail = after && !/^\s/.test(after) ? ' ' : ''
  prompt.value = `${before}${lead}${text}${trail}${after}`
  const landing = before.length + lead.length + text.length
  nextTick(() => {
    autoResizeTextarea()
    if (el) {
      el.focus()
      el.setSelectionRange(landing, landing)
    }
  })
}

// --- Holding ⌘D ---
//
// The shortcut is the button without the mouse: it is held, not pressed. The
// mic opens on the way down and closes when the keys come up, so a hold is a
// hold whichever of the two the hand is on, and nothing has to be pressed a
// second time to stop.
//
// Which key comes up first is not ours to choose — and macOS withholds a
// letter's keyup entirely while Command is still down — so the release is
// taken from the D, from the modifier, or from the window losing focus
// mid-hold (⌘-Tab), whichever arrives.
let keyHeld = false
// The mic is still opening (permission prompt, device negotiation).
let keyOpening = false

function isDictationChord(e: KeyboardEvent): boolean {
  const modifier = isApplePlatform ? e.metaKey : e.ctrlKey
  return !!modifier && !e.altKey && !e.shiftKey && (e.key || '').toLowerCase() === 'd'
}

/** ⌘D from anywhere in the workspace — the point of a shortcut is not having
 *  to find the button first. Left alone when the preview has already taken
 *  the keystroke for the app it is showing (it calls preventDefault), on a
 *  read-only task thread (no composer), and where the browser cannot record. */
function onDictationKeyDown(e: KeyboardEvent) {
  if (e.defaultPrevented) return
  if (!isDictationChord(e)) return
  if (!dictationSupported || !instance.value) return
  // The browser's own ⌘D (bookmark this page) must not fire, on the repeats
  // a held key sends as much as on the first one.
  e.preventDefault()
  if (e.repeat || keyHeld) return
  keyHeld = true
  heldBy.value = 'key'
  // Already live from a hold of the button: the keys take over, and their
  // release stops the recording.
  if (isRecording.value) return
  keyOpening = true
  void startDictation().finally(() => {
    keyOpening = false
  })
}

function onDictationKeyUp(e: KeyboardEvent) {
  const key = (e.key || '').toLowerCase()
  if (key === 'd' || key === 'meta' || key === 'control') releaseDictationKey()
}

/** The end of a ⌘D hold, however it ended. */
function releaseDictationKey() {
  if (!keyHeld) return
  keyHeld = false
  if (isRecording.value) {
    stopDictation()
  } else if (keyOpening) {
    // Let go while the microphone was still opening (the permission prompt
    // was up): nothing was heard, so there is nothing to transcribe.
    cancelDictation()
  }
}

// The shortcut belongs to the composer on screen. The workspace keeps the
// hidden pane alive (KeepAlive), and the coordinator's composer and a
// thread's must not both start recording on one ⌘D.
function listenForDictationKey() {
  document.addEventListener('keydown', onDictationKeyDown)
  document.addEventListener('keyup', onDictationKeyUp)
  window.addEventListener('blur', releaseDictationKey)
}
function stopListeningForDictationKey() {
  document.removeEventListener('keydown', onDictationKeyDown)
  document.removeEventListener('keyup', onDictationKeyUp)
  window.removeEventListener('blur', releaseDictationKey)
  releaseDictationKey()
}
onMounted(listenForDictationKey)
onActivated(listenForDictationKey)
onDeactivated(stopListeningForDictationKey)
onBeforeUnmount(stopListeningForDictationKey)


const promptPlaceholder = computed(() => {
  if (isRecording.value) {
    const mic = micActive.value?.label || 'the default microphone'
    return `Listening on ${mic}… ${releaseHint.value} when you're done.`
  }
  if (isTranscribing.value) return 'Transcribing…'
  return props.placeholder
})

function autoResizeTextarea() {
  if (!promptTextarea.value) return
  promptTextarea.value.style.height = 'auto'
  const scrollHeight = promptTextarea.value.scrollHeight
  const maxHeight = 240
  promptTextarea.value.style.height = `${Math.min(scrollHeight, maxHeight)}px`
}

// After a checkpoint restore, the removed prompt comes back here so the
// user can edit and resend it (the Cursor rewind flow).
function setPromptText(text: string) {
  prompt.value = text
  nextTick(() => {
    autoResizeTextarea()
    promptTextarea.value?.focus()
  })
}

// Context added from elsewhere in the workspace (an element picked in the
// preview) goes after whatever the user has already typed.
function appendPromptText(text: string) {
  setPromptText(prompt.value.trim() ? `${prompt.value.trimEnd()}\n${text}` : text)
}

defineExpose({ setPromptText, appendPromptText })

async function handlePrompt() {
  if (!prompt.value.trim() || !instance.value) return

  const promptText = prompt.value
  prompt.value = '' // Clear immediately

  // Reset textarea height
  if (promptTextarea.value) {
    promptTextarea.value.style.height = '92px'
  }

  // Mid-run, the pane's submit holds the message behind the run (one per
  // instance — a second submit replaces it) rather than racing a second run.
  await props.submit(promptText)
}

function cancelQueuedPrompt() {
  if (instance.value) store.clearQueuedPrompt(instance.value.id)
}

function handleStopClick() {
  const current = instance.value
  // Stop means stop: a queued prompt must not fire into the aborted run's
  // wake, but it shouldn't silently vanish either — hand it back to the
  // input for the user to send or discard.
  if (current?.queuedPrompt) {
    if (!prompt.value.trim()) prompt.value = current.queuedPrompt
    store.clearQueuedPrompt(current.id)
  }
  emit('stop')
}

// Model and effort belong to the instance being typed to: a thread keeps its
// own, apart from the coordinator's and every other thread's.
function handleModelSelect(modelId: string) {
  if (instance.value) store.setInstanceModel(instance.value.id, modelId)
}

function handleEffortSelect(effort: ReasoningEffort) {
  if (instance.value) store.setInstanceEffort(instance.value.id, effort)
}
</script>
