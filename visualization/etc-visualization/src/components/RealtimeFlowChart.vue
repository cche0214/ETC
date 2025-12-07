<template>
  <div class="realtime-flow-card">
    <div class="card-header">
      <div class="header-line"></div>
      <h3>各类别车辆不同时段数量分布历史</h3>
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

// 生成模拟数据
const generateData = () => {
  const times = []
  const now = new Date()
  for (let i = 47; i >= 0; i--) {
    const time = new Date(now.getTime() - i * 30 * 1000)
    times.push(time.getHours() + ':' + String(time.getMinutes()).padStart(2, '0'))
  }
  
  return {
    times,
    data1: times.map(() => Math.floor(Math.random() * 50 + 30)),
    data2: times.map(() => Math.floor(Math.random() * 40 + 25)),
    data3: times.map(() => Math.floor(Math.random() * 35 + 20)),
    data4: times.map(() => Math.floor(Math.random() * 30 + 15))
  }
}

const initChart = () => {
  if (!chartRef.value) return
  
  chart = echarts.init(chartRef.value)
  const { times, data1, data2, data3, data4 } = generateData()
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        label: {
          backgroundColor: 'rgba(74, 158, 255, 0.8)'
        }
      },
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      borderColor: 'rgba(74, 158, 255, 0.5)',
      borderWidth: 1,
      textStyle: {
        color: '#fff'
      }
    },
    legend: {
      data: ['一类车', '二类车', '三类车', '四类车'],
      textStyle: {
        color: '#fff'
      },
      top: '5%',
      right: '5%'
    },
    grid: {
      left: '8%',
      right: '5%',
      top: '20%',
      bottom: '15%'
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: times,
      axisLine: {
        lineStyle: {
          color: 'rgba(74, 158, 255, 0.3)'
        }
      },
      axisLabel: {
        color: 'rgba(255, 255, 255, 0.7)',
        fontSize: 10,
        interval: 5,
        rotate: 45
      },
      axisTick: {
        show: false
      }
    },
    yAxis: {
      type: 'value',
      name: '车辆数',
      nameTextStyle: {
        color: 'rgba(255, 255, 255, 0.7)'
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
        name: '四类车',
        type: 'line',
        stack: 'Total',
        smooth: true,
        lineStyle: {
          width: 0
        },
        showSymbol: false,
        areaStyle: {
          opacity: 0.8,
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(0, 212, 255, 0.5)' },
            { offset: 1, color: 'rgba(0, 212, 255, 0.1)' }
          ])
        },
        emphasis: {
          focus: 'series'
        },
        data: data4
      },
      {
        name: '三类车',
        type: 'line',
        stack: 'Total',
        smooth: true,
        lineStyle: {
          width: 0
        },
        showSymbol: false,
        areaStyle: {
          opacity: 0.8,
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(255, 107, 107, 0.5)' },
            { offset: 1, color: 'rgba(255, 107, 107, 0.1)' }
          ])
        },
        emphasis: {
          focus: 'series'
        },
        data: data3
      },
      {
        name: '二类车',
        type: 'line',
        stack: 'Total',
        smooth: true,
        lineStyle: {
          width: 0
        },
        showSymbol: false,
        areaStyle: {
          opacity: 0.8,
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(255, 184, 0, 0.5)' },
            { offset: 1, color: 'rgba(255, 184, 0, 0.1)' }
          ])
        },
        emphasis: {
          focus: 'series'
        },
        data: data2
      },
      {
        name: '一类车',
        type: 'line',
        stack: 'Total',
        smooth: true,
        lineStyle: {
          width: 0
        },
        showSymbol: false,
        areaStyle: {
          opacity: 0.8,
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(0, 255, 136, 0.5)' },
            { offset: 1, color: 'rgba(0, 255, 136, 0.1)' }
          ])
        },
        emphasis: {
          focus: 'series'
        },
        data: data1
      }
    ]
  }
  
  chart.setOption(option)
}

const updateData = (newData) => {
  if (newData && chart) {
    chart.setOption({
      series: newData
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
.realtime-flow-card {
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
