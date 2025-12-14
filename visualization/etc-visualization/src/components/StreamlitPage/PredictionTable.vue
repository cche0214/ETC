<template>
  <div class="table-card">
    <div class="table-header">
      <h3>📋 全网卡口实时预测详情</h3>
    </div>
    
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>卡口名称</th>
            <th>类型</th>
            <th>当前流量 (5min)</th>
            <th>预测流量 (下个5min)</th>
            <th>趋势</th>
            <th>变化量</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in filteredData" :key="item.name" :class="getRowClass(item)">
            <td class="name-col">{{ item.name }}</td>
            <td>
              <span :class="['tag', item.type === '省际' ? 'prov' : 'city']">
                {{ item.type }}
              </span>
            </td>
            <td class="num-col">{{ item.current }}</td>
            <td class="num-col pred-col">{{ item.prediction }}</td>
            <td class="trend-col">
              <span :class="getTrendClass(item.diff)">
                {{ getTrendIcon(item.diff) }}
              </span>
            </td>
            <td :class="getTrendClass(item.diff)">
              {{ item.diff > 0 ? '+' : '' }}{{ item.diff }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  }
})

const searchQuery = ref('')

const filteredData = computed(() => {
  if (!searchQuery.value) return props.data
  return props.data.filter(item => 
    item.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

const getTrendClass = (diff) => {
  if (diff > 0) return 'up'
  if (diff < 0) return 'down'
  return 'flat'
}

const getTrendIcon = (diff) => {
  if (diff > 0) return '↗ 上升'
  if (diff < 0) return '↘ 下降'
  return '- 持平'
}

const getRowClass = (item) => {
  // 简单的拥堵预警逻辑
  if (item.prediction > 100) return 'warning-row'
  return ''
}
</script>

<style scoped>
.table-card {
  background: rgba(6, 30, 93, 0.5);
  border: 1px solid rgba(74, 158, 255, 0.2);
  border-radius: 8px;
  padding: 15px;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

h3 {
  color: #fff;
  margin: 0;
  font-size: 16px;
}

.search-box input {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid #4A9EFF;
  color: #fff;
  padding: 5px 10px;
  border-radius: 4px;
  outline: none;
}

.table-container {
  flex: 1;
  overflow-y: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  color: #fff;
  font-size: 14px;
}

th {
  text-align: left;
  padding: 10px;
  background: #0a0f2d; /* 使用纯色背景，完全遮挡下方内容 */
  color: #4A9EFF;
  position: sticky;
  top: 0;
  z-index: 20; /* 提高层级 */
  box-shadow: 0 2px 5px rgba(0,0,0,0.5);
}

td {
  padding: 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.name-col {
  font-weight: bold;
}

.num-col {
  font-family: 'Courier New', monospace;
  font-size: 15px;
}

.pred-col {
  color: #faad14;
  font-weight: bold;
}

.tag {
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 12px;
}

.tag.prov {
  background: rgba(255, 77, 79, 0.2);
  color: #ff4d4f;
  border: 1px solid rgba(255, 77, 79, 0.5);
}

.tag.city {
  background: rgba(82, 196, 26, 0.2);
  color: #52c41a;
  border: 1px solid rgba(82, 196, 26, 0.5);
}

.up { color: #ff4d4f; }
.down { color: #52c41a; }
.flat { color: #aaa; }

/* 滚动条样式 */
.table-container::-webkit-scrollbar {
  width: 6px;
}
.table-container::-webkit-scrollbar-thumb {
  background: rgba(74, 158, 255, 0.3);
  border-radius: 3px;
}
</style>
