<template>
  <div class="fan-chart">
    <component
      :is="chartComponent"
      :data="chartData"
      :options="chartOptions"
      :height="height"
    />
  </div>
</template>

<script>
import { computed, defineComponent } from 'vue'

// 这里使用简单的 SVG 图表，实际项目中可以使用 ECharts 或 Chart.js
export default defineComponent({
  name: 'FanChart',
  
  props: {
    type: {
      type: String,
      default: 'bar',
      validator: (value) => ['bar', 'pie', 'line', 'radar'].includes(value)
    },
    data: {
      type: Object,
      required: true
    },
    title: {
      type: String,
      default: ''
    },
    height: {
      type: String,
      default: '300px'
    }
  },
  
  setup(props) {
    const chartComponent = computed(() => {
      switch (props.type) {
        case 'pie':
          return 'div' // 简化实现
        case 'line':
          return 'div'
        case 'radar':
          return 'div'
        default:
          return 'div'
      }
    })
    
    const chartData = computed(() => {
      return props.data
    })
    
    const chartOptions = computed(() => {
      return {
        responsive: true,
        maintainAspectRatio: false
      }
    })
    
    return {
      chartComponent,
      chartData,
      chartOptions
    }
  }
})
</script>

<style scoped>
.fan-chart {
  width: 100%;
  position: relative;
}
</style>
