import { createRouter, createWebHistory } from 'vue-router'
import Welcome from '../pages/Welcome.vue'
import Dashboard from '../pages/Dashboard.vue'
import VehicleSearch from '../pages/VehicleSearch.vue'
import StreamlitPage from '../pages/StreamlitPage.vue'

const routes = [
  { path: '/', component: Welcome },
  { path: '/dashboard', component: Dashboard },
  { path: '/search', component: VehicleSearch },
  { path: '/ai-chat', component: StreamlitPage }
]

export default createRouter({
  history: createWebHistory(),
  routes
})
