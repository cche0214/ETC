<template>
  <div class="vehicle-type-bar-card">
    <div class="card-header">
      <div class="header-line"></div>
      <h3>车辆品牌分布</h3>
      <div class="header-line"></div>
    </div>
    <div ref="chartRef" class="chart-container"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { getBrandStats } from '../../api/dashboard'

const chartRef = ref(null)
let chart = null

// 获取数据
const fetchData = async () => {
  try {
    const res = await getBrandStats()
    if (res.status === 'success') {
      updateChart(res.data)
    }
  } catch (error) {
    console.error('获取品牌数据失败:', error)
  }
}

// 暴露给父组件调用
defineExpose({
  updateData: fetchData
})

// 更新图表
const updateChart = (data) => {
  if (!chart) return
  
  // 1. 数据处理：将 [{name: 'A', value: 10}, ...] 拆分为 X轴 和 Y轴数据
  const xData = data.map(item => item.name)
  const yData = data.map(item => item.value)

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      borderColor: '#4A9EFF',
      textStyle: { color: '#fff' }
    },
    grid: {
      top: '15%',
      left: '3%',
      right: '4%',
      bottom: '5%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: xData, // 这里必须填入品牌名称数组
      axisLabel: {
        color: '#fff',
        interval: 0, // 强制显示所有标签
        rotate: 30,  // 稍微倾斜防止重叠
        fontSize: 10
      },
      axisLine: {
        lineStyle: { color: '#4A9EFF' }
      },
      axisTick: { show: false }
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#fff' },
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
        data: yData, // 这里填入数值数组
        barWidth: '40%',
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#00D4FF' },
            { offset: 1, color: '#4A9EFF' }
          ]),
          borderRadius: [4, 4, 0, 0]
        },
        label: {
          show: true,
          position: 'top',
          color: '#fff',
          fontSize: 10
        }
      }
    ]
  }
  
  chart.setOption(option)
}

// 窗口大小改变时重绘
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
.vehicle-type-bar-card {
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
  min-height: 0; /* 关键：防止 flex 子项溢出 */
  width: 100%;
}
</style>
