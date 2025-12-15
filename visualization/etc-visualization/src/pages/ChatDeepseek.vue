<template>
  <div class="chat-container">
    <h2>ETC RAG 智能问答</h2>

    <textarea
      v-model="question"
      placeholder="请输入你的问题，例如：ETC 项目用了哪些数据库？"
      rows="4"
    ></textarea>

    <button :disabled="loading" @click="sendQuestion">
      {{ loading ? '思考中...' : '提问' }}
    </button>

    <div v-if="answer" class="answer-box">
      <h3>回答</h3>
      <p>{{ answer }}</p>
    </div>

    <div v-if="sources.length" class="sources-box">
      <h3>参考来源</h3>
      <ul>
        <li v-for="(s, index) in sources" :key="index">
          {{ s.title }} ｜ {{ s.source }} ｜ {{ s.language }}
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const question = ref('')
const answer = ref('')
const sources = ref([])
const loading = ref(false)

const sendQuestion = async () => {
  if (!question.value.trim()) {
    alert('请输入问题')
    return
  }

  loading.value = true
  answer.value = ''
  sources.value = []

  try {
    const res = await axios.post('/rag-api/api/rag/chat', {
      question: question.value
    })

    answer.value = res.data.answer || ''
    sources.value = res.data.sources || []
  } catch (err) {
    console.error(err)
    answer.value = '请求失败，请检查后端服务'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.chat-container {
  max-width: 800px;
  margin: 40px auto;
  padding: 20px;
}

textarea {
  width: 100%;
  padding: 10px;
  font-size: 14px;
}

button {
  margin-top: 10px;
  padding: 8px 20px;
  font-size: 14px;
}

.answer-box,
.sources-box {
  margin-top: 20px;
  padding: 12px;
  background: #f6f6f6;
  border-radius: 6px;
}

.sources-box ul {
  padding-left: 20px;
}
</style>
