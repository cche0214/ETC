<template>
  <div class="chat-page">
    <!-- Header (Copied from Dashboard.vue) -->
    <header class="header">
      <div class="header-bg"></div>
      <button class="back-btn" @click="$router.push('/')">
        <span class="icon">←</span> 返回主页
      </button>
      <h1 class="header-title">智能交通助手 Agent</h1>
      <div class="header-time">{{ currentTime }}</div>
    </header>

    <div class="chat-container">
      <div class="messages-area" ref="messagesContainer">
        <div v-if="messages.length === 0" class="welcome-screen">
          <div class="logo">🤖</div>
          <h2>我是您的智能交通助手</h2>
          <p>我可以帮您分析交通数据、预测路况或回答相关问题。</p>
          <div class="suggestions">
            <button v-for="s in suggestions" :key="s" @click="handleSend(s)">{{ s }}</button>
          </div>
        </div>
        
        <chat-message 
          v-for="(msg, index) in messages" 
          :key="index"
          :is-user="msg.isUser"
          :content="msg.content"
          :time="msg.time"
        />
        
        <div v-if="isTyping" class="typing-indicator">
          <div class="dots">
            <span></span>
            <span></span>
            <span></span>
          </div>
          <span>Agent 正在思考...</span>
        </div>
      </div>
      
      <chat-input @send="handleSend" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import ChatMessage from '../components/ChatDeepseek/ChatMessage.vue'
import ChatInput from '../components/ChatDeepseek/ChatInput.vue'

const currentTime = ref('')
const messages = ref([])
const isTyping = ref(false)
const messagesContainer = ref(null)

const suggestions = [
  "分析当前徐州市交通拥堵情况",
  "预测未来一小时的路况",
  "显示今日车流量统计",
  "ETC数据异常检测"
]

// Time update logic (same as Dashboard)
function updateTime() {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  const weekDay = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][now.getDay()]
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  const seconds = String(now.getSeconds()).padStart(2, '0')
  
  currentTime.value = `${year}-${month}-${day} ${weekDay} ${hours}:${minutes}:${seconds}`
}

let timeInterval = null

onMounted(() => {
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
})

onUnmounted(() => {
  if (timeInterval) clearInterval(timeInterval)
})

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const handleSend = async (text) => {
  // Add user message
  messages.value.push({
    isUser: true,
    content: text,
    time: new Date().toLocaleTimeString()
  })
  scrollToBottom()
  
  // Simulate Agent response
  isTyping.value = true
  setTimeout(() => {
    isTyping.value = false
    messages.value.push({
      isUser: false,
      content: "这是一个静态演示页面。后期将接入真正的 DeepSeek Agent 接口来回答您的问题：\n\n" + text + "\n\n(目前仅为UI展示)",
      time: new Date().toLocaleTimeString()
    })
    scrollToBottom()
  }, 1500)
}
</script>

<style scoped>
.chat-page {
  width: 100%;
  height: 100vh;
  background: linear-gradient(135deg, #0a0f2d 0%, #1a1f3a 50%, #0a0f2d 100%);
  color: white;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Header styles copied from Dashboard.vue */
.header {
  position: relative;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(180deg, rgba(27, 42, 82, 0.8) 0%, rgba(27, 42, 82, 0.4) 100%);
  border-bottom: 2px solid rgba(74, 158, 255, 0.3);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  z-index: 10;
  flex-shrink: 0;
}

.header-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: url('data:image/svg+xml,<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg"><defs><pattern id="grid" width="50" height="50" patternUnits="userSpaceOnUse"><path d="M 50 0 L 0 0 0 50" fill="none" stroke="rgba(74,158,255,0.1)" stroke-width="1"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
  opacity: 0.3;
}

.header-title {
  position: relative;
  margin: 0;
  font-size: 32px;
  font-weight: bold;
  letter-spacing: 4px;
  background: linear-gradient(90deg, #4A9EFF 0%, #00D4FF 100%);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 0 0 30px rgba(74, 158, 255, 0.5);
}

.header-time {
  position: absolute;
  right: 30px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 16px;
  color: rgba(255, 255, 255, 0.8);
  font-family: 'Courier New', monospace;
}

.back-btn {
  position: absolute;
  left: 30px;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(74, 158, 255, 0.1);
  border: 1px solid rgba(74, 158, 255, 0.5);
  color: #4A9EFF;
  padding: 8px 20px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  border-radius: 4px;
  z-index: 20;
}

.back-btn:hover {
  background: rgba(74, 158, 255, 0.3);
  box-shadow: 0 0 15px rgba(74, 158, 255, 0.3);
  text-shadow: 0 0 5px rgba(74, 158, 255, 0.8);
}

/* Chat specific styles */
.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  scroll-behavior: smooth;
}

/* Custom Scrollbar */
.messages-area::-webkit-scrollbar {
  width: 8px;
}

.messages-area::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
}

.messages-area::-webkit-scrollbar-thumb {
  background: rgba(74, 158, 255, 0.3);
  border-radius: 4px;
}

.messages-area::-webkit-scrollbar-thumb:hover {
  background: rgba(74, 158, 255, 0.5);
}

.welcome-screen {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.8);
  gap: 20px;
  min-height: 400px;
}

.welcome-screen .logo {
  font-size: 80px;
  margin-bottom: 20px;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0% { transform: translateY(0px); }
  50% { transform: translateY(-20px); }
  100% { transform: translateY(0px); }
}

.welcome-screen h2 {
  font-size: 28px;
  margin: 0;
  background: linear-gradient(90deg, #fff, #4A9EFF);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.suggestions {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  margin-top: 30px;
  max-width: 600px;
  width: 100%;
}

.suggestions button {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(74, 158, 255, 0.3);
  color: rgba(255, 255, 255, 0.9);
  padding: 15px 20px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  text-align: left;
  font-size: 14px;
}

.suggestions button:hover {
  background: rgba(74, 158, 255, 0.2);
  border-color: #4A9EFF;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.typing-indicator {
  padding: 10px 20px;
  color: rgba(255, 255, 255, 0.5);
  font-style: italic;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.dots {
  display: flex;
  gap: 4px;
}

.dots span {
  width: 6px;
  height: 6px;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}

.dots span:nth-child(1) { animation-delay: -0.32s; }
.dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}
</style>
