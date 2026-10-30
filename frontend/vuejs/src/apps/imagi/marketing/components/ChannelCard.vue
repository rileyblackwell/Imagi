<!--
  ChannelCard.vue - One way to run a campaign, on the Campaigns home: what the
  channel does, whether its account is connected, and the action that starts a
  campaign on it. The actions come in through slots so each channel keeps its
  own routes.
-->
<template>
  <!-- The lift on hover is motion-safe only; its transition replaces ui.card's colour one. -->
  <article
    class="channel group flex min-h-[15.5rem] flex-col p-6
      motion-safe:[transition:transform_200ms_cubic-bezier(0.22,1,0.36,1),border-color_200ms_cubic-bezier(0.22,1,0.36,1)]
      motion-safe:hover:-translate-y-0.5 motion-safe:hover:border-sl-line-strong"
    :class="ui.card"
  >
    <div class="flex flex-wrap items-start justify-between gap-x-4 gap-y-3">
      <div class="flex items-center gap-3.5 min-w-[13rem] flex-1">
        <div class="w-12 h-12 shrink-0 text-lg" :class="ui.iconTile">
          <i :class="icon" aria-hidden="true"></i>
        </div>
        <div class="min-w-0">
          <h3 :class="ui.headingText" class="leading-tight">{{ title }}</h3>
          <p :class="ui.hintText" class="mt-0.5">{{ via }}</p>
        </div>
      </div>
      <BaseStatusBadge
        :tone="connected ? 'success' : 'neutral'"
        :label="connected ? 'Connected' : 'Not connected yet'"
      />
    </div>

    <p :class="ui.bodyText" class="mt-5 leading-relaxed">{{ description }}</p>

    <p v-if="detail" class="mt-4 pt-4 border-t border-[color:var(--sl-line)] text-xs text-ink/60 dark:text-bone/60">
      {{ detail }}
    </p>

    <div class="mt-auto pt-6 flex flex-wrap items-center gap-x-4 gap-y-3">
      <slot name="actions"></slot>
    </div>
  </article>
</template>

<script setup lang="ts">
import { StatusBadge as BaseStatusBadge } from '@/shared/components'
import { ui } from '../utils/ui'

defineProps<{
  title: string
  via: string
  icon: string
  description: string
  connected: boolean
  /** One quiet line under the description: reach, drafts, last sync. */
  detail?: string
}>()
</script>
