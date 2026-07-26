<template>
  <div>
    <!-- STATE 1: Landing Hero -->
    <div v-if="currentState === 'landing'" class="landing-hero">
      <section class="hero-section">
        <div class="container">
          <div class="row align-items-center g-5">

            <!-- Left Hero Content -->
            <div class="col-lg-6">
              <h1 class="headline">Host parties.<br><span class="text-orange-brand">Not chaos.</span></h1>
              <h2 class="subheading">AI-powered party orchestration using Swiggy Food, Instamart, and Dineout.</h2>
              <p class="supporting-text mt-3 mb-5">
                Handle complex dietary conflicts, asynchronous multi-order delivery timelines, precise budget optimization, and instant group bill-splitting effortlessly down to the last rupee.
              </p>
              <div class="d-flex flex-row gap-3">
                <button class="btn-swiggy-primary btn-lg px-4 fs-6" @click="handleStartPlanning">
                  Start Planning <i class="bi bi-arrow-right ms-2"></i>
                </button>
                <button class="btn-swiggy-outline btn-lg px-4 fs-6" @click="alert('Demo feature coming soon!')">
                  Watch Demo <i class="bi bi-play-circle ms-2"></i>
                </button>
              </div>
            </div>

            <!-- Right Floating Cards -->
            <div class="col-lg-6 mt-5 mt-lg-0">
              <div class="preview-card-container">

                <!-- Card 1: Timeline -->
                <div class="floating-card card-timeline">
                  <h6 class="fw-bold text-dark mb-3 d-flex align-items-center">
                    <i class="bi bi-clock-history text-warning me-2"></i> Timeline Orchestrator
                  </h6>
                  <div class="timeline-item">
                    <div class="timeline-icon badge-instamart"><i class="bi bi-lightning-charge-fill"></i></div>
                    <div><strong class="d-block">Instamart Delivery</strong><span class="text-muted small">Mixers & Ice • 7:00 PM</span></div>
                  </div>
                  <div class="timeline-item">
                    <div class="timeline-icon badge-food"><i class="bi bi-egg-fried"></i></div>
                    <div><strong class="d-block">Main Course Food</strong><span class="text-muted small">3 Restaurants • 7:30 PM</span></div>
                  </div>
                  <div class="timeline-item mb-0">
                    <div class="timeline-icon badge-late"><i class="bi bi-person-fill-dash"></i></div>
                    <div><strong class="d-block">Rahul (Guest)</strong><span class="text-muted small">Running Late • 8:15 PM</span></div>
                  </div>
                </div>

                <!-- Card 2: AI Engine -->
                <div class="floating-card card-conflict">
                  <div class="d-flex justify-content-between align-items-center mb-2">
                    <h6 class="fw-bold m-0 text-dark"><i class="bi bi-shield-check text-success me-1"></i> AI Engine</h6>
                    <span class="badge bg-success rounded-pill px-2 py-1" style="font-size:0.65rem;">Resolved</span>
                  </div>
                  <p class="text-muted small mb-3">Scanning dietary profiles & smart group budgets...</p>
                  <div class="mb-2">
                    <span class="conflict-tag"><i class="bi bi-check2"></i> Jain Found</span>
                    <span class="conflict-tag"><i class="bi bi-wallet2"></i> Budget Optimized</span>
                    <span class="conflict-tag"><i class="bi bi-heart-pulse"></i> 4 Allergies Safe</span>
                  </div>
                </div>

                <!-- Card 3: Bill Split -->
                <div class="floating-card card-split">
                  <h6 class="fw-bold text-dark mb-3"><i class="bi bi-currency-rupee me-1" style="color:var(--swiggy-orange)"></i> Shared Bill Split</h6>
                  <div class="split-row">
                    <span><i class="bi bi-person-circle me-1 text-secondary"></i> Priya</span>
                    <strong class="text-dark">₹280</strong>
                  </div>
                  <div class="split-row">
                    <span><i class="bi bi-person-circle me-1 text-secondary"></i> Rahul</span>
                    <strong class="text-dark">₹340</strong>
                  </div>
                  <div class="split-row mb-3">
                    <span><i class="bi bi-person-circle me-1 text-secondary"></i> Arjun</span>
                    <strong class="text-dark">₹260</strong>
                  </div>
                  <button
                    class="btn btn-sm w-100 fw-bold py-2"
                    style="background:#fff3eb; color: var(--swiggy-orange); border:none; border-radius:10px;"
                    @click="() => {}">
                    <i class="bi bi-link-45deg me-1"></i> Copy UPI Group Links
                  </button>
                </div>

              </div>
            </div>

          </div>
        </div>
      </section>
    </div>

    <!-- STATE 2: Planning Modal -->
    <div v-if="showModal" class="vue-modal-backdrop" @click.self="showModal = false">
      <div class="vue-modal-box modal-content-custom p-4" style="max-width:480px;">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <h5 class="fw-bold fs-4 text-dark mb-0">Configure Your Event</h5>
          <button class="btn-close" @click="showModal = false"></button>
        </div>

        <div>
          <!-- Budget & Guest Count -->
          <div class="row g-3 mb-4">
            <div class="col-6">
              <label class="form-label form-label-custom">Total Budget (₹)</label>
              <input
                type="number"
                class="form-control form-control-custom"
                v-model.number="form.budget"
                placeholder="e.g., 5000"
                min="500"
              />
            </div>
            <div class="col-6">
              <label class="form-label form-label-custom">Total Guests</label>
              <input
                type="number"
                class="form-control form-control-custom"
                v-model.number="form.guestCount"
                placeholder="e.g., 8"
                min="1"
              />
            </div>
          </div>

          <!-- Occasion Chips -->
          <div class="mb-4">
            <label class="form-label form-label-custom d-block mb-2">Occasion Type</label>
            <div class="occasion-grid">
              <div
                v-for="occ in occasions"
                :key="occ.value"
                class="occasion-chip"
                :class="{ active: form.occasion === occ.value }"
                @click="form.occasion = occ.value"
              >
                {{ occ.label }}
              </div>
            </div>
          </div>

          <button
            class="btn-swiggy-primary w-100 py-3 fs-6"
            :disabled="!form.budget || !form.guestCount"
            @click="handleContinue"
          >
            Continue To Mode Selection <i class="bi bi-chevron-right ms-1"></i>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { isAuthenticated } from '@/api/client'

export default {
  name: 'LandingView',
  data() {
    return {
      currentState: 'landing',
      showModal: false,
      form: {
        budget: null,
        guestCount: null,
        occasion: 'Birthday'
      },
      occasions: [
        { value: 'Birthday', label: '🎉 Birthday' },
        { value: 'Game Night', label: '🎮 Game Night' },
        { value: 'Office Treat', label: '💼 Office Treat' },
        { value: 'House Party', label: '🏠 House Party' }
      ]
    }
  },
  methods: {
    handleStartPlanning() {
      if (!isAuthenticated()) {
        this.$router.push({ path: '/login', query: { redirect: '/selection' } })
        return
      }
      this.showModal = true
    },
    handleContinue() {
      if (!this.form.budget || !this.form.guestCount) return
      this.showModal = false
      // hostName now comes from the logged-in User (account/serializers.py
      // UserSerializer), not a free-text field — SelectionView/Orchestrator
      // read it off the party's nested `host` object instead.
      this.$router.push({
        path: '/selection',
        query: {
          budget: this.form.budget,
          guestCount: this.form.guestCount,
          occasion: this.form.occasion
        }
      })
    }
  }
}
</script>

<style scoped>
/* Hero Layout */
.hero-section {
  padding: 100px 0 140px 0;
  background: radial-gradient(circle at 90% 10%, rgba(252, 128, 25, 0.04) 0%, rgba(255,255,255,1) 70%);
}
.text-orange-brand { color: var(--brand-orange); }

.headline {
  font-size: 4rem;
  font-weight: 800;
  letter-spacing: -1.5px;
  line-height: 1.1;
  color: #1a1c24;
}
.subheading {
  font-size: 1.35rem;
  font-weight: 600;
  color: #282c3f;
  margin-top: 24px;
}
.supporting-text {
  font-size: 1.05rem;
  color: #686b78;
  max-width: 520px;
}

/* Buttons */
.btn-swiggy-primary {
  background-color: var(--brand-orange);
  color: white;
  font-weight: 700;
  padding: 14px 32px;
  border-radius: 12px;
  border: none;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(252, 128, 25, 0.3);
  cursor: pointer;
}
.btn-swiggy-primary:hover:not(:disabled) {
  background-color: #e26d0b;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 15px 30px rgba(252, 128, 25, 0.2);
}
.btn-swiggy-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.btn-swiggy-outline {
  background-color: transparent;
  color: #282c3f;
  font-weight: 600;
  padding: 14px 32px;
  border-radius: 12px;
  border: 2px solid #e0e2e8;
  transition: all 0.3s ease;
  cursor: pointer;
}
.btn-swiggy-outline:hover {
  background-color: #f4f5f7;
  border-color: #282c3f;
  transform: translateY(-2px);
}

/* Floating Cards */
.preview-card-container {
  position: relative;
  height: 480px;
  width: 100%;
}
.floating-card {
  position: absolute;
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 12px 40px rgba(40, 44, 63, 0.08);
  border: 1px solid rgba(40, 44, 63, 0.04);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.floating-card:hover {
  transform: translateY(-5px) scale(1.02) !important;
  box-shadow: 0 20px 40px rgba(40, 44, 63, 0.12);
  z-index: 10 !important;
}
.card-timeline {
  top: 10px; left: 10%; width: 290px; z-index: 3;
  animation: float1 5s ease-in-out infinite;
}
.card-conflict {
  top: 130px; right: 5%; width: 280px; z-index: 2;
  animation: float2 6s ease-in-out infinite;
  border-left: 4px solid var(--brand-orange);
}
.card-split {
  bottom: 10px; left: 20%; width: 280px; z-index: 1;
  animation: float3 5.5s ease-in-out infinite;
}

@keyframes float1 { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-12px)} }
@keyframes float2 { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-15px)} }
@keyframes float3 { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-10px)} }

.timeline-item {
  display: flex; align-items: center; margin-bottom: 12px; font-size: 0.9rem;
}
.timeline-icon {
  width: 32px; height: 32px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  margin-right: 12px; font-size: 0.9rem;
}
.badge-instamart { background-color: #ecfdf3; color: #039855; }
.badge-food { background-color: #fff3eb; color: var(--brand-orange); }
.badge-late { background-color: #f2f4f7; color: #667085; }

.conflict-tag {
  background: rgba(252,128,25,0.15); color: var(--brand-orange);
  font-size: 0.8rem; font-weight: 600; padding: 4px 10px;
  border-radius: 6px; display: inline-block; margin-right: 6px; margin-bottom: 6px;
}
.split-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 6px 0; border-bottom: 1px dashed #f0f1f5; font-size: 0.9rem;
}

/* Modal Styling */
.modal-content-custom {
  border-radius: 24px; border: none;
}
.form-control-custom {
  border: 2px solid #e0e2e8; border-radius: 12px; padding: 12px 16px;
  font-weight: 500; transition: all 0.2s ease;
}
.form-control-custom:focus {
  border-color: var(--brand-orange);
  box-shadow: 0 0 0 4px rgba(252,128,25,0.15);
  outline: none;
}
.form-label-custom {
  font-weight: 600; font-size: 0.9rem; color: #282c3f; margin-bottom: 8px;
}
.occasion-grid {
  display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;
}
.occasion-chip {
  border: 2px solid #e0e2e8; border-radius: 12px; padding: 12px;
  text-align: center; font-weight: 600; cursor: pointer;
  transition: all 0.2s ease; background: white; user-select: none;
}
.occasion-chip:hover { border-color: #282c3f; background-color: #f4f5f7; }
.occasion-chip.active {
  border-color: var(--brand-orange);
  background-color: rgba(252,128,25,0.1);
  color: var(--brand-orange);
}
</style>