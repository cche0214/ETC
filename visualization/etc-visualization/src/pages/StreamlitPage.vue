<template>
  <div class="streamlit-container">
    <iframe 
      src="http://localhost:8501" 
      class="streamlit-iframe"
      frameborder="0"
    ></iframe>
  </div>
</template>

<style scoped>
.streamlit-container {
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

.streamlit-iframe {
  width: 100%;
  height: 100%;
  border: none;
}
</style>
