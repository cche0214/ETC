/**
 * 数据大屏API接口
 * 所有接口都已预留，方便后期对接真实后端
 */

import axios from 'axios'

// API基础地址（后期修改为真实后端地址）
const API_BASE_URL = '/api'

// 创建axios实例
const request = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000
})

// 响应拦截器
request.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API请求失败:', error)
    return Promise.reject(error)
  }
)

/**
 * 数据总览API
 * 获取三个仪表盘的数据：车辆总数、三型车及以下、四型车及以上
 */
export const getDataOverview = async () => {
  // 模拟数据，后期替换为真实API调用
  // return request.get('/data-overview')
  
  return {
    data: [
      { label: '车辆总数', value: 7619, max: 10000, color: '#00D4FF' },
      { label: '三型车及以下', value: 1076, max: 5000, color: '#00FF88' },
      { label: '四型车及以上', value: 6543, max: 10000, color: '#FFB800' }
    ]
  }
}

/**
 * 出站点总量API
 * 获取各出站点的车辆数据
 */
export const getExitStationData = async () => {
  // return request.get('/exit-station')
  
  return {
    data: [
      { name: '松山湖', value: 3165, percentage: 32.82 },
      { name: '广莞高速站', value: 3263, percentage: 33.83 },
      { name: '广东其他站点', value: 3216, percentage: 33.35 }
    ]
  }
}

/**
 * 车辆来源地图API
 * 获取各省份车辆来源数据
 */
export const getVehicleSourceMap = async () => {
  // return request.get('/vehicle-source')
  
  return {
    data: [
      { name: '广东', value: 2500 },
      { name: '湖南', value: 1200 },
      { name: '江西', value: 900 },
      { name: '福建', value: 800 },
      { name: '浙江', value: 600 },
      { name: '上海', value: 400 },
      { name: '江苏', value: 500 },
      { name: '安徽', value: 350 },
      { name: '湖北', value: 300 },
      { name: '河南', value: 250 }
    ]
  }
}

/**
 * 车型堵塞API
 * 获取各车型的堵塞情况数据
 */
export const getVehicleCongestion = async () => {
  // return request.get('/vehicle-congestion')
  
  return {
    data: [
      { name: '一型', value: 2800, rate: '95%' },
      { name: '二型', value: 2900, rate: '100%' },
      { name: '三型', value: 2850, rate: '98%' },
      { name: '四型', value: 2750, rate: '92%' }
    ]
  }
}

/**
 * 24小时车流量API
 * 获取24小时内不同时段的车流量数据
 */
export const getHourlyFlow = async () => {
  // return request.get('/hourly-flow')
  
  // 生成模拟的3D数据
  const hours = Array.from({ length: 24 }, (_, i) => `${i}:00`)
  const days = ['周一', '周二', '周三', '周四', '周五']
  const data = []
  
  for (let i = 0; i < days.length; i++) {
    for (let j = 0; j < hours.length; j++) {
      let value = Math.random() * 800 + 200
      if ((j >= 7 && j <= 9) || (j >= 17 && j <= 19)) {
        value = Math.random() * 1200 + 1000
      }
      data.push([j, i, Math.floor(value)])
    }
  }
  
  return { data, hours, days }
}

/**
 * 车辆趋势API
 * 获取各类别车辆不同时段数量分布历史数据
 */
export const getVehicleTrend = async () => {
  // return request.get('/vehicle-trend')
  
  const times = []
  const now = new Date()
  for (let i = 47; i >= 0; i--) {
    const time = new Date(now.getTime() - i * 30 * 1000)
    times.push(time.getHours() + ':' + String(time.getMinutes()).padStart(2, '0'))
  }
  
  return {
    times,
    series: [
      {
        name: '一类车',
        data: times.map(() => Math.floor(Math.random() * 50 + 30))
      },
      {
        name: '二类车',
        data: times.map(() => Math.floor(Math.random() * 40 + 25))
      },
      {
        name: '三类车',
        data: times.map(() => Math.floor(Math.random() * 35 + 20))
      },
      {
        name: '四类车',
        data: times.map(() => Math.floor(Math.random() * 30 + 15))
      }
    ]
  }
}

/**
 * 车型堵塞横向条形图API
 * 获取各车型的实时堵塞数据
 */
export const getVehicleTypeBar = async () => {
  // return request.get('/vehicle-type-bar')
  
  return {
    data: [
      { name: '三型(核)', value: 2527 },
      { name: '二型(核)', value: 2758 },
      { name: '一型(核)', value: 2795 },
      { name: '二型(空)', value: 2783 },
      { name: '三型(空)', value: 2710 },
      { name: '六型(核)', value: 2690 },
      { name: '五型(核)', value: 2568 },
      { name: '一型(空)', value: 2624 }
    ]
  }
}

/**
 * 数据优先级列表API
 * 获取站点优先级数据列表
 */
export const getDataPriorityList = async () => {
  // return request.get('/data-priority')
  
  return {
    data: [
      {
        station: '松山湖出口',
        date: '2023-01-02 13:48:01',
        address: '东莞 松山湖',
        manager: '法通公路',
        status: '已上报',
        statusClass: 'status-reported',
        priority: 'high'
      },
      {
        station: '石龙出口东向',
        date: '2023-01-02 13:48:01',
        address: '东莞 石龙',
        manager: '法通公路',
        status: '法通公路',
        statusClass: 'status-normal',
        priority: 'normal'
      },
      {
        station: '石龙出口西',
        date: '2023-01-02 13:48:01',
        address: '东莞',
        manager: '正常',
        status: '正常',
        statusClass: 'status-ok',
        priority: 'normal'
      }
    ]
  }
}

/**
 * 统一数据刷新API
 * 一次性获取所有模块的数据
 */
export const getAllData = async () => {
  // return request.get('/all-data')
  
  const [
    dataOverview,
    exitStation,
    vehicleSource,
    vehicleCongestion,
    hourlyFlow,
    vehicleTrend,
    vehicleTypeBar,
    dataPriority
  ] = await Promise.all([
    getDataOverview(),
    getExitStationData(),
    getVehicleSourceMap(),
    getVehicleCongestion(),
    getHourlyFlow(),
    getVehicleTrend(),
    getVehicleTypeBar(),
    getDataPriorityList()
  ])
  
  return {
    dataOverview,
    exitStation,
    vehicleSource,
    vehicleCongestion,
    hourlyFlow,
    vehicleTrend,
    vehicleTypeBar,
    dataPriority
  }
}
