<template>
  <div class="chat-input-container">
    <textarea 
      v-model="inputContent"
      class="input-textarea"
      placeholder="输入您的问题，按 Enter 发送，Shift + Enter 换行..."
      @keydown.enter.exact.prevent="handleSend"
      :disabled="disabled"
    ></textarea>
    <div class="input-actions">
      <button 
        class="send-btn" 
        :class="{ disabled: !inputContent.trim() || disabled }"
        @click="handleSend"
        :disabled="!inputContent.trim() || disabled"
      >
        <span v-if="disabled">发送中...</span>
        <span v-else>发送 🚀</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  disabled: Boolean
})

const emit = defineEmits(['send'])

const inputContent = ref('')

const handleSend = () => {
  if (props.disabled || !inputContent.value.trim()) return
  
  emit('send', inputContent.value)
  inputContent.value = ''
}
</script>

<style scoped>
.chat-input-container {
  padding: 20px;
  background: rgba(13, 20, 40, 0.8);
  border-top: 1px solid rgba(74, 158, 255, 0.2);
  position: relative;
}

.input-textarea {
  width: 98%;
  height: 80px;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(74, 158, 255, 0.3);
  border-radius: 8px;
  color: white;
  padding: 12px;
  font-size: 14px;
  resize: none;
  outline: none;
  transition: all 0.3s;
  font-family: inherit;
}

.input-textarea:focus {
  border-color: #4A9EFF;
  box-shadow: 0 0 15px rgba(74, 158, 255, 0.1);
  background: rgba(0, 0, 0, 0.4);
}

.input-textarea:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.input-actions {
  position: absolute;
  bottom: 40px;
  right: 30px;
}

.send-btn {
  background: linear-gradient(90deg, #4A9EFF 0%, #00D4FF 100%);
  color: white;
  border: none;
  padding: 8px 20px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 13px;
  font-weight: bold;
  transition: all 0.3s;
  box-shadow: 0 4px 10px rgba(74, 158, 255, 0.3);
}

.send-btn:hover:not(.disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(74, 158, 255, 0.4);
}

.send-btn.disabled {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.3);
  cursor: not-allowed;
  box-shadow: none;
}
</style>

