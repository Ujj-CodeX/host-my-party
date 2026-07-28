<template>
  <div class="profile-section">
    <div class="container">
      <div class="row g-4 align-items-stretch">
        <div class="col-lg-4">
          <div class="glass-card profile-card h-100 text-center">
            <div class="avatar mx-auto mb-3">{{ initials }}</div>
            <p class="text-orange fw-bold mb-1">Party Captain</p>
            <h2 class="fw-bold mb-1">{{ user?.name || 'Swiggy Host' }}</h2>
            <p class="text-muted mb-4">{{ user?.email || user?.phone_number || 'Ready to host smarter parties' }}</p>
            <button class="btn btn-orange w-100" @click="$router.push('/')">
              Plan another party <i class="bi bi-arrow-right ms-1"></i>
            </button>
          </div>
        </div>

        <div class="col-lg-8">
          <div class="glass-card h-100">
            <div class="d-flex justify-content-between align-items-start mb-4">
              <div>
                <p class="text-orange fw-bold mb-1 small text-uppercase">Profile Snapshot</p>
                <h3 class="fw-bold mb-0">Your hosting hub</h3>
              </div>
              <span class="badge bg-light text-dark border px-3 py-2">AI Engine Active</span>
            </div>

            <div class="row g-3 mb-4">
              <div class="col-md-6" v-for="item in details" :key="item.label">
                <div class="profile-detail">
                  <span class="text-muted small">{{ item.label }}</span>
                  <strong>{{ item.value }}</strong>
                </div>
              </div>
            </div>

            <div class="row g-3">
              <div class="col-md-4" v-for="stat in stats" :key="stat.label">
                <div class="stat-card text-center">
                  <div class="fs-2 fw-bold text-orange">{{ stat.value }}</div>
                  <div class="small text-muted fw-semibold">{{ stat.label }}</div>
                </div>
              </div>
            </div>

            <div class="mt-4 p-3 rounded-4" style="background:#fff3eb;">
              <strong class="d-block mb-1">Catchy host line</strong>
              <span class="text-muted">You bring the people. SwiggyLabs handles the chaos, the cravings, and the split.</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getCurrentUser } from '@/api/client'

export default {
  name: 'ProfileView',
  data() {
    return {
      user: getCurrentUser(),
      defaultLocation: 'Add your favorite hosting location soon',
    }
  },
  computed: {
    initials() {
      const name = this.user?.name || 'Host'
      return name.split(' ').map(part => part[0]).join('').slice(0, 2).toUpperCase()
    },
    details() {
      return [
        { label: 'Name', value: this.user?.name || 'Not added' },
        { label: 'Phone', value: this.user?.phone_number || 'Not added' },
        { label: 'Email', value: this.user?.email || 'Not connected' },
        { label: 'Address / Location', value: this.defaultLocation },
      ]
    },
    stats() {
      return [
        { label: 'Parties organised', value: '∞' },
        { label: 'Chaos avoided', value: '100%' },
        { label: 'Bills split smarter', value: '₹' },
      ]
    },
  },
}
</script>

<style scoped>
.profile-section { padding: 60px 0 100px; min-height: calc(100vh - 72px); background: #f4f5f7; }
.profile-card { background: linear-gradient(180deg, #fff 0%, #fff8f3 100%); }
.avatar { width: 96px; height: 96px; border-radius: 50%; background: var(--brand-orange); color: white; display: flex; align-items: center; justify-content: center; font-size: 2rem; font-weight: 800; box-shadow: 0 15px 35px rgba(252,128,25,0.25); }
.profile-detail { background: #f8f9fa; border: 1px solid #eef0f4; border-radius: 16px; padding: 16px; display: flex; flex-direction: column; gap: 4px; min-height: 84px; }
.stat-card { background: white; border: 1px solid #eef0f4; border-radius: 18px; padding: 18px; }
</style>




