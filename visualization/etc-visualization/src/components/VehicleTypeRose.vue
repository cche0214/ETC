<template>
  <div class="vehicle-type-rose-card">
    <div class="card-header">
      <div class="header-line"></div>
      <h3>车型分布统计</h3>
      <div class="header-line"></div>
    </div>
    <div ref="chartRef" class="chart-container"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, defineExpose } from 'vue'
import * as echarts from 'echarts'
import { getVehicleTypeStats } from '../api/dashboard'

const chartRef = ref(null)
let chart = null

const fetchData = async () => {
  try {
    const res = await getVehicleTypeStats()
    if (res.code === 200 || res.status === 'success') {
      updateChart(res.data)
    }
  } catch (error) {
    console.error('获取车型分布数据失败:', error)
  }
}

defineExpose({
  updateData: fetchData
})

const updateChart = (data) => {
  if (!chart) return

  // 对数据进行对数处理，缩小差异，但保留原始值用于 tooltip 显示
  // 过滤掉值为0的数据，避免log计算错误
  const processedData = data
    .filter(item => item.value > 0)
    .sort((a, b) => a.value - b.value) // 升序排列，漏斗图通常从小到大或从大到小

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b} : {c}',
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      borderColor: '#4A9EFF',
      textStyle: { color: '#fff' }
    },
    grid: {
      top: '10%',
      left: '5%',
      right: '15%',
      bottom: '5%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      show: false
    },
    yAxis: {
      type: 'category',
      data: processedData.map(item => item.name),
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: {
        color: '#fff',
        fontSize: 12,
        margin: 10
      }
    },
    series: [
      {
        name: '车型数量',
        type: 'bar',
        data: processedData.map(item => item.value),
        barWidth: 12,
        itemStyle: {
          borderRadius: [0, 10, 10, 0],
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#00D4FF' },
            { offset: 1, color: '#4A9EFF' }
          ])
        },
        label: {
          show: true,
          position: 'right',
          color: '#fff',
          fontSize: 12,
          formatter: '{c}'
        },
        // 添加背景条，让极小值也能看清位置
        showBackground: true,
        backgroundStyle: {
          color: 'rgba(255, 255, 255, 0.05)',
          borderRadius: [0, 10, 10, 0]
        }
      }
    ]
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
    window.addEventListener('resize', handleResize)
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (chart) chart.dispose()
})
</script>

<style scoped>
.vehicle-type-rose-card {
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
  flex-shrink: 0;
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
  white-space: nowrap;
}

.chart-container {
  flex: 1;
  min-height: 0;
  width: 100%;
}
</style>