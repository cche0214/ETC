<template>
  <div class="chat-window">
    <div class="messages-container" ref="messagesContainer">
      <div v-if="messages.length === 0" class="welcome-screen">
        <div class="welcome-icon">👋</div>
        <h2>欢迎使用 ETC 智能助手</h2>
        <p>您可以询问交通流量、卡口数据或预测信息</p>
      </div>
      
      <div v-else class="messages-list">
        <chat-message 
          v-for="(msg, index) in messages" 
          :key="index"
          :message="msg"
        />
        
        <!-- 实时生成的 AI 回复（流式） -->
        <div v-if="streamingContent || streamingThought" class="chat-message assistant streaming">
           <div class="avatar">🤖</div>
           <div class="message-content">
             <!-- 思考过程 -->
             <div v-if="streamingThought" class="thought-bubble">
               <div class="thought-header">思考过程</div>
               <div class="thought-content">{{ streamingThought }}</div>
             </div>
             
             <!-- 正文回复 -->
             <div v-if="streamingContent" class="bubble markdown-body" v-html="renderMarkdown(streamingContent)"></div>
             <div v-else-if="!streamingThought" class="bubble loading">
               <span class="dot">.</span><span class="dot">.</span><span class="dot">.</span>
             </div>
           </div>
        </div>
      </div>
    </div>
    
    <chat-input 
      @send="$emit('send-message', $event)" 
      :disabled="loading" 
    />
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import ChatMessage from './ChatMessage.vue'
import ChatInput from './ChatInput.vue'
import MarkdownIt from 'markdown-it'
import DOMPurify from 'dompurify'

const props = defineProps({
  messages: {
    type: Array,
    default: () => []
  },
  loading: Boolean,
  streamingContent: String, // 来自父组件的流式正文
  streamingThought: String  // 来自父组件的流式思考
})

defineEmits(['send-message'])

const messagesContainer = ref(null)
const md = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: true
})

const renderMarkdown = (text) => {
  if (!text) return ''
  const rawHtml = md.render(text)
  return DOMPurify.sanitize(rawHtml)
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

watch(() => props.messages, scrollToBottom, { deep: true })
watch(() => props.streamingContent, scrollToBottom)
watch(() => props.streamingThought, scrollToBottom)
</script>

<style scoped>
.chat-window {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: rgba(10, 15, 30, 0.4);
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  scroll-behavior: smooth;
}

.messages-container::-webkit-scrollbar {
  width: 6px;
}

.messages-container::-webkit-scrollbar-thumb {
  background: rgba(74, 158, 255, 0.2);
  border-radius: 3px;
}

.welcome-screen {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.6);
  text-align: center;
}

.welcome-icon {
  font-size: 64px;
  margin-bottom: 20px;
  opacity: 0.8;
}

.welcome-screen h2 {
  font-size: 24px;
  color: #fff;
  margin-bottom: 10px;
}

/* 流式消息样式 */
.chat-message {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
}
.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(74, 158, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
  border: 1px solid rgba(74, 158, 255, 0.3);
}
.message-content {
  max-width: 70%;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.bubble {
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #e0e6ed;
}

.thought-bubble {
  background: rgba(0, 0, 0, 0.2);
  border: 1px dashed rgba(74, 158, 255, 0.3);
  padding: 10px;
  border-radius: 8px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  font-family: monospace;
  white-space: pre-wrap;
}

.thought-header {
  font-weight: bold;
  margin-bottom: 4px;
  color: rgba(74, 158, 255, 0.6);
}

.loading .dot {
  animation: bounce 1.4s infinite ease-in-out both;
}
.dot:nth-child(1) { animation-delay: -0.32s; }
.dot:nth-child(2) { animation-delay: -0.16s; }
@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

/* Markdown 样式适配 (简单版) */
:deep(.markdown-body) p {
  margin-bottom: 10px;
}
:deep(.markdown-body) ul, :deep(.markdown-body) ol {
  padding-left: 20px;
  margin-bottom: 10px;
}
:deep(.markdown-body) code {
  background: rgba(0,0,0,0.3);
  padding: 2px 4px;
  border-radius: 4px;
  font-family: monospace;
}
:deep(.markdown-body) pre {
  background: rgba(0,0,0,0.3);
  padding: 10px;
  border-radius: 8px;
  overflow-x: auto;
  margin-bottom: 10px;
}
:deep(.markdown-body) h1, :deep(.markdown-body) h2, :deep(.markdown-body) h3 {
  margin-top: 10px;
  margin-bottom: 10px;
  font-weight: bold;
  color: #fff;
}
</style>
