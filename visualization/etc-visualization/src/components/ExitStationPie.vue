<template>
  <div class="exit-station-card">
    <div class="card-header">
      <div class="header-line"></div>
      <h3>出站点总量</h3>
      <div class="header-line"></div>
    </div>
    <div ref="chartRef" class="chart-container"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'

const chartRef = ref(null)
let chart = null

// 模拟数据
const chartData = ref([
  { name: '松山湖', value: 3165, percentage: 32.82 },
  { name: '广莞高速站', value: 3263, percentage: 33.83 },
  { name: '广东其他站点', value: 3216, percentage: 33.35 }
])

const initChart = () => {
  if (!chartRef.value) return
  
  chart = echarts.init(chartRef.value)
  
  const colors = ['#00FF88', '#FFB800', '#4A9EFF']
  
  const option = {
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      borderColor: 'rgba(74, 158, 255, 0.5)',
      borderWidth: 1,
      textStyle: {
        color: '#fff'
      },
      formatter: '{b}<br/>{c} 辆 ({d}%)'
    },
    legend: {
      show: false
    },
    series: [
      {
        name: '出站点统计',
        type: 'pie',
        radius: ['45%', '70%'],
        center: ['50%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 8,
          borderColor: 'rgba(0, 0, 0, 0.5)',
          borderWidth: 2
        },
        label: {
          show: false
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: 'bold',
            color: '#fff'
          },
          itemStyle: {
            shadowBlur: 20,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        labelLine: {
          show: false
        },
        data: chartData.value.map((item, index) => ({
          value: item.value,
          name: item.name,
          itemStyle: {
            color: colors[index]
          }
        }))
      }
    ]
  }
  
  chart.setOption(option)
}

// 自定义图例
const getLegendStyle = (index) => {
  const colors = ['#00FF88', '#FFB800', '#4A9EFF']
  return {
    backgroundColor: colors[index]
  }
}

const updateData = (newData) => {
  if (newData && chart) {
    chartData.value = newData
    const colors = ['#00FF88', '#FFB800', '#4A9EFF']
    chart.setOption({
      series: [{
        data: newData.map((item, index) => ({
          value: item.value,
          name: item.name,
          itemStyle: {
            color: colors[index]
          }
        }))
      }]
    })
  }
}

const resizeChart = () => {
  chart?.resize()
}

onMounted(() => {
  setTimeout(() => {
    initChart()
  }, 100)
  window.addEventListener('resize', resizeChart)
})

onUnmounted(() => {
  chart?.dispose()
  window.removeEventListener('resize', resizeChart)
})

defineExpose({ updateData })
</script>

<style scoped>
.exit-station-card {
  background: rgba(27, 42, 82, 0.6);
  border: 1px solid rgba(74, 158, 255, 0.3);
  border-radius: 8px;
  padding: 20px;
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  height: 100%;
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  gap: 10px;
}

.header-line {
  flex: 1;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(74, 158, 255, 0.5), transparent);
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  color: #4A9EFF;
  white-space: nowrap;
  letter-spacing: 2px;
}

.chart-container {
  flex: 1;
  min-height: 0;
  position: relative;
}
</style>
