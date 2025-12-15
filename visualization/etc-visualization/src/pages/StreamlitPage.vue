<template>
  <div class="streamlit-page">
    <header class="header">
      <div class="header-bg"></div>
      <button class="back-btn" @click="$router.push('/')">
        <span class="icon">←</span> 返回主页
      </button>
      <h1 class="header-title">
        实时交通流量预测中心
        <span class="data-time" v-if="latestDataTime">({{ latestDataTime }})</span>
      </h1>
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
import axios from 'axios'
import { ElMessage } from 'element-plus'

const currentTime = ref('')
const latestDataTime = ref('')
const timer = ref(null)
const dataTimer = ref(null)
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

// 获取数据
const fetchData = async () => {
  try {
    const response = await axios.get('/api/prediction/realtime')
    
    if (response.data.code === 200) {
      const data = response.data.data
      xAxisData.value = data.xAxis
      rawSeriesData.value = data.series
      latestDataTime.value = data.latest_data_time
    } else {
      ElMessage.error('获取数据失败: ' + response.data.message)
    }
  } catch (e) {
    console.error('Fetch error:', e)
    ElMessage.error('网络请求失败，请检查后端服务')
  }
}

// 数据分组逻辑
const provincialData = computed(() => {
  return rawSeriesData.value.filter(item => item.name.includes('省际'))
})

const cityData = computed(() => {
  return rawSeriesData.value.filter(item => !item.name.includes('省际'))
})

// 表格数据转换
const tableData = computed(() => {
  return rawSeriesData.value.map(item => {
    const current = item.data && item.data.length > 0 ? item.data[item.data.length - 1] : 0
    const prediction = item.prediction !== null ? Number(item.prediction).toFixed(2) : 'N/A'
    
    // 计算差值
    let diff = 0
    if (prediction !== 'N/A') {
      diff = Number((prediction - current).toFixed(2))
    }
    
    return {
      name: item.name,
      type: item.name.includes('省际') ? '省际' : '市际',
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
  // 每30秒刷新一次数据
  dataTimer.value = setInterval(fetchData, 30000)
})

onUnmounted(() => {
  if (timer.value) clearInterval(timer.value)
  if (dataTimer.value) clearInterval(dataTimer.value)
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

.data-time {
  font-size: 18px;
  color: #00D4FF;
  margin-left: 15px;
  font-weight: normal;
  -webkit-text-fill-color: #00D4FF; /* 重置文字填充颜色 */
  text-shadow: none;
  vertical-align: middle;
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
