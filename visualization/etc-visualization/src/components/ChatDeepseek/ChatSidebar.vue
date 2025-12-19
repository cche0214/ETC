<template>
  <div class="chat-sidebar">
    <div class="sidebar-header">
      <button class="new-chat-btn" @click="$emit('create-session')">
        <span class="plus-icon">+</span> 新建对话
      </button>
    </div>
    
    <div class="session-list">
      <div 
        v-for="session in sessions" 
        :key="session.id"
        class="session-item"
        :class="{ active: currentSessionId === session.id }"
        @click="$emit('select-session', session.id)"
      >
        <div class="session-icon">💬</div>
        <div class="session-info">
          <div class="session-title">{{ session.title || '新对话' }}</div>
          <div class="session-date">{{ formatDate(session.created_at) }}</div>
        </div>
        <button class="delete-btn" @click.stop="$emit('delete-session', session.id)">×</button>
      </div>
      
      <div v-if="sessions.length === 0" class="empty-tip">
        暂无历史会话
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  sessions: {
    type: Array,
    default: () => []
  },
  currentSessionId: {
    type: String,
    default: ''
  }
})

defineEmits(['create-session', 'select-session', 'delete-session'])

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}/${date.getDate()} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}
</script>

<style scoped>
.chat-sidebar {
  height: 100%;
  background: rgba(13, 20, 40, 0.6);
  border-right: 1px solid rgba(74, 158, 255, 0.1);
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid rgba(74, 158, 255, 0.1);
}

.new-chat-btn {
  width: 100%;
  padding: 12px;
  background: rgba(74, 158, 255, 0.1);
  border: 1px solid rgba(74, 158, 255, 0.3);
  color: #4A9EFF;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 14px;
  transition: all 0.3s;
}

.new-chat-btn:hover {
  background: rgba(74, 158, 255, 0.2);
  box-shadow: 0 0 10px rgba(74, 158, 255, 0.2);
}

.session-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.session-list::-webkit-scrollbar {
  width: 4px;
}

.session-list::-webkit-scrollbar-thumb {
  background: rgba(74, 158, 255, 0.2);
  border-radius: 2px;
}

.session-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 8px;
  border: 1px solid transparent;
  position: relative;
}

.session-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.session-item.active {
  background: rgba(74, 158, 255, 0.15);
  border-color: rgba(74, 158, 255, 0.3);
}

.session-icon {
  font-size: 18px;
}

.session-info {
  flex: 1;
  overflow: hidden;
}

.session-title {
  color: #fff;
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 4px;
}

.session-date {
  color: rgba(255, 255, 255, 0.4);
  font-size: 12px;
}

.delete-btn {
  opacity: 0;
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.4);
  font-size: 18px;
  cursor: pointer;
  padding: 4px;
  transition: all 0.2s;
}

.session-item:hover .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  color: #ff4a4a;
}

.empty-tip {
  text-align: center;
  color: rgba(255, 255, 255, 0.3);
  margin-top: 40px;
  font-size: 13px;
}
</style>
