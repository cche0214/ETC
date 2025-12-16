<template>
  <div class="chat-input-container">
    <div class="input-wrapper">
      <textarea 
        v-model="inputValue" 
        placeholder="输入您的问题..." 
        @keydown.enter.prevent="handleEnter"
        rows="1"
        ref="textareaRef"
      ></textarea>
      <button class="send-btn" @click="sendMessage" :disabled="!inputValue.trim()">
        <span>➤</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'

const emit = defineEmits(['send'])
const inputValue = ref('')
const textareaRef = ref(null)

const handleEnter = (e) => {
  if (!e.shiftKey) {
    sendMessage()
  } else {
    // Allow shift+enter for new line, but we need to manually adjust height
    // Actually textarea default behavior handles newline, we just need to adjust height
    // But since we prevented default, we need to insert newline manually if we want to support it
    // For simplicity in this chat interface, let's just send on Enter
    // If we want shift+enter, we should remove .prevent and check in handler
    // But here let's stick to simple send on Enter
  }
}

const sendMessage = () => {
  if (!inputValue.value.trim()) return
  emit('send', inputValue.value)
  inputValue.value = ''
  adjustHeight()
}

const adjustHeight = () => {
  const textarea = textareaRef.value
  if (textarea) {
    textarea.style.height = 'auto'
    textarea.style.height = Math.min(textarea.scrollHeight, 150) + 'px'
  }
}

watch(inputValue, () => {
  nextTick(adjustHeight)
})
</script>

<style scoped>
.chat-input-container {
  padding: 20px;
  background: rgba(10, 15, 45, 0.9);
  border-top: 1px solid rgba(74, 158, 255, 0.3);
  backdrop-filter: blur(10px);
}

.input-wrapper {
  max-width: 800px;
  margin: 0 auto;
  position: relative;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(74, 158, 255, 0.3);
  border-radius: 12px;
  padding: 10px 15px;
  display: flex;
  align-items: flex-end;
  gap: 10px;
  transition: all 0.3s;
}

.input-wrapper:focus-within {
  border-color: #4A9EFF;
  box-shadow: 0 0 15px rgba(74, 158, 255, 0.2);
  background: rgba(255, 255, 255, 0.08);
}

textarea {
  flex: 1;
  background: transparent;
  border: none;
  color: white;
  font-size: 16px;
  resize: none;
  outline: none;
  padding: 8px 0;
  max-height: 150px;
  font-family: inherit;
  line-height: 1.5;
}

textarea::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.send-btn {
  background: #4A9EFF;
  border: none;
  border-radius: 8px;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
  color: white;
  flex-shrink: 0;
}

.send-btn:hover:not(:disabled) {
  background: #00D4FF;
  transform: scale(1.05);
  box-shadow: 0 0 10px rgba(74, 158, 255, 0.5);
}

.send-btn:disabled {
  background: rgba(255, 255, 255, 0.1);
  cursor: not-allowed;
  color: rgba(255, 255, 255, 0.3);
}
</style>
