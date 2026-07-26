import { createRouter, createWebHistory } from 'vue-router'
import { isAuthenticated } from '@/api/client'
import LandingView from '../views/LandingView.vue'
import SelectionView from '../views/SelectionView.vue'
import OrchestratorView from '../views/OrchestratorView.vue'
import DineoutView from '../views/DineoutView.vue'
import LoginView from '../views/LoginView.vue'
import SignupView from '../views/SignupView.vue'
import JoinPartyView from '../views/JoinPartyView.vue'
import GuestOrderView from '../views/GuestOrderView.vue'
import ProfileView from '../views/ProfileView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', component: LandingView },
    { path: '/login', component: LoginView },
    { path: '/signup', component: SignupView },
    { path: '/selection', component: SelectionView, meta: { requiresAuth: true } },
    { path: '/orchestrator', component: OrchestratorView, meta: { requiresAuth: true } },
    { path: '/dineout', component: DineoutView, meta: { requiresAuth: true } },
    { path: '/join/:code', component: JoinPartyView, props: true },
    { path: '/guest-order', component: GuestOrderView },
    { path: '/profile', component: ProfileView, meta: { requiresAuth: true } },
  ],
})

router.beforeEach((to) => {
  if (to.meta.requiresAuth && !isAuthenticated()) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }
  return true
})

export default router
