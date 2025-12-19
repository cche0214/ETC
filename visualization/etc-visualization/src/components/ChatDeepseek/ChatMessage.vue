<template>
  <div class="chat-message" :class="message.role">
    <div class="avatar">
      {{ message.role === 'user' ? '👤' : '🤖' }}
    </div>
    <div class="message-content">
      <div class="bubble markdown-body" v-html="renderContent(message.content)"></div>
      <div class="time" v-if="message.created_at">
        {{ formatTime(message.created_at) }}
      </div>
    </div>
  </div>
</template>

<script setup>
import MarkdownIt from 'markdown-it'
import DOMPurify from 'dompurify'

defineProps({
  message: {
    type: Object,
    required: true
  }
})

const md = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: true
})

const renderContent = (text) => {
  if (!text) return ''
  const rawHtml = md.render(text)
  return DOMPurify.sanitize(rawHtml)
}

const formatTime = (timeStr) => {
  const date = new Date(timeStr)
  return `${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`
}
</script>

<style scoped>
.chat-message {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.chat-message.user {
  flex-direction: row-reverse;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
  border: 1px solid rgba(74, 158, 255, 0.3);
}

.chat-message.assistant .avatar {
  background: rgba(74, 158, 255, 0.2);
  box-shadow: 0 0 15px rgba(74, 158, 255, 0.2);
}

.message-content {
  max-width: 70%;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.chat-message.user .message-content {
  align-items: flex-end;
}

.bubble {
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
  word-break: break-word; /* 允许长单词换行 */
}

.chat-message.assistant .bubble {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-top-left-radius: 2px;
  color: #e0e6ed;
}

.chat-message.user .bubble {
  background: rgba(74, 158, 255, 0.2);
  border: 1px solid rgba(74, 158, 255, 0.3);
  border-top-right-radius: 2px;
  color: #fff;
  box-shadow: 0 4px 15px rgba(74, 158, 255, 0.1);
}

.time {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.3);
  padding: 0 4px;
}

/* Markdown 样式适配 */
:deep(.markdown-body) p {
  margin-bottom: 8px;
}
:deep(.markdown-body) p:last-child {
  margin-bottom: 0;
}
:deep(.markdown-body) ul, :deep(.markdown-body) ol {
  padding-left: 20px;
  margin-bottom: 8px;
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
  margin-bottom: 8px;
}
:deep(.markdown-body) h1, :deep(.markdown-body) h2, :deep(.markdown-body) h3 {
  margin-top: 10px;
  margin-bottom: 8px;
  font-weight: bold;
  font-size: 1.1em;
}
:deep(.markdown-body) a {
  color: #4A9EFF;
  text-decoration: none;
}
:deep(.markdown-body) blockquote {
  border-left: 3px solid rgba(74, 158, 255, 0.5);
  padding-left: 10px;
  color: rgba(255,255,255,0.7);
  margin: 8px 0;
}
</style>
