import axios from 'axios'

// 使用相对路径，Vite 会根据 '/api/chat' 前缀自动代理到 FastAPI (8001)
const API_BASE_URL = '/api/chat'

const aiRequest = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000 // 120秒超时
})

aiRequest.interceptors.response.use(
  response => response.data,
  error => {
    console.error('AI API Error:', error)
    return Promise.reject(error)
  }
)

// 1. 创建新会话
export function createSession(sessionData = { title: '新对话' }) {
  return aiRequest.post('/sessions', sessionData)
}

// 2. 获取会话列表
export function getSessions() {
  return aiRequest.get('/sessions')
}

// 3. 获取特定会话详情（包含消息）
export function getSession(sessionId) {
  return aiRequest.get(`/sessions/${sessionId}`)
}

// 4. 更新会话信息 (如标题)
export function updateSession(sessionId, updateData) {
  return aiRequest.put(`/sessions/${sessionId}`, updateData)
}

// 5. 删除会话
export function deleteSession(sessionId) {
  return aiRequest.delete(`/sessions/${sessionId}`)
}

/**
 * 流式发送消息
 * @param {string} sessionId 
 * @param {string} content 
 * @param {function} onMessageCallback - 回调函数，接收 (type, content)
 * @returns {Promise<void>}
 */
export async function streamMessage(sessionId, content, onMessageCallback) {
    const response = await fetch(`${API_BASE_URL}/sessions/${sessionId}/messages`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            content: content,
            session_id: sessionId,
            stream: true
        })
    });

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    try {
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });
            buffer += chunk;
            
            // 处理 buffer 中的 SSE 消息
            const lines = buffer.split('\n\n');
            // 保留最后一个可能不完整的块
            buffer = lines.pop(); 

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const jsonStr = line.slice(6); // 去掉 'data: '
                    try {
                        const data = JSON.parse(jsonStr);
                        if (data.type === 'done') return;
                        onMessageCallback(data.type, data.content);
                    } catch (e) {
                        console.warn('Parse error', e, jsonStr);
                    }
                }
            }
        }
    } finally {
        reader.releaseLock();
    }
}
