<template>
  <div class="container py-5">
    <div class="glass-card text-center mx-auto" style="max-width:720px">
      <div class="display-4 mb-3">🍽️</div>
      <h2 class="fw-bold">Dineout Experience</h2>
      <p class="text-muted fs-5">
        The backend route is ready for dineout bookings. This frontend screen keeps the current layout and marks the experience as coming soon.
      </p>
      <button class="btn btn-orange px-4" @click="$router.push('/selection')">Back to selection</button>
    </div>
  </div>
</template>

<script>
export default { name: 'DineoutView' }
</script>
