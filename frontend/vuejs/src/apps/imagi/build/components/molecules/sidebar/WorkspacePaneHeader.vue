<!--
  WorkspacePaneHeader.vue — the masthead shared by the two sidebar panes.

  Built from the same parts as everything under it. A pane names itself in the
  brand serif and then says where it stands on a second line led by a state
  dot — the identical construction the crew cards use (title, then a marked
  status line), in the identical monochrome vocabulary: blue while a run is
  live, navy ink when something wants you, faint ink at rest. The plate itself
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
  <div class="pane-header-shell shrink-0">
    <!-- The shell around this plate exists to be measured: it declares the
         size container every rule below queries. Nothing is drawn there — the
         material, the hairline and the padding all still belong here. -->
    <div class="pane-header iw-surface">
      <!-- Left column: a ghost of the switch cluster, and load-bearing. Reserving
           the same width the real controls take on the right is what puts the
           identity at the true centre of the plate — an empty gutter gets
           squeezed by a long title and the name drifts left of centre. It is
           inert in every sense: invisible, unhittable, and skipped by
           assistive tech.

           Only on a wide pane. Centring costs the plate the switch cluster's
           width twice over, and a 22rem sidebar does not have it to spend: the
           identity gives up true centring below that and reads from the left
           instead (see the compact block in the styles). -->
      <div class="pane-header-gutter" aria-hidden="true">
        <div class="pane-switches pane-switches--ghost">
          <span
            v-for="s in switches"
            :key="s.id"
            :class="['pane-switch', s.mobileOnly && 'pane-switch--mobile']"
          >
            <i v-if="s.direction === 'back'" class="fas fa-chevron-left pane-switch-chevron"></i>
            <span class="pane-switch-icon-wrap">
              <i :class="[s.icon, 'pane-switch-icon']"></i>
            </span>
            <span class="pane-switch-label">{{ s.label }}</span>
            <span v-if="s.count" class="pane-switch-count">{{ s.count }}</span>
            <i v-if="s.direction !== 'back'" class="fas fa-chevron-right pane-switch-chevron"></i>
          </span>
        </div>
      </div>

      <div class="pane-identity">
        <h2 class="pane-title truncate">{{ title }}</h2>

        <!-- Where this pane stands: a state dot, then the reading. The dot is
             the pane's only status marker — it replaced a filled identity badge
             that carried the navy-ink recipe reserved for actions, and a
             separate live pulse. One object, one job.

             The status line is the most-changing text in the workspace
             ("Reading files…" → "Editing…" → "Ready when you are"). Swapping it
             in place reads as a flicker; cross-fading reads as the same line
             being updated, which is what it is. Keyed on the text so each new
             reading gets its own fade — the dot sits outside, because state
             outlives any one wording of it. -->
        <div v-if="status" class="pane-status-line">
          <span :class="['pane-dot', `pane-dot--${state}`]" aria-hidden="true"></span>
          <Transition name="pane-status" mode="out-in">
            <p :key="status" :class="['pane-status', `pane-status--${state}`]">{{ status }}</p>
          </Transition>
        </div>
      </div>

      <!-- Pane switches — the only way across the workspace, at every width. The
           cluster is ordered the way the workspace nests: the pane you'd step
           into first sits nearest the identity. -->
      <div class="pane-switches">
        <button
          v-for="s in switches"
          :key="s.id"
          type="button"
          :class="['pane-switch', 'iw-press', 'group', s.mobileOnly && 'pane-switch--mobile']"
          :aria-label="`Switch to ${s.label}`"
          @click="emit('switch', s.id)"
        >
          <i
            v-if="s.direction === 'back'"
            class="fas fa-chevron-left pane-switch-chevron"
          ></i>
          <!-- The destination has a live run (a subagent working over there): the
               icon carries the same dot the status line uses, so the link to the
               working subagent is always visible from the thread you're in. -->
          <span class="pane-switch-icon-wrap">
            <i :class="[s.icon, 'pane-switch-icon']"></i>
            <span v-if="s.live" class="pane-switch-pulse" aria-hidden="true"></span>
          </span>
          <!-- The word is the first thing to go when the pane runs out of room
               (see the narrow rungs in the styles), which is what the icon and
               the aria-label are there for. -->
          <span class="pane-switch-label">{{ s.label }}</span>
          <!-- Ambient count of what is waiting on the other side. Keyed on the
               number so it springs when the fleet grows instead of silently
               becoming a different digit. -->
          <Transition name="pane-count" mode="out-in">
            <span v-if="s.count" :key="s.count" class="pane-switch-count">{{ s.count }}</span>
          </Transition>
          <i
            v-if="s.direction !== 'back'"
            class="fas fa-chevron-right pane-switch-chevron"
          ></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    title: string
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
    }>
  }>(),
  { state: 'idle', switches: () => [] }
)

const emit = defineEmits<{ (e: 'switch', id: string): void }>()
</script>

<style scoped>
/* The plate: a translucent material rather than a painted strip. The pane
   scrolls beneath it, so the masthead takes its colour from whatever is
   passing underneath — saturated and blurred past legibility — and closes
   with a true hairline. This is what keeps the header feeling like a layer
   above the transcript instead of its first row.

   Its metrics are the preview toolbar's (.pv-bar), to the pixel: the two sit
   shoulder to shoulder at the top of the workspace, and a four-pixel
   difference in height put a visible step in the hairline running between
   them. */
/* The size container, and the reason this component has a wrapper at all. The
   plate has to arrange itself by how much room the *pane* gives it: the
   sidebar is a fixed 22rem at every window width, so a viewport media query
   read "desktop" and laid out a plate twice as wide as the one it had. An
   element can't query itself, hence the shell.

   It also carries the stacking: `container-type` brings layout containment
   with it, which makes this element the stacking context the plate's z-index
   would otherwise have escaped into. Lifting the pane above the transcript
   scrolling under it is the shell's job now. */
.pane-header-shell {
  container-type: inline-size;
  position: relative;
  z-index: 20;
}

.pane-header {
  position: relative;
  /* Three columns: the switches, the gutter that mirrors them, and the
     identity between the two — which is what centres the name on the plate
     rather than in the space left over.

     The sizing is a priority order, and it is the whole fix. The switch
     cluster is `auto` against a track that can no longer be talked below its
     content (see .pane-switches), so the pills always get their full width.
     The gutter is `minmax(0, auto)`: it takes the same width when the plate
     can afford the symmetry and gives it back, quietly, when it cannot. The
     identity keeps a floor and truncates. Nothing here can overflow its track
     onto its neighbour, which is exactly what used to happen — a `1fr` track
     that could shrink to nothing, holding pills that could not shrink at all,
     so they spilled out of it and printed themselves over the title. */
  display: grid;
  grid-template-columns: minmax(0, auto) minmax(3.5rem, 1fr) auto;
  align-items: center;
  /* Tight, because the two reserved columns spend this plate's width twice
     over: every pixel here comes off the status line in the middle. */
  gap: 0.25rem;
  min-height: 3.0625rem;
  padding: 0.4375rem 0.5rem;
  background: var(--iw-material-bg);
  -webkit-backdrop-filter: var(--iw-material-filter);
  backdrop-filter: var(--iw-material-filter);
}

/* The separator is drawn rather than bordered: at 1px a border rounds up to a
   full device pixel on retina and reads as a line; a scaled pseudo-element
   stays a true hairline at any density. */
.pane-header::after {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 1px;
  background: var(--iw-hairline);
  transform: scaleY(0.5);
  transform-origin: bottom;
}

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

/* The name carries the brand serif (Fraunces) — the same face as the Imagi
   mark — so the workspace chrome speaks in the product's own voice instead of
   another line of bold UI sans. Set at the preview nameplate's size and optical
   axis, because the two are the same thing on opposite sides of the divider:
   what you are looking at, named. */
/* The gutter holds the switch's ghost: it occupies the width, paints nothing,
   and takes no clicks. `visibility: hidden` rather than `display: none`
   precisely because the box still has to be measured.

   It is the one thing on the plate that yields quietly. Its track is
   `minmax(0, auto)`, so on a pane wide enough it mirrors the cluster exactly
   and the name sits at true centre; on a tighter one it hands its width to
   the identity a pixel at a time. Off-centre by a hair beats a title with
   nowhere to go — and below 28rem it stops pretending altogether. */
.pane-header-gutter {
  display: flex;
  overflow: hidden;
}

.pane-switches--ghost {
  visibility: hidden;
  pointer-events: none;
}

/* The identity block: name over reading, centred as one object. It takes only
   the width it needs (the grid's `auto` column) and truncates rather than
   pushing the switch off the plate. */
.pane-identity {
  min-width: 0;
  text-align: center;
}

.pane-title {
  font-family: theme('fontFamily.display');
  font-variation-settings: 'opsz' 18, 'SOFT' 24, 'WONK' 1;
  font-size: 0.875rem;
  font-weight: 600;
  line-height: 1.2;
  letter-spacing: -0.008em;
  color: theme('colors.blue.950');
}

.dark .pane-title {
  color: rgba(255, 255, 255, 0.94);
}

/* Marker + reading, on the crew card's status-line metrics. Reserves its own
   height so the masthead never resizes underneath a cross-fade — the two
   readings swap inside a box that does not move. */
.pane-status-line {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.3125rem;
  min-height: 0.9375rem;
  margin-top: 0.125rem;
}

/* State as a dot, in the preview's dot family and the crew ledger's colours:
   blue for a live run, navy ink for something that wants you, faint ink at
   rest. Sized and seated so it reads as punctuation on the line rather than
   as a badge beside it. */
.pane-dot {
  flex-shrink: 0;
  width: 0.4375rem;
  height: 0.4375rem;
  border-radius: 9999px;
  transition: background-color var(--iw-dur-3) var(--iw-ease-out);
}

.pane-dot--idle {
  background: rgba(23, 37, 84, 0.22);
}

.pane-dot--waiting {
  background: theme('colors.blue.950');
}

/* A live run: the dot itself holds steady — a marker that flickers looks like
   a rendering fault — and a halo breathes outward from under it. Reads as a
   signal radiating rather than a light being switched. */
.pane-dot--working {
  position: relative;
  background: theme('colors.blue.500');
  animation: pane-pulse-core 2.4s var(--iw-ease-ambient) infinite;
}

.pane-dot--working::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 9999px;
  background: inherit;
  animation: pane-pulse-halo 2.4s var(--iw-ease-ambient) infinite;
}

.dark .pane-dot--idle { background: rgba(255, 255, 255, 0.22); }
.dark .pane-dot--waiting { background: #f3ede2; }
.dark .pane-dot--working { background: theme('colors.blue.300'); }

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

/* The reading itself takes the state's ink, exactly as a card's status line
   does — a header that stayed uniformly grey while every row beneath it
   coloured its own status was the loudest thing out of step here. */
.pane-status {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 0.625rem;
  line-height: 1.35;
  transition: color var(--iw-dur-3) var(--iw-ease-out);
}

.pane-status--idle { color: rgba(23, 37, 84, 0.42); }
.pane-status--waiting { color: rgba(23, 37, 84, 0.78); }
.pane-status--working { color: theme('colors.blue.600'); }

.dark .pane-status--idle { color: rgba(219, 234, 254, 0.4); }
.dark .pane-status--waiting { color: rgba(243, 237, 226, 0.85); }
.dark .pane-status--working { color: theme('colors.blue.300'); }

/* One reading giving way to the next: down and out, up and in — the direction
   of a line being replaced from below. */
.pane-status-enter-active,
.pane-status-leave-active {
  transition:
    opacity var(--iw-dur-1) var(--iw-ease-out),
    transform var(--iw-dur-1) var(--iw-ease-out);
}

.pane-status-enter-from {
  opacity: 0;
  transform: translateY(3px);
}

.pane-status-leave-to {
  opacity: 0;
  transform: translateY(-3px);
}

/* Switch: names its destination instead of hiding behind a tooltip. Wears the
   preview plate's bordered material and sits at the height of the preview's
   nav buttons, so the two panes' chrome uses one elevation model — the button
   used to lift off the plate on hover while everything opposite it stayed
   seated. It still gives under the press (.iw-press). */
/* The cluster: however many destinations this pane offers, seated as one
   object on the right so the plate reads as identity-then-exits rather than a
   row of loose buttons. */
/* No `min-width: 0` here, and that is deliberate rather than an omission. It
   was the bug: an explicit zero minimum overrides a grid item's automatic
   minimum size, so the track was free to shrink to nothing under a cluster of
   pills that never shrink — and the overflow landed on the title. Leaving the
   automatic minimum alone makes the track's floor the cluster's real width,
   so the identity beside it gives way instead. */
.pane-switches {
  display: flex;
  align-items: center;
  justify-self: end;
  gap: 0.3125rem;
}

.pane-switch {
  display: inline-flex;
  align-items: center;
  gap: 0.3125rem;
  flex-shrink: 0;
  height: 1.75rem;
  padding: 0 0.5625rem;
  border-radius: 9999px;
  border: 1px solid rgba(23, 37, 84, 0.1);
  background: rgba(255, 255, 255, 0.85);
  color: rgba(23, 37, 84, 0.72);
  font-size: 0.6875rem;
  font-weight: 500;
  cursor: pointer;
  box-shadow: inset 0 1px 0 #ffffff;
  transition:
    background-color var(--iw-dur-2) var(--iw-ease-out),
    border-color var(--iw-dur-2) var(--iw-ease-out),
    color var(--iw-dur-2) var(--iw-ease-out),
    box-shadow var(--iw-dur-2) var(--iw-ease-out);
}

/* A destination that is already on screen on desktop (the preview, which sits
   beside the panes there) — offered only where it actually replaces this pane.
   Stated here rather than with a `md:hidden` utility: the scoped
   `.pane-switch[data-v-…]` rule above outranks a single-class Tailwind
   utility, so the utility would have been silently ignored. */
@media (min-width: 768px) {
  .pane-switch--mobile {
    display: none;
  }
}

/* Below this the plate cannot afford to spend the switch cluster's width
   twice, so it stops trying: the ghost goes, and with it true centring. The
   identity reads from the left — the app-bar arrangement — and the switches
   keep the right. Everything tightens by a couple of pixels to buy the title
   back some room.

   28rem, because the widest cluster this masthead carries is a shade over
   7rem: two of those plus a name worth reading is about where a centred plate
   stops being a good trade. It catches the 22rem sidebar at every window size
   and every phone — which is to say, the whole app as it stands today — and
   hands centring back automatically if a pane ever gets wide enough to wear
   it. This is the rule the old `max-width: 767px` was reaching for; it just
   asked the window instead of the pane, and the window never knew. */
@container (max-width: 28rem) {
  .pane-header {
    grid-template-columns: minmax(0, 1fr) auto;
  }

  .pane-header-gutter {
    display: none;
  }

  .pane-identity {
    text-align: left;
  }

  .pane-status-line {
    justify-content: flex-start;
  }

  .pane-switches {
    gap: 0.25rem;
  }

  .pane-switch {
    height: 1.625rem;
    gap: 0.25rem;
    padding: 0 0.5rem;
  }
}

/* Narrow panes — a small phone, or an iPad running the app in Slide Over. The
   chevrons are the first thing to go: the icon and the word already say where
   the button leads, and dropping them hands the pane's own name ~24px back. */
@container (max-width: 20rem) {
  .pane-switch-chevron {
    display: none;
  }
}

/* The last rung. Narrower than this the words on the pills would leave the
   pane nameless, so the words go instead and the switches stand as icons —
   still the full 26px target, still named to a screen reader by the
   aria-label. A pane this narrow shouldn't happen; the plate holds together
   if it does. */
@container (max-width: 15rem) {
  .pane-switch {
    padding: 0 0.4375rem;
  }

  .pane-switch-label {
    display: none;
  }
}

.pane-switch:hover {
  background: #ffffff;
  border-color: rgba(23, 37, 84, 0.22);
  color: theme('colors.blue.950');
  box-shadow: inset 0 1px 0 #ffffff, 0 1px 3px rgba(23, 37, 84, 0.08);
}

.pane-switch:focus-visible {
  outline: none;
  box-shadow: var(--iw-focus-ring);
}

.dark .pane-switch {
  border-color: rgba(255, 255, 255, 0.14);
  background: rgba(255, 255, 255, 0.045);
  color: rgba(219, 234, 254, 0.72);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

.dark .pane-switch:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.26);
  color: #ffffff;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

.pane-switch-icon-wrap {
  position: relative;
  display: inline-flex;
  align-items: center;
}

.pane-switch-icon {
  font-size: 0.625rem;
  opacity: 0.7;
  transition: opacity var(--iw-dur-2) var(--iw-ease-out);
}

.pane-switch:hover .pane-switch-icon {
  opacity: 0.95;
}

/* Same dot as the status line, sized down for the switch icon — the link to a
   working subagent reads as live without stealing attention. */
.pane-switch-pulse {
  position: absolute;
  top: -2px;
  right: -3px;
  width: 0.375rem;
  height: 0.375rem;
  border-radius: 9999px;
  background: theme('colors.blue.500');
  box-shadow: 0 0 0 2px rgba(var(--iw-surface), 0.9);
  animation: pane-pulse-core 2.4s var(--iw-ease-ambient) infinite;
}

.pane-switch-pulse::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 9999px;
  background: inherit;
  animation: pane-pulse-halo 2.4s var(--iw-ease-ambient) infinite;
}

.dark .pane-switch-pulse {
  background: theme('colors.blue.300');
}

.pane-switch-chevron {
  font-size: 0.5rem;
  opacity: 0.45;
  transition:
    transform var(--iw-dur-2) var(--iw-ease-out),
    opacity var(--iw-dur-2) var(--iw-ease-out);
}

.pane-switch:hover .pane-switch-chevron {
  opacity: 0.8;
}

.group:hover .fa-chevron-right.pane-switch-chevron {
  transform: translateX(2px);
}

.group:hover .fa-chevron-left.pane-switch-chevron {
  transform: translateX(-2px);
}

.pane-switch-label {
  white-space: nowrap;
}

/* Count of what is waiting on the other side — navy ink, the recipe this
   workspace keeps for things you act on. It is the one element in the
   masthead that earns it. */
.pane-switch-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 1.0625rem;
  height: 1.0625rem;
  padding: 0 0.25rem;
  border-radius: 9999px;
  background: theme('colors.blue.950');
  color: #fdf9f2;
  font-size: 0.625rem;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  line-height: 1;
}

.dark .pane-switch-count {
  background: #f3ede2;
  color: theme('colors.blue.950');
}

/* The badge springs in rather than appearing already there — the one place in
   the masthead where a change in the number is itself the news. */
.pane-count-enter-active {
  transition:
    opacity var(--iw-dur-2) var(--iw-ease-out),
    transform var(--iw-dur-2) var(--iw-ease-spring);
}

.pane-count-leave-active {
  transition:
    opacity var(--iw-dur-1) var(--iw-ease-out),
    transform var(--iw-dur-1) var(--iw-ease-out);
}

.pane-count-enter-from {
  opacity: 0;
  transform: scale(0.5);
}

.pane-count-leave-to {
  opacity: 0;
  transform: scale(0.7);
}
</style>
