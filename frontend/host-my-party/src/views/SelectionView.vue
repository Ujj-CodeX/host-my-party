<template>
  <div class="selection-section">
    <div class="container">
      <div class="text-center mb-5">
        <h2 class="selection-title">How are we partying tonight, <span class="text-orange-brand">{{ hostName }}</span>?</h2>
        <p class="text-muted fs-5">Choose the smart experience you want to orchestrate for your <span class="fw-bold text-dark">{{ occasion }}</span>.</p>
        <div class="config-summary mt-3">
          <span class="config-pill"><i class="bi bi-people-fill me-1"></i>{{ guestCount }} Guests</span>
          <span class="config-pill"><i class="bi bi-currency-rupee me-1"></i>₹{{ budget }} Budget</span>
          <span class="config-pill"><i class="bi bi-calendar-event me-1"></i>{{ occasion }}</span>
        </div>
        <div v-if="error" class="alert alert-danger d-inline-block mt-3 py-2 small">{{ error }}</div>
      </div>

      <div class="row g-4 justify-content-center">
        <div class="col-lg-4 col-md-6">
          <div class="mode-card card-food-delivery" :class="{ 'pe-none opacity-50': creating }" @click="selectMode('food_delivery')">
            <div>
              <div class="d-flex justify-content-between align-items-start">
                <div class="icon-box" style="background:#fff3eb; color:var(--brand-orange)"><i class="bi bi-egg-fried fs-3"></i></div>
                <span class="badge bg-light text-dark border px-2 py-1 small fw-bold"><i class="bi bi-lightning text-warning"></i> Hyperlocal</span>
              </div>
              <h4 class="fw-bold text-dark mt-4 mb-2">Food Delivery Party</h4>
              <p class="text-muted small mb-3">Coordinate multi-cart orders across individual food combinations, tracking dietary exceptions synchronously.</p>
              <div class="visual-display-area text-center"><div class="w-100">
                <div class="mb-2 text-muted fw-bold small">Active Scan Profile:</div>
                <span class="dietary-badge text-success">● Jain</span><span class="dietary-badge text-success">● Vegan</span>
                <span class="dietary-badge text-danger">● Non-Veg</span><span class="dietary-badge text-primary">● Diabetic</span>
              </div></div>
            </div>
            <span class="badge-footer-tag"><i class="bi bi-house-heart me-1 text-danger"></i> Best for home parties</span>
          </div>
        </div>

        <div class="col-lg-4 col-md-6">
          <div class="mode-card card-dineout" :class="{ 'pe-none opacity-50': creating }" @click="selectMode('dineout')">
            <div>
              <div class="d-flex justify-content-between align-items-start">
                <div class="icon-box" style="background:#f5ecff; color:#8f00ff"><i class="bi bi-shop fs-3"></i></div>
                <span class="badge bg-light text-dark border px-2 py-1 small fw-bold"><i class="bi bi-star-fill text-warning"></i> Premium Lounge</span>
              </div>
              <h4 class="fw-bold text-dark mt-4 mb-2">Dineout Experience</h4>
              <p class="text-muted small mb-3">Secure a table, filter by dietary fit and capacity, and book directly — no per-guest ordering to manage.</p>
              <div class="visual-display-area"><div class="text-center w-100">
                <div class="d-flex justify-content-center align-items-center gap-2 mb-2"><span class="badge bg-dark px-3 py-2"><i class="bi bi-calendar-event"></i> Table reserved</span></div>
                <small class="text-muted d-block font-monospace">Capacity Check: Verified OK</small>
              </div></div>
            </div>
            <span class="badge-footer-tag"><i class="bi bi-award me-1 text-warning"></i> Book now</span>
          </div>
        </div>
      </div>

      <div class="text-center mt-5"><button class="btn btn-link text-decoration-none text-secondary fw-bold" @click="$router.push('/')"><i class="bi bi-arrow-left"></i> Change Configuration Details</button></div>
    </div>
  </div>
</template>

<script>
import { createParty } from '@/api/party'
import { getCurrentUser } from '@/api/client'

export default {
  name: 'SelectionView',
  data() { return { creating: false, error: '' } },
  computed: {
    hostName() { return getCurrentUser()?.name || this.$route.query.hostName || 'Host' },
    budget() { return Number(this.$route.query.budget || 0) },
    guestCount() { return Number(this.$route.query.guestCount || 0) },
    occasion() { return this.$route.query.occasion || 'Event' },
  },
  methods: {
    async selectMode(mode) {
      if (this.creating || !['food_delivery', 'dineout'].includes(mode)) return
      this.creating = true
      this.error = ''
      try {
        const payload = {
          mode,
          occasion: this.occasion,
          budget: this.budget,
          expected_guest_count: this.guestCount,
        }
        if (mode === 'food_delivery') payload.strategy = 'member'
        const party = await createParty(payload)
        this.$router.push({ path: mode === 'food_delivery' ? '/orchestrator' : '/dineout', query: { code: party.code } })
      } catch (e) {
        this.error = e.body?.detail || e.message || 'Could not create the party. Please try again.'
      } finally {
        this.creating = false
      }
    },
  },
}
</script>

<style scoped>
.selection-section { padding:60px 0 100px; background-color:#f4f5f7; min-height:calc(100vh - 72px); }
.text-orange-brand { color:var(--brand-orange); }
.selection-title { font-weight:800; font-size:2.5rem; color:#1a1c24; letter-spacing:-0.5px; }
.config-summary { display:flex; justify-content:center; gap:12px; flex-wrap:wrap; }
.config-pill { background:white; border:1px solid #e0e2e8; border-radius:30px; padding:6px 16px; font-size:.85rem; font-weight:600; color:#282c3f; }
.mode-card { background:white; border-radius:24px; border:none; padding:32px; height:100%; display:flex; flex-direction:column; justify-content:space-between; box-shadow:0 4px 20px rgba(40,44,63,.03); transition:all .4s cubic-bezier(.165,.84,.44,1); position:relative; overflow:hidden; cursor:pointer; }
.mode-card::before { content:''; position:absolute; top:0; left:0; width:100%; height:5px; background:transparent; transition:background .3s ease; }
.mode-card:hover { transform:translateY(-8px); box-shadow:0 20px 40px rgba(40,44,63,.12); }
.card-food-delivery:hover::before { background:var(--brand-orange); }.card-food-delivery:hover { box-shadow:0 20px 40px rgba(252,128,25,.15); }
.card-dineout:hover::before { background:#8f00ff; }.card-dineout:hover { box-shadow:0 20px 40px rgba(143,0,255,.12); }
.icon-box { padding:12px; border-radius:12px; display:inline-flex; align-items:center; justify-content:center; }
.visual-display-area { background-color:#f4f5f7; border-radius:16px; padding:20px; margin:20px 0; min-height:120px; display:flex; align-items:center; justify-content:center; }
.dietary-badge { font-size:.75rem; font-weight:700; padding:4px 10px; border-radius:20px; background:white; border:1px solid #e0e2e8; margin:3px; display:inline-block; }
.badge-footer-tag { font-size:.8rem; font-weight:700; color:#686b78; background:#eef0f4; padding:6px 14px; border-radius:30px; display:inline-block; margin-top:auto; text-align:center; width:100%; }
</style>
