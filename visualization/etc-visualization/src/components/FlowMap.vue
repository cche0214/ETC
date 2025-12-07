<template>
  <div class="flow-map-card">
    <div class="card-header">
      <div class="header-line"></div>
      <h3>来深车辆来源</h3>
      <div class="header-line"></div>
    </div>
    <div ref="chartRef" class="map-container"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'

const chartRef = ref(null)
let chart = null

// 模拟各省份数据
const provinceData = [
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

const initChart = () => {
  if (!chartRef.value) return
  
  chart = echarts.init(chartRef.value)
  
  const option = {
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      borderColor: 'rgba(74, 158, 255, 0.5)',
      borderWidth: 1,
      textStyle: { color: '#fff' },
      formatter: '{b}<br/>车辆数: {c}'
    },
    visualMap: {
      show: true,
      min: 0,
      max: 3000,
      text: ['高', '低'],
      left: '5%',
      bottom: '10%',
      textStyle: {
        color: '#fff'
      },
      inRange: {
        color: ['#0a3d62', '#1e5f8c', '#3282b8', '#4A9EFF', '#00D4FF']
      }
    },
    geo: {
      map: 'china',
      roam: false,
      aspectScale: 0.85,
      layoutCenter: ['50%', '50%'],
      layoutSize: '100%',
      itemStyle: {
        areaColor: 'rgba(27, 42, 82, 0.4)',
        borderColor: 'rgba(74, 158, 255, 0.3)',
        borderWidth: 1
      },
      emphasis: {
        itemStyle: {
          areaColor: 'rgba(74, 158, 255, 0.5)',
          borderColor: '#00D4FF',
          borderWidth: 2
        },
        label: {
          color: '#fff',
          fontSize: 14
        }
      }
    },
    series: [
      {
        name: '车辆来源',
        type: 'map',
        geoIndex: 0,
        data: provinceData
      },
      // 添加散点效果
      {
        name: '热点城市',
        type: 'effectScatter',
        coordinateSystem: 'geo',
        data: [
          { name: '深圳', value: [114.0579, 22.5431, 2500] },
          { name: '广州', value: [113.2644, 23.1291, 1800] },
          { name: '长沙', value: [112.9388, 28.2282, 1200] }
        ],
        symbolSize: (val) => val[2] / 100,
        showEffectOn: 'render',
        rippleEffect: {
          brushType: 'stroke',
          scale: 3,
          period: 4
        },
        label: {
          formatter: '{b}',
          position: 'right',
          show: false
        },
        itemStyle: {
          color: '#FFB800',
          shadowBlur: 10,
          shadowColor: '#FFB800'
        },
        zlevel: 1
      }
    ]
  }
  
  // 注册中国地图（简化版）
  echarts.registerMap('china', {
    type: 'FeatureCollection',
    features: generateSimplifiedChinaMap()
  })
  
  chart.setOption(option)
}

// 生成简化的中国地图数据
const generateSimplifiedChinaMap = () => {
  // 这里是简化版，实际使用时需要引入完整的中国地图JSON数据
  const provinces = [
    { name: '广东', cp: [113.4668, 23.0950] },
    { name: '湖南', cp: [112.9388, 28.2282] },
    { name: '江西', cp: [115.8581, 28.6832] },
    { name: '福建', cp: [119.2965, 26.1002] }
  ]
  
  return provinces.map(p => ({
    type: 'Feature',
    properties: { name: p.name },
    geometry: {
      type: 'Polygon',
      coordinates: [[[p.cp[0]-2, p.cp[1]-2], [p.cp[0]+2, p.cp[1]-2], 
                      [p.cp[0]+2, p.cp[1]+2], [p.cp[0]-2, p.cp[1]+2]]]
    }
  }))
}

const updateData = (newData) => {
  if (newData && chart) {
    chart.setOption({
      series: [{ data: newData }]
    })
  }
}

const resizeChart = () => {
  chart?.resize()
}

onMounted(() => {
  setTimeout(() => {
    initChart()
  }, 100)
  window.addEventListener('resize', resizeChart)
})

onUnmounted(() => {
  chart?.dispose()
  window.removeEventListener('resize', resizeChart)
})

defineExpose({ updateData })
</script>

<style scoped>
.flow-map-card {
  background: rgba(27, 42, 82, 0.6);
  border: 1px solid rgba(74, 158, 255, 0.3);
  border-radius: 8px;
  padding: 20px;
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  height: 100%;
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  gap: 10px;
}

.header-line {
  flex: 1;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(74, 158, 255, 0.5), transparent);
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  color: #4A9EFF;
  white-space: nowrap;
  letter-spacing: 2px;
}

.map-container {
  flex: 1;
  min-height: 0;
}
</style>