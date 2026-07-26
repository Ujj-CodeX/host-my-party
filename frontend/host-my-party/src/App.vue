<template>
  <div>
    <!-- Global Navbar -->
    <nav class="navbar swiggy-nav py-3">
      <div class="container">
        <a class="navbar-brand fw-bold d-flex align-items-center" href="#" @click.prevent="$router.push('/')">
          <span class="fs-4 text-orange me-2"><i class="bi bi-box-seam-fill"></i></span>
          SwiggyLabs
        </a>
        <div class="d-flex align-items-center gap-3">
          <span class="px-3 py-1 ai-pill fw-medium d-none d-sm-inline-block">
            <i class="bi bi-cpu-fill me-1"></i> AI Engine Active
          </span>
          <button v-if="!isAuthed" class="btn btn-sm btn-outline-orange px-3" @click="$router.push('/login')">
            Login
          </button>
          <button v-else class="rounded-circle bg-light d-flex align-items-center justify-content-center border profile-button"
            title="Open profile" @click="$router.push('/profile')">
            <i class="bi bi-person-fill text-muted"></i>
          </button>
        </div>
      </div>
    </nav>

    <!-- Floating Background Decor -->
    <i class="bi bi-cup-straw floating-icon" style="top: 15%; left: 10%;"></i>
    <i class="bi bi-music-note-beamed floating-icon" style="top: 40%; right: 5%;"></i>
    <i class="bi bi-stars floating-icon" style="bottom: 20%; left: 15%;"></i>

    <!-- Router View -->
    <router-view />
  </div>
</template>

<script>
import { isAuthenticated } from '@/api/client'

export default {
  name: 'App',
  data() {
    return { isAuthed: isAuthenticated() }
  },
  watch: {
    $route() {
      this.isAuthed = isAuthenticated()
    }
  }
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
@import url('https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css');

:root {
  --brand-orange: #FC8019;
  --brand-orange-hover: #e06d12;
  --brand-purple: #8A2BE2;
  --brand-green: #2ecc71;
  --bg-light: #f8f9fa;
  --text-main: #282c3f;
  --text-muted: #686b78;
  --glass-bg: rgba(255, 255, 255, 0.95);
  --glass-border: rgba(255, 255, 255, 0.2);
}

* { box-sizing: border-box; }

body {
  font-family: 'Poppins', sans-serif;
  background-color: var(--bg-light);
  color: var(--text-main);
  overflow-x: hidden;
  scroll-behavior: smooth;
  margin: 0;
}

.text-orange { color: var(--brand-orange) !important; }
.bg-orange { background-color: var(--brand-orange) !important; }

.btn-orange {
  background-color: var(--brand-orange);
  color: white;
  font-weight: 600;
  border: none;
  cursor: pointer;
}
.btn-orange:hover { background-color: var(--brand-orange-hover); color: white; }

.btn-outline-orange {
  border: 1px solid var(--brand-orange);
  color: var(--brand-orange);
  font-weight: 500;
  background: transparent;
  cursor: pointer;
}
.btn-outline-orange:hover { background-color: var(--brand-orange); color: white; }

.profile-button {
  width: 40px;
  height: 40px;
  cursor: pointer;
}

.swiggy-nav {
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 15px rgba(0,0,0,0.04);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.ai-pill {
  background: rgba(46, 204, 113, 0.1);
  color: var(--brand-green);
  border: 1px solid rgba(46, 204, 113, 0.3);
  border-radius: 50px;
  font-size: 0.8rem;
  animation: pulse-green 2s infinite;
}

.glass-card {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.03);
  padding: 1.5rem;
}

.hover-lift {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.hover-lift:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0,0,0,0.08);
  cursor: pointer;
}

.floating-icon {
  position: fixed;
  opacity: 0.05;
  font-size: 3rem;
  z-index: -1;
}

.quantity-stepper { display: flex; align-items: center; gap: 10px; }
.quantity-stepper button {
  width: 32px; height: 32px;
  border-radius: 50%;
  border: 1px solid #ccc;
  background: white;
  font-weight: bold;
  cursor: pointer;
}

/* Vue Modal Overlay */
.vue-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}
.vue-modal-box {
  background: white;
  border-radius: 16px;
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  animation: modalIn 0.3s ease;
}
@keyframes modalIn {
  from { transform: scale(0.9); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

.progress-bar-swiggy { background-color: var(--brand-orange); transition: width 0.4s ease; }

@keyframes pulse-green {
  0% { box-shadow: 0 0 0 0 rgba(46, 204, 113, 0.4); }
  70% { box-shadow: 0 0 0 10px rgba(46, 204, 113, 0); }
  100% { box-shadow: 0 0 0 0 rgba(46, 204, 113, 0); }
}

@keyframes ai-scan {
  0% { top: -10%; opacity: 0; }
  50% { opacity: 1; }
  100% { top: 110%; opacity: 0; }
}

.ai-map-card {
  background: #1a1a2e;
  border-radius: 12px;
  height: 100%;
  min-height: 150px;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}
.ai-map-scanner {
  position: absolute;
  width: 100%;
  height: 20px;
  background: linear-gradient(to bottom, transparent, var(--brand-orange));
  animation: ai-scan 3s linear infinite;
}

.strategy-card {
  border: 2px solid #eee;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}
.strategy-card.selected {
  border-color: var(--brand-orange);
  background-color: rgba(252, 128, 25, 0.05);
}

.restaurant-item {
  border: 1px solid #eee;
  border-radius: 12px;
  transition: all 0.2s;
  cursor: pointer;
}
.restaurant-item:hover {
  border-color: var(--brand-orange);
  background: #fffcf9;
}

.form-control:focus, .form-select:focus {
  border-color: var(--brand-orange) !important;
  box-shadow: 0 0 0 0.25rem rgba(252, 128, 25, 0.25) !important;
}
</style>