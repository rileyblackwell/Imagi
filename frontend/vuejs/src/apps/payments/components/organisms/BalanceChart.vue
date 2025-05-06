<template>
  <div class="balance-chart">
    <div v-if="loading" class="h-full flex justify-center items-center">
      <div class="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-primary-400 border-r-transparent align-[-0.125em] motion-reduce:animate-[spin_1.5s_linear_infinite]"></div>
    </div>
    <div v-else-if="isEmpty" class="h-full flex justify-center items-center">
      <p class="text-gray-400">No data available</p>
    </div>
    <LineChart
      v-else
      :data="chartData"
      :options="chartOptions"
      class="h-full"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Line as LineChart } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, LineElement, LinearScale, PointElement, CategoryScale, Filler } from 'chart.js'

// Register Chart.js components
ChartJS.register(Title, Tooltip, Legend, LineElement, LinearScale, PointElement, CategoryScale, Filler)

// Define props
const props = defineProps<{
  chartData: {
    labels: string[];
    datasets: {
      label: string;
      data: number[];
      borderColor: string;
      backgroundColor: string;
      fill: boolean;
      tension: number;
    }[];
  };
  loading: boolean;
}>()

// Computed properties
const isEmpty = computed(() => {
  return !props.chartData.labels.length || 
    !props.chartData.datasets.length || 
    !props.chartData.datasets[0].data.length
})

// Chart options
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    mode: 'index' as const,
    intersect: false,
  },
  plugins: {
    legend: {
      display: true,
      position: 'top' as const,
      labels: {
        color: '#d1d5db', // text-gray-300
        font: {
          family: "'Inter', sans-serif",
          size: 12
        }
      }
    },
    tooltip: {
      backgroundColor: 'rgba(17, 24, 39, 0.9)', // bg-dark-900/90
      titleColor: '#f9fafb', // text-gray-50
      bodyColor: '#d1d5db', // text-gray-300
      borderColor: 'rgba(75, 85, 99, 0.3)', // border-gray-600/30
      borderWidth: 1,
      padding: 10,
      boxPadding: 5,
      bodyFont: {
        family: "'Inter', sans-serif",
      },
      titleFont: {
        family: "'Inter', sans-serif",
        weight: 'bold' as const
      },
      callbacks: {
        label: function(context: any) {
          return `${context.dataset.label}: ${context.parsed.y} credits`;
        }
      }
    }
  },
  scales: {
    x: {
      grid: {
        color: 'rgba(75, 85, 99, 0.2)', // border-gray-600/20
      },
      ticks: {
        color: '#9ca3af', // text-gray-400
        font: {
          family: "'Inter', sans-serif",
          size: 11
        },
        maxRotation: 45,
        minRotation: 45
      }
    },
    y: {
      grid: {
        color: 'rgba(75, 85, 99, 0.2)', // border-gray-600/20
      },
      ticks: {
        color: '#9ca3af', // text-gray-400
        font: {
          family: "'Inter', sans-serif",
          size: 11
        }
      }
    }
  }
}
</script> 