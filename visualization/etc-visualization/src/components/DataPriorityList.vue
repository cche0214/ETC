<template>
  <div class="data-priority-card">
    <!-- DEBUG INFO -->
    <div style="background: rgba(0,0,0,0.8); color: #0f0; padding: 5px; font-size: 10px; max-height: 100px; overflow: auto; position: absolute; top: 0; left: 0; width: 100%; z-index: 1000;">
      DEBUG: Count={{ dataList.length }} <br>
      First={{ JSON.stringify(dataList[0]) }}
    </div>
    <div class="card-header">
      <div class="header-line"></div>
      <h3>套牌车实时报警监控</h3>
      <div class="header-line"></div>
    </div>
    <div class="list-container">
      <div 
        v-for="(item, index) in dataList" 
        :key="index"
        class="list-item high-priority"
      >
        <div class="item-number">{{ index + 1 }}</div>
        <div class="item-content">
          <div class="item-header">
            <span class="item-title">车牌：{{ item.plate || '未知车牌' }}</span>
            <span class="item-time">{{ item.time }}</span>
          </div>
          <div class="item-detail">
            <div class="location-flow">
              <span class="loc">{{ item.loc1 || '未知点位' }}</span>
              <span class="arrow">→</span>
              <span class="loc">{{ item.loc2 || '未知点位' }}</span>
            </div>
          </div>
          <div class="item-footer">
            <span class="item-msg" :title="item.msg">{{ item.msg || '疑似套牌' }}</span>
          </div>
        </div>
      </div>
      <div v-if="dataList.length === 0" class="no-data">
        暂无报警数据
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { getDeckedVehicles } from '../api/dashboard'

const dataList = ref([
  // 模拟数据，匹配真实数据结构
  {
    msg: "套牌嫌疑: 10分钟内跨越不可达距离",
    loc2: "S323-K10-市际卡口",
    loc1: "S250-K1-省际卡口",
    plate: "鲁Q66***",
    time: "2025-12-09 17:05:00"
  },
  {
    msg: "套牌嫌疑: 5分钟内出现于两地",
    loc2: "G104-K873-省际卡口",
    loc1: "G3-K731-省际卡口",
    plate: "粤B88***",
    time: "2025-12-09 17:02:30"
  }
])
let timer = null

const fetchData = async () => {
  try {
    const res = await getDeckedVehicles()
    console.log('Decked Vehicles API Response:', res)
    if (res.code === 200 && res.data) {
      dataList.value = res.data
    }
  } catch (error) {
    console.error('获取报警数据失败:', error)
  }
}

onMounted(() => {
  fetchData()
  timer = setInterval(fetchData, 5000) // 5秒刷新一次
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
.data-priority-card {
  position: relative;
  background: rgba(10, 15, 45, 0.5);
  border: 1px solid rgba(74, 158, 255, 0.2);
  border-radius: 8px;
  padding: 10px;
  box-sizing: border-box;
  height: 100%;
  display: flex;
  flex-direction: column;
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
}

.list-container {
  flex: 1;
  overflow-y: auto;
  padding-right: 5px;
}

/* 滚动条样式 */
.list-container::-webkit-scrollbar {
  width: 4px;
}
.list-container::-webkit-scrollbar-thumb {
  background: rgba(74, 158, 255, 0.3);
  border-radius: 2px;
}
.list-container::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.1);
}

.list-item {
  display: flex;
  margin-bottom: 10px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
  border-left: 3px solid transparent;
  transition: all 0.3s;
}

.list-item:hover {
  background: rgba(255, 255, 255, 0.1);
}

.high-priority {
  border-left-color: #FF6B6B;
  background: linear-gradient(90deg, rgba(255, 107, 107, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
}

.item-number {
  width: 24px;
  height: 24px;
  background: rgba(74, 158, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 10px;
  font-size: 12px;
  color: #4A9EFF;
  flex-shrink: 0;
}

.high-priority .item-number {
  background: rgba(255, 107, 107, 0.2);
  color: #FF6B6B;
}

.item-content {
  flex: 1;
  min-width: 0;
}

.item-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
}

.item-title {
  font-size: 14px;
  color: #fff;
  font-weight: bold;
}

.item-time {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

.item-detail {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 5px;
}

.location-flow {
  display: flex;
  align-items: center;
  gap: 5px;
  color: rgba(255, 255, 255, 0.9);
}

.arrow {
  color: #FF6B6B;
  font-weight: bold;
}

.loc {
  background: rgba(74, 158, 255, 0.1);
  padding: 2px 4px;
  border-radius: 2px;
  font-size: 11px;
}

.item-footer {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
}

.item-msg {
  color: #FF6B6B;
  font-size: 11px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.no-data {
  text-align: center;
  color: rgba(255, 255, 255, 0.5);
  padding: 20px;
  font-size: 14px;
}
</style>
