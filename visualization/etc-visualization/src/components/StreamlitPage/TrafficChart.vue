<template>
  <div class="chart-card">
    <div class="chart-header">
      <h3 class="chart-title">
        <span class="icon">📊</span> {{ title }}
      </h3>
    </div>
    <div ref="chartRef" class="chart-container"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  title: {
    type: String,
    default: '流量趋势'
  },
  xAxisData: {
    type: Array,
    default: () => []
  },
  seriesData: {
    type: Array,
    default: () => []
  }
})

const chartRef = ref(null)
let chartInstance = null

const initChart = () => {
  if (!chartRef.value) return
  
  chartInstance = echarts.init(chartRef.value)
  updateChart()
  
  window.addEventListener('resize', handleResize)
}

const handleResize = () => {
  chartInstance?.resize()
}

const updateChart = () => {
  if (!chartInstance) return

  // 构造 X 轴：历史时间点 + 下一个5分钟
  let nextTimeLabel = '预测'
  if (props.xAxisData.length > 0) {
    const lastTime = props.xAxisData[props.xAxisData.length - 1]
    try {
      const [h, m] = lastTime.split(':').map(Number)
      const date = new Date()
      date.setHours(h)
      date.setMinutes(m + 5)
      nextTimeLabel = `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
    } catch (e) {
      console.warn('Time parse error', e)
    }
  }
  
  const fullXAxis = [...props.xAxisData, nextTimeLabel]

  // 构造 Series
  // 为了实现“实线+虚线”效果，我们需要对每条线做处理，或者简单点，用 markLine 分隔
  // 这里采用 markLine 分隔历史和预测区域的方式，保持多折线图的清晰度
  
  const processedSeries = props.seriesData.map(item => {
    // 拼接历史数据和预测数据
    const fullData = [...item.data, item.prediction]
    
    return {
      name: item.name.split('-')[0] + ' ' + item.name.split('-')[1], // 简化名称 G3-K731
      type: 'line',
      data: fullData,
      smooth: true,
      symbol: 'circle',
      symbolSize: 6
    }
  })

  const option = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(0,0,0,0.8)',
      borderColor: '#4A9EFF',
      textStyle: { color: '#fff' }
    },
    grid: {
      top: '15%',
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: fullXAxis,
      axisLine: { lineStyle: { color: '#4A9EFF' } },
      axisLabel: { color: '#fff' },
      // 添加分隔带
      splitArea: {
        show: true,
        areaStyle: {
          color: ['rgba(255,255,255,0)', 'rgba(255,255,255,0.05)']
        }
      }
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } },
      axisLabel: { color: '#fff' }
    },
    series: [
      ...processedSeries,
      {
        type: 'line',
        markLine: {
          symbol: ['none', 'none'],
          label: { show: true, position: 'end', formatter: '当前时刻' },
          lineStyle: { type: 'dashed', color: '#faad14' },
          data: [
            { xAxis: props.xAxisData.length - 1 }
          ]
        }
      }
    ]
  }

  chartInstance.setOption(option)
}

watch(() => props.seriesData, () => {
  updateChart()
}, { deep: true })

onMounted(() => {
  initChart()
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chartInstance?.dispose()
})
</script>

<style scoped>
.chart-card {
  /* 移除背景和边框，完全由父容器控制样式 */
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden; /* 防止内部内容溢出 */
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.chart-title {
  color: #fff;
  margin: 0;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.chart-legend {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

.chart-container {
  flex: 1;
  min-height: 0;
}
</style>
