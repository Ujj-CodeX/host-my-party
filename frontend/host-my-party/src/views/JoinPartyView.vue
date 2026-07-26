<template>
  <div class="container py-5">
    <div class="glass-card mx-auto" style="max-width:560px">
      <div v-if="loading" class="text-center py-5 text-muted">Loading party...</div>

      <div v-else>
        <p class="text-orange fw-bold mb-1">Guest Invite</p>
        <h2 class="fw-bold">Join {{ party.host_name }}'s {{ party.occasion || 'party' }}</h2>
        <p class="text-muted">Tell the host your food preference, then place your own order.</p>

        <form @submit.prevent="join">
          <div class="mb-3">
            <label class="form-label fw-semibold">Your Name</label>
            <input v-model="form.name" class="form-control" required />
          </div>

          <div class="mb-3">
            <label class="form-label fw-semibold">Dietary Preference</label>
            <select v-model="form.dietary_pref" class="form-select">
              <option value="any">Any</option>
              <option value="veg">Veg</option>
              <option value="non_veg">Non-Veg</option>
              <option value="vegan">Vegan</option>
              <option value="jain">Jain</option>
              <option value="diabetic">Diabetic</option>
            </select>
          </div>

          <div class="form-check form-switch mb-3">
            <input id="late" v-model="form.is_late" class="form-check-input" type="checkbox" />
            <label for="late" class="form-check-label">I will arrive late</label>
          </div>

          <div v-if="form.is_late" class="mb-3">
            <label class="form-label fw-semibold">Late by minutes</label>
            <input v-model.number="form.late_offset_minutes" type="number" min="5" class="form-control" />
          </div>

          <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>

          <button class="btn btn-orange w-100 py-3" :disabled="submitting">
            {{ submitting ? 'Joining...' : 'Join & Order' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { apiRequest, setGuestSession } from '@/api/client'

export default {
  name: 'JoinPartyView',
  props: {
    code: { type: String, required: true },
  },
  data() {
    return {
      loading: true,
      submitting: false,
      error: '',
      party: {},
      form: {
        name: '',
        dietary_pref: 'any',
        is_late: false,
        late_offset_minutes: 30,
      },
    }
  },
  async mounted() {
    try {
      this.party = await apiRequest(`/join/${this.code}/`)
    } catch (e) {
      this.error = e.message
    } finally {
      this.loading = false
    }
  },
  methods: {
    async join() {
      this.submitting = true
      this.error = ''

      try {
        const payload = {
          ...this.form,
          late_offset_minutes: this.form.is_late ? this.form.late_offset_minutes : null,
        }
        const data = await apiRequest(`/join/${this.code}/`, { method: 'POST', body: payload })
        setGuestSession({ ...data, party: this.party, code: this.code })
        this.$router.push('/guest-order')
      } catch (e) {
        this.error = e.data ? Object.values(e.data).flat().join(' ') : e.message
      } finally {
        this.submitting = false
      }
    },
  },
}
</script>
