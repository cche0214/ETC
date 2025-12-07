<template>
  <div class="data-overview-card">
    <div class="card-header">
      <div class="header-line"></div>
      <h3>数据总览</h3>
      <div class="header-line"></div>
    </div>
    <div class="gauge-container">
      <div 
        v-for="(item, index) in gaugeData" 
        :key="index"
        class="gauge-item"
      >
        <div :ref="el => setChartRef(el, index)" class="gauge-chart"></div>
        <div class="gauge-label">{{ item.label }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'

// 定义仪表盘数据结构
const gaugeData = ref([
  { label: '车辆总数', value: 7619, max: 10000, color: '#00D4FF' },
  { label: '三型车及以下', value: 1076, max: 5000, color: '#00FF88' },
  { label: '四型车及以上', value: 6543, max: 10000, color: '#FFB800' }
])

const charts = []
const chartRefs = []

const setChartRef = (el, index) => {
  if (el) {
    chartRefs[index] = el
  }
}

const initCharts = () => {
  gaugeData.value.forEach((item, index) => {
    if (!chartRefs[index]) return
    
    const chart = echarts.init(chartRefs[index])
    
    const option = {
      series: [
        {
          type: 'gauge',
          radius: '80%',
          startAngle: 225,
          endAngle: -45,
          min: 0,
          max: item.max,
          splitNumber: 8,
          axisLine: {
            lineStyle: {
              width: 10,
              color: [
                [item.value / item.max, item.color],
                [1, 'rgba(255,255,255,0.1)']
              ]
            }
          },
          pointer: {
            show: false
          },
          axisTick: {
            show: false
          },
          splitLine: {
            distance: -10,
            length: 8,
            lineStyle: {
              color: 'rgba(255,255,255,0.3)',
              width: 1
            }
          },
          axisLabel: {
            distance: 15,
            color: 'rgba(255,255,255,0.5)',
            fontSize: 10
          },
          detail: {
            valueAnimation: true,
            formatter: '{value}',
            color: item.color,
            fontSize: 28,
            fontWeight: 'bold',
            offsetCenter: [0, '0%']
          },
          data: [{ value: item.value }]
        },
        // 外圈装饰
        {
          type: 'gauge',
          radius: '85%',
          startAngle: 225,
          endAngle: -45,
          axisLine: {
            lineStyle: {
              width: 2,
              color: [[1, `${item.color}40`]]
            }
          },
          splitLine: { show: false },
          axisTick: { show: false },
          axisLabel: { show: false },
          detail: { show: false },
          pointer: { show: false }
        }
      ]
    }
    
    chart.setOption(option)
    charts.push(chart)
  })
}

const updateData = (newData) => {
  // 更新数据的方法，供父组件调用
  if (newData && newData.length === 3) {
    gaugeData.value = newData
    charts.forEach((chart, index) => {
      chart.setOption({
        series: [{
          data: [{ value: newData[index].value }]
        }]
      })
    })
  }
}

const resizeCharts = () => {
  charts.forEach(chart => chart.resize())
}

onMounted(() => {
  setTimeout(() => {
    initCharts()
  }, 100)
  window.addEventListener('resize', resizeCharts)
})

onUnmounted(() => {
  charts.forEach(chart => chart.dispose())
  window.removeEventListener('resize', resizeCharts)
})

// 暴露方法供父组件使用
defineExpose({ updateData })
</script>

<style scoped>
.data-overview-card {
  background: rgba(27, 42, 82, 0.6);
  border: 1px solid rgba(74, 158, 255, 0.3);
  border-radius: 8px;
  padding: 20px;
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  height: 100%;
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

.gauge-container {
  display: flex;
  justify-content: space-around;
  align-items: center;
  gap: 20px;
  height: calc(100% - 60px);
}

.gauge-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.gauge-chart {
  width: 100%;
  height: 160px;
}

.gauge-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  text-align: center;
  font-weight: 500;
}

@media (max-width: 1400px) {
  .gauge-chart {
    height: 140px;
  }
}
</style>
