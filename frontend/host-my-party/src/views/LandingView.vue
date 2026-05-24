<template>
  <div class="container py-5">
    <div class="text-center mb-5 mt-4">
      <h1 class="display-5 fw-bold text-dark">How are we partying tonight, <span class="text-orange">Ujjawal</span>?</h1>
      <p class="text-muted fs-5 mt-3">Choose the smart experience you want to orchestrate for your Birthday.</p>
    </div>

    <div class="row g-4 justify-content-center">
      <!-- Card 1: Food Delivery -->
      <div class="col-lg-4 col-md-6">
        <div class="glass-card card-orange-glow hover-lift h-100 position-relative"
          @click="$router.push('/orchestrator')">
          <span class="badge bg-orange mb-3">Hyperlocal</span>
          <h3 class="fw-bold mb-3">Food Delivery<br>Party</h3>
          <p class="text-muted small mb-4">
            Coordinate multi-cart orders across individual food combinations perfectly timed by AI.
          </p>
          <div class="d-flex flex-wrap gap-2 mb-4">
            <span class="badge rounded-pill border text-dark">Jain</span>
            <span class="badge rounded-pill border text-dark">Vegan</span>
            <span class="badge rounded-pill border text-dark">Non-Veg</span>
            <span class="badge rounded-pill border text-dark">Diabetic</span>
          </div>
          <div class="mt-auto">
            <span class="text-orange fw-semibold small">
              <i class="bi bi-house-door-fill me-1"></i> Best for home parties
            </span>
          </div>
        </div>
      </div>

      <!-- Card 2: Dineout (Coming Soon) -->
      <div class="col-lg-4 col-md-6">
        <div class="glass-card card-purple-glow hover-lift h-100 opacity-75">
          <span class="badge mb-3" style="background: var(--brand-purple);">Premium</span>
          <h3 class="fw-bold mb-3 mt-3">Dineout<br>Experience</h3>
          <p class="text-muted small">
            Reserve premium lounge seating with AI pre-ordering and dynamic split bills.
          </p>
          <div class="mt-auto pt-4">
            <span class="text-muted fw-semibold small">
              <i class="bi bi-geo-alt-fill me-1"></i> Lounge & Clubs
            </span>
          </div>
        </div>
      </div>

      <!-- Card 3: Instamart (Coming Soon) -->
      <div class="col-lg-4 col-md-6">
        <div class="glass-card card-green-glow hover-lift h-100 opacity-75">
          <span class="badge bg-success mb-3">Flash Bash</span>
          <h3 class="fw-bold mb-3">Instamart<br>Gathering</h3>
          <p class="text-muted small">
            Instant delivery of snacks, beverages, and party props in 10 minutes.
          </p>
          <div class="mt-auto pt-4">
            <span class="text-muted fw-semibold small">
              <i class="bi bi-lightning-charge-fill me-1"></i> Quick setup
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LandingView'
}
</script>

<style scoped>
.card-orange-glow:hover {
  border-color: var(--brand-orange);
  box-shadow: 0 0 20px rgba(252, 128, 25, 0.15);
}
.card-purple-glow:hover {
  border-color: var(--brand-purple);
  box-shadow: 0 0 20px rgba(138, 43, 226, 0.15);
}
.card-green-glow:hover {
  border-color: var(--brand-green);
  box-shadow: 0 0 20px rgba(46, 204, 113, 0.15);
}
</style>