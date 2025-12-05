<template>
  <div style="padding: 20px">
    <!-- 新增：品牌统计图表 -->
    <BrandStats />
    
    <div style="margin-top: 40px; border-top: 1px solid #eee; padding-top: 20px;">
      <h2>🚗 实时交通监测数据 (Live)</h2>
      <div style="margin-bottom: 10px; color: #666;">
        数据每 2 秒自动刷新 | 当前展示最新 20 条记录
      </div>
      <button @click="fetchTraffic">手动刷新</button>

      <table v-if="rows.length" border="1" cellpadding="8" style="margin-top: 20px; width: 100%;">
      <thead>
        <tr>
          <th>RowKey (Time-Reverse)</th>
          <th>行政区</th>
          <th>卡口名称</th>
          <th>方向</th>
          <th>过车时间</th>
          <th>号牌种类</th>
          <th>号牌号码</th>
          <th>车辆品牌</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="r in rows" :key="r.rowkey">
          <td style="font-family: monospace; font-size: 12px;">{{ r.rowkey }}</td>
          <td>{{ r.XZQHMC }}</td>
          <!-- Flink 写入的是 CLEAN_KKMC -->
          <td>{{ r.CLEAN_KKMC }}</td>
          <td>{{ r.FXLX }}</td>
          <td>{{ r.GCSJ }}</td>
          <!-- 优先展示中文标签 -->
          <td>{{ r.HPZL_LABEL || r.HPZL }}</td>
          <td style="font-weight: bold; color: #2c3e50;">{{ r.HPHM }}</td>
          <!-- Flink 写入的是 BRAND -->
          <td>{{ r.BRAND }}</td>
        </tr>
      </tbody>
    </table>
    <div v-else style="margin-top: 20px; color: #999;">
      暂无数据，请确保 Flink 任务正在运行且 Kafka 有数据输入...
    </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue"
import axios from "axios"
import BrandStats from './components/BrandStats.vue'

const rows = ref([])
let timer = null

// 调用 Flask 接口
async function fetchTraffic() {
  try {
    // 使用新的实时接口 /api/traffic/latest
    const res = await axios.get("/api/traffic/latest")
    if (res.data && res.data.data) {
      rows.value = res.data.data
    }
  } catch (e) {
    console.error("获取数据失败：" + e)
  }
}

onMounted(() => {
  fetchTraffic()
  // 开启轮询，每 2 秒获取一次最新数据
  timer = setInterval(fetchTraffic, 2000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<style>
table {
  border-collapse: collapse;
}
th {
  background: #f2f2f2;
  text-align: left;
}
button {
  padding: 6px 12px;
  background: #42b983;
  color: white;
  border: none;
  cursor: pointer;
  border-radius: 6px;
}
button:hover {
  background: #3aa876;
}
</style>
