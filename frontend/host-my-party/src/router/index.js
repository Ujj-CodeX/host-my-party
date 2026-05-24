import { createRouter, createWebHistory } from 'vue-router'
import LandingView from '../views/LandingView.vue'
import SelectionView from '../views/SelectionView.vue'
import OrchestratorView from '../views/OrchestratorView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', component: LandingView },
    { path: '/selection', component: SelectionView },
    { path: '/orchestrator', component: OrchestratorView }
  ]
})

export default router