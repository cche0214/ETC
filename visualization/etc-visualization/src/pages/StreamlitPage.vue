<template>
  <div class="streamlit-page">
    <header class="header">
      <div class="header-bg"></div>
      <button class="back-btn" @click="$router.push('/')">
        <span class="icon">←</span> 返回主页
      </button>
      <h1 class="header-title">实时交通流量预测中心</h1>
      <div class="header-time">{{ currentTime }}</div>
    </header>

    <div class="content-grid">
      <!-- 上半部分：左右两个大图 -->
      <div class="charts-row">
        <div class="chart-wrapper">
          <traffic-chart 
            title="省界卡口流量趋势 (Provincial)" 
            :x-axis-data="xAxisData"
            :series-data="provincialData"
          />
        </div>
        <div class="chart-wrapper">
          <traffic-chart 
            title="市界卡口流量趋势 (City)" 
            :x-axis-data="xAxisData"
            :series-data="cityData"
          />
        </div>
      </div>

      <!-- 下半部分：详细数据表格 -->
      <div class="table-row">
        <prediction-table :data="tableData" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import TrafficChart from '../components/StreamlitPage/TrafficChart.vue'
import PredictionTable from '../components/StreamlitPage/PredictionTable.vue'
import dayjs from 'dayjs'

const currentTime = ref('')
const timer = ref(null)
const xAxisData = ref([])
const rawSeriesData = ref([])

// 更新时间
const updateTime = () => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  const weekDay = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][now.getDay()]
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  const seconds = String(now.getSeconds()).padStart(2, '0')
  
  currentTime.value = `${year}-${month}-${day} ${weekDay} ${hours}:${minutes}:${seconds}`
}

// 生成模拟数据
const generateMockData = () => {
  // 生成最近12个时间点（每5分钟）
  const times = []
  const now = dayjs()
  for (let i = 11; i >= 0; i--) {
    times.push(now.subtract(i * 5, 'minute').format('HH:mm'))
  }
  xAxisData.value = times

  // 模拟卡口列表
  const checkpoints = [
    'G30苏皖省界', 'G3京台苏鲁省界', 'G2513苏鲁省界', 'G30连霍苏皖省界', 'S69济徐苏鲁省界', // 省界
    '徐州东收费站', '徐州南收费站', '徐州西收费站', '彭城收费站', '汉王收费站', '柳新收费站' // 市界
  ]

  rawSeriesData.value = checkpoints.map(name => {
    const data = []
    // 随机生成基准流量
    let baseFlow = Math.floor(Math.random() * 100) + 50
    if (name.includes('省界')) baseFlow += 100 // 省界流量大一些

    for (let i = 0; i < 12; i++) {
      // 随机波动
      const fluctuation = Math.floor(Math.random() * 20) - 10
      let value = baseFlow + fluctuation
      if (value < 0) value = 0
      data.push(value)
      // 下一个点基于当前点波动
      baseFlow = value
    }
    
    // 预测值
    const prediction = baseFlow + Math.floor(Math.random() * 15) - 5
    
    return {
      name: name,
      data: data,
      prediction: prediction
    }
  })
}

// 获取数据
const fetchData = async () => {
  try {
    // 优先尝试调用后端接口，如果失败则使用模拟数据
    // const res = await fetch('/api/dashboard/flow_history')
    // const data = await res.json()
    
    // if (data.code === 200) {
    //   xAxisData.value = data.xAxis
    //   rawSeriesData.value = data.series
    // } else {
      generateMockData()
    // }
  } catch (e) {
    console.error('Fetch error, using mock data:', e)
    generateMockData()
  }
}

// 数据分组逻辑
const provincialData = computed(() => {
  return rawSeriesData.value.filter(item => item.name.includes('省界'))
})

const cityData = computed(() => {
  return rawSeriesData.value.filter(item => !item.name.includes('省界'))
})

// 表格数据转换
const tableData = computed(() => {
  return rawSeriesData.value.map(item => {
    const current = item.data[item.data.length - 1] || 0
    const prediction = item.prediction || 0
    const diff = Number((prediction - current).toFixed(1))
    
    return {
      name: item.name,
      type: item.name.includes('省界') ? '省界' : '市界',
      current: current,
      prediction: prediction,
      diff: diff
    }
  })
})

onMounted(() => {
  updateTime()
  timer.value = setInterval(updateTime, 1000)
  fetchData()
  // 每5秒刷新一次模拟数据，演示动态效果
  setInterval(generateMockData, 5000)
})

onUnmounted(() => {
  if (timer.value) clearInterval(timer.value)
})
</script>

<style scoped>
.streamlit-page {
  width: 100vw;
  height: 100vh;
  background: linear-gradient(135deg, #0a0f2d 0%, #1a1f3a 50%, #0a0f2d 100%);
  color: white;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.header {
  position: relative;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(180deg, rgba(27, 42, 82, 0.8) 0%, rgba(27, 42, 82, 0.4) 100%);
  border-bottom: 2px solid rgba(74, 158, 255, 0.3);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  z-index: 10;
}

.header-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: url('data:image/svg+xml,<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg"><defs><pattern id="grid" width="50" height="50" patternUnits="userSpaceOnUse"><path d="M 50 0 L 0 0 0 50" fill="none" stroke="rgba(74,158,255,0.1)" stroke-width="1"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
  opacity: 0.3;
}

.header-title {
  position: relative;
  margin: 0;
  font-size: 36px;
  font-weight: bold;
  letter-spacing: 4px;
  background: linear-gradient(90deg, #4A9EFF 0%, #00D4FF 100%);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 0 0 30px rgba(74, 158, 255, 0.5);
}

.header-time {
  position: absolute;
  right: 30px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 16px;
  color: rgba(255, 255, 255, 0.8);
  font-family: 'Courier New', monospace;
}

.back-btn {
  position: absolute;
  left: 30px;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(74, 158, 255, 0.1);
  border: 1px solid rgba(74, 158, 255, 0.5);
  color: #4A9EFF;
  padding: 8px 20px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  border-radius: 4px;
  z-index: 20;
}

.back-btn:hover {
  background: rgba(74, 158, 255, 0.3);
  box-shadow: 0 0 15px rgba(74, 158, 255, 0.3);
  text-shadow: 0 0 5px rgba(74, 158, 255, 0.8);
}

.content-grid {
  flex: 1;
  padding: 20px;
  display: grid;
  grid-template-rows: 55% 1fr; /* 上半部分占比增加，下半部分自然变小 */
  gap: 20px;
  min-height: 0;
  overflow: hidden;
  box-sizing: border-box;
}

.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  min-height: 0;
  box-sizing: border-box;
}

.table-row {
  min-height: 0;
  background: rgba(10, 15, 45, 0.3);
  border-radius: 8px;
  border: 1px solid rgba(74, 158, 255, 0.1);
  overflow: hidden;
  box-sizing: border-box;
}

.chart-wrapper {
  height: 100%;
  min-height: 0;
  background: rgba(10, 15, 45, 0.3);
  border-radius: 8px;
  border: 1px solid rgba(74, 158, 255, 0.1);
  padding: 10px;
  box-sizing: border-box; /* 关键：防止padding导致尺寸溢出 */
  overflow: hidden; /* 确保内容不溢出圆角边框 */
  box-shadow: 0 0 15px rgba(74, 158, 255, 0.1); /* 增强阴影效果 */
}
</style>
