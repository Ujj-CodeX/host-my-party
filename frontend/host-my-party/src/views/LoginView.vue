<template>
  <div class="auth-section">
    <div class="auth-card glass-card">
      <h2 class="fw-bold mb-1">Welcome back</h2>
      <p class="text-muted mb-4">Login with your phone number to continue planning.</p>

      <form @submit.prevent="submit">
        <div class="mb-3">
          <label class="form-label fw-semibold">Phone Number</label>
          <input v-model="form.phone_number" class="form-control form-control-lg" required placeholder="9876543210" />
        </div>

        <div class="mb-3">
          <label class="form-label fw-semibold">Password</label>
          <input v-model="form.password" type="password" class="form-control form-control-lg" required />
        </div>

        <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>

        <button class="btn btn-orange w-100 py-3" :disabled="loading">
          {{ loading ? 'Logging in...' : 'Login' }}
        </button>
      </form>

      <p class="text-center text-muted mt-4 mb-0">
        New here?
        <router-link to="/signup" class="text-orange fw-bold">Create account</router-link>
      </p>
    </div>
  </div>
</template>

<script>
import { authApi } from '@/api/client'

export default {
  name: 'LoginView',
  data() {
    return {
      form: { phone_number: '', password: '' },
      loading: false,
      error: '',
    }
  },
  methods: {
    async submit() {
      this.loading = true
      this.error = ''

      try {
        await authApi.login(this.form)
        this.$router.push(this.$route.query.redirect || '/')
      } catch (e) {
        this.error = e.message
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
  max-width: 460px;
  width: 100%;
  background: white;
}
</style>
