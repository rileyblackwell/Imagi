<template>
  <div class="space-y-4">
    <div v-if="!activities.length" class="text-center py-8">
      <EmptyState
        icon="fas fa-clock"
        title="No recent activity"
        description="Your activity feed will appear here"
      />
    </div>
    <div v-else class="divide-y divide-dark-700">
      <div
        v-for="activity in activities"
        :key="activity.id"
        class="py-4 first:pt-0 last:pb-0"
      >
        <div class="flex items-start">
          <div
            class="w-8 h-8 rounded-full flex items-center justify-center"
            :class="getActivityColor(activity.type)"
          >
            <i :class="getActivityIcon(activity.type)" class="text-sm"></i>
          </div>
          <div class="ml-4 flex-grow">
            <p class="text-white">{{ activity.message }}</p>
            <p class="text-sm text-gray-400">{{ formatDate(activity.createdAt) }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { EmptyState } from '@/shared/components/molecules'
import type { Activity, ActivityType } from '@/apps/home/types/dashboard'

interface Props {
  activities: Activity[]
}

defineProps<Props>()

function getActivityIcon(type: ActivityType): string {
  const icons: Record<ActivityType | 'default', string> = {
    created: 'fas fa-plus',
    updated: 'fas fa-pencil',
    deleted: 'fas fa-trash',
    deployed: 'fas fa-rocket',
    default: 'fas fa-circle'
  }
  return icons[type] || icons.default
}

function getActivityColor(type: ActivityType): string {
  const colors: Record<ActivityType | 'default', string> = {
    created: 'bg-green-900/50 text-green-400',
    updated: 'bg-blue-900/50 text-blue-400',
    deleted: 'bg-red-900/50 text-red-400',
    deployed: 'bg-purple-900/50 text-purple-400',
    default: 'bg-gray-900/50 text-gray-400'
  }
  return colors[type] || colors.default
}

function formatDate(date: string): string {
  return new Intl.RelativeTimeFormat('en', { numeric: 'auto' }).format(
    -Math.round((Date.now() - new Date(date).getTime()) / (1000 * 60 * 60 * 24)),
    'day'
  )
}
</script>
