<template>
  <div class="message-wrapper" :class="{ 'user-message': isUser, 'agent-message': !isUser }">
    <div class="avatar">
      <span v-if="isUser">👤</span>
      <span v-else>🤖</span>
    </div>
    <div class="message-content">
      <div class="message-header">
        <span class="name">{{ isUser ? 'User' : 'DeepSeek Agent' }}</span>
        <span class="time">{{ time }}</span>
      </div>
      <div class="message-text">{{ content }}</div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  isUser: {
    type: Boolean,
    default: false
  },
  content: {
    type: String,
    required: true
  },
  time: {
    type: String,
    default: ''
  }
})
</script>

<style scoped>
.message-wrapper {
  display: flex;
  gap: 15px;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 15px;
  max-width: 80%;
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.user-message {
  align-self: flex-end;
  flex-direction: row-reverse;
  background: rgba(74, 158, 255, 0.1);
  border: 1px solid rgba(74, 158, 255, 0.3);
}

.agent-message {
  align-self: flex-start;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.message-content {
  display: flex;
  flex-direction: column;
  gap: 5px;
  max-width: calc(100% - 60px);
}

.message-header {
  display: flex;
  gap: 10px;
  align-items: center;
  font-size: 0.85em;
  color: rgba(255, 255, 255, 0.6);
}

.user-message .message-header {
  flex-direction: row-reverse;
}

.message-text {
  line-height: 1.6;
  color: #fff;
  white-space: pre-wrap;
  word-break: break-word;
}
</style>
