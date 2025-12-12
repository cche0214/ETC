<template>
  <div class="overview-card">
    <div class="card-header">
      <div class="header-line"></div>
      <h3>实时车流总览</h3>
      <div class="header-line"></div>
    </div>
    
    <div class="data-container">
      <!-- 总车流量 -->
      <div class="data-item total">
        <div class="item-icon">
          <div class="icon-inner"></div>
        </div>
        <div class="item-content">
          <div class="item-label">总车流量</div>
          <div class="item-value">{{ formatNumber(data.total) }}</div>
        </div>
      </div>

      <!-- 入徐车流 -->
      <div class="data-item inbound">
        <div class="item-icon">
          <div class="icon-inner"></div>
        </div>
        <div class="item-content">
          <div class="item-label">入徐车流</div>
          <div class="item-value">{{ formatNumber(data.inbound) }}</div>
        </div>
      </div>

      <!-- 离徐车流 -->
      <div class="data-item outbound">
        <div class="item-icon">
          <div class="icon-inner"></div>
        </div>
        <div class="item-content">
          <div class="item-label">离徐车流</div>
          <div class="item-value">{{ formatNumber(data.outbound) }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, defineExpose, onMounted } from 'vue'
import { getOverview } from '../api/dashboard'

const data = reactive({
  total: 0,
  inbound: 0,
  outbound: 0
})

const formatNumber = (num) => {
  return num ? num.toLocaleString() : '0'
}

const fetchData = async () => {
  try {
    const res = await getOverview()
    if (res.code === 200 || res.status === 'success') {
      // 兼容不同的字段名
      data.total = res.data.total_records || res.data.total || 0
      data.inbound = res.data.traffic_in || res.data.inbound || 0
      data.outbound = res.data.traffic_out || res.data.outbound || 0
    }
  } catch (error) {
    console.error('获取数据总览失败:', error)
  }
}

defineExpose({
  updateData: fetchData
})

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.overview-card {
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
  margin-bottom: 15px;
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

.data-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-around;
  padding: 0 10px;
}

.data-item {
  display: flex;
  align-items: center;
  padding: 10px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 6px;
  transition: all 0.3s ease;
}

.data-item:hover {
  background: rgba(255, 255, 255, 0.08);
  transform: translateX(5px);
}

.item-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  background: rgba(0, 0, 0, 0.2);
}

.icon-inner {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.item-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.item-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 4px;
}

.item-value {
  font-size: 24px;
  font-weight: bold;
  font-family: 'DIN Alternate', 'Arial', sans-serif;
  letter-spacing: 1px;
}

/* 颜色主题 */
.total .item-icon { border: 1px solid rgba(74, 158, 255, 0.5); }
.total .icon-inner { background: #4A9EFF; box-shadow: 0 0 10px #4A9EFF; }
.total .item-value { color: #4A9EFF; text-shadow: 0 0 10px rgba(74, 158, 255, 0.3); }

.inbound .item-icon { border: 1px solid rgba(255, 213, 110, 0.5); }
.inbound .icon-inner { background: #FFD56E; box-shadow: 0 0 10px #FFD56E; }
.inbound .item-value { color: #FFD56E; text-shadow: 0 0 10px rgba(255, 213, 110, 0.3); }

.outbound .item-icon { border: 1px solid rgba(103, 249, 216, 0.5); }
.outbound .icon-inner { background: #67F9D8; box-shadow: 0 0 10px #67F9D8; }
.outbound .item-value { color: #67F9D8; text-shadow: 0 0 10px rgba(103, 249, 216, 0.3); }
</style>
