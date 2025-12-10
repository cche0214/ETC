<template>
  <div class="realtime-flow-card">
    <div class="card-header">
      <div class="header-line"></div>
      <h3>各卡口实时流量趋势 (5分钟粒度)</h3>
      <div class="header-line"></div>
    </div>
    <div ref="chartRef" class="chart-container"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { getTrafficFlowHistory } from '../api/dashboard'

const chartRef = ref(null)
let chart = null
let timer = null

const fetchData = async () => {
  try {
    const res = await getTrafficFlowHistory()
    if (res.code === 200) {
      updateChart(res.xAxis, res.series)
    }
  } catch (error) {
    console.error('获取流量趋势失败:', error)
  }
}

const updateChart = (xAxisData, seriesData) => {
  if (!chart) return
  
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
      textStyle: { color: '#fff' }
    },
    legend: {
      type: 'scroll',
      top: '5%',
      right: '5%',
      textStyle: { color: '#fff' },
      pageIconColor: '#4A9EFF',
      pageTextStyle: { color: '#fff' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: xAxisData,
      axisLine: {
        lineStyle: { color: 'rgba(74, 158, 255, 0.3)' }
      },
      axisLabel: {
        color: 'rgba(255, 255, 255, 0.7)',
        fontSize: 10,
        rotate: 30
      },
      axisTick: { show: false }
    },
    yAxis: {
      type: 'value',
      name: '流量',
      nameTextStyle: { color: 'rgba(255, 255, 255, 0.7)' },
      axisLine: { show: false },
      axisLabel: { color: 'rgba(255, 255, 255, 0.7)' },
      splitLine: {
        lineStyle: {
          color: 'rgba(74, 158, 255, 0.1)',
          type: 'dashed'
        }
      }
    },
    series: seriesData.map(item => ({
      ...item,
      symbol: 'none', // 默认不显示点，鼠标悬停才显示
      lineStyle: { width: 2 }
    }))
  }
  
  chart.setOption(option)
}

const handleResize = () => {
  chart && chart.resize()
}

onMounted(() => {
  if (chartRef.value) {
    chart = echarts.init(chartRef.value)
    fetchData()
    timer = setInterval(fetchData, 30000) // 30秒刷新一次
    window.addEventListener('resize', handleResize)
  }
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
  window.removeEventListener('resize', handleResize)
  if (chart) chart.dispose()
})
</script>

<style scoped>
.realtime-flow-card {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: rgba(10, 15, 45, 0.5);
  border: 1px solid rgba(74, 158, 255, 0.2);
  border-radius: 8px;
  padding: 10px;
  box-sizing: border-box;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 30px;
  margin-bottom: 10px;
}

.header-line {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, rgba(74, 158, 255, 0) 0%, rgba(74, 158, 255, 0.5) 50%, rgba(74, 158, 255, 0) 100%);
}

.card-header h3 {
  margin: 0 15px;
  font-size: 16px;
  color: #00D4FF;
  font-weight: normal;
}

.chart-container {
  flex: 1;
  min-height: 0;
  width: 100%;
}
</style>
