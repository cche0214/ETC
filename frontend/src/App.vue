<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div class="app-layout">
    <header>
      <div class="wrapper">
        <nav>
          <RouterLink to="/">数据大屏</RouterLink>
          <RouterLink to="/ai-chat">AI 智能助手</RouterLink>
        </nav>
      </div>
    </header>

    <RouterView />
  </div>
</template>

<style scoped>
header {
  line-height: 1.5;
  max-height: 100vh;
  background-color: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
  padding: 1rem 2rem;
}

nav {
  width: 100%;
  font-size: 16px;
  text-align: left;
}

nav a.router-link-exact-active {
  color: #42b983;
  font-weight: bold;
}

nav a.router-link-exact-active:hover {
  background-color: transparent;
}

nav a {
  display: inline-block;
  padding: 0 1rem;
  border-left: 1px solid var(--color-border);
  text-decoration: none;
  color: #2c3e50;
}

nav a:first-of-type {
  border: 0;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
  }

  .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }
}
</style>
