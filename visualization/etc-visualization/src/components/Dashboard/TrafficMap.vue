<template>
  <div class="china-map-wrapper">
    <div class="card-header">
      <div class="header-line"></div>
      <h3>江苏省来徐车辆分布热力图</h3>
      <div class="header-line"></div>
    </div>
    <div class="china-map-container" ref="chartRef"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';
import * as echarts from 'echarts';
// 引入江苏地图数据
import jiangsuJson from '../../assets/jiangsu.json';

const chartRef = ref(null);
let chart = null;

// 模拟数据：江苏省各城市来徐州的车流量
const mockData = [
  { name: '南京市', value: 3000 },
  { name: '无锡市', value: 2000 },
  { name: '徐州市', value: 5000 }, // 本地
  { name: '常州市', value: 1500 },
  { name: '苏州市', value: 2500 },
  { name: '南通市', value: 1800 },
  { name: '连云港市', value: 2200 },
  { name: '淮安市', value: 2800 },
  { name: '盐城市', value: 1600 },
  { name: '扬州市', value: 1400 },
  { name: '镇江市', value: 1200 },
  { name: '泰州市', value: 1300 },
  { name: '宿迁市', value: 2600 }
];

// 卡口数据 (经纬度 + 模拟实时流量)
const checkpoints = [
  { name: 'G3-K731-省际卡口', value: [117.07, 36.15, 120] },
  { name: 'G104-K744-省际卡口', value: [117.33, 34.53, 85] },
  { name: 'G104-K873-省际卡口', value: [117.59, 34.04, 92] },
  { name: 'G206-K816-省际卡口', value: [117.18, 34.10, 76] },
  { name: 'G235-K10-市际卡口', value: [118.36, 34.38, 45] },
  { name: 'G310-K310-省际卡口', value: [117.03, 34.29, 110] },
  { name: 'G311-K207-省际卡口', value: [117.07, 34.25, 65] },
  { name: 'G518-K358-省际卡口', value: [116.41, 34.75, 55] },
  { name: 'S250-K1-省际卡口', value: [118.06, 34.62, 40] },
  { name: 'S251-K5-省际卡口', value: [117.76, 34.48, 38] },
  { name: 'S252-K56-省际卡口', value: [117.59, 34.03, 42] },
  { name: 'S253-K0-省际卡口', value: [116.81, 34.92, 95] },
  { name: 'S323-K10-市际卡口', value: [118.62, 34.38, 30] },
  { name: 'S323-K96-市际卡口', value: [118.35, 34.34, 28] },
  { name: 'S324-K201-市际卡口', value: [118.14, 33.90, 35] },
  { name: 'S325-K63-市际卡口', value: [118.08, 33.91, 33] },
  { name: 'S505-K10-市际卡口', value: [118.21, 34.26, 25] },
  { name: 'X308-K19-市际卡口', value: [116.86, 34.49, 20] },
  { name: 'G237-K148-省际卡口', value: [116.50, 34.60, 60] }
];

const initChart = () => {
  if (!chartRef.value) return;
  
  // 注册江苏地图
  echarts.registerMap('jiangsu', jiangsuJson);

  chart = echarts.init(chartRef.value);

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      formatter: (params) => {
        if (params.seriesName === '卡口实时流量') {
          return `${params.name}<br/>实时流量: ${params.value[2]} 辆`;
        }
        return `${params.name}: ${params.value} 辆`;
      }
    },
    visualMap: {
      min: 0,
      max: 5000, // 根据数据调整
      left: 'left',
      bottom: '20',
      text: ['高', '低'],
      textStyle: {
        color: '#fff'
      },
      inRange: {
        color: ['#e0ffff', '#006edd'] // 浅蓝到深蓝
      },
      calculable: true,
      seriesIndex: 0 // 仅控制第一个系列（热力图）
    },
    geo: {
      map: 'jiangsu', // 使用注册的江苏地图
      roam: true, // 允许缩放和平移
      zoom: 1.2, // 初始放大倍数
      label: {
        show: true,
        color: '#fff',
        fontSize: 10
      },
      itemStyle: {
        areaColor: '#323c48',
        borderColor: '#111'
      },
      emphasis: {
        itemStyle: {
          areaColor: '#2a333d'
        },
        label: {
          show: true,
          color: '#fff'
        }
      }
    },
    series: [
      {
        name: '车流量',
        type: 'map',
        geoIndex: 0, // 使用 geo 组件的坐标系
        data: mockData
      },
      // 卡口位置
      {
        name: '卡口实时流量',
        type: 'scatter', // 使用散点图
        coordinateSystem: 'geo',
        data: checkpoints,
        symbolSize: 6, // 点的大小
        itemStyle: {
          color: '#ff0000', // 红色
          shadowBlur: 5,
          shadowColor: '#333'
        },
        zlevel: 2
      }
    ]
  };

  chart.setOption(option);
};

onMounted(() => {
  initChart();
  window.addEventListener('resize', resizeChart);
});

onUnmounted(() => {
  window.removeEventListener('resize', resizeChart);
  if (chart) {
    chart.dispose();
  }
});

const resizeChart = () => {
  if (chart) {
    chart.resize();
  }
};
</script>

<style scoped>
.china-map-wrapper {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: rgba(10, 15, 45, 0.5);
  border: 1px solid rgba(74, 158, 255, 0.2);
  border-radius: 8px;
  padding: 10px;
  box-sizing: border-box;
  overflow: hidden;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 30px;
  margin-bottom: 10px;
  flex-shrink: 0;
}

.header-line {
  width: 40px;
  height: 2px;
  background: linear-gradient(90deg, transparent, #00f2ff, transparent);
  margin: 0 10px;
}

h3 {
  margin: 0;
  color: #00f2ff;
  font-size: 16px;
  text-shadow: 0 0 10px rgba(0, 242, 255, 0.5);
  letter-spacing: 1px;
}

.china-map-container {
  width: 100%;
  flex: 1;
  min-height: 0; /* 允许 flex 子项收缩 */
}
</style>
