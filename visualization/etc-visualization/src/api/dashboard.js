import axios from 'axios'

// 假设后端运行在本地 8080 端口
const API_BASE_URL = 'http://localhost:8080/api'

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
  return request.get('/traffic/stats/brand')
}

// 2. 获取流量历史趋势 (对应 RealtimeFlowChart)
export function getTrafficFlowHistory() {
  return request.get('/traffic/flow_history')
}

// 3. 获取套牌车报警 (对应 DataPriorityList)
export function getDeckedVehicles() {
  return request.get('/decked_vehicles')
}