<template>
  <div class="china-map-wrapper">
    <div class="card-header">
      <div class="header-line"></div>
      <h3>江苏省来徐车辆分布热力图（高德地图）</h3>
      <div class="header-line"></div>
    </div>
    <div class="china-map-container" ref="mapRef">
      <div v-if="errorMsg" class="error-mask">
        <div class="error-content">
          <p class="error-title">地图加载失败</p>
          <p class="error-desc">{{ errorMsg }}</p>
          <p class="error-tip">请检查 index.html 中的 API Key 配置</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import axios from 'axios';

const mapRef = ref(null);
const errorMsg = ref('');
let map = null;
let heatmap = null;
let markers = [];
const updateTime = ref('');
let timer = null;

// 卡口基础坐标数据 [经度, 纬度]
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

// 江苏省13个城市的中心坐标
const cityCenters = {
  '南京市': [118.767413, 32.041544],
  '无锡市': [120.301663, 31.574729],
  '徐州市': [117.184811, 34.261792],
  '常州市': [119.946973, 31.772752],
  '苏州市': [120.619585, 31.299379],
  '南通市': [120.864608, 32.016212],
  '连云港市': [119.178821, 34.600018],
  '淮安市': [119.021265, 33.597506],
  '盐城市': [120.139998, 33.377631],
  '扬州市': [119.421003, 32.393159],
  '镇江市': [119.452753, 32.204402],
  '泰州市': [119.915176, 32.484882],
  '宿迁市': [118.275162, 33.963008]
};

const fetchData = async () => {
  try {
    console.log('正在请求地图数据...');
    const response = await axios.get('/api/dashboard/map_data');
    console.log('地图数据响应:', response.data);
    
    if (response.data.code === 200) {
      const { cityDistribution, checkpointFlows, updateTime: time } = response.data.data;
      updateTime.value = time;
      updateMap(cityDistribution, checkpointFlows);
    } else {
      console.warn('地图数据请求成功但返回码非200:', response.data);
    }
  } catch (error) {
    console.error('获取地图数据失败:', error);
  }
};

const updateMap = (cityData, flowData) => {
  if (!map || !heatmap) return;

  // 1. 准备热力图数据
  const heatmapData = [];
  cityData.forEach(city => {
    const coords = cityCenters[city.name];
    if (coords && city.value > 0) {
      heatmapData.push({
        lng: coords[0],
        lat: coords[1],
        count: city.value
      });
    }
  });

  // 更新热力图
  heatmap.setDataSet({
    data: heatmapData,
    max: Math.max(...cityData.map(c => c.value), 100)
  });

  // 2. 更新卡口标记点的流量数据
  updateCheckpointFlows(flowData);
};

// 更新卡口流量数据和图标颜色
const updateCheckpointFlows = (flowData) => {
  if (!map || markers.length === 0) return;

  markers.forEach(marker => {
    const name = marker.getTitle();
    const flow = flowData[name] || 0;
    
    // 更新图标
    marker.setIcon(new AMap.Icon({
      size: new AMap.Size(24, 24),
      image: createMarkerIcon(flow),
      imageSize: new AMap.Size(24, 24)
    }));
    
    // 更新标签
    marker.setLabel({
      content: `<div class="checkpoint-label">${name.split('-')[0]}<br/><span style="color: #00ff00;">${flow}辆</span></div>`,
      offset: new AMap.Pixel(0, -30),
      direction: 'top'
    });
    
    // 更新点击事件内容
    marker.off('click');
    marker.on('click', () => {
      const infoWindow = new AMap.InfoWindow({
        content: `
          <div style="padding: 10px; min-width: 200px; background: rgba(10, 15, 45, 0.95); color: #fff;">
            <h4 style="margin: 0 0 8px 0; color: #00d4ff;">${name}</h4>
            <p style="margin: 4px 0; color: #fff;">实时流量: <strong style="color: #00ff00;">${flow}</strong> 辆</p>
            <p style="margin: 4px 0; color: #999; font-size: 12px;">更新时间: ${updateTime.value}</p>
          </div>
        `,
        offset: new AMap.Pixel(0, -30)
      });
      infoWindow.open(map, marker.getPosition());
    });
  });
  
  console.log('卡口流量数据已更新');
};

// 创建标记点图标（基于流量大小）
const createMarkerIcon = (flow) => {
  const canvas = document.createElement('canvas');
  canvas.width = 24;
  canvas.height = 24;
  const ctx = canvas.getContext('2d');

  // 根据流量确定颜色
  let color = '#00ff00'; // 绿色：低流量
  if (flow > 100) color = '#ffff00'; // 黄色：中等流量
  if (flow > 200) color = '#ff0000'; // 红色：高流量

  // 绘制圆形标记
  ctx.beginPath();
  ctx.arc(12, 12, 8, 0, 2 * Math.PI);
  ctx.fillStyle = color;
  ctx.fill();
  ctx.strokeStyle = '#fff';
  ctx.lineWidth = 2;
  ctx.stroke();

  // 添加光晕效果
  ctx.beginPath();
  ctx.arc(12, 12, 11, 0, 2 * Math.PI);
  ctx.strokeStyle = color;
  ctx.lineWidth = 1;
  ctx.globalAlpha = 0.3;
  ctx.stroke();

  return canvas.toDataURL();
};

const initMap = () => {
  if (!mapRef.value || !window.AMap) {
    errorMsg.value = '高德地图 API 未加载，请检查网络或 Key 配置';
    return;
  }

  try {
    // 初始化地图
    map = new AMap.Map(mapRef.value, {
      zoom: 8, // 地图缩放级别
      center: [119.763232, 33.041544], // 江苏省中心位置
      mapStyle: 'amap://styles/darkblue', // 使用深色主题
      viewMode: '2D', // 使用2D视图
      features: ['bg', 'road', 'building', 'point'], // 显示背景、道路、建筑和标注
      showLabel: true // 显示标注
    });

    // 添加江苏省行政区边界
    if (AMap.DistrictSearch) {
      const district = new AMap.DistrictSearch({
        extensions: 'all',
        subdistrict: 0
      });

      district.search('江苏省', (status, result) => {
        if (status === 'complete' && result.districtList) {
          const bounds = result.districtList[0].boundaries;
          if (bounds) {
            bounds.forEach(bound => {
              new AMap.Polygon({
                path: bound,
                strokeColor: '#00d4ff',
                strokeWeight: 2,
                fillColor: 'rgba(0, 212, 255, 0.05)',
                fillOpacity: 0.1,
                map: map
              });
            });
          }
        }
      });
    } else {
      console.warn('AMap.DistrictSearch 插件未加载');
    }

    // 初始化热力图
    if (!AMap.HeatMap) {
      console.error('热力图插件未加载');
      return;
    }

    heatmap = new AMap.HeatMap(map, {
      radius: 60, // 热力点半径
      opacity: [0, 0.8], // 透明度范围
      gradient: {
        0.5: 'blue',
        0.65: 'cyan',
        0.7: 'lime',
        0.9: 'yellow',
        1.0: 'red'
      }
    });

    console.log('高德地图初始化成功');
    
    // 初始化时就显示卡口位置（即使没有流量数据）
    initCheckpoints();
  } catch (error) {
    console.error('地图初始化失败:', error);
  }
};

// 初始化卡口标记点（默认显示）
const initCheckpoints = () => {
  if (!map) return;
  
  for (const [name, coords] of Object.entries(checkpointCoords)) {
    const marker = new AMap.Marker({
      position: new AMap.LngLat(coords[0], coords[1]),
      title: name,
      icon: new AMap.Icon({
        size: new AMap.Size(24, 24),
        image: createDefaultMarkerIcon(),
        imageSize: new AMap.Size(24, 24)
      }),
      offset: new AMap.Pixel(-12, -12),
      label: {
        content: `<div class="checkpoint-label">${name.split('-')[0]}</div>`,
        offset: new AMap.Pixel(0, -30),
        direction: 'top'
      }
    });

    marker.setMap(map);
    
    // 添加点击事件
    marker.on('click', () => {
      const infoWindow = new AMap.InfoWindow({
        content: `
          <div style="padding: 10px; min-width: 200px; background: rgba(10, 15, 45, 0.95); color: #fff;">
            <h4 style="margin: 0 0 8px 0; color: #00d4ff;">${name}</h4>
            <p style="margin: 4px 0; color: #aaa; font-size: 12px;">等待数据更新...</p>
          </div>
        `,
        offset: new AMap.Pixel(0, -30)
      });
      infoWindow.open(map, marker.getPosition());
    });

    markers.push(marker);
  }
  
  console.log(`已标注 ${markers.length} 个卡口位置`);
};

// 创建默认标记图标（蓝色）
const createDefaultMarkerIcon = () => {
  const canvas = document.createElement('canvas');
  canvas.width = 24;
  canvas.height = 24;
  const ctx = canvas.getContext('2d');

  // 绘制圆形标记
  ctx.beginPath();
  ctx.arc(12, 12, 8, 0, 2 * Math.PI);
  ctx.fillStyle = '#1890ff';
  ctx.fill();
  ctx.strokeStyle = '#fff';
  ctx.lineWidth = 2;
  ctx.stroke();

  // 添加光晕效果
  ctx.beginPath();
  ctx.arc(12, 12, 11, 0, 2 * Math.PI);
  ctx.strokeStyle = '#1890ff';
  ctx.lineWidth = 1;
  ctx.globalAlpha = 0.3;
  ctx.stroke();

  return canvas.toDataURL();
};

onMounted(() => {
  // 等待高德地图API加载完成
  const checkAMap = setInterval(() => {
    if (window.AMap) {
      clearInterval(checkAMap);
      initMap();
      fetchData();
      // 每30秒刷新一次
      timer = setInterval(fetchData, 30000);
    }
  }, 100);

  // 5秒后如果还没加载成功，显示错误
  setTimeout(() => {
    if (!window.AMap) {
      clearInterval(checkAMap);
      errorMsg.value = '高德地图 API 加载超时，请检查网络或 Key 配置';
      console.error('高德地图API加载超时');
    }
  }, 5000);
});

onUnmounted(() => {
  if (timer) clearInterval(timer);
  
  // 清理标记点
  markers.forEach(marker => marker.setMap(null));
  markers = [];
  
  // 清理地图
  if (map) {
    map.destroy();
    map = null;
  }
});
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
  position: relative;
}

.error-mask {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.error-content {
  text-align: center;
  color: #ff4d4f;
}

.error-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 10px;
}

.error-desc {
  font-size: 14px;
  margin-bottom: 5px;
  color: #fff;
}

.error-tip {
  font-size: 12px;
  color: #999;
}

/* 高德地图标注样式 */
:deep(.checkpoint-label) {
  background: rgba(0, 0, 0, 0.8);
  color: #00d4ff;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  white-space: nowrap;
  border: 1px solid #00d4ff;
  text-align: center;
  line-height: 1.4;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.5);
}

:deep(.marker-label) {
  background: rgba(0, 0, 0, 0.75);
  color: #00ff00;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 12px;
  white-space: nowrap;
  border: 1px solid #00ff00;
}

/* 信息窗口样式 */
:deep(.amap-info-content) {
  background: rgba(10, 15, 45, 0.95) !important;
  border: 1px solid #00d4ff !important;
  border-radius: 4px !important;
}
</style>