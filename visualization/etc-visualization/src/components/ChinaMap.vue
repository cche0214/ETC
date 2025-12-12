<template>
  <div class="china-map-wrapper">
    <div class="card-header">
      <div class="header-line"></div>
      <h3>全国来徐车辆分布热力图</h3>
      <div class="header-line"></div>
    </div>
    <div class="china-map-container" ref="chartRef"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';
import * as echarts from 'echarts';
// 注意：你需要下载 china.json 文件并放入 src/assets/ 目录
// 如果没有这个文件，地图将无法显示
// 你可以在网上搜索 "echarts china.json" 下载
import chinaJson from '../assets/china.json';

const chartRef = ref(null);
let chart = null;

// 模拟数据：各省份来徐州的车流量
const mockData = [
  { name: '江苏', value: 5000 }, // 本省流量最大
  { name: '山东', value: 2000 }, // 邻省
  { name: '安徽', value: 1800 }, // 邻省
  { name: '河南', value: 1500 }, // 邻省
  { name: '浙江', value: 800 },
  { name: '上海', value: 900 },
  { name: '北京', value: 400 },
  { name: '广东', value: 300 },
  { name: '河北', value: 350 },
  { name: '湖北', value: 200 },
  { name: '天津', value: 150 },
  { name: '福建', value: 100 },
  { name: '湖南', value: 120 },
  { name: '四川', value: 80 },
  { name: '重庆', value: 70 },
  { name: '陕西', value: 60 },
  { name: '黑龙江', value: 20 },
  { name: '辽宁', value: 30 },
  { name: '吉林', value: 25 },
  { name: '山西', value: 50 },
  { name: '江西', value: 90 },
  { name: '广西', value: 40 },
  { name: '云南', value: 30 },
  { name: '贵州', value: 20 },
  { name: '内蒙古', value: 15 },
  { name: '西藏', value: 5 },
  { name: '青海', value: 8 },
  { name: '宁夏', value: 10 },
  { name: '新疆', value: 12 },
  { name: '海南', value: 45 },
  { name: '台湾', value: 0 },
  { name: '香港', value: 0 },
  { name: '澳门', value: 0 },
  { name: '甘肃', value: 0 }
];

const initChart = () => {
  if (!chartRef.value) return;
  
  // 注册地图 (请在引入 china.json 后取消注释)
  echarts.registerMap('china', chinaJson);

  chart = echarts.init(chartRef.value);

  const option = {
    backgroundColor: 'transparent',
    // title: {
    //   text: '全国来徐车辆分布热力图',
    //   left: 'center',
    //   top: 20,
    //   textStyle: {
    //     color: '#fff',
    //     fontSize: 16
    //   }
    // },
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} 辆'
    },
    visualMap: {
      min: 0,
      max: 2500, // 根据数据调整
      left: 'left',
      bottom: '20',
      text: ['高', '低'],
      textStyle: {
        color: '#fff'
      },
      inRange: {
        color: ['#e0ffff', '#006edd'] // 浅蓝到深蓝
        // 或者热力图色系: ['#blue', 'blue', 'green', 'yellow', 'red']
        // color: ['#50a3ba', '#eac736', '#d94e5d']
      },
      calculable: true
    },
    geo: {
      map: 'china',
      roam: true, // 允许缩放和平移
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
      // 如果需要显示徐州的位置，可以加一个散点图
      {
        name: '徐州',
        type: 'effectScatter',
        coordinateSystem: 'geo',
        data: [
          { name: '徐州', value: [117.284124, 34.205768, 5000] } // 徐州坐标
        ],
        symbolSize: 8,
        itemStyle: {
          color: '#ff0000',
          shadowBlur: 10,
          shadowColor: '#333'
        },
        zlevel: 1
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
