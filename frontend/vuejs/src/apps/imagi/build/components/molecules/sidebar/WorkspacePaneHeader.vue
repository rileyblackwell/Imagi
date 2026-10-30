<!--
  WorkspacePaneHeader.vue — the masthead shared by the two sidebar panes.

  Built from the same parts as everything under it. A pane may name itself in
  the brand serif and may add a second line, led by a state dot, saying where it
  stands — the identical construction the crew cards use (title, then a marked
  status line), in the identical monochrome vocabulary: blue while work is
  live, navy ink when something wants you, faint ink at rest.

  Both halves of the identity are optional, and a pane that is obviously itself
  takes neither. The main thread is the case: you are looking at the agent you
  came here to talk to, so naming it spends a line saying what the pane already
  is. What replaces it is nothing — the plate holds its height, the switches
  keep their place, and the reading (when there is one) moves up into the space.

  That second line is for standing, not for activity. A thread pane leaves it
  empty while its agent is running and lets the transcript narrate the run
  under the message that started it; what stays here is the kind of thing you
  need before you type ("3 agents are waiting on you", "Read only"), which has
  nowhere better to live. The roster pane is the one place the line reports
  live work, because there its subject is the fleet rather than one agent.

  The plate itself
  matches the preview toolbar across the divider — same wash, same hairline,
  same height — so the top of the workspace reads as one bar rather than two
  panes that happen to be adjacent.

  The identity sits centred on the plate — it is what the pane is, not one more
  control, and the eye should find it in the same place whatever is bolted to
  either side of it.

  The right-hand controls name the panes they switch to and how much is
  happening over there. That count is the point: you can see background work
  piling up without leaving the thread you're in. They are the only way across
  at every width — a phone gets the same pills in the same place, plus the ones
  marked `mobileOnly` for destinations that are already on screen on desktop
  (the preview, which sits beside the panes there and replaces them here).

  Everything about how this plate arranges itself keys off the width of the
  pane it is sitting in, not the width of the window (see .pane-header-shell).
  The two are not the same thing and never were: the sidebar is 22rem on a
  phone-in-landscape and on a 27" display alike, so a viewport breakpoint here
  was answering a question nobody asked. The switches are what the pane is for
  — they are the only way out of it — so they are sized first and never give
  ground; the name and its reading take what is left and truncate.
-->
<template>
  <div class="pane-header-shell shrink-0 [container-type:inline-size] relative z-20">
    <!-- The size container, and the reason this component has a wrapper at
         all. The plate has to arrange itself by how much room the *pane* gives
         it: the sidebar is a fixed 22rem at every window width, so a viewport
         media query read "desktop" and laid out a plate twice as wide as the one
         it had. An element can't query itself, hence the shell — nothing is
         drawn here; the material, the hairline and the padding all belong to the
         plate.

         It also carries the stacking: `container-type` brings layout
         containment with it, which makes this element the stacking context the
         plate's z-index would otherwise have escaped into. Lifting the pane above
         the transcript scrolling under it is the shell's job now. -->
    <!-- The plate: a translucent material rather than a painted strip. The
         pane scrolls beneath it, so the masthead takes its colour from
         whatever is passing underneath — saturated and blurred past
         legibility — and closes with a true hairline (::after: at 1px a
         border rounds up to a full device pixel on retina; a scaled
         pseudo-element stays a true hairline at any density). Its metrics
         are the preview toolbar's (.pv-bar), to the pixel: the two sit
         shoulder to shoulder at the top of the workspace.

         Three columns: the gutter that mirrors the switches, the identity,
         and the switches — which is what centres the name on the plate rather
         than in the space left over. The sizing is a priority order: the
         switch cluster is `auto` against a track that can't be talked below
         its content, so the pills always get their full width; the gutter is
         `minmax(0, auto)` and gives its width back, quietly, when the plate
         can't afford the symmetry; the identity keeps a floor and truncates.
         The gap is tight because the two reserved columns spend this plate's
         width twice over.

         Below 28rem of pane the plate stops spending the switch cluster's
         width twice: the ghost goes, and with it true centring. The identity
         reads from the left — the app-bar arrangement — and the switches keep
         the right. 28rem because the widest cluster is a shade over 7rem: two
         of those plus a name worth reading is about where a centred plate
         stops being a good trade. It catches the 22rem sidebar at every window
         size and every phone. -->
    <div
      class="pane-header iw-surface relative grid grid-cols-[minmax(0,auto)_minmax(3.5rem,1fr)_auto] items-center gap-1 min-h-[3.0625rem] py-[0.4375rem] px-2
        bg-iw-material-bg [backdrop-filter:var(--iw-material-filter)]
        after:content-[''] after:absolute after:left-0 after:right-0 after:bottom-0 after:h-px after:bg-[color:var(--iw-hairline)] after:[transform:scaleY(0.5)] after:origin-bottom
        [@container(max-width:28rem)]:grid-cols-[minmax(0,1fr)_auto]"
    >
      <!-- Left column: a ghost of the switch cluster, and load-bearing. Reserving
           the same width the real controls take on the right is what puts the
           identity at the true centre of the plate — an empty gutter gets
           squeezed by a long title and the name drifts left of centre. It is
           inert in every sense: invisible (`visibility: hidden` rather than
           `display: none`, because the box still has to be measured),
           unhittable, and skipped by assistive tech.

           Only on a wide pane. Centring costs the plate the switch cluster's
           width twice over, and a 22rem sidebar does not have it to spend: the
           identity gives up true centring below that and reads from the left
           instead. -->
      <div class="pane-header-gutter flex overflow-hidden [@container(max-width:28rem)]:hidden" aria-hidden="true">
        <div :class="[CLUSTER, 'invisible pointer-events-none']">
          <span
            v-for="s in switches"
            :key="s.id"
            :class="switchClass(s)"
          >
            <i v-if="s.direction === 'back' && !s.iconOnly" :class="['fas fa-chevron-left', CHEVRON]"></i>
            <span class="relative inline-flex items-center">
              <i :class="[s.icon, ICON]"></i>
            </span>
            <span v-if="!s.iconOnly" :class="LABEL">{{ s.label }}</span>
            <span v-if="s.count" :class="COUNT">{{ s.count }}</span>
            <i v-if="s.direction !== 'back' && !s.iconOnly" :class="['fas fa-chevron-right', CHEVRON]"></i>
          </span>
        </div>
      </div>

      <!-- The identity block: name over reading, centred as one object. It
           takes only the width it needs and truncates rather than pushing the
           switch off the plate. -->
      <div class="pane-identity min-w-0 text-center [@container(max-width:28rem)]:text-left">
        <!-- Only panes that need naming carry a name. A pane you arrived at by
             stepping into it — a subagent's thread, the roster — says which one
             you are in; the main thread doesn't, because there is nothing to
             tell it apart from.

             The name carries the display face (Bricolage under Spotlight) — so
             the workspace chrome speaks in the product's own voice instead of
             another line of bold UI sans. Set at the preview nameplate's size
             and optical axis: the two are the same thing on opposite sides of
             the divider. -->
        <h2
          v-if="title"
          class="pane-title truncate font-sl-display [font-variation-settings:'opsz'_18,'SOFT'_24,'WONK'_1] text-[0.875rem] font-semibold leading-[1.2] tracking-[-0.008em] text-blue-950 dark:text-white/[0.94]"
        >{{ title }}</h2>

        <!-- Where this pane stands: a state dot, then the reading. The dot is
             the pane's only status marker — it replaced a filled identity badge
             that carried the navy-ink recipe reserved for actions, and a
             separate live pulse. One object, one job.

             The line reserves its own height so the masthead never resizes
             underneath a cross-fade, and its gap from the name belongs to the
             pair: on an unnamed pane the reading sits on the plate's
             centreline, where a hanging top margin would push it a hair low.

             The reading changes under its own feet ("3 agents are waiting on
             you" → "1 agent is waiting on you"). Swapping it in place reads as
             a flicker; cross-fading reads as the same line being updated,
             which is what it is. Keyed on the text so each new reading gets
             its own fade — down and out, up and in — the dot sits outside,
             because state outlives any one wording of it. -->
        <div
          v-if="status"
          :class="[
            'pane-status-line flex items-center justify-center gap-[0.3125rem] min-h-[0.9375rem] [@container(max-width:28rem)]:justify-start',
            title && 'mt-0.5'
          ]"
        >
          <!-- State as a dot, in the preview's dot family and the crew
               ledger's colours: blue for a live run, amber for something that
               wants you, faint ink at rest. A live run's dot holds steady — a
               marker that flickers looks like a rendering fault — and a halo
               breathes outward from under it (see the styles). -->
          <span
            :class="[
              'pane-dot shrink-0 w-[0.4375rem] h-[0.4375rem] rounded-full [transition:background-color_var(--iw-dur-3)_var(--iw-ease-out)]',
              `pane-dot--${state}`,
              DOT[state]
            ]"
            aria-hidden="true"
          ></span>
          <Transition
            mode="out-in"
            enter-active-class="![transition:opacity_var(--iw-dur-1)_var(--iw-ease-out),transform_var(--iw-dur-1)_var(--iw-ease-out)]"
            leave-active-class="![transition:opacity_var(--iw-dur-1)_var(--iw-ease-out),transform_var(--iw-dur-1)_var(--iw-ease-out)]"
            enter-from-class="opacity-0 [transform:translateY(3px)]"
            leave-to-class="opacity-0 [transform:translateY(-3px)]"
          >
            <!-- The reading takes the state's ink, exactly as a card's status
                 line does. -->
            <p
              :key="status"
              :class="[
                'pane-status min-w-0 truncate text-[0.625rem] leading-[1.35] [transition:color_var(--iw-dur-3)_var(--iw-ease-out)]',
                `pane-status--${state}`,
                STATUS[state]
              ]"
            >{{ status }}</p>
          </Transition>
        </div>
      </div>

      <!-- Pane switches — the only way across the workspace, at every width. The
           cluster is ordered the way the workspace nests: the pane you'd step
           into first sits nearest the identity. -->
      <div :class="CLUSTER">
        <button
          v-for="s in switches"
          :key="s.id"
          type="button"
          :class="['iw-press group group/switch', switchClass(s)]"
          :aria-label="s.iconOnly ? s.label : `Switch to ${s.label}`"
          :title="s.iconOnly ? s.label : undefined"
          @click="emit('switch', s.id)"
        >
          <i
            v-if="s.direction === 'back' && !s.iconOnly"
            :class="['fas fa-chevron-left group-hover:-translate-x-0.5', CHEVRON]"
          ></i>
          <!-- The destination has a live run (a subagent working over there): the
               icon carries the same dot the status line uses, so the link to the
               working subagent is always visible from the thread you're in.
               Something new since it was last opened gets the info tone,
               still, so it never reads as work. -->
          <span class="relative inline-flex items-center">
            <i :class="[s.icon, ICON]"></i>
            <span
              v-if="s.live"
              class="pane-switch-pulse bg-sl-work after:content-[''] after:absolute after:inset-0 after:rounded-full after:[background:inherit]"
              :class="BADGE_DOT"
              aria-hidden="true"
            ></span>
            <span v-else-if="s.fresh" :class="[BADGE_DOT, 'bg-sl-cool']" aria-hidden="true"></span>
          </span>
          <!-- The word is the first thing to go when the pane runs out of room
               (see the narrow rungs on the label), which is what the icon and
               the aria-label are there for. -->
          <span v-if="!s.iconOnly" :class="LABEL">{{ s.label }}</span>
          <!-- Ambient count of what is waiting on the other side. Keyed on the
               number so it springs when the fleet grows instead of silently
               becoming a different digit. -->
          <Transition
            mode="out-in"
            enter-active-class="[transition:opacity_var(--iw-dur-2)_var(--iw-ease-out),transform_var(--iw-dur-2)_var(--iw-ease-spring)]"
            leave-active-class="[transition:opacity_var(--iw-dur-1)_var(--iw-ease-out),transform_var(--iw-dur-1)_var(--iw-ease-out)]"
            enter-from-class="opacity-0 [transform:scale(0.5)]"
            leave-to-class="opacity-0 [transform:scale(0.7)]"
          >
            <span v-if="s.count" :key="s.count" :class="COUNT">{{ s.count }}</span>
          </Transition>
          <i
            v-if="s.direction !== 'back' && !s.iconOnly"
            :class="['fas fa-chevron-right group-hover:translate-x-0.5', CHEVRON]"
          ></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    /** What this pane is, when that isn't already obvious from being in it. */
    title?: string
    /**
     * Where the pane stands, in the crew ledger's own vocabulary — the same
     * three tokens an agent card keys its rail and status colour off, so a
     * pane and the cards inside it never describe one state two ways.
     * 'working' outranks the rest: a pane with a live run is working whatever
     * else is queued behind it.
     */
    state?: 'working' | 'waiting' | 'idle'
    /** One line on what this pane is doing right now */
    status?: string
    /** Where you can go from this pane, left to right. */
    switches?: Array<{
      /** Emitted back on click — the caller's name for the destination */
      id: string
      icon: string
      label: string
      /** A run is live over there — the switch icon carries a pulse */
      live?: boolean
      /** Badge: how much is going on in the destination pane. Each caller picks
       *  what it counts, but it must always be something you'd act on — 0 is
       *  "nothing over there" and draws nothing. */
      count?: number
      /** 'back' puts the chevron in front; anything else points forward */
      direction?: 'forward' | 'back'
      /**
       * Only offered below the md breakpoint. For destinations that are
       * already on screen on desktop — the preview sits beside the panes
       * there, so a button to "go to" it would be a button to go nowhere.
       */
      mobileOnly?: boolean
      /** Something changed over there since it was last opened (project
       *  memory saved new lines): a still dot, quieter than `live`. */
      fresh?: boolean
      /** A control rather than a destination (workspace settings): the icon
       *  alone, with `label` as its accessible name and tooltip. */
      iconOnly?: boolean
    }>
  }>(),
  { state: 'idle', switches: () => [] }
)

const emit = defineEmits<{ (e: 'switch', id: string): void }>()

type PaneSwitch = NonNullable<typeof props.switches>[number]

/* The cluster: however many destinations this pane offers, seated as one
   object on the right so the plate reads as identity-then-exits rather than a
   row of loose buttons. No `min-w-0`, deliberately: an explicit zero minimum
   overrides a grid item's automatic minimum size, so the track was free to
   shrink to nothing under a cluster of pills that never shrink — and the
   overflow landed on the title. The automatic minimum makes the track's floor
   the cluster's real width, so the identity beside it gives way instead. */
const CLUSTER = 'pane-switches flex items-center justify-self-end gap-[0.3125rem] [@container(max-width:28rem)]:gap-1'

/*
  Switch: names its destination instead of hiding behind a tooltip. Wears the
  preview plate's bordered material at the height of the preview's nav
  buttons, so the two panes' chrome uses one elevation model. It still gives
  under the press (.iw-press; its transition is overridden here, so `!`).

  On a narrow pane everything tightens by a couple of pixels to buy the title
  back some room (28rem); below 20rem the chevrons go — the icon and the word
  already say where the button leads; below 15rem the words go too and the
  switches stand as icons, still the full 26px target and still named by
  their aria-label. A pane that narrow shouldn't happen; the plate holds
  together if it does.
*/
const SWITCH = [
  'pane-switch inline-flex items-center gap-[0.3125rem] shrink-0 h-7 rounded-full border cursor-pointer text-[0.6875rem] font-medium',
  '[@container(max-width:28rem)]:h-[1.625rem] [@container(max-width:28rem)]:gap-1',
  '[transition:background-color_var(--iw-dur-2)_var(--iw-ease-out),border-color_var(--iw-dur-2)_var(--iw-ease-out),color_var(--iw-dur-2)_var(--iw-ease-out),box-shadow_var(--iw-dur-2)_var(--iw-ease-out)]',
  'border-ink/10 bg-white/85 text-ink/[0.72] [box-shadow:inset_0_1px_0_#ffffff]',
  'hover:bg-white hover:border-ink/[0.22] hover:text-blue-950 hover:[box-shadow:inset_0_1px_0_#ffffff,0_1px_3px_rgba(19,26,44,0.08)]',
  'focus-visible:![outline:none] focus-visible:[box-shadow:var(--iw-focus-ring)]',
  'dark:border-white/[0.14] dark:bg-white/[0.045] dark:text-blue-100/[0.72] dark:[box-shadow:inset_0_1px_0_rgba(255,255,255,0.05)]',
  'dark:hover:bg-white/[0.08] dark:hover:border-white/[0.26] dark:hover:text-white dark:hover:[box-shadow:inset_0_1px_0_rgba(255,255,255,0.05)]',
]
/* A destination: the pill. */
const SWITCH_PILL = 'px-[0.5625rem] [@container(max-width:28rem)]:px-2 [@container(max-width:15rem)]:!px-[0.4375rem]'
/* A control rather than a destination: a round button around its icon. */
const SWITCH_ICON = 'justify-center w-7 p-0 [@container(max-width:28rem)]:w-[1.625rem]'

function switchClass(s: PaneSwitch) {
  return [
    SWITCH,
    s.iconOnly ? SWITCH_ICON : SWITCH_PILL,
    // A destination that is already on screen on desktop (the preview, which
    // sits beside the panes there) — offered only where it replaces this pane.
    s.mobileOnly && 'pane-switch--mobile md:hidden',
  ]
}

const ICON = 'text-[0.625rem] opacity-70 [transition:opacity_var(--iw-dur-2)_var(--iw-ease-out)] group-hover/switch:opacity-95'
const CHEVRON = 'pane-switch-chevron text-[0.5rem] opacity-[0.45] [transition:transform_var(--iw-dur-2)_var(--iw-ease-out),opacity_var(--iw-dur-2)_var(--iw-ease-out)] group-hover/switch:opacity-80 [@container(max-width:20rem)]:hidden'
const LABEL = 'pane-switch-label whitespace-nowrap [@container(max-width:15rem)]:hidden'
/* Count of what is waiting on the other side — navy ink, the recipe this
   workspace keeps for things you act on. It is the one element in the
   masthead that earns it. */
const COUNT = 'pane-switch-count inline-flex items-center justify-center min-w-[1.0625rem] h-[1.0625rem] px-1 rounded-full bg-blue-950 text-[#fbfaf7] text-[0.625rem] font-semibold tabular-nums leading-none dark:bg-[#f3ede2] dark:text-blue-950'
/* The status line's dot, sized down for the switch icon: the link to a
   working subagent reads as live without stealing attention. */
const BADGE_DOT = 'absolute -top-0.5 -right-[3px] w-1.5 h-1.5 rounded-full [box-shadow:0_0_0_2px_rgba(var(--iw-surface),0.9)]'

const DOT = {
  idle: 'bg-ink/[0.22] dark:bg-white/[0.22]',
  waiting: 'bg-sl-wait [box-shadow:0_0_8px_-1px_var(--sl-wait)]',
  working: "relative bg-sl-work after:content-[''] after:absolute after:inset-0 after:rounded-full after:[background:inherit]",
}
const STATUS = {
  idle: 'text-ink/[0.42] dark:text-blue-100/40',
  waiting: 'text-sl-wait',
  working: 'text-sl-work',
}
</script>

<style scoped>
/* What stays here: keyframed motion (scoped keyframe names can't be reached
   from a utility) and the no-backdrop-filter fallback, whose @supports
   condition is unreadable as a variant. */

/* No backdrop-filter (older Firefox, some Linux GPUs): fall back to the
   opaque wash the header used to carry, so it never turns see-through. */
@supports not ((backdrop-filter: blur(1px)) or (-webkit-backdrop-filter: blur(1px))) {
  .pane-header {
    background: linear-gradient(180deg, rgba(239, 246, 255, 0.92) 0%, rgba(239, 246, 255, 0.6) 100%);
  }

  .dark .pane-header {
    background: linear-gradient(180deg, rgba(24, 24, 27, 0.96) 0%, rgba(18, 18, 20, 0.85) 100%);
  }
}

/* A live run: the dot itself holds steady-ish and a halo breathes outward
   from under it. Reads as a signal radiating rather than a light being
   switched. The switch icon's pulse is the same dot. */
.pane-dot--working,
.pane-switch-pulse {
  animation: pane-pulse-core 2.4s var(--iw-ease-ambient) infinite;
}

.pane-dot--working::after,
.pane-switch-pulse::after {
  animation: pane-pulse-halo 2.4s var(--iw-ease-ambient) infinite;
}

@keyframes pane-pulse-core {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.78; }
}

@keyframes pane-pulse-halo {
  0% { opacity: 0.45; transform: scale(1); }
  70%, 100% { opacity: 0; transform: scale(2.4); }
}

@media (prefers-reduced-motion: reduce) {
  .pane-dot--working,
  .pane-dot--working::after,
  .pane-switch-pulse,
  .pane-switch-pulse::after { animation: none; }

  .pane-dot--working::after,
  .pane-switch-pulse::after { opacity: 0; }
}
</style>
