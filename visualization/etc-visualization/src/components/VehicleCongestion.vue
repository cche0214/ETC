<template>
  <div class="vehicle-congestion-card">
    <div class="card-header">
      <div class="header-line"></div>
      <h3>各型车堵塞</h3>
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
  { name: '一型', value: 2800, rate: '95%' },
  { name: '二型', value: 2900, rate: '100%' },
  { name: '三型', value: 2850, rate: '98%' },
  { name: '四型', value: 2750, rate: '92%' }
])

const initChart = () => {
  if (!chartRef.value) return
  
  chart = echarts.init(chartRef.value)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      borderColor: 'rgba(74, 158, 255, 0.5)',
      borderWidth: 1,
      textStyle: {
        color: '#fff'
      },
      formatter: (params) => {
        const data = params[0]
        return `${data.name}<br/>车辆数: ${data.value}<br/>拥堵率: ${chartData.value[data.dataIndex].rate}`
      }
    },
    grid: {
      left: '15%',
      right: '10%',
      top: '15%',
      bottom: '15%'
    },
    xAxis: {
      type: 'category',
      data: chartData.value.map(item => item.name),
      axisLine: {
        lineStyle: {
          color: 'rgba(74, 158, 255, 0.3)'
        }
      },
      axisLabel: {
        color: '#fff',
        fontSize: 12
      }
    },
    yAxis: {
      type: 'value',
      name: '车辆数',
      nameTextStyle: {
        color: 'rgba(255, 255, 255, 0.7)',
        fontSize: 12
      },
      axisLine: {
        show: false
      },
      axisTick: {
        show: false
      },
      axisLabel: {
        color: 'rgba(255, 255, 255, 0.6)',
        fontSize: 11
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(74, 158, 255, 0.1)',
          type: 'dashed'
        }
      }
    },
    series: [
      {
        name: '车辆数',
        type: 'bar',
        barWidth: '40%',
        data: chartData.value.map((item, index) => ({
          value: item.value,
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: ['#4A9EFF', '#00FF88', '#FFB800', '#FF6B6B'][index] },
              { offset: 1, color: ['#1e5f8c', '#008844', '#CC9200', '#CC3333'][index] }
            ]),
            borderRadius: [8, 8, 0, 0]
          }
        })),
        emphasis: {
          itemStyle: {
            shadowBlur: 20,
            shadowColor: 'rgba(74, 158, 255, 0.5)'
          }
        },
        label: {
          show: true,
          position: 'top',
          color: '#fff',
          fontSize: 12,
          formatter: (params) => chartData.value[params.dataIndex].rate
        }
      }
    ]
  }
  
  chart.setOption(option)
}

const updateData = (newData) => {
  if (newData && chart) {
    chartData.value = newData
    chart.setOption({
      xAxis: {
        data: newData.map(item => item.name)
      },
      series: [{
        data: newData.map((item, index) => ({
          value: item.value,
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: ['#4A9EFF', '#00FF88', '#FFB800', '#FF6B6B'][index] },
              { offset: 1, color: ['#1e5f8c', '#008844', '#CC9200', '#CC3333'][index] }
            ])
          }
        })),
        label: {
          formatter: (params) => newData[params.dataIndex].rate
        }
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
.vehicle-congestion-card {
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
}
</style>
