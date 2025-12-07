<template>
  <div class="chart-container">
    <div class="chart-header">
      <h2 class="chart-title">📈 实时交通流量趋势 (Real-time Traffic Flow)</h2>
      <div class="chart-info">
        <span class="info-item">数据来源：Redis (Flink Aggregation)</span>
        <span class="info-item">当前数据时间：<span class="highlight-time">{{ latestTime }}</span></span>
      </div>
    </div>
    <div ref="chartRef" class="chart-body"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import axios from 'axios'

const chartRef = ref(null)
const latestTime = ref('Loading...')
let myChart = null
let timer = null

const initChart = () => {
  myChart = echarts.init(chartRef.value)
  const option = {
    backgroundColor: '#fff',
    title: {
      text: '各卡口车流量实时监控',
      left: 'center',
      top: 10,
      textStyle: {
        color: '#333',
        fontSize: 16
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
      backgroundColor: 'rgba(255, 255, 255, 0.9)',
      borderColor: '#ccc',
      borderWidth: 1,
      textStyle: {
        color: '#333'
      },
      // 按照数值大小排序，方便查看
      order: 'valueDesc'
    },
    legend: {
      type: 'scroll',
      bottom: 10,
      left: 'center',
      width: '90%',
      data: [] // 动态加载
    },
    toolbox: {
      feature: {
        dataZoom: {
          yAxisIndex: 'none'
        },
        restore: {},
        saveAsImage: {}
      },
      right: 20
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%', // 给 legend 留空间
      top: '15%',    // 给 title 留空间
      containLabel: true
    },
    dataZoom: [
      {
        type: 'inside',
        start: 0,
        end: 100
      },
      {
        start: 0,
        end: 100
      }
    ],
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: [], // 动态加载时间轴
      axisLine: {
        lineStyle: {
          color: '#666'
        }
      }
    },
    yAxis: {
      type: 'value',
      name: '流量 (辆/5min)',
      splitLine: {
        lineStyle: {
          type: 'dashed',
          color: '#eee'
        }
      }
    },
    series: [] // 动态加载数据
  }
  myChart.setOption(option)
}

const fetchData = async () => {
  try {
    const res = await axios.get('/api/traffic/flow_history')
    if (res.data && res.data.code === 200) {
      const data = res.data
      
      // 更新最新数据时间
      latestTime.value = data.latest_data_time

      // 更新图表
      myChart.setOption({
        xAxis: {
          data: data.xAxis
        },
        legend: {
          data: data.series.map(item => item.name)
        },
        series: data.series
      })
    }
  } catch (e) {
    console.error("获取流量数据失败:", e)
  }
}

onMounted(() => {
  initChart()
  fetchData()
  // 每 3 秒刷新一次
  timer = setInterval(fetchData, 3000)
  
  // 监听窗口大小变化
  window.addEventListener('resize', () => myChart?.resize())
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
  window.removeEventListener('resize', () => myChart?.resize())
  myChart?.dispose()
})
</script>

<style scoped>
.chart-container {
  margin-top: 20px;
  border: 1px solid #e0e0e0;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 20px 0 rgba(0,0,0,0.08);
  background-color: #fff;
  transition: all 0.3s ease;
}

.chart-container:hover {
  box-shadow: 0 6px 24px 0 rgba(0,0,0,0.12);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #f0f0f0;
}

.chart-title {
  color: #2c3e50;
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.chart-info {
  color: #666;
  font-size: 14px;
}

.info-item {
  margin-left: 15px;
}

.highlight-time {
  font-weight: bold;
  color: #E6A23C;
  font-family: monospace;
  font-size: 16px;
}

.chart-body {
  width: 100%;
  height: 600px; /* 增加高度 */
}
</style>
