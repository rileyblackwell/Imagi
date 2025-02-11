<template>
  <div class="space-y-4">
    <!-- Activity Items -->
    <div v-if="activities.length" class="space-y-4">
      <div v-for="activity in activities" :key="activity.id"
           class="flex items-start space-x-3 p-3 rounded-lg bg-dark-800/50 border border-dark-700/50">
        <!-- Activity Icon -->
        <div class="flex-shrink-0 w-8 h-8 rounded-lg bg-primary-500/10 flex items-center justify-center">
          <i :class="getActivityIcon(activity.type)" class="text-primary-400"></i>
        </div>

        <!-- Activity Content -->
        <div class="flex-1 min-w-0">
          <p class="text-sm text-white font-medium">
            {{ activity.description }}
          </p>
          <p class="text-xs text-gray-400 mt-1">
            {{ formatTime(activity.timestamp) }}
          </p>
        </div>

        <!-- Optional Status Indicator -->
        <div v-if="activity.status" class="flex-shrink-0">
          <span :class="getStatusClass(activity.status)"
                class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium">
            {{ activity.status }}
          </span>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-6">
      <div class="text-gray-400">No recent activity</div>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue'
import { formatDistanceToNow } from 'date-fns'

export default defineComponent({
  name: 'ActivityFeed',
  
  props: {
    activities: {
      type: Array,
      default: () => [],
      validator: (value) => {
        return value.every(activity => 
          activity.id && 
          activity.type && 
          activity.description && 
          activity.timestamp
        )
      }
    }
  },

  methods: {
    getActivityIcon(type) {
      const icons = {
        create: 'fas fa-plus',
        update: 'fas fa-pen',
        delete: 'fas fa-trash',
        deploy: 'fas fa-rocket',
        build: 'fas fa-hammer',
        default: 'fas fa-circle-info'
      }
      return icons[type] || icons.default
    },

    getStatusClass(status) {
      const classes = {
        success: 'bg-green-100 text-green-800',
        warning: 'bg-yellow-100 text-yellow-800',
        error: 'bg-red-100 text-red-800',
        info: 'bg-blue-100 text-blue-800'
      }
      return classes[status] || classes.info
    },

    formatTime(timestamp) {
      return formatDistanceToNow(new Date(timestamp), { addSuffix: true })
    }
  }
})
</script>
