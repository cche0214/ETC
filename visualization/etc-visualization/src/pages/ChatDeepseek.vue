<template>
  <div class="dashboard chat-page">
    <header class="header">
      <div class="header-bg"></div>
      <button class="back-btn" @click="$router.push('/')">
        <span class="icon">←</span> 返回主页
      </button>
      <h1 class="header-title">ETC 智能交通助手</h1>
      <div class="header-time">{{ currentTime }}</div>
    </header>

    <div class="main-container">
      <div class="content-wrapper">
        <!-- 左侧边栏：会话列表 -->
        <div class="sidebar-wrapper">
          <chat-sidebar 
            :sessions="sessions"
            :current-session-id="currentSessionId"
            @create-session="handleCreateSession"
            @select-session="handleSelectSession"
            @delete-session="handleDeleteSession"
          />
        </div>

        <!-- 右侧主窗口：对话界面 -->
        <div class="chat-wrapper">
          <chat-window 
            :messages="currentMessages"
            :loading="loading"
            :streaming-content="streamingContent"
            :streaming-thought="streamingThought"
            @send-message="handleSendMessage"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import ChatSidebar from '../components/ChatDeepseek/ChatSidebar.vue'
import ChatWindow from '../components/ChatDeepseek/ChatWindow.vue'
import { getSessions, createSession, getSession, streamMessage, deleteSession } from '../api/ai'

const currentTime = ref('')
const sessions = ref([])
const currentSessionId = ref('')
const currentMessages = ref([])
const loading = ref(false)

// 流式状态
const streamingContent = ref('')
const streamingThought = ref('')

// 时间更新
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

// 加载会话列表
const loadSessions = async () => {
  try {
    const res = await getSessions()
    sessions.value = res || []
    
    // 如果没有选中会话但有列表，默认选中第一个
    if (!currentSessionId.value && sessions.value.length > 0) {
      handleSelectSession(sessions.value[0].id)
    }
  } catch (error) {
    console.error('Failed to load sessions:', error)
  }
}

// 创建新会话
const handleCreateSession = async () => {
  try {
    const newSession = await createSession()
    sessions.value.unshift(newSession)
    currentSessionId.value = newSession.id
    currentMessages.value = []
    streamingContent.value = ''
    streamingThought.value = ''
  } catch (error) {
    console.error('Failed to create session:', error)
  }
}

// 选择会话
const handleSelectSession = async (sessionId) => {
  currentSessionId.value = sessionId
  streamingContent.value = ''
  streamingThought.value = ''
  
  try {
    const sessionDetail = await getSession(sessionId)
    currentMessages.value = sessionDetail.messages || []
  } catch (error) {
    console.error('Failed to load session detail:', error)
    currentMessages.value = []
  }
}

// 删除会话
const handleDeleteSession = async (sessionId) => {
  if (!confirm('确定要删除这个会话吗？')) return
  try {
    await deleteSession(sessionId)
    sessions.value = sessions.value.filter(s => s.id !== sessionId)
    if (currentSessionId.value === sessionId) {
      currentSessionId.value = ''
      currentMessages.value = []
      streamingContent.value = ''
      streamingThought.value = ''
      if (sessions.value.length > 0) {
        handleSelectSession(sessions.value[0].id)
      }
    }
  } catch (error) {
    console.error('Failed to delete session:', error)
  }
}

// 发送消息
const handleSendMessage = async (content) => {
  if (!currentSessionId.value) {
    await handleCreateSession()
  }

  // 1. 立即显示用户消息
  const userMsg = {
    role: 'user',
    content: content,
    created_at: new Date().toISOString()
  }
  currentMessages.value.push(userMsg)
  
  loading.value = true
  streamingContent.value = ''
  streamingThought.value = ''

  try {
    // 2. 调用流式接口
    await streamMessage(currentSessionId.value, content, (type, text) => {
        // 回调处理
        if (type === 'thought') {
            // 如果是思考过程，更新思考变量
            // 注意：有时候思考过程是分段送来的，这里简单处理为直接显示最新状态
            // 或者累加。根据后端实现，yield "🤖 正在思考..." 是完整的句子，不是增量字符。
            // 后端 api.py: yield "🤖 正在思考: ...\n"
            // 我们直接赋值或换行追加
            streamingThought.value = text 
        } else if (type === 'message') {
            // 消息正文是 token 流，需要累加
            streamingContent.value += text
        } else if (type === 'error') {
            // 错误信息也显示在正文里
            streamingContent.value += `\n\n**${text}**`
        }
    })
    
    // 3. 结束后，重新获取完整消息列表（确保一致性）
    // 或者直接把 streamingContent 转为一条 message push 进去
    const sessionDetail = await getSession(currentSessionId.value)
    currentMessages.value = sessionDetail.messages || []
    
  } catch (error) {
    console.error('Failed to send message:', error)
    currentMessages.value.push({
      role: 'assistant',
      content: '⚠️ 发送失败，请检查网络连接。',
      created_at: new Date().toISOString()
    })
  } finally {
    loading.value = false
    streamingContent.value = ''
    streamingThought.value = ''
  }
}

onMounted(() => {
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
  loadSessions()
})

onUnmounted(() => {
  if (timeInterval) clearInterval(timeInterval)
})
</script>

<style scoped>
/* 复用 Dashboard 的基础样式 */
.dashboard {
  width: 100%;
  height: 100vh;
  background: linear-gradient(135deg, #0a0f2d 0%, #1a1f3a 50%, #0a0f2d 100%);
  color: white;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

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
}

/* 聊天页面特有布局 */
.main-container {
  flex: 1;
  padding: 20px;
  overflow: hidden;
  display: flex;
  justify-content: center;
  height: calc(100vh - 80px); /* 减去header高度 */
}

.content-wrapper {
  width: 100%;
  max-width: 1400px;
  height: 100%;
  display: flex;
  gap: 20px;
  background: rgba(10, 15, 45, 0.5);
  border: 1px solid rgba(74, 158, 255, 0.2);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 0 30px rgba(0, 0, 0, 0.3);
}

.sidebar-wrapper {
  width: 280px;
  flex-shrink: 0;
  height: 100%;
}

.chat-wrapper {
  flex: 1;
  min-width: 0;
  height: 100%;
}
</style>
