<template>
  <div class="auth-section d-flex align-items-center justify-content-center">
    <div class="auth-card">
      <h3 class="fw-bold mb-1">Create your account</h3>
      <p class="text-muted mb-4">Host parties. Not chaos.</p>

      <div v-if="error" class="alert alert-danger py-2 small">{{ error }}</div>

      <form @submit.prevent="submit">
        <div class="mb-3">
          <label class="form-label fw-semibold small">Full Name</label>
          <input v-model="name" type="text" class="form-control" required />
        </div>
        <div class="mb-3">
          <label class="form-label fw-semibold small">Phone Number</label>
          <input v-model="phone" type="tel" class="form-control" placeholder="9876543210" required />
        </div>
        <div class="mb-4">
          <label class="form-label fw-semibold small">Password</label>
          <input v-model="password" type="password" class="form-control" minlength="8" required />
          <span class="text-muted small">At least 8 characters.</span>
        </div>
        <button class="btn btn-orange w-100 py-2" :disabled="loading">
          {{ loading ? 'Creating account…' : 'Sign Up' }}
        </button>
      </form>

      <p class="text-center mt-4 small text-muted">
        Already have an account? <router-link to="/login">Log in</router-link>
      </p>
    </div>
  </div>
</template>

<script>
import { signupPhone } from '@/api/auth'

export default {
  name: 'SignupView',
  data() {
    return { name: '', phone: '', password: '', error: '', loading: false }
  },
  methods: {
    async submit() {
      this.error = ''
      this.loading = true
      try {
        await signupPhone({ phone_number: this.phone, password: this.password, name: this.name })
        const redirect = this.$route.query.redirect || '/'
        this.$router.push(redirect)
      } catch (e) {
        const body = e.body
        this.error = body ? Object.values(body).flat().join(' ') : 'Signup failed.'
      } finally {
        this.loading = false
      }
    },
  },
}
</script>

<style scoped>
.auth-section { min-height: calc(100vh - 72px); background: #f4f5f7; padding: 40px 16px; }
.auth-card {
  background: white; border-radius: 20px; padding: 2.5rem;
  width: 100%; max-width: 420px; box-shadow: 0 10px 40px rgba(40,44,63,0.08);
}
</style>