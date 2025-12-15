import axios from 'axios'

// 使用相对路径，通过 Vite 代理转发到后端
const API_BASE_URL = '/api'

const request = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000
})

request.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// 1. 获取车辆品牌统计 (对应 VehicleTypeBar)
export function getBrandStats() {
  return request.get('/dashboard/brand_stats')
}

// 2. 获取流量历史趋势 (对应 RealtimeFlowChart)
export function getTrafficFlowHistory() {
  return request.get('/dashboard/flow_history')
}

// 3. 获取套牌车报警 (对应 DataPriorityList)
export function getDeckedVehicles() {
  return request.get('/dashboard/alerts')
}

// 4. 获取数据总览 (对应 DataOverview)
export function getOverview() {
  return request.get('/dashboard/overview')
}

// 5. 获取实时车流 (对应 DataPriorityList 或其他列表)
export function getRealtimeTraffic(limit = 20) {
  return request.get('/dashboard/realtime', { params: { limit } })
}

// 6. 获取车型分布统计 (对应 VehicleTypeRose)
export function getVehicleTypeStats() {
  return request.get('/dashboard/vehicle_type_stats')
}