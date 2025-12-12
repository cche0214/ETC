<template>
  <div class="dashboard">
    <header class="header">
      <div class="header-bg"></div>
      <h1 class="header-title">江苏·徐州大数据实时交通监控平台</h1>
      <div class="header-time">{{ currentTime }}</div>
    </header>

    <div class="container">
      <!-- 左侧区域 -->
      <div class="left-column">
        <div class="section overview-section">
          <data-overview ref="overviewRef" />
        </div>
        <div class="section rose-section">
          <vehicle-type-rose ref="vehicleTypeRoseRef" />
        </div>
      </div>

      <!-- 中间区域 -->
      <div class="center-column">
        <div class="section map-section">
          <china-map />
        </div>
        <div class="section realtime-section" style="flex-basis: 200px;">
          <realtime-traffic-list ref="realtimeListRef" />
        </div>
      </div>

      <!-- 右侧区域 -->
      <div class="right-column">
        <div class="section vehicle-type-section">
          <vehicle-type-bar ref="vehicleTypeRef" />
        </div>
        <div class="section priority-list-section">
          <data-priority-list ref="dataListRef" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import VehicleTypeBar from '../components/VehicleTypeBar.vue'
import DataPriorityList from '../components/DataPriorityList.vue'
import DataOverview from '../components/DataOverview.vue'
import VehicleTypeRose from '../components/VehicleTypeRose.vue'
import RealtimeTrafficList from '../components/RealtimeTrafficList.vue'
import ChinaMap from '../components/ChinaMap.vue'

const currentTime = ref('')

// 组件引用
const vehicleTypeRef = ref(null)
const dataListRef = ref(null)
const overviewRef = ref(null)
const vehicleTypeRoseRef = ref(null)
const realtimeListRef = ref(null)

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
  if (vehicleTypeRef.value && vehicleTypeRef.value.updateData) {
    vehicleTypeRef.value.updateData()
  }
  if (dataListRef.value && dataListRef.value.updateData) {
    dataListRef.value.updateData()
  }
  if (overviewRef.value && overviewRef.value.updateData) {
    overviewRef.value.updateData()
  }
  if (vehicleTypeRoseRef.value && vehicleTypeRoseRef.value.updateData) {
    vehicleTypeRoseRef.value.updateData()
  }
  if (realtimeListRef.value && realtimeListRef.value.updateData) {
    realtimeListRef.value.updateData()
  }
}

let timeInterval = null
let dataInterval = null

onMounted(() => {
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
  // 初始加载一次数据
  setTimeout(refreshData, 500)
  dataInterval = setInterval(refreshData, 5000) // 每5秒刷新一次数据
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
.overview-section {
  flex: 0 0 320px; /* 增加高度以容纳三个数据项 */
}

.rose-section {
  flex: 1;
  min-height: 0;
}

/* 中间布局 */
.map-section {
  flex: 1; /* 占据大部分空间 */
  min-height: 0;
}

.realtime-section {
  flex: 0 0 260px; /* 底部较小空间用于实时列表 (约展示5-6条数据) */
  min-height: 0;
}

/* 右侧布局 */
.vehicle-type-section {
  flex: 0 0 350px; /* 调整高度 */
}

.priority-list-section {
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
