<template>
  <div class="welcome-page">
    <!-- 背景轮播 -->
    <div class="background-slider">
      <transition-group name="fade">
        <div 
          v-for="(bg, index) in backgrounds" 
          v-show="currentBg === index"
          :key="index"
          class="bg-slide"
          :style="{ backgroundImage: `url(${bg})` }"
        ></div>
      </transition-group>
    </div>

    <!-- 内容覆盖层 -->
    <div class="content-overlay">
      <div class="main-content">
        <!-- 主标题 -->
        <h1 class="main-title">
          <span class="title-line1">ETC</span>
          <span class="title-line2">BIGDATASTORAGE</span>
        </h1>

        <!-- 描述文本 -->
        <p class="description">
          Through the special short-range communication between the on-board electronic tag installed on 
          the windshield of the vehicle and the microwave antenna on the ETC lane of the toll station, the 
          computer networking technology is used to carry out background settlement with the bank, so as 
          to achieve the goal that the vehicle can pay the expressway or bridge fees without stopping at the 
          expressway or bridge toll station.
        </p>

        <!-- 按钮 -->
        <button class="learn-more-btn" @click="goToDashboard">
          Learn More
        </button>
      </div>

      <!-- 导航指示器 -->
      <div class="nav-dots">
        <span 
          v-for="(bg, index) in backgrounds" 
          :key="index"
          :class="['dot', { active: currentBg === index }]"
          @click="currentBg = index"
        ></span>
      </div>

      <!-- 顶部导航 -->
      <nav class="top-nav">
        <RouterLink to="/dashboard" class="nav-link">数据大屏</RouterLink>
        <RouterLink to="/dashboard" class="nav-link">趋势分析</RouterLink>
        <RouterLink to="/search" class="nav-link">交互式查询</RouterLink>
        <RouterLink to="/ai-chat" class="nav-link">AI 对话</RouterLink>
      </nav>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import bg1 from '../assets/bg1.jpg'
import bg2 from '../assets/bg2.jpg'
import bg3 from '../assets/bg3.jpg'

const router = useRouter()
const currentBg = ref(0)
const backgrounds = [bg1, bg2, bg3]
let intervalId = null

// 自动轮播
onMounted(() => {
  intervalId = setInterval(() => {
    currentBg.value = (currentBg.value + 1) % backgrounds.length
  }, 5000) // 每5秒切换一次
})

onUnmounted(() => {
  if (intervalId) {
    clearInterval(intervalId)
  }
})

const goToDashboard = () => {
  router.push('/dashboard')
}
</script>

<style scoped>
.welcome-page {
  position: relative;
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

/* 背景轮播 */
.background-slider {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.bg-slide {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 1s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* 内容覆盖层 */
.content-overlay {
  position: relative;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 主内容 */
.main-content {
  max-width: 900px;
  padding: 0 40px;
  color: white;
  text-align: left;
}

.main-title {
  margin: 0 0 30px 0;
  font-weight: bold;
  line-height: 1.2;
}

.title-line1 {
  display: block;
  font-size: 80px;
  letter-spacing: 8px;
}

.title-line2 {
  display: block;
  font-size: 60px;
  letter-spacing: 4px;
  margin-top: 10px;
}

.description {
  font-size: 16px;
  line-height: 1.8;
  margin: 0 0 40px 0;
  max-width: 800px;
  text-align: justify;
  color: rgba(255, 255, 255, 0.95);
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

.learn-more-btn {
  padding: 15px 50px;
  font-size: 16px;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 2px solid white;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
  letter-spacing: 1px;
}

.learn-more-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 255, 255, 0.3);
}

/* 导航指示器 */
.nav-dots {
  position: absolute;
  bottom: 40px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 15px;
}

.dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  transition: all 0.3s ease;
}

.dot.active {
  background: #4A9EFF;
  width: 30px;
  border-radius: 6px;
}

.dot:hover {
  background: rgba(255, 255, 255, 0.8);
}

/* 顶部导航 */
.top-nav {
  position: absolute;
  top: 30px;
  right: 50px;
  display: flex;
  gap: 40px;
}

.nav-link {
  color: white;
  text-decoration: none;
  font-size: 16px;
  font-weight: 400;
  transition: all 0.3s ease;
  position: relative;
}

.nav-link.active {
  font-weight: 600;
}

.nav-link::after {
  content: '';
  position: absolute;
  bottom: -5px;
  left: 0;
  width: 0;
  height: 2px;
  background: white;
  transition: width 0.3s ease;
}

.nav-link:hover::after,
.nav-link.active::after {
  width: 100%;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .title-line1 {
    font-size: 50px;
  }
  
  .title-line2 {
    font-size: 40px;
  }
  
  .description {
    font-size: 14px;
  }
  
  .main-content {
    padding: 0 20px;
  }
  
  .top-nav {
    flex-direction: column;
    gap: 20px;
    right: 20px;
    top: 20px;
  }
}
</style>
