<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'

const chartRef = ref(null)
let chartInstance = null
let timer = null

const initChart = () => {
  chartInstance = echarts.init(chartRef.value)
  
  const option = {
    title: {
      text: 'Top 10 车辆品牌统计 (实时更新)',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: [
      {
        type: 'category',
        data: [],
        axisTick: {
          alignWithLabel: true
        },
        axisLabel: {
          interval: 0,
          rotate: 30
        }
      }
    ],
    yAxis: [
      {
        type: 'value'
      }
    ],
    series: [
      {
        name: '车辆数量',
        type: 'bar',
        barWidth: '60%',
        data: [],
        itemStyle: {
          color: '#5470c6'
        },
        // 增加动画配置，让更新更丝滑
        animationDuration: 1000,
        animationDurationUpdate: 1000,
        animationEasing: 'cubicOut',
        animationEasingUpdate: 'cubicOut'
      }
    ]
  }

  chartInstance.setOption(option)
}

const updateChart = (data) => {
  if (!chartInstance) return

  const brands = data.map(item => item.name)
  const values = data.map(item => item.value)

  // ECharts 会自动合并配置，实现动态更新动画
  chartInstance.setOption({
    xAxis: [
      {
        data: brands
      }
    ],
    series: [
      {
        data: values
      }
    ]
  })
}

const fetchData = async () => {
  try {
    const response = await fetch('/api/traffic/stats/brand?limit=1000')
    const result = await response.json()
    if (result.status === 'success') {
      updateChart(result.data)
    } else {
      console.error('Failed to fetch brand stats:', result.msg)
    }
  } catch (error) {
    console.error('Error fetching brand stats:', error)
  }
}

const handleResize = () => {
  chartInstance && chartInstance.resize()
}

onMounted(() => {
  initChart()
  fetchData()
  window.addEventListener('resize', handleResize)
  // 每 2 秒轮询一次数据
  timer = setInterval(fetchData, 2000)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (timer) clearInterval(timer)
  chartInstance && chartInstance.dispose()
})
</script>

<template>
  <div class="chart-container">
    <div ref="chartRef" class="chart"></div>
  </div>
</template>

<style scoped>
.chart-container {
  width: 100%;
  height: 400px;
  margin-top: 20px;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.chart {
  width: 100%;
  height: 100%;
}
</style>
