<template>
  <div class="dashboard">
    <header class="header">
      <div class="header-bg"></div>
      <h1 class="header-title">大数据存储平台交通监控</h1>
      <div class="header-time">{{ currentTime }}</div>
    </header>

    <div class="container">
      <!-- 左侧区域 -->
      <div class="left-column">
        <div class="section data-overview-section">
          <!-- <data-overview ref="dataOverviewRef" /> -->
        </div>
        <div class="section exit-station-section">
          <!-- <exit-station-pie ref="exitStationRef" /> -->
        </div>
        <div class="section vehicle-congestion-section">
          <!-- 交换位置：将套牌车报警列表移到左下角 -->
          <data-priority-list ref="dataListRef" />
        </div>
      </div>

      <!-- 中间区域 -->
      <div class="center-column">
        <div class="section map-section">
          <!-- <flow-map ref="flowMapRef" /> -->
        </div>
        <div class="section hourly-flow-section">
          <!-- <hourly-flow3d ref="hourlyFlowRef" /> -->
        </div>
      </div>

      <!-- 右侧区域 -->
      <div class="right-column">
        <div class="section trend-section">
          <realtime-flow-chart ref="trendChartRef" />
        </div>
        <div class="section vehicle-type-section">
          <vehicle-type-bar ref="vehicleTypeRef" />
        </div>
        <div class="section data-list-section">
          <!-- 交换位置：将拥堵指数移到右下角 -->
          <!-- <vehicle-congestion ref="vehicleCongestionRef" /> -->
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import DataOverview from '../components/DataOverview.vue'
import ExitStationPie from '../components/ExitStationPie.vue'
import FlowMap from '../components/FlowMap.vue'
import VehicleCongestion from '../components/VehicleCongestion.vue'
import HourlyFlow3D from '../components/HourlyFlow3D.vue'
import RealtimeFlowChart from '../components/RealtimeFlowChart.vue'
import VehicleTypeBar from '../components/VehicleTypeBar.vue'
import DataPriorityList from '../components/DataPriorityList.vue'

const currentTime = ref('')

// 组件引用
const dataOverviewRef = ref(null)
const exitStationRef = ref(null)
const flowMapRef = ref(null)
const vehicleCongestionRef = ref(null)
const hourlyFlowRef = ref(null)
const trendChartRef = ref(null)
const vehicleTypeRef = ref(null)
const dataListRef = ref(null)

function updateTime() {
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

// 模拟数据刷新（实际使用时替换为真实API调用）
const refreshData = () => {
  // 这里可以调用各个组件的updateData方法更新数据
  // 例如：
  // dataOverviewRef.value?.updateData(newData)
  // exitStationRef.value?.updateData(newData)
  console.log('数据刷新中...')
}

let timeInterval = null
let dataInterval = null

onMounted(() => {
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
  dataInterval = setInterval(refreshData, 30000) // 每30秒刷新一次数据
})

onUnmounted(() => {
  if (timeInterval) clearInterval(timeInterval)
  if (dataInterval) clearInterval(dataInterval)
})
</script>

<style scoped>
.dashboard {
  width: 100%;
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

.container {
  flex: 1;
  display: grid;
  grid-template-columns: 420px 1fr 420px;
  gap: 15px;
  padding: 15px;
  min-height: 0;
  overflow: hidden;
}

.left-column,
.center-column,
.right-column {
  display: flex;
  flex-direction: column;
  gap: 15px;
  min-height: 0;
}

.section {
  display: flex;
  flex-direction: column;
  min-height: 0;
}

/* 左侧布局 */
.data-overview-section {
  flex: 0 0 240px;
}

.exit-station-section {
  flex: 0 0 280px;
}

.vehicle-congestion-section {
  flex: 1;
  min-height: 0;
}

/* 中间布局 */
.map-section {
  flex: 1;
  min-height: 0;
}

.hourly-flow-section {
  flex: 0 0 350px;
}

/* 右侧布局 */
.trend-section {
  flex: 0 0 280px;
}

.vehicle-type-section {
  flex: 0 0 320px;
}

.data-list-section {
  flex: 1;
  min-height: 0;
}

/* 响应式设计 */
@media (max-width: 1600px) {
  .container {
    grid-template-columns: 360px 1fr 360px;
  }
  
  .header-title {
    font-size: 28px;
  }
}

@media (max-width: 1400px) {
  .container {
    grid-template-columns: 320px 1fr 320px;
    gap: 10px;
    padding: 10px;
  }
}
</style>
