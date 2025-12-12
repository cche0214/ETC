<template>
  <div class="realtime-traffic-list">
    <div class="card-header">
      <div class="header-line"></div>
      <h3>实时过车明细</h3>
      <div class="header-line"></div>
    </div>
    
    <div class="list-header">
      <span class="col-time">时间</span>
      <span class="col-plate">车牌号</span>
      <span class="col-brand">品牌</span>
      <span class="col-station">卡口名称</span>
      <span class="col-direction">方向</span>
      <span class="col-type">车型</span>
    </div>

    <div class="list-container" ref="listContainer">
      <div class="scroll-wrapper" :class="{ 'animating': isAnimating }" :style="{ transform: `translateY(-${scrollOffset}px)` }">
        <div v-for="(item, index) in displayList" :key="item.rowkey || index" class="list-item" :class="{ 'new-item': index < newCount }">
          <span class="col-time">{{ formatTime(item.GCSJ) }}</span>
          <span class="col-plate" :class="getPlateClass(item.HPZL_LABEL)">{{ item.HPHM }}</span>
          <span class="col-brand">{{ item.BRAND || '-' }}</span>
          <span class="col-station" :title="item.CLEAN_KKMC">{{ item.CLEAN_KKMC }}</span>
          <span class="col-direction">{{ item.FXLX || '-' }}</span>
          <span class="col-type">{{ item.HPZL_LABEL || '未知' }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, defineExpose, computed } from 'vue'
import { getRealtimeTraffic } from '../api/dashboard'

const list = ref([])
const isAnimating = ref(false)
const scrollOffset = ref(0)
const newCount = ref(0) // 标记新数据的数量，用于高亮显示

// 格式化时间，只显示时分秒
const formatTime = (timeStr) => {
  if (!timeStr) return '--:--:--'
  // 假设格式为 "2023-12-01 10:00:00"
  return timeStr.split(' ')[1] || timeStr
}

// 根据车型返回不同的样式类
const getPlateClass = (type) => {
  if (type === '大型汽车') return 'plate-yellow'
  if (type === '小型汽车') return 'plate-blue'
  if (type === '新能源汽车') return 'plate-green'
  return 'plate-normal'
}

const fetchData = async () => {
  try {
    const res = await getRealtimeTraffic(20) // 获取最新的20条
    if (res.status === 'success' && res.data && res.data.length > 0) {
      updateList(res.data)
    }
  } catch (error) {
    console.error('获取实时过车数据失败:', error)
  }
}

// 更新列表逻辑：模拟滚动效果
const updateList = (newData) => {
  if (list.value.length === 0) {
    list.value = newData
    return
  }

  // 找出真正的新数据（通过 rowkey 对比）
  const currentTopKey = list.value[0]?.rowkey
  const newItems = []
  
  for (const item of newData) {
    if (item.rowkey === currentTopKey) break
    newItems.push(item)
  }

  if (newItems.length > 0) {
    // 标记新数据数量
    newCount.value = newItems.length
    
    // 将新数据加到头部
    // 实际上为了动画效果，我们可能需要更复杂的处理，这里简化为直接替换
    // 为了视觉上的“流动”，我们可以先不高亮，等下次更新
    
    // 简单策略：直接更新列表，利用 Vue 的列表过渡（如果需要更平滑的滚动，需要 CSS 动画配合）
    // 这里采用一种“无缝滚动”的视觉欺骗：
    // 1. 列表保持不动
    // 2. 新数据插入顶部
    // 3. 列表瞬间向下偏移（translateY）
    // 4. 动画过渡回 0
    
    const oldList = [...list.value]
    // 保持总数不超过 50 条
    list.value = [...newItems, ...oldList].slice(0, 50)
  } else {
    newCount.value = 0
  }
}

// 自动滚动逻辑
// 既然是“实时流”，我们可以让它自动慢慢向上滚动，或者有新数据时向下挤压
// 这里实现一个自动向上缓慢滚动的效果，配合定时刷新数据
const autoScroll = () => {
  // 简单的自动滚动实现
  // 实际大屏中，通常是数据不动，有新数据时“顶”下来；或者列表一直在缓慢向上滚动
  // 根据用户需求“一条条上下滚动”，这里实现：有新数据时，新数据从顶部出现
}

defineExpose({
  updateData: fetchData
})

// 计算属性用于渲染，这里直接用 list
const displayList = computed(() => list.value)

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.realtime-traffic-list {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: rgba(10, 15, 45, 0.5);
  border: 1px solid rgba(74, 158, 255, 0.2);
  border-radius: 8px;
  padding: 10px;
  box-sizing: border-box;
  overflow: hidden;
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
  white-space: nowrap;
}

.list-header {
  display: flex;
  padding: 8px 10px;
  background: rgba(74, 158, 255, 0.1);
  color: #00D4FF;
  font-size: 12px;
  font-weight: bold;
  border-radius: 4px;
  margin-bottom: 5px;
}

.list-container {
  flex: 1;
  overflow: hidden; /* 隐藏滚动条 */
  position: relative;
}

.scroll-wrapper {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.list-item {
  display: flex;
  align-items: center;
  padding: 8px 10px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 4px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
  transition: all 0.5s ease;
}

.list-item:hover {
  background: rgba(255, 255, 255, 0.08);
}

/* 新数据高亮动画 */
.new-item {
  animation: flash 2s ease-out;
  background: rgba(74, 158, 255, 0.2);
}

@keyframes flash {
  0% { background: rgba(74, 158, 255, 0.5); }
  100% { background: rgba(255, 255, 255, 0.03); }
}

/* 列宽控制 */
.col-time { width: 70px; flex-shrink: 0; }
.col-plate { width: 90px; flex-shrink: 0; font-weight: bold; }
.col-brand { width: 60px; flex-shrink: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.col-station { flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; padding-right: 10px; }
.col-direction { width: 40px; flex-shrink: 0; text-align: center; }
.col-type { width: 60px; flex-shrink: 0; text-align: right; }

/* 车牌颜色样式 */
.plate-blue { color: #4A9EFF; text-shadow: 0 0 5px rgba(74, 158, 255, 0.5); }
.plate-yellow { color: #FFD56E; text-shadow: 0 0 5px rgba(255, 213, 110, 0.5); }
.plate-green { color: #67F9D8; text-shadow: 0 0 5px rgba(103, 249, 216, 0.5); }
.plate-normal { color: #fff; }

</style>