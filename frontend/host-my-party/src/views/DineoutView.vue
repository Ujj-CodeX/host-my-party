<template>
  <div class="dineout-section">
    <div class="bg-white border-bottom py-4 mb-4">
      <div class="container d-flex flex-column flex-lg-row justify-content-between gap-3">
        <div>
          <p class="text-orange fw-bold mb-1 small text-uppercase">Dineout Orchestration Active</p>
          <h2 class="fw-bold mb-0">Reserve tables. <span class="text-orange">Not confusion.</span></h2>
          <p class="text-muted mb-0">Groq-assisted mock Dineout matching for seats, dietary fit, timing, and budget.</p>
        </div>
        <div class="glass-card py-2 px-3 bg-light border align-self-start">
          <span class="text-muted small d-block">Budget</span>
          <strong class="fs-4">₹{{ form.budget }}</strong>
        </div>
      </div>
    </div>

    <div class="container main-content-area">
      <div class="row g-4">
        <div class="col-lg-4">
          <div class="glass-card sticky-summary">
            <h5 class="fw-bold mb-4">Dineout details</h5>

            <div class="mb-3">
              <label class="form-label fw-semibold">Location</label>
              <input v-model="form.location" class="form-control" placeholder="Kondapur, Hyderabad" />
            </div>

            <div class="row g-2 mb-3">
              <div class="col-6">
                <label class="form-label fw-semibold">Members</label>
                <input v-model.number="form.guest_count" type="number" min="1" class="form-control" />
              </div>
              <div class="col-6">
                <label class="form-label fw-semibold">Budget ₹</label>
                <input v-model.number="form.budget" type="number" min="500" class="form-control" />
              </div>
            </div>

            <div class="row g-2 mb-3">
              <div class="col-6">
                <label class="form-label fw-semibold">Date</label>
                <input v-model="form.date" type="date" class="form-control" />
              </div>
              <div class="col-6">
                <label class="form-label fw-semibold">Arrival</label>
                <input v-model="form.time" type="time" class="form-control" />
              </div>
            </div>

            <div class="mb-3">
              <label class="form-label fw-semibold d-block">Dietary needs</label>
              <div class="d-flex flex-wrap gap-2">
                <button v-for="pref in dietaryOptions" :key="pref" type="button" class="pref-chip" :class="{ active: form.dietary_prefs.includes(pref) }" @click="togglePref(pref)">
                  {{ pref }}
                </button>
              </div>
            </div>

            <div class="mb-4">
              <label class="form-label fw-semibold">Special request</label>
              <textarea v-model="form.special_request" class="form-control" rows="3" placeholder="Birthday table, quiet corner, Jain-friendly service..."></textarea>
            </div>

            <button class="btn btn-orange w-100 py-3" :disabled="loading" @click="findRestaurants">
              <i class="bi bi-stars me-1"></i>{{ loading ? 'Scanning...' : 'Find Dineout Matches' }}
            </button>
          </div>
        </div>

        <div class="col-lg-8">
          <div class="glass-card mb-4">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <div>
                <h5 class="fw-bold mb-1">Groq ranked restaurants</h5>
                <p class="text-muted small mb-0">Filtered by location radius, dietary needs, seat availability, arrival slots, and budget guard.</p>
              </div>
              <span class="badge bg-light text-dark border">{{ restaurants.length }} matches</span>
            </div>

            <div v-if="loading" class="text-center text-muted py-5">AI is checking Dineout mock data...</div>
            <div v-else-if="restaurants.length === 0" class="text-center text-muted py-5">Add details and scan for Dineout restaurants.</div>

            <div v-else class="row g-3">
              <div v-for="restaurant in restaurants" :key="restaurant.id" class="col-md-6">
                <div class="dineout-card h-100" :class="{ selected: selectedRestaurant?.id === restaurant.id }" @click="selectRestaurant(restaurant)">
                  <div class="d-flex justify-content-between align-items-start mb-2">
                    <h5 class="fw-bold mb-0">{{ restaurant.name }}</h5>
                    <span class="badge" :class="restaurant.budgetStatus === 'ok' ? 'bg-success' : 'bg-warning text-dark'">
                      {{ restaurant.budgetStatus === 'ok' ? 'Budget OK' : 'Over budget' }}
                    </span>
                  </div>
                  <p class="text-muted small mb-2">{{ restaurant.cuisines.join(', ') }}</p>
                  <div class="d-flex flex-wrap gap-2 small mb-3">
                    <span class="info-pill">★ {{ restaurant.rating }}</span>
                    <span class="info-pill">{{ restaurant.distanceKm }} km</span>
                    <span class="info-pill">Seats {{ restaurant.seatingCapacity }}</span>
                    <span class="info-pill">₹{{ restaurant.estimatedPerHead }}/head</span>
                  </div>
                  <p class="small text-muted mb-0"><i class="bi bi-cpu text-orange me-1"></i>{{ restaurant.aiReason }}</p>
                </div>
              </div>
            </div>
          </div>

          <div v-if="selectedRestaurant" class="glass-card mb-4">
            <div class="d-flex flex-column flex-md-row justify-content-between gap-3">
              <div>
                <p class="text-orange fw-bold mb-1 small text-uppercase">Selected Restaurant</p>
                <h4 class="fw-bold mb-1">{{ selectedRestaurant.name }}</h4>
                <p class="text-muted mb-0">{{ selectedRestaurant.budgetNote }}</p>
              </div>
              <div class="text-md-end">
                <span class="text-muted small d-block">Estimated Total</span>
                <strong class="fs-3">₹{{ selectedRestaurant.estimatedTotal }}</strong>
              </div>
            </div>

            <div class="mt-4">
              <h6 class="fw-bold">Available slots</h6>
              <div class="d-flex flex-wrap gap-2">
                <button v-for="slot in slots" :key="slot" class="slot-chip" :class="{ active: selectedSlot === slot }" @click="selectedSlot = slot">
                  {{ slot }}
                </button>
              </div>
            </div>

            <button class="btn btn-orange w-100 py-3 mt-4" :disabled="!selectedSlot || paying" @click="mockPayment">
              {{ paying ? 'Processing mock payment...' : 'Reserve Table & Mock Pay' }}
            </button>
          </div>

          <div v-if="confirmation" class="glass-card success-card">
            <div class="d-flex justify-content-between align-items-start mb-3">
              <div>
                <p class="text-success fw-bold mb-1"><i class="bi bi-check-circle-fill me-1"></i>Booking Confirmed</p>
                <h4 class="fw-bold mb-0">{{ confirmation.restaurant_name }}</h4>
              </div>
              <span class="badge bg-success">{{ confirmation.booking_reference }}</span>
            </div>
            <textarea v-model="whatsappMessage" class="form-control mb-3" rows="8" readonly></textarea>
            <button class="btn btn-outline-success w-100" @click="copyShareText">
              <i class="bi bi-copy me-1"></i>{{ copied ? 'Copied!' : 'Copy WhatsApp Message' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { apiRequest } from '@/api/client'

export default {
  name: 'DineoutView',
  data() {
    const tomorrow = new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString().slice(0, 10)
    return {
      form: {
        location: this.$route.query.location || 'Kondapur, Hyderabad',
        guest_count: Number(this.$route.query.guestCount) || 4,
        budget: Number(this.$route.query.budget) || 4000,
        date: tomorrow,
        time: '20:00',
        dietary_prefs: ['Any'],
        special_request: this.$route.query.occasion ? `${this.$route.query.occasion} celebration` : '',
      },
      dietaryOptions: ['Any', 'Veg', 'Non-Veg', 'Vegan', 'Jain', 'Diabetic'],
      restaurants: [],
      selectedRestaurant: null,
      selectedSlot: '',
      slots: [],
      loading: false,
      paying: false,
      confirmation: null,
      whatsappMessage: '',
      copied: false,
      partyCode: '',
    }
  },
  methods: {
    togglePref(pref) {
      if (pref === 'Any') {
        this.form.dietary_prefs = ['Any']
        return
      }
      this.form.dietary_prefs = this.form.dietary_prefs.filter(item => item !== 'Any')
      if (this.form.dietary_prefs.includes(pref)) {
        this.form.dietary_prefs = this.form.dietary_prefs.filter(item => item !== pref)
      } else {
        this.form.dietary_prefs.push(pref)
      }
      if (this.form.dietary_prefs.length === 0) this.form.dietary_prefs = ['Any']
    },
    async findRestaurants() {
      this.loading = true
      this.selectedRestaurant = null
      this.confirmation = null
      try {
        const data = await apiRequest('/ai/dineout/restaurants/', { method: 'POST', body: this.form })
        this.restaurants = data.restaurants || []
      } catch {
        this.restaurants = []
      } finally {
        this.loading = false
      }
    },
    async selectRestaurant(restaurant) {
      this.selectedRestaurant = restaurant
      this.selectedSlot = ''
      const data = await apiRequest('/ai/dineout/slots/', {
        method: 'POST',
        body: { restaurant_id: restaurant.id, date: this.form.date, guest_count: this.form.guest_count },
      }).catch(() => ({ slots: [] }))
      this.slots = data.slots || []
    },
    async ensureParty() {
      if (this.partyCode) return
      const party = await apiRequest('/parties/', {
        method: 'POST',
        body: {
          mode: 'dineout',
          occasion: this.$route.query.occasion || 'Dineout Party',
          budget: this.form.budget,
          expected_guest_count: this.form.guest_count,
          delivery_address: this.form.location,
          status: 'active',
          party_start_time: `${this.form.date}T${this.selectedSlot || this.form.time}:00Z`,
        },
      })
      this.partyCode = party.code
    },
    async mockPayment() {
      this.paying = true
      try {
        await this.ensureParty()
        const booked = await apiRequest('/ai/dineout/book/', {
          method: 'POST',
          body: {
            restaurant_id: this.selectedRestaurant.id,
            date: this.form.date,
            time: this.selectedSlot,
            guest_count: this.form.guest_count,
            special_request: this.form.special_request,
          },
        })
        await apiRequest(`/parties/${this.partyCode}/booking/`, {
          method: 'POST',
          body: {
            restaurant_id: this.selectedRestaurant.id,
            restaurant_name: this.selectedRestaurant.name,
            seating_capacity_required: this.form.guest_count,
            arrival_time: `${this.form.date}T${this.selectedSlot}:00Z`,
            special_request: this.form.special_request,
          },
        }).catch(() => null)
        this.confirmation = booked
        this.generateWhatsAppMessage()
      } finally {
        this.paying = false
      }
    },
    generateWhatsAppMessage() {
      this.whatsappMessage = `🍽️ *DINEOUT PARTY CONFIRMED*\n\n📍 *Restaurant:* ${this.selectedRestaurant.name}\n🗓️ *Date:* ${this.form.date}\n⏰ *Arrival:* ${this.selectedSlot}\n👥 *Members:* ${this.form.guest_count}\n🥗 *Dietary:* ${this.form.dietary_prefs.join(', ')}\n💰 *Estimated total:* ₹${this.selectedRestaurant.estimatedTotal}\n\n${this.form.special_request ? `📝 *Note:* ${this.form.special_request}\n\n` : ''}See you there! SwiggyLabs handled the chaos.`
    },
    copyShareText() {
      navigator.clipboard.writeText(this.whatsappMessage)
      this.copied = true
      setTimeout(() => { this.copied = false }, 2000)
    },
  },
}
</script>

<style scoped>
.dineout-section { min-height: calc(100vh - 72px); background: #f4f5f7; padding-bottom: 100px; }
.main-content-area { padding-bottom: 40px; }
.sticky-summary { position: sticky; top: 90px; }
.pref-chip, .slot-chip { border: 1px solid #e0e2e8; background: white; border-radius: 999px; padding: 8px 14px; font-weight: 700; color: #686b78; }
.pref-chip.active, .slot-chip.active { background: var(--brand-orange); color: white; border-color: var(--brand-orange); }
.dineout-card { background: white; border: 1px solid #eef0f4; border-radius: 18px; padding: 18px; cursor: pointer; transition: all 0.25s ease; }
.dineout-card:hover, .dineout-card.selected { transform: translateY(-4px); border-color: var(--brand-orange); box-shadow: 0 18px 35px rgba(252,128,25,0.12); }
.info-pill { background: #f4f5f7; border-radius: 999px; padding: 5px 10px; font-weight: 700; }
.success-card { border: 1px solid rgba(46, 204, 113, 0.3); }
</style>
       



