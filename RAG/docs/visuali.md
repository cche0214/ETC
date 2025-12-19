# 江苏徐州ETC大数据管理平台

## 可视化概述

 这是一个基于Vue 3和ECharts的ETC高速公路大数据可视化监控平台，主要用于实时展示交通流量、车辆分布、拥堵情况等数据。

## 核心目录

```javascriptsrc/
├── api/
│   └── dashboard.js          # 数据接口API（对接后端）
├── components/
│   ├── DataOverview.vue      # 数据总览（三个仪表盘）
│   ├── ExitStationPie.vue    # 出站点总量饼图
│   ├── FlowMap.vue           # 车辆来源地图
│   ├── VehicleCongestion.vue # 车型堵塞柱状图
│   ├── HourlyFlow3D.vue      # 24小时车流量3D柱状图
│   ├── RealtimeFlowChart.vue # 车辆趋势面积图
│   ├── VehicleTypeBar.vue    # 车型堵塞横向条形图
│   └── DataPriorityList.vue  # 数据优先级列表
├── pages/
│   ├── Welcome.vue           # 欢迎页面（背景轮播）
│   └── Dashboard.vue         # 主数据大屏
└── router/
    └── index.js              # 路由配置
```
## 功能说明
### 1. 欢迎页面 (Welcome)
- 多张背景图片自动轮播（每5秒切换）
- 点击"Learn More"按钮进入数据大屏
- 顶部导航菜单
- 底部图片轮播指示器

### 2. 数据大屏 (dashboard)
#### 左侧区域
- **数据总览**: 三个圆形仪表盘显示车辆总数、三型车及以下、四型车及以上
- **出站点总量**: 饼图显示松山湖、广莞高速站等出站点数据分布
- **车型堵塞**: 柱状图显示各车型的堵塞情况
#### 中间区域
- **车辆来源地图**: 中国地图显示经过徐州的车辆来源分布（带热点标记）
      显示卡口位置和实时流量
      根据流量大小显示不同颜色（绿/黄/红）
      支持点击查看详细信息 
- **实时过车明细**: 展示最新车辆来徐访问记录

#### 右侧区域
- **车辆品牌分布**:
- **套牌车实时预警**:

## 如何对接后端数据

### 方法1：修改API配置
在 `src/api/dashboard.js` 文件中：

1. 修改API基础地址：
```javascript
const API_BASE_URL = 'http://your-backend-url:port'
```

2. 取消注释真实API调用，注释掉模拟数据：
```javascript
export const getDataOverview = async () => {
  // 启用真实API
  return request.get('/data-overview')
  
  // 注释掉模拟数据
  // return { data: [...] }
}
```

### 方法2：在Dashboard页面中使用API
在 `src/pages/Dashboard.vue` 中：

```javascript
import { getAllData } from '../api/dashboard'

const refreshData = async () => {
  try {
    const data = await getAllData()
    
    // 更新各个组件的数据
    dataOverviewRef.value?.updateData(data.dataOverview.data)
    exitStationRef.value?.updateData(data.exitStation.data)
    flowMapRef.value?.updateData(data.vehicleSource.data)
    vehicleCongestionRef.value?.updateData(data.vehicleCongestion.data)
    // ... 其他组件
  } catch (error) {
    console.error('数据刷新失败:', error)
  }
}
```

## 数据格式规范

### 数据总览
```javascript
[
  { label: '车辆总数', value: 7619, max: 10000, color: '#00D4FF' },
  { label: '三型车及以下', value: 1076, max: 5000, color: '#00FF88' },
  { label: '四型车及以上', value: 6543, max: 10000, color: '#FFB800' }
]
```

### 出站点数据
```javascript
[
  { name: '松山湖', value: 3165, percentage: 32.82 },
  { name: '广莞高速站', value: 3263, percentage: 33.83 }
]
```

### 地图数据
```javascript
[
  { name: '广东', value: 2500 },
  { name: '湖南', value: 1200 }
]
```

### 车型堵塞数据
```javascript
[
  { name: '一型', value: 2800, rate: '95%' },
  { name: '二型', value: 2900, rate: '100%' }
]
```

### 24小时数据
```javascript
{
  data: [[hour, day, value], ...],  // [0-23, 0-4, number]
  hours: ['0:00', '1:00', ...],
  days: ['周一', '周二', ...]
}
```

## 组件扩展

每个组件都暴露了 `updateData` 方法，可以动态更新数据：

```javascript
// 获取组件引用
const componentRef = ref(null)

// 更新数据
componentRef.value?.updateData(newData)
```

## 样式定制
### 修改主题色
在各组件的样式中修改颜色变量：
- 主色调: `#4A9EFF`
- 辅助色: `#00D4FF`
- 强调色: `#FFB800`
- 成功色: `#00FF88`
- 警告色: `#FF6B6B`

### 修改布局
在 `Dashboard.vue` 中调整grid布局：
```css
grid-template-columns: 420px 1fr 420px;  /* 左 中 右 宽度 */
```

## 启动项目

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build
```
##组件技术实现详解
###高德地图API集成
```
// 地图初始化和热力图配置  
const updateMap = (cityData, flowData) => {  
  // 热力图数据处理  
  const heatmapData = cityData.map(city => ({  
    lng: cityCenters[city.name][0],  
    lat: cityCenters[city.name][1],  
    count: city.value  
  }))  
    
  // 动态更新热力图数据集  
  heatmap.setDataSet({  
    data: heatmapData,  
    max: Math.max(...cityData.map(c => c.value), 100)  
  })  
}
```
###实时标记点渲染
- 使用Canvas API动态生成流量标记图标
- 根据流量大小动态调整颜色（绿/黄/红）
- 实现点击交互，显示详细信息窗口

##图表组件技术细节
###饼图组件实现
- 使用环形图设计，半径配置为['45%', '70%']
- 配置渐变色和阴影效果增强视觉层次
- 自定义tooltip格式化显示百分比

###3D柱状图技术
- 数据结构：[hour, day, value]三维数组
- 视角控制：配置alpha=30°, beta=40°的观察角度
- 光照系统：主光源+环境光源组合