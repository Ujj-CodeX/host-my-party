
<template>
  <div class="container py-5">
    <div class="glass-card mx-auto" style="max-width:760px">
      <div v-if="!session" class="text-center py-5">
        <h3 class="fw-bold">No guest session found</h3>
        <p class="text-muted">Open your host's invite link again.</p>
      </div>

      <div v-else>
        <p class="text-orange fw-bold mb-1">Guest Order</p>
        <h2 class="fw-bold mb-4">Hi {{ session.guest.name }}, choose your meal</h2>
        <div v-if="success" class="alert alert-success">Order placed! The host dashboard will update.</div>

        <div class="row g-3">
          <div v-for="rest in restaurants" :key="rest.id" class="col-md-6">
            <div class="border rounded p-3 h-100">
              <h5 class="fw-bold">{{ rest.name }}</h5>
              <p class="text-muted small mb-2">★ {{ rest.rating }} • {{ rest.deliveryTime }}</p>

              <div v-for="item in menuFor(rest)" :key="item.id" class="d-flex justify-content-between align-items-center border-top py-2">
                <span>{{ item.name }} <small class="text-muted">₹{{ item.price }}</small></span>
                <button class="btn btn-sm btn-outline-orange" @click="addItem(rest, item)">Add</button>
              </div>
            </div>
          </div>
        </div>

        <div class="mt-4 border-top pt-3">
          <h5 class="fw-bold">Cart</h5>
          <p v-if="cart.length === 0" class="text-muted">No items added.</p>

          <div v-for="(item, idx) in cart" :key="idx" class="d-flex justify-content-between">
            <span>{{ item.quantity }}x {{ item.name }}</span>
            <strong>₹{{ item.unit_price * item.quantity }}</strong>
          </div>

          <button class="btn btn-orange w-100 mt-3 py-3" :disabled="cart.length === 0 || placing" @click="placeOrder">
            {{ placing ? 'Placing...' : `Place Order • ₹${total}` }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { apiRequest, getGuestSession } from '@/api/client'

export default {
  name: 'GuestOrderView',
  data() {
    return {
      session: getGuestSession(),
      restaurants: [],
      selectedRestaurant: null,
      cart: [],
      placing: false,
      success: false,
    }
  },
  computed: {
    total() {
      return this.cart.reduce((sum, item) => sum + item.unit_price * item.quantity, 0)
    },
  },
  async mounted() {
    if (!this.session) return

    const data = await apiRequest('/ai/guest/restaurants/', { method: 'GET', guest: true }).catch(() => null)
    this.restaurants = data?.restaurants || this.fallbackRestaurants()
  },
  methods: {
    menuFor(rest) {
      return rest.eligibleMenu || rest.menu || []
    },
    addItem(rest, item) {
      if (this.selectedRestaurant && this.selectedRestaurant.id !== rest.id) this.cart = []
      this.selectedRestaurant = rest

      const found = this.cart.find((cartItem) => cartItem.external_item_id === item.id)
      if (found) {
        found.quantity += 1
      } else {
        this.cart.push({
          external_item_id: item.id,
          name: item.name,
          unit_price: item.price,
          quantity: 1,
          is_veg: Boolean(item.isVeg),
          is_jain_compatible: Boolean(item.isJainCompatible),
          is_diabetic_friendly: Boolean(item.isDiabeticFriendly),
        })
      }
    },
    async placeOrder() {
      this.placing = true

      try {
        await apiRequest('/guest/orders/', {
          method: 'POST',
          guest: true,
          body: {
            placed_by: 'guest',
            restaurant_id: this.selectedRestaurant.id,
            restaurant_name: this.selectedRestaurant.name,
            items: this.cart,
          },
        })
        this.success = true
        this.cart = []
      } finally {
        this.placing = false
      }
    },
    fallbackRestaurants() {
      return [
        {
          id: 'rest_001',
          name: 'Punjab Grill',
          rating: 4.3,
          deliveryTime: '30-35 mins',
          menu: [
            { id: 'item_001', name: 'Paneer Butter Masala', price: 280, isVeg: true },
            { id: 'item_003', name: 'Chicken Tikka', price: 320, isVeg: false },
          ],
        },
      ]
    },
  },
}
</script>




