<template>
  <div class="result-list-card">
    <div class="card-header">
      <div class="header-left">
        <h3>📋 检索结果</h3>
        <span v-if="total > 0" class="result-count">共找到 <strong>{{ total }}</strong> 条记录</span>
      </div>
      <div class="header-right">
        <button class="btn-export" :disabled="total === 0" @click="$emit('export')">
          <span class="icon">📥</span> 导出数据
        </button>
      </div>
    </div>

    <div class="table-container">
      <table v-if="data.length > 0">
        <thead>
          <tr>
            <th>序号</th>
            <th>车牌号码</th>
            <th>车辆类型</th>
            <th>过车时间</th>
            <th>行政区划</th>
            <th>道路卡口</th>
            <th>边界级别</th>
            <th>方向</th>
            <th>品牌</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, index) in data" :key="index">
            <td>{{ (currentPage - 1) * pageSize + index + 1 }}</td>
            <td class="plate-col">{{ item.HPHM }}</td>
            <td>{{ item.HPZL_LABEL }}</td>
            <td class="time-col">{{ item.GCSJ }}</td>
            <td>{{ item.XZQHMC }}</td>
            <td>{{ item.CLEAN_KKMC }}</td>
            <td>
              <span :class="['tag', item.BOUNDARY_LEVEL === 'PROVINCE' ? 'prov' : 'city']">
                {{ item.BOUNDARY_LEVEL === 'PROVINCE' ? '省际' : '市际' }}
              </span>
            </td>
            <td>{{ item.FXLX == '1' ? '进入' : '离开' }}</td>
            <td>{{ item.BRAND || '-' }}</td>
            <td>
              <button class="btn-link" @click="$emit('view', item)">详情</button>
            </td>
          </tr>
        </tbody>
      </table>
      
      <div v-else class="empty-state">
        <div class="empty-icon">📭</div>
        <p>暂无数据，请调整查询条件</p>
      </div>
    </div>

    <div v-if="total > 0" class="pagination">
      <button 
        class="page-btn" 
        :disabled="currentPage === 1"
        @click="$emit('page-change', currentPage - 1)"
      >上一页</button>
      <span class="page-info">第 {{ currentPage }} 页 / 共 {{ Math.ceil(total / pageSize) }} 页</span>
      <button 
        class="page-btn" 
        :disabled="currentPage >= Math.ceil(total / pageSize)"
        @click="$emit('page-change', currentPage + 1)"
      >下一页</button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  data: {
    type: Array,
    default: () => []
  },
  total: {
    type: Number,
    default: 0
  },
  currentPage: {
    type: Number,
    default: 1
  },
  pageSize: {
    type: Number,
    default: 20
  }
})

defineEmits(['page-change', 'export', 'view'])
</script>

<style scoped>
.result-list-card {
  background: rgba(10, 15, 45, 0.3);
  border: 1px solid rgba(74, 158, 255, 0.2);
  border-radius: 8px;
  padding: 20px;
  color: #fff;
  display: flex;
  flex-direction: column;
  height: 100%; /* Ensure it takes full height of parent */
  min-height: 400px; /* Minimum height to ensure visibility */
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  color: #4A9EFF;
}

.result-count {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
}

.result-count strong {
  color: #00D4FF;
  font-size: 16px;
}

.btn-export {
  background: rgba(16, 185, 129, 0.2);
  border: 1px solid rgba(16, 185, 129, 0.5);
  color: #10b981;
  padding: 6px 15px;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: all 0.3s;
}

.btn-export:hover:not(:disabled) {
  background: rgba(16, 185, 129, 0.4);
}

.btn-export:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.table-container {
  flex: 1;
  overflow: auto;
  border: 1px solid rgba(74, 158, 255, 0.1);
  border-radius: 4px;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

thead {
  background: #0e1638; /* Solid background color to prevent overlap transparency issues */
  position: sticky;
  top: 0;
  z-index: 10;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

th {
  padding: 12px;
  text-align: left;
  color: #4A9EFF;
  font-weight: bold;
}

td {
  padding: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.8);
}

tr:hover {
  background: rgba(74, 158, 255, 0.05);
}

.plate-col {
  color: #00D4FF;
  font-weight: bold;
  font-family: monospace;
}

.time-col {
  font-family: monospace;
}

.tag {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.tag.prov {
  background: rgba(255, 77, 79, 0.2);
  color: #ff4d4f;
  border: 1px solid rgba(255, 77, 79, 0.3);
}

.tag.city {
  background: rgba(82, 196, 26, 0.2);
  color: #52c41a;
  border: 1px solid rgba(82, 196, 26, 0.3);
}

.btn-link {
  background: none;
  border: none;
  color: #4A9EFF;
  cursor: pointer;
  text-decoration: underline;
}

.btn-link:hover {
  color: #00D4FF;
}

.empty-state {
  padding: 40px;
  text-align: center;
  color: rgba(255, 255, 255, 0.4);
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 10px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid rgba(74, 158, 255, 0.1);
}

.page-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #fff;
  padding: 5px 15px;
  border-radius: 4px;
  cursor: pointer;
}

.page-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.page-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.2);
}

.page-info {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
}
</style>