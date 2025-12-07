<template>
  <el-card>
    <h3>套牌车实时告警</h3>
    <ul>
      <li v-for="(item, i) in warnings" :key="i">
        车牌 {{ item.plate }} 出现异常（{{ item.detail }}）
      </li>
    </ul>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const warnings = ref([])

onMounted(() => {
  const ws = new WebSocket("ws://localhost:8080/clone-warning")

  ws.onmessage = (msg) => {
    warnings.value.unshift(JSON.parse(msg.data))
    if (warnings.value.length > 10) warnings.value.pop()
  }
})
</script>
