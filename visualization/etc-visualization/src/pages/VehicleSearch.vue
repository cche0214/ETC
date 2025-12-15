<template>
  <div class="vehicle-search-page">
    <header class="header">
      <div class="header-bg"></div>
      <button class="back-btn" @click="$router.push('/')">
        <span class="icon">←</span> 返回主页
      </button>
      <h1 class="header-title">车辆通行记录查询</h1>
      <div class="header-time">{{ currentTime }}</div>
    </header>

    <div class="content-container">
      <!-- 搜索表单区域 -->
      <div class="search-section">
        <search-form 
          @search="handleSearch" 
          @reset="handleReset" 
        />
      </div>

      <!-- 结果列表区域 -->
      <div class="result-section">
        <result-list 
          :data="searchResults" 
          :total="totalResults"
          :current-page="currentPage"
          @page-change="handlePageChange"
          @export="handleExport"
          @view="handleViewDetail"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import SearchForm from '../components/VehicleSearch/SearchForm.vue'
import ResultList from '../components/VehicleSearch/ResultList.vue'
import axios from 'axios'
import { ElMessage, ElLoading } from 'element-plus'

const currentTime = ref('')
let timer = null

// 搜索状态
const searchResults = ref([])
const totalResults = ref(0)
const currentPage = ref(1)
const pageSize = 20
const currentParams = ref({}) // 保存当前查询参数用于分页

// 更新时间
const updateTime = () => {
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

// 执行API查询
const fetchResults = async (params) => {
  const loading = ElLoading.service({
    lock: true,
    text: '正在检索数据...',
    background: 'rgba(0, 0, 0, 0.7)',
  })

  try {
    const response = await axios.post('/api/search', {
      ...params,
      page: currentPage.value,
      pageSize: pageSize
    })

    if (response.data.code === 200) {
      searchResults.value = response.data.data.list
      totalResults.value = response.data.data.total
      ElMessage.success(`查询成功，共找到 ${totalResults.value} 条记录`)
    } else {
      ElMessage.error(response.data.message || '查询失败')
    }
  } catch (error) {
    console.error('Search error:', error)
    ElMessage.error('网络请求失败，请检查后端服务是否启动')
  } finally {
    loading.close()
  }
}

// 处理搜索
const handleSearch = (params) => {
  console.log('Search params:', params)
  currentPage.value = 1
  currentParams.value = params
  fetchResults(params)
}

// 处理重置
const handleReset = () => {
  searchResults.value = []
  totalResults.value = 0
  currentPage.value = 1
  currentParams.value = {}
}

// 处理分页
const handlePageChange = (page) => {
  currentPage.value = page
  fetchResults(currentParams.value)
}

// 处理导出
const handleExport = async () => {
  const loading = ElLoading.service({
    lock: true,
    text: '正在生成导出文件，请稍候...',
    background: 'rgba(0, 0, 0, 0.7)',
  })

  try {
    const response = await axios.post('/api/export', {
      ...currentParams.value
    }, {
      responseType: 'blob' // 重要：指定响应类型为 blob
    })

    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    
    // 获取文件名 (尝试从 Content-Disposition 获取，或者使用默认值)
    let filename = 'vehicle_records.csv'
    const contentDisposition = response.headers['content-disposition']
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="?(.+)"?/)
      if (filenameMatch && filenameMatch.length === 2)
        filename = filenameMatch[1]
    }
    
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    
    // 清理
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('Export error:', error)
    ElMessage.error('导出失败，请稍后重试')
  } finally {
    loading.close()
  }
}

// 查看详情
const handleViewDetail = (item) => {
  ElMessage.info(`查看车辆详情: ${item.HPHM}`)
}

onMounted(() => {
  updateTime()
  timer = setInterval(updateTime, 1000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
.vehicle-search-page {
  width: 100vw;
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
  font-size: 36px;
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

.content-container {
  flex: 1;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-height: 0;
  overflow-y: auto; /* Allow vertical scrolling for the whole content area */
}

.search-section {
  flex-shrink: 0;
}

.result-section {
  flex: 1;
  min-height: 500px; /* Ensure enough space for results */
  display: flex;
  flex-direction: column;
}
</style>
