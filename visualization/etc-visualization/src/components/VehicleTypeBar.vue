<template>
  <div class="vehicle-type-bar-card">
    <div class="card-header">
      <div class="header-line"></div>
      <h3>车型堵塞</h3>
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
  { name: '三型(核)', value: 2527 },
  { name: '二型(核)', value: 2758 },
  { name: '一型(核)', value: 2795 },
  { name: '二型(空)', value: 2783 },
  { name: '三型(空)', value: 2710 },
  { name: '六型(核)', value: 2690 },
  { name: '五型(核)', value: 2568 },
  { name: '一型(空)', value: 2624 }
])

const initChart = () => {
  if (!chartRef.value) return
  
  chart = echarts.init(chartRef.value)
  
  const colors = ['#4A9EFF', '#00FF88', '#FFB800', '#FF6B6B', '#9B59B6', '#3498DB', '#E74C3C', '#1ABC9C']
  
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
      formatter: '{b}<br/>车辆数: {c}'
    },
    grid: {
      left: '25%',
      right: '15%',
      top: '5%',
      bottom: '5%'
    },
    xAxis: {
      type: 'value',
      max: 3000,
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
    yAxis: {
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
      },
      axisTick: {
        show: false
      }
    },
    series: [
      {
        name: '车辆数',
        type: 'bar',
        barWidth: '60%',
        data: chartData.value.map((item, index) => ({
          value: item.value,
          itemStyle: {
            color: new echarts.graphic.LinearGradient(1, 0, 0, 0, [
              { offset: 0, color: colors[index] },
              { offset: 1, color: colors[index] + '40' }
            ]),
            borderRadius: [0, 8, 8, 0]
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
          position: 'right',
          color: '#fff',
          fontSize: 12,
          formatter: '{c}'
        }
      }
    ]
  }
  
  chart.setOption(option)
}

const updateData = (newData) => {
  if (newData && chart) {
    chartData.value = newData
    const colors = ['#4A9EFF', '#00FF88', '#FFB800', '#FF6B6B', '#9B59B6', '#3498DB', '#E74C3C', '#1ABC9C']
    chart.setOption({
      yAxis: {
        data: newData.map(item => item.name)
      },
      series: [{
        data: newData.map((item, index) => ({
          value: item.value,
          itemStyle: {
            color: new echarts.graphic.LinearGradient(1, 0, 0, 0, [
              { offset: 0, color: colors[index] },
              { offset: 1, color: colors[index] + '40' }
            ])
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
.vehicle-type-bar-card {
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
