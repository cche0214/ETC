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
import { ref, onMounted, onUnmounted } from 'vue';
import * as echarts from 'echarts';
import axios from 'axios';
// 引入江苏地图数据
import jiangsuJson from '../../assets/jiangsu.json';

const chartRef = ref(null);
let chart = null;
const updateTime = ref('');
let timer = null;

// 卡口基础坐标数据
const checkpointCoords = {
  'G3-K731-省际卡口': [117.07, 36.15],
  'G104-K744-省际卡口': [117.33, 34.53],
  'G104-K873-省际卡口': [117.59, 34.04],
  'G206-K816-省际卡口': [117.18, 34.10],
  'G235-K10-市际卡口': [118.36, 34.38],
  'G310-K310-省际卡口': [117.03, 34.29],
  'G311-K207-省际卡口': [117.07, 34.25],
  'G518-K358-省际卡口': [116.41, 34.75],
  'S250-K1-省际卡口': [118.06, 34.62],
  'S251-K5-省际卡口': [117.76, 34.48],
  'S252-K56-省际卡口': [117.59, 34.03],
  'S253-K0-省际卡口': [116.81, 34.92],
  'S323-K10-市际卡口': [118.62, 34.38],
  'S323-K96-市际卡口': [118.35, 34.34],
  'S324-K201-市际卡口': [118.14, 33.90],
  'S325-K63-市际卡口': [118.08, 33.91],
  'S505-K10-市际卡口': [118.21, 34.26],
  'X308-K19-市际卡口': [116.86, 34.49],
  'G237-K148-省际卡口': [116.50, 34.60]
};

const fetchData = async () => {
  try {
    console.log('正在请求地图数据...');
    const response = await axios.get('/api/dashboard/map_data');
    console.log('地图数据响应:', response.data);
    
    if (response.data.code === 200) {
      const { cityDistribution, checkpointFlows, updateTime: time } = response.data.data;
      updateTime.value = time;
      updateChart(cityDistribution, checkpointFlows);
    } else {
      console.warn('地图数据请求成功但返回码非200:', response.data);
    }
  } catch (error) {
    console.error('获取地图数据失败:', error);
  }
};

// 完整江苏城市列表，用于补全数据
const JIANGSU_CITIES = [
  '南京市', '无锡市', '徐州市', '常州市', '苏州市', 
  '南通市', '连云港市', '淮安市', '盐城市', '扬州市', 
  '镇江市', '泰州市', '宿迁市'
];

const updateChart = (cityData, flowData) => {
  if (!chart) return;

  // 1. 补全城市数据 (防止后端返回部分城市导致地图显示 NaN)
  const fullCityData = JIANGSU_CITIES.map(city => {
    const found = cityData.find(item => item.name === city);
    return {
      name: city,
      value: found ? found.value : 0
    };
  });

  // 2. 构造卡口散点数据
  const scatterData = [];
  for (const [name, coords] of Object.entries(checkpointCoords)) {
    const flow = flowData[name] || 0;
    scatterData.push({
      name: name,
      value: [...coords, flow] // [lon, lat, flow]
    });
  }

  chart.setOption({
    series: [
      {
        name: '车流量',
        data: fullCityData
      },
      {
        name: '卡口实时流量',
        data: scatterData
      }
    ]
  });
};

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
          const flow = params.value[2];
          const time = updateTime.value || '暂无数据';
          return `${params.name}<br/>实时流量: ${flow} 辆<br/>更新时间: ${time}`;
        }
        // 处理地图区域数据，防止 NaN
        const val = params.value;
        return `${params.name}: ${Number.isNaN(val) ? 0 : val} 辆`;
      }
    },
    visualMap: {
      min: 0,
      max: 1000, // 根据实际数据调整，徐州市705，其他较小
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
        data: [] // 初始为空
      },
      // 卡口位置
      {
        name: '卡口实时流量',
        type: 'scatter', // 使用散点图
        coordinateSystem: 'geo',
        data: Object.entries(checkpointCoords).map(([name, coords]) => ({
          name: name,
          value: [...coords, 0]
        })), // 初始显示所有卡口，流量为0
        symbolSize: 8, // 点的大小
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
  fetchData();
  // 每30秒刷新一次
  timer = setInterval(fetchData, 30000);
  window.addEventListener('resize', resizeChart);
});

onUnmounted(() => {
  if (timer) clearInterval(timer);
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
