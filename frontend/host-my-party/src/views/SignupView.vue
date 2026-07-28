<template>
  <div class="auth-section">
    <div class="auth-card glass-card">
      <h2 class="fw-bold mb-1">Create your host account</h2>
      <p class="text-muted mb-4">Save parties, invite guests, and checkout securely.</p>

      <form @submit.prevent="submit">
        <div class="mb-3">
          <label class="form-label fw-semibold">Name</label>
          <input v-model="form.name" class="form-control form-control-lg" required placeholder="Amit Sharma" />
        </div>

        <div class="mb-3">
          <label class="form-label fw-semibold">Phone Number</label>
          <input v-model="form.phone_number" class="form-control form-control-lg" required placeholder="9876543210" />
        </div>

        <div class="mb-3">
          <label class="form-label fw-semibold">Password</label>
          <input v-model="form.password" type="password" minlength="8" class="form-control form-control-lg" required />
        </div>

        <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>

        <button class="btn btn-orange w-100 py-3" :disabled="loading">
          {{ loading ? 'Creating...' : 'Sign up' }}
        </button>
      </form>

      <p class="text-center text-muted mt-4 mb-0">
        Already registered?
        <router-link to="/login" class="text-orange fw-bold">Login</router-link>
      </p>
    </div>
  </div>
</template>

<script>
import { authApi } from '@/api/client'

export default {
  name: 'SignupView',
  data() {
    return {
      form: { name: '', phone_number: '', password: '' },
      loading: false,
      error: '',
    }
  },
  methods: {
    async submit() {
      this.loading = true
      this.error = ''

      try {
        await authApi.signup(this.form)
        this.$router.push(this.$route.query.redirect || '/selection')
      } catch (e) {
        this.error = e.data ? Object.values(e.data).flat().join(' ') : e.message
      } finally {
        this.loading = false
      }
    },
  },
}
</script>

<style scoped>
.auth-section {
  min-height: calc(100vh - 72px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px 16px;
  background: #f4f5f7;
}
.auth-card {
  max-width: 500px;
  width: 100%;
  background: white;
}
</style>



