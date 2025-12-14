<template>
  <div class="search-form-card">
    <div class="card-header">
      <h3>🔍 车辆检索条件</h3>
    </div>
    
    <div class="form-container">
      <!-- 第一行：车牌与车型 -->
      <div class="form-row">
        <div class="form-group">
          <label>车牌号码</label>
          <div class="input-group">
            <input 
              v-model="form.plateNumber" 
              class="dark-input"
              placeholder="例如: 苏C12345"
            />
            <select v-model="form.plateMatchType" class="dark-select small">
              <option value="exact">精确</option>
              <option value="fuzzy">模糊</option>
              <option value="prefix">前缀</option>
            </select>
          </div>
        </div>

        <div class="form-group flex-2">
          <label>车辆类型</label>
          <div class="checkbox-group">
            <label v-for="type in vehicleTypes" :key="type.value" class="checkbox-item">
              <input 
                type="checkbox" 
                :value="type.value" 
                v-model="form.vehicleTypes"
              />
              <span>{{ type.label }}</span>
            </label>
          </div>
        </div>
      </div>

      <!-- 第二行：时间范围 -->
      <div class="form-row">
        <div class="form-group flex-full">
          <label>过车时间范围</label>
          <div class="input-group">
            <input 
              type="datetime-local" 
              v-model="form.startTime" 
              class="dark-input"
            />
            <span class="separator">至</span>
            <input 
              type="datetime-local" 
              v-model="form.endTime" 
              class="dark-input"
            />
          </div>
        </div>
      </div>

      <!-- 第三行：位置信息 -->
      <div class="form-row">
        <div class="form-group">
          <label>行政区划</label>
          <select v-model="form.district" class="dark-select">
            <option value="">全部区域</option>
            <option value="邳州市">邳州市</option>
            <option value="丰县">丰县</option>
            <option value="睢宁县">睢宁县</option>
            <option value="铜山县">铜山县</option>
            <option value="高速五大队">高速五大队</option>
          </select>
        </div>

        <div class="form-group">
          <label>道路/卡口</label>
          <div class="input-group">
            <input 
              v-model="form.roadId" 
              class="dark-input"
              placeholder="道路编号 (如G3)"
            />
            <input 
              v-model="form.kIndex" 
              class="dark-input"
              placeholder="桩号 (如K731)"
            />
          </div>
        </div>

        <div class="form-group">
          <label>边界属性</label>
          <select v-model="form.boundaryLevel" class="dark-select">
            <option value="">全部</option>
            <option value="PROVINCE">省际卡口</option>
            <option value="CITY">市际卡口</option>
          </select>
        </div>
      </div>

      <!-- 第四行：车辆品牌 -->
      <div class="form-row">
        <div class="form-group" style="flex: 1; min-width: 0;">
          <label>车辆品牌</label>
          <input 
            v-model="form.brand" 
            class="dark-input"
            placeholder="选填"
            style="width: 98.5%;"
          />
        </div>
      </div>

      <!-- 第五行：行驶方向 -->
      <div class="form-row">
        <div class="form-group" style="flex: 1; min-width: 0;">
          <label>行驶方向</label>
          <select v-model="form.direction" class="dark-select" style="width: 100%;">
            <option value="">全部</option>
            <option value="1">入徐</option>
            <option value="2">离徐</option>
          </select>
        </div>
      </div>

      <!-- 按钮区 -->
      <div class="form-actions">
        <button class="btn-primary" @click="handleSearch">
          <span class="icon">🔍</span> 开始检索
        </button>
        <button class="btn-secondary" @click="handleReset">
          <span class="icon">🔄</span> 重置条件
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'

const emit = defineEmits(['search', 'reset'])

const vehicleTypes = [
  { value: '01', label: '大型汽车' },
  { value: '02', label: '小型汽车' },
  { value: '51', label: '挂车' },
  { value: '52', label: '教练车' }
]

const form = reactive({
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

const handleSearch = () => {
  emit('search', { ...form })
}

const handleReset = () => {
  Object.assign(form, {
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
  emit('reset')
}
</script>

<style scoped>
.search-form-card {
  background: rgba(10, 15, 45, 0.3);
  border: 1px solid rgba(74, 158, 255, 0.2);
  border-radius: 8px;
  padding: 20px;
  color: #fff;
}

.card-header {
  margin-bottom: 20px;
  border-bottom: 1px solid rgba(74, 158, 255, 0.1);
  padding-bottom: 10px;
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  color: #4A9EFF;
  display: flex;
  align-items: center;
  gap: 8px;
}

.form-container {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.form-row {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.form-group {
  flex: 1;
  min-width: 200px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group.flex-2 {
  flex: 2;
}

.form-group.flex-full {
  flex: 100%;
}

label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
}

.input-group {
  display: flex;
  gap: 10px;
  align-items: center;
}

.dark-input, .dark-select {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(74, 158, 255, 0.3);
  color: #fff;
  padding: 8px 10px;
  border-radius: 4px;
  font-size: 14px;
  width: 100%;
  outline: none;
  transition: all 0.3s;
}

.dark-input:focus, .dark-select:focus {
  border-color: #4A9EFF;
  box-shadow: 0 0 10px rgba(74, 158, 255, 0.2);
}

.dark-select.small {
  width: 80px;
  flex: none;
}

.checkbox-group, .radio-group {
  display: flex;
  gap: 15px;
  align-items: center;
  height: 38px; /* Match input height */
  background: rgba(0, 0, 0, 0.2);
  padding: 0 15px;
  border-radius: 4px;
  border: 1px solid rgba(74, 158, 255, 0.1);
}

.checkbox-item, .radio-item {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  font-size: 14px;
}

.separator {
  color: rgba(255, 255, 255, 0.5);
}

.form-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 10px;
  padding-top: 20px;
  border-top: 1px solid rgba(74, 158, 255, 0.1);
}

.btn-primary, .btn-secondary {
  padding: 10px 30px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 15px;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s;
}

.btn-primary {
  background: linear-gradient(90deg, #4A9EFF 0%, #00D4FF 100%);
  color: #fff;
  font-weight: bold;
}

.btn-primary:hover {
  box-shadow: 0 0 15px rgba(74, 158, 255, 0.4);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.2);
}
</style>