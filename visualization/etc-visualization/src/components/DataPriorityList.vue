<template>
  <div class="data-priority-card">
    <div class="card-header">
      <div class="header-line"></div>
      <h3>数据优先级</h3>
      <div class="header-line"></div>
    </div>
    <div class="list-container">
      <div 
        v-for="(item, index) in dataList" 
        :key="index"
        class="list-item"
        :class="{ 'high-priority': item.priority === 'high', 'normal': item.priority === 'normal' }"
      >
        <div class="item-number">{{ index + 1 }}</div>
        <div class="item-content">
          <div class="item-header">
            <span class="item-title">站口名称：{{ item.station }}</span>
            <span class="item-time">交易日期：{{ item.date }}</span>
          </div>
          <div class="item-detail">
            <span>地址：{{ item.address }}</span>
          </div>
          <div class="item-footer">
            <span class="item-manager">监督管理：{{ item.manager }}</span>
            <span class="item-status" :class="item.statusClass">{{ item.status }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// 模拟数据
const dataList = ref([
  {
    station: '松山湖出口',
    date: '2023-01-02 13:48:01',
    address: '东莞 松山湖',
    manager: '法通公路',
    status: '已上报',
    statusClass: 'status-reported',
    priority: 'high'
  },
  {
    station: '石龙出口东向',
    date: '2023-01-02 13:48:01',
    address: '东莞 石龙',
    manager: '法通公路',
    status: '法通公路',
    statusClass: 'status-normal',
    priority: 'normal'
  },
  {
    station: '石龙出口西',
    date: '2023-01-02 13:48:01',
    address: '东莞',
    manager: '正常',
    status: '正常',
    statusClass: 'status-ok',
    priority: 'normal'
  }
])

const updateData = (newData) => {
  if (newData) {
    dataList.value = newData
  }
}

defineExpose({ updateData })
</script>

<style scoped>
.data-priority-card {
  background: rgba(27, 42, 82, 0.6);
  border: 1px solid rgba(74, 158, 255, 0.3);
  border-radius: 8px;
  padding: 20px;
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  height: 100%;
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  gap: 10px;
}

.header-line {
  flex: 1;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(74, 158, 255, 0.5), transparent);
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  color: #4A9EFF;
  white-space: nowrap;
  letter-spacing: 2px;
}

.list-container {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.list-container::-webkit-scrollbar {
  width: 6px;
}

.list-container::-webkit-scrollbar-track {
  background: rgba(74, 158, 255, 0.1);
  border-radius: 3px;
}

.list-container::-webkit-scrollbar-thumb {
  background: rgba(74, 158, 255, 0.3);
  border-radius: 3px;
}

.list-container::-webkit-scrollbar-thumb:hover {
  background: rgba(74, 158, 255, 0.5);
}

.list-item {
  background: rgba(10, 15, 45, 0.6);
  border: 1px solid rgba(74, 158, 255, 0.2);
  border-radius: 6px;
  padding: 12px;
  display: flex;
  gap: 12px;
  transition: all 0.3s ease;
  border-left: 3px solid rgba(74, 158, 255, 0.5);
}

.list-item.high-priority {
  border-left-color: #FFB800;
  background: rgba(255, 184, 0, 0.05);
}

.list-item:hover {
  border-color: rgba(74, 158, 255, 0.6);
  transform: translateX(5px);
  box-shadow: 0 2px 10px rgba(74, 158, 255, 0.2);
}

.item-number {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 28px;
  height: 28px;
  background: linear-gradient(135deg, #4A9EFF, #00D4FF);
  border-radius: 50%;
  color: #fff;
  font-size: 14px;
  font-weight: bold;
}

.item-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.item-title {
  color: #00D4FF;
  font-size: 14px;
  font-weight: 500;
}

.item-time {
  color: rgba(255, 255, 255, 0.6);
  font-size: 12px;
}

.item-detail {
  color: rgba(255, 255, 255, 0.7);
  font-size: 12px;
}

.item-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.item-manager {
  color: rgba(255, 255, 255, 0.7);
  font-size: 12px;
}

.item-status {
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
}

.status-reported {
  background: rgba(255, 184, 0, 0.2);
  color: #FFB800;
  border: 1px solid rgba(255, 184, 0, 0.3);
}

.status-normal {
  background: rgba(74, 158, 255, 0.2);
  color: #4A9EFF;
  border: 1px solid rgba(74, 158, 255, 0.3);
}

.status-ok {
  background: rgba(0, 255, 136, 0.2);
  color: #00FF88;
  border: 1px solid rgba(0, 255, 136, 0.3);
}
</style>
