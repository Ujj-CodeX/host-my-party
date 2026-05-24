<template>
  <div>
    <!-- Dashboard Header -->
    <div class="bg-white border-bottom py-4 mb-4">
      <div class="container">
        <div class="row align-items-center">
          <div class="col-md-8">
            <p class="text-orange fw-bold mb-1 small text-uppercase">Food Delivery Orchestration Active</p>
            <h2 class="fw-bold mb-0">Coordinate the party. <span class="text-orange">Not the chaos.</span></h2>
          </div>
          <div class="col-md-4 text-md-end mt-3 mt-md-0">
            <div class="glass-card py-2 px-3 d-inline-block bg-light border">
              <span class="text-muted small d-block">Party Budget</span>
              <div class="d-flex align-items-center gap-2">
                <span class="fs-4 fw-bold">₹</span>
                <input
                  type="number"
                  v-model.number="budget"
                  class="form-control form-control-sm fw-bold fs-4 border-0 bg-transparent p-0 w-auto"
                  style="max-width: 80px;"
                />
                <i class="bi bi-pencil-square text-orange" style="cursor:pointer;"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="container main-content-area">
      <div class="row g-4">

        <!-- LEFT COLUMN -->
        <div class="col-lg-8">

          <!-- Strategy Selection -->
          <div class="glass-card mb-4">
            <h5 class="fw-bold mb-4">How should we coordinate this party?</h5>
            <div class="row g-3">
              <!-- Member-wise -->
              <div class="col-md-6">
                <div
                  class="strategy-card p-3 h-100"
                  :class="{ selected: strategy === 'member' }"
                  @click="strategy = 'member'">
                  <div class="d-flex justify-content-between align-items-start mb-2">
                    <h6 class="fw-bold mb-0">
                      <i class="bi bi-people-fill me-2" :class="strategy === 'member' ? 'text-orange' : 'text-muted'"></i>
                      Member-wise Order
                    </h6>
                    <i class="bi" :class="strategy === 'member' ? 'bi-check-circle-fill text-orange' : 'bi-circle text-muted'"></i>
                  </div>
                  <p class="text-muted small mb-3">Each guest orders individually based on preferences.</p>
                  <div class="d-flex flex-wrap gap-1">
                    <span class="badge bg-light text-dark border">Individual Meals</span>
                    <span class="badge bg-light text-dark border">Late Arrivals</span>
                  </div>
                </div>
              </div>

              <!-- Whole Party -->
              <div class="col-md-6">
                <div
                  class="strategy-card p-3 h-100"
                  :class="{ selected: strategy === 'whole' }"
                  @click="strategy = 'whole'">
                  <div class="d-flex justify-content-between align-items-start mb-2">
                    <h6 class="fw-bold mb-0">
                      <i class="bi bi-pie-chart-fill me-2" :class="strategy === 'whole' ? 'text-orange' : 'text-muted'"></i>
                      Whole Party Order
                    </h6>
                    <i class="bi" :class="strategy === 'whole' ? 'bi-check-circle-fill text-orange' : 'bi-circle text-muted'"></i>
                  </div>
                  <p class="text-muted small mb-3">Host places one optimized shared order for everyone.</p>
                  <div class="d-flex flex-wrap gap-1">
                    <span class="badge bg-light text-dark border">Shared Platters</span>
                    <span class="badge bg-light text-dark border">Combo Optimized</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Whole Party Guest Count -->
            <div v-if="strategy === 'whole'" class="mt-4 pt-3 border-top">
              <div class="d-flex justify-content-between align-items-center">
                <span class="fw-semibold">Total Number of Guests</span>
                <div class="quantity-stepper">
                  <button @click="partySize = Math.max(1, partySize - 1)"><i class="bi bi-dash"></i></button>
                  <span class="fw-bold fs-5 px-2">{{ partySize }}</span>
                  <button @click="partySize = Math.min(50, partySize + 1)"><i class="bi bi-plus"></i></button>
                </div>
              </div>
            </div>
          </div>

          <!-- Location -->
          <div class="glass-card mb-4">
            <div class="row g-3 align-items-center">
              <div class="col-md-7">
                <h5 class="fw-bold mb-3">Where's the party happening?</h5>
                <div class="mb-3">
                  <input type="text" v-model="location.address" class="form-control" placeholder="Full Address" />
                </div>
                <div class="row g-2">
                  <div class="col-6">
                    <input type="text" v-model="location.city" class="form-control form-control-sm" placeholder="City" />
                  </div>
                  <div class="col-6">
                    <input type="text" v-model="location.pin" class="form-control form-control-sm" placeholder="PIN Code" />
                  </div>
                </div>
                <button class="btn btn-sm btn-outline-orange mt-3">
                  <i class="bi bi-geo-alt"></i> Use Current Location
                </button>
              </div>
              <div class="col-md-5 h-100">
                <div class="ai-map-card p-3 text-center">
                  <div class="ai-map-scanner"></div>
                  <i class="bi bi-map text-white-50 fs-1 mb-2 d-block"></i>
                  <span class="small text-white-50">AI Location Synced</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Host / Shared Preferences -->
          <div class="glass-card mb-4">
            <div class="d-flex justify-content-between align-items-center mb-4">
              <h5 class="fw-bold mb-0">{{ strategy === 'member' ? 'Host Preferences' : 'Shared Party Preferences' }}</h5>
              <select v-model="hostPref" class="form-select form-select-sm w-auto">
                <option>Any Preference</option>
                <option>Pure Veg</option>
                <option>Non-Veg</option>
                <option>Jain</option>
                <option>Vegan</option>
              </select>
            </div>

            <!-- Food Category Cards -->
            <div class="row flex-nowrap overflow-auto pb-2" style="scrollbar-width: thin;">
              <div class="col-5 col-md-4 col-lg-3" v-for="cat in foodCategories" :key="cat.name">
                <div class="card h-100 border-0 shadow-sm text-center p-2 hover-lift">
                  <div class="fs-1 mb-2">{{ cat.emoji }}</div>
                  <h6 class="mb-1 fw-bold">{{ cat.name }}</h6>
                  <span class="small text-muted d-block mb-2">★ {{ cat.rating }} | {{ cat.time }}m</span>
                  <button class="btn btn-sm btn-outline-orange w-100" @click="startOrderFlow('host', 'Host')">
                    Order Now
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Member Management (only for member strategy) -->
          <div v-if="strategy === 'member'" class="glass-card mb-4">
            <div class="d-flex justify-content-between align-items-center mb-4">
              <h5 class="fw-bold mb-0">Who's joining the party?</h5>
              <button class="btn btn-sm btn-orange" @click="addGuest">
                <i class="bi bi-plus-lg"></i> Add Guest
              </button>
            </div>

            <div class="d-flex flex-column gap-3">
              <div
                v-for="member in members"
                :key="member.id"
                class="border rounded p-3 bg-white hover-lift">
                <div class="d-flex justify-content-between align-items-start mb-3">
                  <div class="d-flex align-items-center gap-2">
                    <div class="bg-light rounded-circle d-flex align-items-center justify-content-center fw-bold text-orange"
                      style="width:40px; height:40px;">
                      {{ member.name.charAt(0) }}
                    </div>
                    <div>
                      <h6 class="fw-bold mb-0">{{ member.name }}</h6>
                      <span class="small text-muted">
                        <span v-if="hasOrdered(member.name)">
                          <i class="bi bi-check-circle-fill text-success"></i> Ordered
                        </span>
                        <span v-else>Waiting to order</span>
                      </span>
                    </div>
                  </div>
                  <button class="btn btn-sm btn-light text-danger border-0" @click="removeMember(member.id)">
                    <i class="bi bi-trash"></i>
                  </button>
                </div>

                <div class="row g-2 align-items-center">
                  <div class="col-5">
                    <select v-model="member.pref" class="form-select form-select-sm">
                      <option>Any</option>
                      <option>Veg</option>
                      <option>Non-Veg</option>
                      <option>Vegan</option>
                      <option>Jain</option>
                      <option>Diabetic</option>
                    </select>
                  </div>
                  <div class="col-7 d-flex justify-content-end align-items-center gap-3">
                    <div class="form-check form-switch m-0">
                      <input class="form-check-input" type="checkbox" v-model="member.late" :id="'late-' + member.id" />
                      <label class="form-check-label small" :for="'late-' + member.id">Late</label>
                    </div>
                    <button
                      class="btn btn-sm"
                      :class="hasOrdered(member.name) ? 'btn-outline-success' : 'btn-outline-orange'"
                      @click="startOrderFlow(member.id, member.name)">
                      {{ hasOrdered(member.name) ? 'Edit Order' : 'Order' }}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

        </div>

        <!-- RIGHT COLUMN: Order Summary -->
        <div class="col-lg-4">
          <div class="glass-card sticky-summary">
            <h5 class="fw-bold mb-4 border-bottom pb-2">Order Summary</h5>

            <!-- Orders List -->
            <div class="mb-3 small">
              <div v-if="orders.length === 0" class="text-muted text-center py-3">
                No orders placed yet. Start orchestrating!
              </div>
              <div v-for="order in orders" :key="order.id" class="mb-3 border-bottom pb-2">
                <div class="d-flex justify-content-between align-items-center mb-1">
                  <span class="fw-bold text-dark">
                    <i class="bi bi-person-fill text-muted"></i> {{ order.who }}
                  </span>
                  <span class="fw-bold">₹{{ order.itemTotal }}</span>
                </div>
                <div class="text-muted" style="font-size:0.75rem;">
                  <i class="bi bi-shop"></i> {{ order.restaurant }} • ETA {{ order.eta }}m
                </div>
                <div class="text-muted fst-italic" style="font-size:0.75rem;">
                  {{ order.items.map(i => `${i.qty}x ${i.name}`).join(', ') }}
                </div>
              </div>
            </div>

            <!-- Bill Breakdown -->
            <div class="border-top pt-3 mb-4">
              <div class="d-flex justify-content-between small mb-2 text-muted">
                <span>Item Total</span><span>₹{{ billItemTotal }}</span>
              </div>
              <div class="d-flex justify-content-between small mb-2 text-muted">
                <span>Delivery Fee (Optimized)</span><span>₹{{ billDelivery }}</span>
              </div>
              <div class="d-flex justify-content-between small mb-2 text-muted">
                <span>Taxes & Platform Fee</span><span>₹{{ billTaxes }}</span>
              </div>
              <div class="d-flex justify-content-between fw-bold mt-2 pt-2 border-top fs-5">
                <span>Total</span><span>₹{{ billFinalTotal }}</span>
              </div>
            </div>

            <!-- Budget Tracker -->
            <div class="bg-light rounded p-3">
              <div class="d-flex justify-content-between align-items-end mb-2">
                <span class="small text-muted fw-semibold">Budget Tracker</span>
                <span class="fw-bold fs-6" :class="isOverBudget ? 'text-danger' : ''">
                  <span v-if="isOverBudget">Over by ₹{{ Math.abs(budgetLeft) }}</span>
                  <span v-else>₹{{ budgetLeft }} left</span>
                </span>
              </div>
              <div class="progress" style="height: 8px;">
                <div
                  class="progress-bar"
                  :class="budgetBarClass"
                  :style="{ width: budgetPercent + '%' }">
                </div>
              </div>
              <div class="text-end mt-1">
                <span class="small text-muted">of ₹{{ budget }}</span>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- Bottom Action Bar -->
    <div class="bottom-action-bar">
      <div class="container">
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <span class="fs-5 fw-bold d-block">₹{{ billFinalTotal }}</span>
            <a href="#" class="text-orange text-decoration-none small fw-semibold">
              View Detailed Bill <i class="bi bi-chevron-up"></i>
            </a>
          </div>
          <div class="d-flex gap-2">
            <button class="btn btn-outline-secondary d-none d-md-block px-4">Save Draft</button>
            <button class="btn btn-orange px-4 py-2 fs-6" @click="openCheckout">
              Proceed to Checkout <i class="bi bi-arrow-right ms-1"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ===== MODAL 1: AI Scan ===== -->
    <div v-if="showAiScan" class="vue-modal-backdrop" @click.self="showAiScan = false">
      <div class="vue-modal-box">
        <!-- Scanning State -->
        <div v-if="isScanning" class="p-4 text-center py-5">
          <div class="spinner-grow text-orange mb-3" style="width:3rem; height:3rem;" role="status"></div>
          <h5 class="fw-bold">AI Agent Searching...</h5>
          <p class="text-muted small">
            Scanning hyperlocal top-rated options for
            <span class="fw-bold text-dark">{{ currentOrderingFor }}</span>
          </p>
        </div>

        <!-- Results State -->
        <div v-else>
          <div class="p-3 border-bottom d-flex justify-content-between align-items-center">
            <h6 class="fw-bold mb-0">AI Recommended Matches</h6>
            <button class="btn-close" @click="showAiScan = false"></button>
          </div>
          <div class="p-3 bg-light">
            <div
              v-for="resto in restaurants"
              :key="resto.name"
              class="restaurant-item bg-white p-3 mb-2"
              @click="selectRestaurant(resto.name, resto.eta)">
              <div class="d-flex justify-content-between">
                <h6 class="fw-bold mb-1">{{ resto.name }}</h6>
                <span class="badge bg-success bg-opacity-10 text-success">
                  <i class="bi bi-stars"></i> {{ resto.match }}% Match
                </span>
              </div>
              <span class="small text-muted">★ {{ resto.rating }} | {{ resto.eta }} mins | ₹{{ resto.delivery }} Delivery</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ===== MODAL 2: Menu ===== -->
    <div v-if="showMenu" class="vue-modal-backdrop" @click.self="showMenu = false">
      <div class="vue-modal-box">
        <div class="p-3 border-bottom d-flex justify-content-between align-items-center">
          <div>
            <h5 class="fw-bold mb-0">{{ tempRestaurant }}</h5>
            <span class="small text-muted">ETA: {{ tempETA }} mins</span>
          </div>
          <button class="btn-close" @click="showMenu = false"></button>
        </div>

        <ul class="list-group list-group-flush">
          <li
            v-for="(item, idx) in tempMenuSelection"
            :key="idx"
            class="list-group-item d-flex justify-content-between align-items-center py-3">
            <div>
              <div class="fw-semibold">{{ item.name }}</div>
              <div class="small text-muted">₹{{ item.price }}</div>
            </div>
            <div class="quantity-stepper">
              <button v-if="item.qty > 0" class="btn btn-sm btn-outline-danger" @click="updateMenuQty(idx, -1)">
                <i class="bi bi-dash"></i>
              </button>
              <span v-if="item.qty > 0" class="fw-bold mx-2">{{ item.qty }}</span>
              <button class="btn btn-sm btn-outline-success" @click="updateMenuQty(idx, 1)">
                <i class="bi bi-plus"></i> {{ item.qty === 0 ? 'ADD' : '' }}
              </button>
            </div>
          </li>
        </ul>

        <div class="p-3 bg-light d-flex justify-content-between align-items-center">
          <div>
            <span class="text-muted small">Cart Total</span>
            <h5 class="fw-bold mb-0">₹{{ menuTempTotal }}</h5>
          </div>
          <button class="btn btn-orange px-4" @click="confirmMenuSelection">Done</button>
        </div>
      </div>
    </div>

    <!-- ===== MODAL 3: Checkout ===== -->
    <div v-if="showCheckout" class="vue-modal-backdrop" @click.self="showCheckout = false">
      <div class="vue-modal-box p-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h5 class="fw-bold mb-0">Select Payment Method</h5>
          <button class="btn-close" @click="showCheckout = false"></button>
        </div>

        <div v-if="!isProcessing">
          <div class="border rounded p-3 mb-2 d-flex align-items-center justify-content-between hover-lift bg-light"
            style="cursor:pointer;" @click="processPayment">
            <div class="d-flex align-items-center gap-3">
              <img src="https://upload.wikimedia.org/wikipedia/commons/e/e1/UPI-Logo-vector.svg" height="20" alt="UPI" />
              <span class="fw-semibold">Pay via UPI</span>
            </div>
            <i class="bi bi-chevron-right text-muted"></i>
          </div>
          <div class="border rounded p-3 d-flex align-items-center justify-content-between hover-lift"
            style="cursor:pointer;" @click="processPayment">
            <div class="d-flex align-items-center gap-3">
              <i class="bi bi-credit-card fs-4 text-secondary"></i>
              <span class="fw-semibold">Credit / Debit Cards</span>
            </div>
            <i class="bi bi-chevron-right text-muted"></i>
          </div>
        </div>

        <div v-else class="text-center py-4">
          <div class="spinner-border text-orange mb-3" role="status"></div>
          <h6 class="fw-bold">Processing securely...</h6>
        </div>
      </div>
    </div>

    <!-- ===== MODAL 4: Success ===== -->
    <div v-if="showSuccess" class="vue-modal-backdrop">
      <div class="vue-modal-box overflow-hidden">
        <div class="bg-success text-white text-center py-4">
          <i class="bi bi-check-circle-fill" style="font-size:3rem;"></i>
          <h4 class="fw-bold mt-2 mb-0">Party Orchestrated!</h4>
          <p class="small opacity-75 mb-0">AI has synchronized all deliveries.</p>
        </div>
        <div class="p-4 bg-light">
          <h6 class="fw-bold mb-3 text-center">Share with the group</h6>
          <div class="bg-white border rounded p-3 mb-3">
            <textarea
              :value="whatsappMessage"
              class="form-control border-0 bg-transparent p-0 text-dark small"
              rows="10"
              readonly
              style="resize:none; font-family:monospace;">
            </textarea>
          </div>
          <div class="d-flex gap-2">
            <button class="btn btn-outline-success w-50" @click="copyShareText">
              <i class="bi bi-copy me-1"></i>
              {{ copied ? 'Copied!' : 'Copy' }}
            </button>
            <button class="btn btn-success w-50" @click="resetAll">
              <i class="bi bi-whatsapp me-1"></i> Done
            </button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
export default {
  name: 'OrchestratorView',

  data() {
    return {
      budget: 4000,
      strategy: 'member',
      partySize: 4,
      hostPref: 'Any Preference',
      copied: false,

      location: {
        address: 'A-Block, Room 504, Signature Heights',
        city: 'Kondapur',
        pin: '500084'
      },

      members: [
        { id: 'm1', name: 'Rahul', pref: 'Non-Veg', late: false },
        { id: 'm2', name: 'Priya', pref: 'Veg', late: true },
        { id: 'm3', name: 'Aman', pref: 'Vegan', late: false },
        { id: 'm4', name: 'Sneha', pref: 'Jain', late: false }
      ],

      orders: [],

      foodCategories: [
        { name: 'Pizza', emoji: '🍕', rating: 4.2, time: 35 },
        { name: 'Burgers', emoji: '🍔', rating: 4.5, time: 25 },
        { name: 'Biryani', emoji: '🍗', rating: 4.1, time: 40 },
        { name: 'Chinese', emoji: '🍝', rating: 4.3, time: 30 }
      ],

      restaurants: [
        { name: "Domino's Pizza", eta: 30, rating: 4.4, delivery: 40, match: 98 },
        { name: 'Burger Singh', eta: 25, rating: 4.2, delivery: 30, match: 92 },
        { name: 'Behrouz Biryani', eta: 45, rating: 4.5, delivery: 50, match: 88 },
        { name: "La Pino'z Pizza", eta: 35, rating: 4.1, delivery: 40, match: 85 }
      ],

      dummyMenus: {
        "Domino's Pizza": [
          { name: 'Margherita Pizza (M)', price: 239, qty: 0 },
          { name: 'Peppy Paneer (M)', price: 399, qty: 0 },
          { name: 'Chicken Dominator (M)', price: 549, qty: 0 },
          { name: 'Garlic Breadsticks', price: 109, qty: 0 }
        ],
        'Burger Singh': [
          { name: 'United States of Punjab Burger', price: 189, qty: 0 },
          { name: 'Udta Punjab Burger', price: 249, qty: 0 },
          { name: 'Large Fries', price: 99, qty: 0 },
          { name: 'Coke (330ml)', price: 60, qty: 0 }
        ],
        'Behrouz Biryani': [
          { name: 'Subz-e-Falafel Biryani', price: 329, qty: 0 },
          { name: 'Murgh Afghani Biryani', price: 449, qty: 0 },
          { name: 'Gulab Jamun (2 pcs)', price: 89, qty: 0 }
        ],
        "La Pino'z Pizza": [
          { name: 'Cheesy 7 Pizza', price: 345, qty: 0 },
          { name: 'Burn to Hell Pizza', price: 425, qty: 0 },
          { name: 'Choco Lava Cake', price: 110, qty: 0 }
        ]
      },

      // Modal states
      showAiScan: false,
      isScanning: false,
      showMenu: false,
      showCheckout: false,
      showSuccess: false,
      isProcessing: false,

      // Temp order state
      currentOrderingForId: null,
      currentOrderingFor: '',
      tempRestaurant: null,
      tempETA: 0,
      tempMenuSelection: [],

      whatsappMessage: ''
    }
  },

  computed: {
    billItemTotal() {
      return this.orders.reduce((sum, o) => sum + o.itemTotal, 0)
    },
    billDelivery() {
      const unique = new Set(this.orders.map(o => o.restaurant)).size
      return unique > 0 ? 30 + unique * 10 : 0
    },
    billTaxes() {
      return Math.round(this.billItemTotal * 0.05 + (this.orders.length > 0 ? 15 : 0))
    },
    billFinalTotal() {
      return this.billItemTotal + this.billDelivery + this.billTaxes
    },
    budgetLeft() {
      return this.budget - this.billFinalTotal
    },
    isOverBudget() {
      return this.billFinalTotal > this.budget
    },
    budgetPercent() {
      return Math.min((this.billFinalTotal / this.budget) * 100, 100)
    },
    budgetBarClass() {
      if (this.isOverBudget) return 'bg-danger'
      if (this.budgetPercent > 85) return 'bg-warning'
      return 'progress-bar-swiggy'
    },
    menuTempTotal() {
      return this.tempMenuSelection.reduce((sum, i) => sum + i.price * i.qty, 0)
    }
  },

  methods: {
    hasOrdered(name) {
      return this.orders.some(o => o.who === name)
    },

    addGuest() {
      const names = ['Karan', 'Neha', 'Vikram', 'Anjali', 'Rohan']
      const name = names[Math.floor(Math.random() * names.length)]
      this.members.push({ id: 'm' + Date.now(), name, pref: 'Any', late: false })
    },

    removeMember(id) {
      const member = this.members.find(m => m.id === id)
      if (member) {
        this.orders = this.orders.filter(o => o.who !== member.name)
      }
      this.members = this.members.filter(m => m.id !== id)
    },

    startOrderFlow(id, name) {
      this.currentOrderingForId = id
      this.currentOrderingFor = name
      this.isScanning = true
      this.showAiScan = true

      setTimeout(() => { this.isScanning = false }, 1800)
    },

    selectRestaurant(name, eta) {
      this.showAiScan = false
      this.tempRestaurant = name
      this.tempETA = eta
      this.tempMenuSelection = this.dummyMenus[name].map(item => ({ ...item, qty: 0 }))
      setTimeout(() => { this.showMenu = true }, 300)
    },

    updateMenuQty(idx, change) {
      const newQty = this.tempMenuSelection[idx].qty + change
      if (newQty >= 0) {
        this.tempMenuSelection[idx] = { ...this.tempMenuSelection[idx], qty: newQty }
        this.tempMenuSelection = [...this.tempMenuSelection]
      }
    },

    confirmMenuSelection() {
      const selected = this.tempMenuSelection.filter(i => i.qty > 0)
      if (selected.length === 0) {
        alert('Please add items to cart.')
        return
      }
      const itemTotal = selected.reduce((sum, i) => sum + i.price * i.qty, 0)
      this.orders = this.orders.filter(o => o.who !== this.currentOrderingFor)
      this.orders.push({
        id: Date.now(),
        who: this.currentOrderingFor,
        restaurant: this.tempRestaurant,
        eta: this.tempETA,
        items: selected,
        itemTotal
      })
      this.showMenu = false
    },

    openCheckout() {
      if (this.orders.length === 0) {
        alert('Please add some orders before checking out!')
        return
      }
      this.isProcessing = false
      this.showCheckout = true
    },

    processPayment() {
      this.isProcessing = true
      setTimeout(() => {
        this.showCheckout = false
        this.generateWhatsAppMessage()
        this.showSuccess = true
      }, 2000)
    },

    generateWhatsAppMessage() {
      let msg = `🎉 *PARTY DETAILS* 🎉\n\n`
      msg += `📍 *Venue:*\n${this.location.address}, ${this.location.city}\n\n`
      msg += `🍕 *Orders:*\n`
      this.orders.forEach(o => {
        const itemsStr = o.items.map(i => i.name).join(', ')
        msg += `• ${o.who} → ${itemsStr} (${o.restaurant})\n`
      })

      const lateMembers = this.members.filter(m => m.late).map(m => m.name)
      if (this.strategy === 'member' && lateMembers.length > 0) {
        msg += `\n⏰ *Late Arrivals (AI Delayed Order):*\n${lateMembers.join(', ')}\n`
      }

      const maxEta = Math.max(...this.orders.map(o => o.eta))
      msg += `\n🚴 *Max ETA:* ${maxEta} mins\n`
      msg += `\n💰 *Total:* ₹${this.billFinalTotal}`
      msg += `\n🔗 *UPI Split Link:*\nupi://pay?pa=ujju@upi&pn=Ujju&am=${Math.round(this.billFinalTotal / this.members.length)}\n`

      this.whatsappMessage = msg
    },

    copyShareText() {
      navigator.clipboard.writeText(this.whatsappMessage)
      this.copied = true
      setTimeout(() => { this.copied = false }, 2000)
    },

    resetAll() {
      this.showSuccess = false
      this.orders = []
      this.$router.push('/')
    }
  }
}
</script>

<style scoped>
.main-content-area {
  padding-bottom: 100px;
}
.sticky-summary {
  position: sticky;
  top: 90px;
  z-index: 10;
}
.bottom-action-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  background: white;
  box-shadow: 0 -4px 20px rgba(0,0,0,0.08);
  z-index: 1050;
  padding: 1rem 0;
}
</style>