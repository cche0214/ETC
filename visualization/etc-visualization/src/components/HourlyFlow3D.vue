<template>
  <div class="hourly-flow-card">
    <div class="card-header">
      <div class="header-line"></div>
      <h3>24小时车辆情况</h3>
      <div class="header-line"></div>
    </div>
    <div ref="chartRef" class="chart-container"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import 'echarts-gl'

const chartRef = ref(null)
let chart = null

// 生成模拟的24小时数据
const generateData = () => {
  const hours = ['0am', '1am', '2am', '3am', '4am', '5am', '6am', '7am', '8am', '9am', '10am', '11am',
                 '12pm', '1pm', '2pm', '3pm', '4pm', '5pm', '6pm', '7pm', '8pm', '9pm', '10pm', '11pm']
  const days = ['周一', '周二', '周三', '周四', '周五']
  const data = []
  
  for (let i = 0; i < days.length; i++) {
    for (let j = 0; j < hours.length; j++) {
      // 模拟不同时段的车流量
      let value = Math.random() * 800 + 200
      // 高峰期（7-9am, 5-7pm）增加车流量
      if ((j >= 7 && j <= 9) || (j >= 17 && j <= 19)) {
        value = Math.random() * 1200 + 1000
      }
      data.push([j, i, Math.floor(value)])
    }
  }
  return { hours, days, data }
}

const initChart = () => {
  if (!chartRef.value) return
  
  chart = echarts.init(chartRef.value)
  const { hours, days, data } = generateData()
  
  const option = {
    tooltip: {
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      borderColor: 'rgba(74, 158, 255, 0.5)',
      borderWidth: 1,
      textStyle: {
        color: '#fff'
      },
      formatter: (params) => {
        return `${days[params.value[1]]} ${hours[params.value[0]]}<br/>车流量: ${params.value[2]} 辆`
      }
    },
    visualMap: {
      show: true,
      min: 0,
      max: 2200,
      inRange: {
        color: ['#0a3d62', '#1e5f8c', '#3282b8', '#4A9EFF', '#00D4FF', '#FFB800', '#FF6B6B']
      },
      textStyle: {
        color: '#fff'
      },
      left: '5%',
      bottom: '5%'
    },
    xAxis3D: {
      type: 'category',
      data: hours,
      name: '时间',
      nameTextStyle: {
        color: '#fff',
        fontSize: 12
      },
      axisLabel: {
        color: 'rgba(255, 255, 255, 0.7)',
        fontSize: 10,
        interval: 2
      },
      axisLine: {
        lineStyle: {
          color: 'rgba(74, 158, 255, 0.3)'
        }
      }
    },
    yAxis3D: {
      type: 'category',
      data: days,
      name: '日期',
      nameTextStyle: {
        color: '#fff',
        fontSize: 12
      },
      axisLabel: {
        color: 'rgba(255, 255, 255, 0.7)',
        fontSize: 10
      },
      axisLine: {
        lineStyle: {
          color: 'rgba(74, 158, 255, 0.3)'
        }
      }
    },
    zAxis3D: {
      type: 'value',
      name: '车流量',
      nameTextStyle: {
        color: '#fff',
        fontSize: 12
      },
      axisLabel: {
        color: 'rgba(255, 255, 255, 0.7)',
        fontSize: 10
      },
      axisLine: {
        lineStyle: {
          color: 'rgba(74, 158, 255, 0.3)'
        }
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(74, 158, 255, 0.1)'
        }
      }
    },
    grid3D: {
      boxWidth: 200,
      boxDepth: 80,
      boxHeight: 100,
      viewControl: {
        alpha: 30,
        beta: 40,
        rotateSensitivity: 1,
        zoomSensitivity: 1,
        panSensitivity: 1,
        autoRotate: false,
        distance: 200
      },
      light: {
        main: {
          intensity: 1.2,
          shadow: true
        },
        ambient: {
          intensity: 0.3
        }
      }
    },
    series: [
      {
        type: 'bar3D',
        data: data,
        shading: 'lambert',
        label: {
          show: false
        },
        emphasis: {
          label: {
            show: false
          },
          itemStyle: {
            color: '#FFB800'
          }
        }
      }
    ]
  }
  
  chart.setOption(option)
}

const updateData = (newData) => {
  if (newData && chart) {
    chart.setOption({
      series: [{
        data: newData
      }]
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
.hourly-flow-card {
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

.chart-container {
  flex: 1;
  min-height: 0;
}
</style>
