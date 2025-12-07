<template>
  <div class="vehicle-search-page">
    <!-- 顶部导航栏 -->
    <header class="header">
      <div class="header-left">
        <RouterLink to="/" class="logo">
          <div class="logo-icon">🚗</div>
          <span class="logo-text">ETC车辆查询系统</span>
        </RouterLink>
      </div>
      <nav class="header-nav">
        <RouterLink to="/" class="nav-item">首页</RouterLink>
        <RouterLink to="/dashboard" class="nav-item">数据大屏</RouterLink>
        <RouterLink to="/search" class="nav-item active">车辆查询</RouterLink>
        <RouterLink to="/ai-chat" class="nav-item">AI 对话</RouterLink>
      </nav>
      <div class="header-right">
        <span class="user-info">欢迎访问</span>
      </div>
    </header>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 切换标签 -->
      <div class="search-tabs">
        <button 
          :class="['tab-btn', { active: activeTab === 'traditional' }]"
          @click="switchTab('traditional')"
        >
          <span class="tab-icon">🔍</span>
          高级检索
        </button>
        <button 
          :class="['tab-btn', { active: activeTab === 'ai' }]"
          @click="switchTab('ai')"
        >
          <span class="tab-icon">🤖</span>
          智能查询
        </button>
      </div>

      <!-- 高级检索面板 -->
      <div v-show="activeTab === 'traditional'" class="search-panel traditional-panel">
        <div class="panel-header">
          <h2>高级检索</h2>
          <p class="subtitle">精确查询车辆通行记录</p>
        </div>

        <div class="search-form">
          <!-- 车牌号码 -->
          <div class="form-row">
            <label class="form-label">车牌号码</label>
            <div class="form-input-group">
              <input 
                v-model="traditionalForm.plateNumber" 
                class="form-input"
                placeholder="例如: 苏C12345"
              />
              <select v-model="traditionalForm.plateMatchType" class="form-select-small">
                <option value="exact">精确匹配</option>
                <option value="fuzzy">模糊匹配</option>
                <option value="prefix">前缀匹配</option>
              </select>
            </div>
          </div>

          <!-- 车辆类型 -->
          <div class="form-row">
            <label class="form-label">车辆类型</label>
            <div class="form-checkbox-group">
              <label v-for="type in vehicleTypes" :key="type.value" class="checkbox-item">
                <input 
                  type="checkbox" 
                  :value="type.value" 
                  v-model="traditionalForm.vehicleTypes"
                />
                <span>{{ type.label }}</span>
              </label>
            </div>
          </div>

          <!-- 行政区划 -->
          <div class="form-row">
            <label class="form-label">行政区划</label>
            <div class="form-input-group">
              <select v-model="traditionalForm.district" class="form-select">
                <option value="">全部区域</option>
                <option value="邳州市">邳州市</option>
                <option value="丰县">丰县</option>
                <option value="睢宁县">睢宁县</option>
                <option value="铜山县">铜山县</option>
                <option value="高速五大队">高速五大队</option>
              </select>
            </div>
          </div>

          <!-- 道路/卡口 -->
          <div class="form-row">
            <label class="form-label">道路卡口</label>
            <div class="form-input-group multi-input">
              <input 
                v-model="traditionalForm.roadId" 
                class="form-input"
                placeholder="道路编号 (G3, S250, G104等)"
              />
              <input 
                v-model="traditionalForm.kIndex" 
                class="form-input"
                placeholder="卡口位置 (K731, K1等)"
              />
            </div>
          </div>

          <!-- 边界级别 -->
          <div class="form-row">
            <label class="form-label">边界级别</label>
            <div class="form-radio-group">
              <label class="radio-item">
                <input type="radio" value="" v-model="traditionalForm.boundaryLevel" />
                <span>全部</span>
              </label>
              <label class="radio-item">
                <input type="radio" value="PROVINCE" v-model="traditionalForm.boundaryLevel" />
                <span>省际卡口</span>
              </label>
              <label class="radio-item">
                <input type="radio" value="CITY" v-model="traditionalForm.boundaryLevel" />
                <span>市际卡口</span>
              </label>
            </div>
          </div>

          <!-- 过车时间 -->
          <div class="form-row">
            <label class="form-label">过车时间</label>
            <div class="form-input-group multi-input">
              <input 
                type="datetime-local" 
                v-model="traditionalForm.startTime" 
                class="form-input"
              />
              <span class="separator">至</span>
              <input 
                type="datetime-local" 
                v-model="traditionalForm.endTime" 
                class="form-input"
              />
            </div>
          </div>

          <!-- 车辆品牌 -->
          <div class="form-row">
            <label class="form-label">车辆品牌</label>
            <div class="form-input-group">
              <input 
                v-model="traditionalForm.brand" 
                class="form-input"
                placeholder="例如: 大众, 本田 (选填)"
              />
            </div>
          </div>

          <!-- 方向类型 -->
          <div class="form-row">
            <label class="form-label">方向类型</label>
            <div class="form-radio-group">
              <label class="radio-item">
                <input type="radio" value="" v-model="traditionalForm.direction" />
                <span>全部方向</span>
              </label>
              <label class="radio-item">
                <input type="radio" value="1" v-model="traditionalForm.direction" />
                <span>进入</span>
              </label>
              <label class="radio-item">
                <input type="radio" value="2" v-model="traditionalForm.direction" />
                <span>离开</span>
              </label>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="form-actions">
            <button class="btn btn-primary" @click="handleTraditionalSearch">
              <span class="btn-icon">🔍</span>
              开始检索
            </button>
            <button class="btn btn-secondary" @click="resetTraditionalForm">
              <span class="btn-icon">🔄</span>
              重置表单
            </button>
            <button class="btn btn-export" @click="handleExport" :disabled="!hasResults">
              <span class="btn-icon">📥</span>
              导出结果
            </button>
          </div>
        </div>
      </div>

      <!-- AI智能查询面板 -->
      <div v-show="activeTab === 'ai'" class="search-panel ai-panel">
        <div class="panel-header">
          <h2>AI智能查询</h2>
          <p class="subtitle">使用自然语言描述查询需求</p>
        </div>

        <div class="ai-search-container">
          <!-- 查询模式 -->
          <div class="ai-mode-selector">
            <button 
              v-for="mode in aiModes" 
              :key="mode.value"
              :class="['mode-btn', { active: aiForm.mode === mode.value }]"
              @click="aiForm.mode = mode.value"
            >
              <span class="mode-icon">{{ mode.icon }}</span>
              <span class="mode-label">{{ mode.label }}</span>
            </button>
          </div>

          <!-- 输入区域 -->
          <div class="ai-input-container">
            <div class="input-header">
              <span class="input-title">查询描述</span>
              <span class="input-hint">示例: 查询昨天从江苏进入山东的苏C开头的小型汽车</span>
            </div>
            <textarea 
              v-model="aiForm.query"
              class="ai-textarea"
              placeholder="请用自然语言描述您的查询需求，AI将自动理解并生成查询条件..."
              rows="6"
            ></textarea>
            
            <!-- 快捷查询示例 -->
            <div class="quick-queries">
              <span class="quick-label">快捷查询:</span>
              <button 
                v-for="(example, index) in queryExamples" 
                :key="index"
                class="quick-btn"
                @click="aiForm.query = example"
              >
                {{ example }}
              </button>
            </div>

            <!-- 过滤条件 -->
            <div class="ai-filters">
              <div class="filter-section">
                <label class="filter-label">时间范围</label>
                <select v-model="aiForm.timeRange" class="filter-select">
                  <option value="today">今天</option>
                  <option value="yesterday">昨天</option>
                  <option value="week">最近7天</option>
                  <option value="month">最近30天</option>
                  <option value="custom">自定义</option>
                </select>
              </div>
              
              <div class="filter-section">
                <label class="filter-label">结果数量</label>
                <select v-model="aiForm.limit" class="filter-select">
                  <option :value="50">50条</option>
                  <option :value="100">100条</option>
                  <option :value="500">500条</option>
                  <option :value="1000">1000条</option>
                </select>
              </div>

              <div class="filter-section">
                <label class="filter-label">排序方式</label>
                <select v-model="aiForm.sortBy" class="filter-select">
                  <option value="time_desc">时间倒序</option>
                  <option value="time_asc">时间正序</option>
                  <option value="relevance">相关度</option>
                </select>
              </div>
            </div>

            <!-- 操作按钮 -->
            <div class="ai-actions">
              <button class="btn btn-ai-search" @click="handleAiSearch">
                <span class="btn-icon">🚀</span>
                AI智能查询
              </button>
              <button class="btn btn-secondary" @click="resetAiForm">
                <span class="btn-icon">🔄</span>
                清空
              </button>
            </div>
          </div>

          <!-- AI 回答展示 -->
          <div v-if="aiAnswer" class="ai-parsed-conditions">
            <div class="parsed-header">
              <span class="parsed-icon">🤖</span>
              <span class="parsed-title">AI 分析结果</span>
            </div>
            <div class="parsed-content" style="white-space: pre-wrap; line-height: 1.6; padding: 15px; color: #333; font-size: 15px;">
              {{ aiAnswer }}
            </div>
          </div>

          <!-- AI解析结果展示 -->
          <div v-if="aiParsedConditions" class="ai-parsed-conditions">
            <div class="parsed-header">
              <span class="parsed-icon">🧠</span>
              <span class="parsed-title">AI理解的查询条件</span>
            </div>
            <div class="parsed-content">
              <div v-for="(value, key) in aiParsedConditions" :key="key" class="parsed-item">
                <span class="parsed-key">{{ key }}</span>
                <span class="parsed-value">{{ value }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 搜索结果区域 -->
      <div v-if="hasResults" class="results-section">
        <div class="results-header">
          <div class="results-info">
            <span class="results-count">找到 <strong>{{ totalResults }}</strong> 条记录</span>
            <span class="results-time">检索用时: {{ searchTime }}ms</span>
          </div>
          <div class="results-actions">
            <button class="btn-icon-only" @click="toggleResultView" :title="resultView === 'table' ? '卡片视图' : '表格视图'">
              {{ resultView === 'table' ? '📊' : '📋' }}
            </button>
          </div>
        </div>

        <!-- 表格视图 -->
        <div v-if="resultView === 'table'" class="results-table-container">
          <table class="results-table">
            <thead>
              <tr>
                <th>序号</th>
                <th>车牌号码</th>
                <th>车辆类型</th>
                <th>过车时间</th>
                <th>行政区划</th>
                <th>道路卡口</th>
                <th>边界级别</th>
                <th>方向</th>
                <th>品牌</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in searchResults" :key="index" class="result-row">
                <td>{{ index + 1 }}</td>
                <td class="highlight-text">{{ item.HPHM }}</td>
                <td>{{ item.HPZL_LABEL }}</td>
                <td>{{ item.GCSJ }}</td>
                <td>{{ item.XZQHMC }}</td>
                <td>{{ item.CLEAN_KKMC }}</td>
                <td>
                  <span :class="['badge', item.BOUNDARY_LEVEL === 'PROVINCE' ? 'badge-province' : 'badge-city']">
                    {{ item.BOUNDARY_LEVEL === 'PROVINCE' ? '省际' : '市际' }}
                  </span>
                </td>
                <td>{{ item.FXLX == '1' ? '进入' : '离开' }}</td>
                <td>{{ item.BRAND || '未知' }}</td>
                <td>
                  <button class="btn-link" @click="viewDetail(item)">详情</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 卡片视图 -->
        <div v-else class="results-cards-container">
          <div v-for="(item, index) in searchResults" :key="index" class="result-card">
            <div class="card-header">
              <span class="card-number">#{{ index + 1 }}</span>
              <span class="card-plate">{{ item.HPHM }}</span>
              <span :class="['card-badge', item.BOUNDARY_LEVEL === 'PROVINCE' ? 'badge-province' : 'badge-city']">
                {{ item.BOUNDARY_LEVEL === 'PROVINCE' ? '省际' : '市际' }}
              </span>
            </div>
            <div class="card-body">
              <div class="card-row">
                <span class="card-label">车辆类型:</span>
                <span class="card-value">{{ item.HPZL_LABEL }}</span>
              </div>
              <div class="card-row">
                <span class="card-label">过车时间:</span>
                <span class="card-value">{{ item.GCSJ }}</span>
              </div>
              <div class="card-row">
                <span class="card-label">卡口位置:</span>
                <span class="card-value">{{ item.CLEAN_KKMC }}</span>
              </div>
              <div class="card-row">
                <span class="card-label">行政区划:</span>
                <span class="card-value">{{ item.XZQHMC }}</span>
              </div>
              <div class="card-row">
                <span class="card-label">方向类型:</span>
                <span class="card-value">{{ item.FXLX == '1' ? '进入' : '离开' }}</span>
              </div>
            </div>
            <div class="card-footer">
              <button class="btn-card-action" @click="viewDetail(item)">查看详情</button>
            </div>
          </div>
        </div>

        <!-- 分页 -->
        <div class="pagination">
          <button class="pagination-btn" :disabled="currentPage === 1" @click="currentPage--">
            上一页
          </button>
          <span class="pagination-info">第 {{ currentPage }} 页 / 共 {{ totalPages }} 页</span>
          <button class="pagination-btn" :disabled="currentPage === totalPages" @click="currentPage++">
            下一页
          </button>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else class="empty-state">
        <div class="empty-icon">🔍</div>
        <p class="empty-text">请输入查询条件开始检索</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { RouterLink } from 'vue-router'
import axios from 'axios'

// 当前激活的标签页
const activeTab = ref('traditional')

// 车辆类型选项
const vehicleTypes = [
  { value: '01', label: '大型汽车' },
  { value: '02', label: '小型汽车' },
  { value: '51', label: '挂车' },
  { value: '52', label: '教练车' }
]

// 高级检索表单
const traditionalForm = ref({
  plateNumber: '',
  plateMatchType: 'exact',
  vehicleTypes: [],
  district: '',
  roadId: '',
  kIndex: '',
  boundaryLevel: '',
  startTime: '',
  endTime: '',
  brand: '',
  direction: ''
})

// AI查询模式
const aiModes = [
  { value: 'intelligent', icon: '🎯', label: '智能理解' },
  { value: 'semantic', icon: '💡', label: '语义分析' },
  { value: 'contextual', icon: '🔗', label: '上下文' },
  { value: 'pattern', icon: '📊', label: '模式匹配' }
]

// AI查询表单
const aiForm = ref({
  query: '',
  mode: 'intelligent',
  timeRange: 'week',
  limit: 100,
  sortBy: 'time_desc'
})

// 快捷查询示例
const queryExamples = [
  '查询昨天从江苏进入山东的苏C开头小型汽车',
  '最近7天通过G3高速省际卡口的大型货车',
  '邳州市S250卡口今天的所有车辆记录',
  '查询鲁Q牌照在12月1日的通行记录'
]

// AI解析的条件
const aiAnswer = ref('')
const aiParsedConditions = ref(null)

// 搜索结果
const searchResults = ref([])
const totalResults = ref(0)
const searchTime = ref(0)
const currentPage = ref(1)
const resultView = ref('table') // 'table' or 'card'

// 计算属性
const hasResults = computed(() => searchResults.value.length > 0)
const totalPages = computed(() => Math.ceil(totalResults.value / 20))

// 切换标签页
const switchTab = (tab) => {
  activeTab.value = tab
  // 清空结果
  searchResults.value = []
  totalResults.value = 0
}

// 高级检索
const handleTraditionalSearch = async () => {
  const startTime = Date.now()
  
  // 模拟API调用
  await new Promise(resolve => setTimeout(resolve, 500))
  
  // 模拟搜索结果
  searchResults.value = [
    {
      GCXH: 'G320300109027253771',
      XZQHMC: '邳州市',
      ROAD_ID: 'S250',
      K_INDEX: 'K1',
      BOUNDARY_LEVEL: 'PROVINCE',
      BOUNDARY_DETAIL: '江苏-山东',
      BOUNDARY_LABEL: '苏鲁界',
      CLEAN_KKMC: 'S250-K1-省际卡口',
      FXLX: '1',
      GCSJ: '2023-12-01 08:15:30',
      GCSJ_TS: '1701388530000',
      HPZL: '02',
      HPZL_LABEL: '小型汽车',
      HPHM: '苏C12345',
      BRAND: '大众'
    },
    {
      GCXH: 'G320300109027253799',
      XZQHMC: '丰县',
      ROAD_ID: 'G3',
      K_INDEX: 'K731',
      BOUNDARY_LEVEL: 'PROVINCE',
      BOUNDARY_DETAIL: '江苏-山东',
      BOUNDARY_LABEL: '苏鲁界',
      CLEAN_KKMC: 'G3-K731-省际卡口',
      FXLX: '1',
      GCSJ: '2023-12-01 09:22:15',
      GCSJ_TS: '1701392535000',
      HPZL: '01',
      HPZL_LABEL: '大型汽车',
      HPHM: '鲁Q93567',
      BRAND: '解放'
    },
    {
      GCXH: 'G320300109027254738',
      XZQHMC: '铜山县',
      ROAD_ID: 'G311',
      K_INDEX: 'K207',
      BOUNDARY_LEVEL: 'PROVINCE',
      BOUNDARY_DETAIL: '江苏-安徽',
      BOUNDARY_LABEL: '苏皖界',
      CLEAN_KKMC: 'G311-K207-省际卡口',
      FXLX: '2',
      GCSJ: '2023-12-01 10:45:20',
      GCSJ_TS: '1701397520000',
      HPZL: '02',
      HPZL_LABEL: '小型汽车',
      HPHM: '皖L16789',
      BRAND: '本田'
    },
    {
      GCXH: 'G320300109027255007',
      XZQHMC: '睢宁县',
      ROAD_ID: 'S325',
      K_INDEX: 'K63',
      BOUNDARY_LEVEL: 'CITY',
      BOUNDARY_DETAIL: '徐州-宿迁',
      BOUNDARY_LABEL: '宿迁界',
      CLEAN_KKMC: 'S325-K63-市际卡口',
      FXLX: '1',
      GCSJ: '2023-12-01 11:30:45',
      GCSJ_TS: '1701400245000',
      HPZL: '02',
      HPZL_LABEL: '小型汽车',
      HPHM: '苏E6K234',
      BRAND: '丰田'
    },
    {
      GCXH: 'G320300109027255357',
      XZQHMC: '邳州市',
      ROAD_ID: 'S251',
      K_INDEX: 'K5',
      BOUNDARY_LEVEL: 'PROVINCE',
      BOUNDARY_DETAIL: '江苏-山东',
      BOUNDARY_LABEL: '苏鲁界',
      CLEAN_KKMC: 'S251-K5-省际卡口',
      FXLX: '1',
      GCSJ: '2023-12-01 14:20:10',
      GCSJ_TS: '1701410410000',
      HPZL: '51',
      HPZL_LABEL: '挂车',
      HPHM: '苏K78901',
      BRAND: '未知'
    }
  ]
  
  totalResults.value = 127 // 模拟总数
  searchTime.value = Date.now() - startTime
  currentPage.value = 1
}

// AI智能查询
const handleAiSearch = async () => {
  const startTime = Date.now()
  aiAnswer.value = ''
  aiParsedConditions.value = null
  
  try {
    const response = await axios.post('http://localhost:8080/api/ai/search', {
      query: aiForm.value.query
    })
    
    if (response.data.status === 'success') {
      aiAnswer.value = response.data.answer
    } else {
      console.error('AI Search Failed:', response.data)
      alert('查询失败: ' + (response.data.msg || '未知错误'))
    }
  } catch (error) {
    console.error('AI Search Error:', error)
    alert('请求失败，请检查后端服务是否启动')
  }
  
  searchTime.value = Date.now() - startTime
}

// 重置表单
const resetTraditionalForm = () => {
  traditionalForm.value = {
    plateNumber: '',
    plateMatchType: 'exact',
    vehicleTypes: [],
    district: '',
    roadId: '',
    kIndex: '',
    boundaryLevel: '',
    startTime: '',
    endTime: '',
    brand: '',
    direction: ''
  }
  searchResults.value = []
  totalResults.value = 0
}

const resetAiForm = () => {
  aiForm.value = {
    query: '',
    mode: 'intelligent',
    timeRange: 'week',
    limit: 100,
    sortBy: 'time_desc'
  }
  aiAnswer.value = ''
  aiParsedConditions.value = null
  searchResults.value = []
  totalResults.value = 0
}

// 导出结果
const handleExport = () => {
  alert('导出功能将调用后端API生成Excel文件')
}

// 切换视图
const toggleResultView = () => {
  resultView.value = resultView.value === 'table' ? 'card' : 'table'
}

// 查看详情
const viewDetail = (item) => {
  alert(`查看车辆详情:\n车牌: ${item.HPHM}\n过车时间: ${item.GCSJ}\n卡口: ${item.CLEAN_KKMC}`)
}
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.vehicle-search-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  overflow-y: auto;
  overflow-x: hidden;
}

/* 顶部导航 */
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 40px;
  height: 70px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
}

.header-left {
  display: flex;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
  color: #2c3e50;
  font-weight: 600;
  font-size: 20px;
  transition: all 0.3s;
}

.logo:hover {
  transform: translateY(-2px);
}

.logo-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: 14px;
}

.header-nav {
  display: flex;
  gap: 30px;
}

.nav-item {
  text-decoration: none;
  color: #666;
  font-size: 16px;
  padding: 8px 16px;
  border-radius: 8px;
  transition: all 0.3s;
}

.nav-item:hover {
  color: #667eea;
  background: rgba(102, 126, 234, 0.1);
}

.nav-item.active {
  color: #667eea;
  background: rgba(102, 126, 234, 0.15);
  font-weight: 600;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 15px;
}

.user-info {
  color: #666;
  font-size: 14px;
}

/* 主内容区 */
.main-content {
  max-width: 1400px;
  margin: 30px auto;
  padding: 0 20px;
}

/* 标签切换 */
.search-tabs {
  display: flex;
  gap: 15px;
  margin-bottom: 25px;
}

.tab-btn {
  flex: 1;
  padding: 18px 30px;
  background: rgba(255, 255, 255, 0.9);
  border: 2px solid transparent;
  border-radius: 15px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 600;
  color: #666;
  transition: all 0.3s;
}

.tab-btn:hover {
  background: white;
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
}

.tab-btn.active {
  background: white;
  border-color: #667eea;
  color: #667eea;
  box-shadow: 0 5px 25px rgba(102, 126, 234, 0.3);
}

.tab-icon {
  font-size: 20px;
}

/* 搜索面板 */
.search-panel {
  background: white;
  border-radius: 20px;
  padding: 35px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
}

.panel-header {
  margin-bottom: 30px;
  border-bottom: 2px solid #f0f0f0;
  padding-bottom: 20px;
}

.panel-header h2 {
  font-size: 26px;
  color: #2c3e50;
  margin-bottom: 8px;
}

.subtitle {
  color: #999;
  font-size: 14px;
}

/* 表单样式 */
.search-form {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.form-row {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

.form-label {
  min-width: 100px;
  padding-top: 10px;
  font-weight: 600;
  color: #444;
  font-size: 15px;
}

.form-input-group {
  flex: 1;
  display: flex;
  gap: 12px;
  align-items: center;
}

.form-input-group.multi-input {
  display: flex;
  gap: 15px;
}

.form-input {
  flex: 1;
  padding: 12px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  font-size: 14px;
  transition: all 0.3s;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-select {
  flex: 1;
  padding: 12px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  font-size: 14px;
  background: white;
  cursor: pointer;
  transition: all 0.3s;
}

.form-select:focus {
  outline: none;
  border-color: #667eea;
}

.form-select-small {
  padding: 12px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  font-size: 14px;
  background: white;
  cursor: pointer;
  min-width: 120px;
}

.separator {
  color: #999;
  font-size: 14px;
}

/* 复选框组 */
.form-checkbox-group {
  flex: 1;
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.checkbox-item {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  transition: all 0.3s;
}

.checkbox-item:hover {
  border-color: #667eea;
  background: rgba(102, 126, 234, 0.05);
}

.checkbox-item input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

/* 单选按钮组 */
.form-radio-group {
  flex: 1;
  display: flex;
  gap: 15px;
}

.radio-item {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  transition: all 0.3s;
}

.radio-item:hover {
  border-color: #667eea;
  background: rgba(102, 126, 234, 0.05);
}

.radio-item input[type="radio"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

/* 操作按钮 */
.form-actions {
  display: flex;
  gap: 15px;
  padding-top: 20px;
  border-top: 2px solid #f0f0f0;
}

.btn {
  padding: 14px 30px;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  background: #f5f5f5;
  color: #666;
}

.btn-secondary:hover {
  background: #e8e8e8;
}

.btn-export {
  background: #10b981;
  color: white;
}

.btn-export:hover {
  background: #059669;
  transform: translateY(-2px);
}

.btn-export:disabled {
  background: #d1d5db;
  cursor: not-allowed;
  transform: none;
}

.btn-icon {
  font-size: 16px;
}

/* AI面板 */
.ai-search-container {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.ai-mode-selector {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 15px;
}

.mode-btn {
  padding: 15px;
  background: #f8f9fa;
  border: 2px solid transparent;
  border-radius: 12px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  transition: all 0.3s;
}

.mode-btn:hover {
  background: #f0f0f0;
  transform: translateY(-2px);
}

.mode-btn.active {
  background: rgba(102, 126, 234, 0.1);
  border-color: #667eea;
}

.mode-icon {
  font-size: 24px;
}

.mode-label {
  font-size: 13px;
  font-weight: 600;
  color: #666;
}

.ai-input-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.input-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.input-title {
  font-weight: 600;
  color: #444;
  font-size: 16px;
}

.input-hint {
  font-size: 13px;
  color: #999;
}

.ai-textarea {
  width: 100%;
  padding: 16px;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  font-size: 15px;
  font-family: inherit;
  resize: vertical;
  transition: all 0.3s;
}

.ai-textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* 快捷查询 */
.quick-queries {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}

.quick-label {
  font-size: 14px;
  color: #666;
  font-weight: 600;
}

.quick-btn {
  padding: 8px 15px;
  background: rgba(102, 126, 234, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 20px;
  color: #667eea;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s;
}

.quick-btn:hover {
  background: rgba(102, 126, 234, 0.2);
  transform: translateY(-1px);
}

/* AI过滤条件 */
.ai-filters {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.filter-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-label {
  font-size: 14px;
  font-weight: 600;
  color: #444;
}

.filter-select {
  padding: 10px 14px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  background: white;
  cursor: pointer;
}

.filter-select:focus {
  outline: none;
  border-color: #667eea;
}

/* AI操作按钮 */
.ai-actions {
  display: flex;
  gap: 15px;
  padding-top: 10px;
}

.btn-ai-search {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
}

.btn-ai-search:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(16, 185, 129, 0.4);
}

/* AI解析条件 */
.ai-parsed-conditions {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
  border: 2px solid rgba(102, 126, 234, 0.2);
  border-radius: 12px;
  padding: 20px;
}

.parsed-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

.parsed-icon {
  font-size: 20px;
}

.parsed-title {
  font-weight: 600;
  color: #667eea;
  font-size: 15px;
}

.parsed-content {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.parsed-item {
  display: flex;
  gap: 10px;
  padding: 10px;
  background: white;
  border-radius: 8px;
}

.parsed-key {
  font-weight: 600;
  color: #666;
  font-size: 14px;
}

.parsed-value {
  color: #667eea;
  font-size: 14px;
}

/* 搜索结果 */
.results-section {
  background: white;
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  padding-bottom: 20px;
  border-bottom: 2px solid #f0f0f0;
}

.results-info {
  display: flex;
  gap: 30px;
  align-items: center;
}

.results-count {
  font-size: 16px;
  color: #666;
}

.results-count strong {
  color: #667eea;
  font-size: 20px;
}

.results-time {
  font-size: 14px;
  color: #999;
}

.results-actions {
  display: flex;
  gap: 10px;
}

.btn-icon-only {
  width: 40px;
  height: 40px;
  border: none;
  background: #f5f5f5;
  border-radius: 8px;
  font-size: 18px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-icon-only:hover {
  background: #e8e8e8;
  transform: translateY(-2px);
}

/* 表格视图 */
.results-table-container {
  overflow-x: auto;
}

.results-table {
  width: 100%;
  border-collapse: collapse;
}

.results-table thead {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.results-table th {
  padding: 15px 12px;
  text-align: left;
  font-weight: 600;
  font-size: 14px;
  white-space: nowrap;
}

.results-table td {
  padding: 15px 12px;
  border-bottom: 1px solid #f0f0f0;
  font-size: 14px;
  color: #666;
}

.result-row:hover {
  background: rgba(102, 126, 234, 0.05);
}

.highlight-text {
  color: #667eea;
  font-weight: 600;
}

.badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.badge-province {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.badge-city {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.btn-link {
  background: none;
  border: none;
  color: #667eea;
  cursor: pointer;
  text-decoration: underline;
  font-size: 14px;
}

.btn-link:hover {
  color: #764ba2;
}

/* 卡片视图 */
.results-cards-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.result-card {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
  border: 2px solid #f0f0f0;
  border-radius: 15px;
  padding: 20px;
  transition: all 0.3s;
}

.result-card:hover {
  border-color: #667eea;
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.2);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 2px solid rgba(102, 126, 234, 0.1);
}

.card-number {
  font-size: 12px;
  color: #999;
}

.card-plate {
  font-size: 18px;
  font-weight: 600;
  color: #667eea;
  flex: 1;
}

.card-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 15px;
}

.card-row {
  display: flex;
  gap: 10px;
  font-size: 14px;
}

.card-label {
  color: #999;
  min-width: 80px;
}

.card-value {
  color: #444;
  font-weight: 500;
}

.card-footer {
  display: flex;
  justify-content: flex-end;
}

.btn-card-action {
  padding: 8px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s;
}

.btn-card-action:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
}

/* 分页 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-top: 30px;
  padding-top: 25px;
  border-top: 2px solid #f0f0f0;
}

.pagination-btn {
  padding: 10px 20px;
  background: white;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  color: #666;
  transition: all 0.3s;
}

.pagination-btn:hover:not(:disabled) {
  border-color: #667eea;
  color: #667eea;
  transform: translateY(-2px);
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-info {
  font-size: 14px;
  color: #666;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 100px 20px;
}

.empty-icon {
  font-size: 80px;
  margin-bottom: 20px;
  opacity: 0.5;
}

.empty-text {
  font-size: 18px;
  color: #999;
}

/* 响应式 */
@media (max-width: 1200px) {
  .ai-mode-selector {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .parsed-content {
    grid-template-columns: 1fr;
  }
  
  .results-cards-container {
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  }
}

@media (max-width: 768px) {
  .header {
    padding: 0 20px;
  }
  
  .form-row {
    flex-direction: column;
    gap: 10px;
  }
  
  .form-label {
    padding-top: 0;
  }
  
  .ai-filters {
    grid-template-columns: 1fr;
  }
  
  .results-cards-container {
    grid-template-columns: 1fr;
  }
}
</style>
