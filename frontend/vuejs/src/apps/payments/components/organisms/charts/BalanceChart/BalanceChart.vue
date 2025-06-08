<template>
  <div class="balance-chart">
    <div v-if="loading" class="h-full flex justify-center items-center">
      <div class="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-cyan-400 border-r-transparent align-[-0.125em] motion-reduce:animate-[spin_1.5s_linear_infinite]"></div>
    </div>
    <div v-else-if="isEmpty" class="h-full flex flex-col justify-center items-center">
      <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-cyan-500/10 flex items-center justify-center">
        <i class="fas fa-chart-line text-cyan-400 text-xl"></i>
      </div>
      <p class="text-gray-400 text-lg mb-2">No chart data available</p>
      <p class="text-gray-500 text-sm">Make your first transaction to see your balance history</p>
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

// Chart options with modern styling
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
        color: '#e5e7eb', // text-gray-200
        font: {
          family: "'Inter', sans-serif",
          size: 12
        },
        usePointStyle: true,
        pointStyle: 'circle'
      }
    },
    tooltip: {
      backgroundColor: 'rgba(17, 24, 39, 0.95)', // bg-dark-900/95
      titleColor: '#f9fafb', // text-gray-50
      bodyColor: '#d1d5db', // text-gray-300
      borderColor: 'rgba(34, 197, 194, 0.3)', // border-cyan-400/30
      borderWidth: 1,
      padding: 12,
      boxPadding: 6,
      cornerRadius: 8,
      bodyFont: {
        family: "'Inter', sans-serif",
        size: 13
      },
      titleFont: {
        family: "'Inter', sans-serif",
        weight: 'bold' as const,
        size: 14
      },
      callbacks: {
        label: function(context: any) {
          return `${context.dataset.label}: $${context.parsed.y.toFixed(2)}`;
        }
      }
    }
  },
  scales: {
    x: {
      grid: {
        color: 'rgba(255, 255, 255, 0.1)', // white/10
        drawBorder: false
      },
      ticks: {
        color: '#9ca3af', // text-gray-400
        font: {
          family: "'Inter', sans-serif",
          size: 11
        },
        maxRotation: 45,
        minRotation: 45,
        padding: 10
      }
    },
    y: {
      grid: {
        color: 'rgba(255, 255, 255, 0.1)', // white/10
        drawBorder: false
      },
      ticks: {
        color: '#9ca3af', // text-gray-400
        font: {
          family: "'Inter', sans-serif",
          size: 11
        },
        padding: 10,
        callback: function(value: any) {
          return '$' + value.toFixed(2);
        }
      }
    }
  },
  elements: {
    point: {
      radius: 4,
      hoverRadius: 6,
      backgroundColor: '#22d3ee', // cyan-400
      borderColor: '#06b6d4', // cyan-500
      borderWidth: 2
    },
    line: {
      tension: 0.4
    }
  }
}
</script> 