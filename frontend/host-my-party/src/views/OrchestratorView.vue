<template>
  <div>
    <!-- Dashboard Header -->
    <div class="bg-white border-bottom py-4 mb-4">
      <div class="container">
        <div class="row align-items-center">
          <div class="col-md-8">
            <p class="text-orange fw-bold mb-1 small text-uppercase">
              Food Delivery Orchestration Active
              <span v-if="occasion" class="ms-2 badge bg-light text-dark border">{{ occasion }}</span>
            </p>
            <h2 class="fw-bold mb-0">
              {{ hostName ? hostName + "'s Party" : 'Coordinate the party.' }}
              <span class="text-orange">Not the chaos.</span>
            </h2>
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
              <div class="col-md-6">
                <div class="strategy-card p-3 h-100" :class="{ selected: strategy === 'member' }" @click="strategy = 'member'">
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
              <div class="col-md-6">
                <div class="strategy-card p-3 h-100" :class="{ selected: strategy === 'whole' }" @click="strategy = 'whole'">
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
              
            </div>
          </div>

          <!-- Host / Shared Preferences + Order -->
          <div class="glass-card mb-4">
            <div class="d-flex justify-content-between align-items-center mb-4">
              <h5 class="fw-bold mb-0">{{ strategy === 'member' ? 'Host Order' : 'Shared Party Order' }}</h5>
              <span class="badge bg-light text-dark border">
                <i class="bi bi-person-fill text-orange me-1"></i>{{ hostName || 'Host' }}
              </span>
            </div>
            <div class="row flex-nowrap overflow-auto pb-2" style="scrollbar-width: thin;">
              <div class="col-5 col-md-4 col-lg-3" v-for="cat in foodCategories" :key="cat.name">
                <div class="card h-100 border-0 shadow-sm text-center p-2 hover-lift">
                  <div class="fs-1 mb-2">{{ cat.emoji }}</div>
                  <h6 class="mb-1 fw-bold">{{ cat.name }}</h6>
                  <span class="small text-muted d-block mb-2">★ {{ cat.rating }} | {{ cat.time }}m</span>
                  <button class="btn btn-sm btn-outline-orange w-100" @click="startOrderFlow('host', hostName || 'Host', 'Any', false, 0, cat.name)">
                    Order Now
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Member Management (member strategy only) -->
          <div v-if="strategy === 'member'" class="glass-card mb-4">
            <div class="d-flex justify-content-between align-items-center mb-4">
              <h5 class="fw-bold mb-0">Who's joining the party?</h5>
              <button class="btn btn-sm btn-orange" @click="addGuest">
                <i class="bi bi-plus-lg"></i> Add Guest
              </button>
            </div>

            <div class="d-flex flex-column gap-3">
              <div v-for="member in members" :key="member.id" class="border rounded p-3 bg-white hover-lift">
                <div class="d-flex justify-content-between align-items-start mb-3">
                  <div class="d-flex align-items-center gap-2">
                    <div class="bg-light rounded-circle d-flex align-items-center justify-content-center fw-bold text-orange"
                      style="width:40px; height:40px;">
                      {{ member.name.charAt(0) }}
                    </div>
                    <div>
                      <h6 class="fw-bold mb-0">
                        {{ member.name }}
                        <span v-if="member.isHost" class="badge bg-orange ms-1" style="font-size:0.65rem;">Host</span>
                      </h6>
                      <span class="small text-muted">
                        <span v-if="hasOrdered(member.name)">
                          <i class="bi bi-check-circle-fill text-success"></i> Ordered
                        </span>
                        <span v-else-if="member.late && getScheduledOrder(member.name)" class="text-warning">
                          <i class="bi bi-clock-history"></i>
                          Fires at {{ getScheduledOrder(member.name).fire_at }}
                          <span class="text-muted ms-1 fst-italic" style="font-size:0.7rem;">
                            ({{ getScheduledOrder(member.name).reasoning }})
                          </span>
                        </span>
                        <span v-else>Waiting to order</span>
                      </span>
                    </div>
                  </div>
                  <button
                    v-if="!member.isHost"
                    class="btn btn-sm btn-light text-danger border-0"
                    @click="removeMember(member.id)">
                    <i class="bi bi-trash"></i>
                  </button>
                </div>

                <div class="row g-2 align-items-center">
                  <div class="col-4">
                    <select v-model="member.pref" class="form-select form-select-sm">
                      <option>Any</option>
                      <option>Veg</option>
                      <option>Non-Veg</option>
                      <option>Vegan</option>
                      <option>Jain</option>
                      <option>Diabetic</option>
                    </select>
                  </div>
                  <!-- Late arrival toggle + minutes -->
                  <div class="col-5 d-flex align-items-center gap-2">
                    <div class="form-check form-switch m-0">
                      <input class="form-check-input" type="checkbox" v-model="member.late" :id="'late-' + member.id" />
                      <label class="form-check-label small" :for="'late-' + member.id">Late</label>
                    </div>
                    <div v-if="member.late" class="d-flex align-items-center gap-1">
                      <input
                        type="number"
                        v-model.number="member.lateMinutes"
                        class="form-control form-control-sm"
                        style="width:54px;"
                        min="5" max="120" placeholder="30"
                      />
                      <span class="small text-muted">min</span>
                    </div>
                  </div>
                  <div class="col-3 d-flex justify-content-end">
                    <button
                      class="btn btn-sm"
                      :class="hasOrdered(member.name) ? 'btn-outline-success' : 'btn-outline-orange'"
                      @click="startOrderFlow(member.id, member.name, member.pref, member.late, member.lateMinutes)">
                      {{ hasOrdered(member.name) ? 'Edit' : 'Order' }}
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

            <div class="mb-3 small">
              <div v-if="orders.length === 0" class="text-muted text-center py-3">
                No orders placed yet. Start orchestrating!
              </div>
              <div v-for="order in orders" :key="order.id" class="mb-3 border-bottom pb-2">
                <div class="d-flex justify-content-between align-items-center mb-1">
                  <span class="fw-bold text-dark">
                    <i class="bi bi-person-fill text-muted"></i> {{ order.who }}
                    <span v-if="order.isLate" class="badge bg-warning text-dark ms-1" style="font-size:0.65rem;">
                      <i class="bi bi-clock"></i> Late
                    </span>
                  </span>
                  <span class="fw-bold">₹{{ order.itemTotal }}</span>
                </div>
                <div class="text-muted" style="font-size:0.75rem;">
                  <i class="bi bi-shop"></i> {{ order.restaurant }}
                  • <i class="bi bi-geo-alt"></i> {{ order.distanceKm }}km
                  • ETA {{ order.eta }}m
                </div>
                <div class="text-muted fst-italic" style="font-size:0.75rem;">
                  {{ orderItemsLabel(order) }}
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
                <div class="progress-bar" :class="budgetBarClass" :style="{ width: budgetPercent + '%' }"></div>
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
            <button class="btn btn-outline-secondary d-none d-md-block px-4" @click="savePartyOrders">Save Draft</button>
            <button class="btn btn-orange px-4 py-2 fs-6" @click="openCheckout">
              Proceed to Checkout <i class="bi bi-arrow-right ms-1"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ===== MODAL 0: Add Guest ===== -->
    <div v-if="showAddGuest" class="vue-modal-backdrop" @click.self="showAddGuest = false">
      <div class="vue-modal-box p-4" style="max-width: 420px;">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h5 class="fw-bold mb-0"><i class="bi bi-person-plus-fill text-orange me-2"></i>Add Guest</h5>
          <button class="btn-close" @click="showAddGuest = false"></button>
        </div>

        <div class="mb-3">
          <label class="form-label fw-semibold small">Guest Name</label>
          <input
            type="text"
            class="form-control"
            v-model="newGuest.name"
            placeholder="e.g. Rahul, Priya..."
            @keyup.enter="confirmAddGuest"
            autofocus
          />
        </div>

        <div class="mb-3">
          <label class="form-label fw-semibold small">Dietary Preference</label>
          <select v-model="newGuest.pref" class="form-select">
            <option>Any</option>
            <option>Veg</option>
            <option>Non-Veg</option>
            <option>Vegan</option>
            <option>Jain</option>
            <option>Diabetic</option>
          </select>
        </div>

        <div class="mb-4 d-flex align-items-center gap-3">
          <div class="form-check form-switch m-0">
            <input class="form-check-input" type="checkbox" v-model="newGuest.late" id="newGuestLate" />
            <label class="form-check-label fw-semibold small" for="newGuestLate">Arriving Late?</label>
          </div>
          <div v-if="newGuest.late" class="d-flex align-items-center gap-2">
            <input
              type="number"
              v-model.number="newGuest.lateMinutes"
              class="form-control form-control-sm"
              style="width:64px;"
              min="5" max="120"
            />
            <span class="small text-muted">mins late</span>
          </div>
        </div>

        <div class="d-flex gap-2">
          <button class="btn btn-outline-secondary flex-fill" @click="showAddGuest = false">Cancel</button>
          <button
            class="btn btn-orange flex-fill"
            :disabled="!newGuest.name.trim()"
            @click="confirmAddGuest">
            <i class="bi bi-plus-lg me-1"></i> Add to Party
          </button>
        </div>
      </div>
    </div>

    <!-- ===== MODAL 1: AI Scan (calls real backend) ===== -->
    <div v-if="showAiScan" class="vue-modal-backdrop" @click.self="showAiScan = false">
      <div class="vue-modal-box">
        <div v-if="isScanning" class="p-4 text-center py-5">
          <div class="spinner-grow text-orange mb-3" style="width:3rem; height:3rem;" role="status"></div>
          <h5 class="fw-bold">Groq AI Filtering...</h5>
          <p class="text-muted small">
            Finding nearest restaurants for
            <strong>{{ currentOrderingFor }}</strong>
            <span v-if="currentOrderingPref && currentOrderingPref !== 'Any'" class="badge bg-light text-dark border ms-1">{{ currentOrderingPref }}</span>
          </p>
          <span class="badge bg-success bg-opacity-10 text-success small">
            <i class="bi bi-robot me-1"></i> llama-3.3-70b filtering mock data
          </span>
        </div>
        <div v-else>
          <div class="p-3 border-bottom d-flex justify-content-between align-items-center">
            <div>
              <h6 class="fw-bold mb-0">
                Nearest Matches for {{ currentOrderingFor }}
                <span v-if="currentCategory" class="badge bg-orange ms-1" style="font-size:0.7rem;">{{ currentCategory }}</span>
              </h6>
              <span class="small text-muted" v-if="currentOrderingPref && currentOrderingPref !== 'Any' && currentOrderingPref !== 'Any Preference'">
                <i class="bi bi-funnel-fill me-1"></i>Filtered for: <strong>{{ currentOrderingPref }}</strong>
              </span>
              <span v-if="scanWidened" class="small text-warning d-block">
                <i class="bi bi-info-circle"></i> Search widened to find options
              </span>
            </div>
            <button class="btn-close" @click="showAiScan = false"></button>
          </div>
          <div class="p-3 bg-light" style="max-height:420px; overflow-y:auto;">
            <div v-if="scannedRestaurants.length === 0" class="text-center text-muted py-4">
              No restaurants found nearby. Try changing preference.
            </div>
            <div
              v-for="resto in scannedRestaurants"
              :key="resto.id"
              class="restaurant-item bg-white p-3 mb-2"
              @click="selectRestaurant(resto)">
              <div class="d-flex justify-content-between align-items-start">
                <h6 class="fw-bold mb-1">{{ resto.name }}</h6>
                <span class="badge bg-success bg-opacity-10 text-success small">
                  <i class="bi bi-geo-alt"></i> {{ resto.distanceKm }}km
                </span>
              </div>
              <div class="small text-muted mb-1">
                ★ {{ resto.rating }} &nbsp;|&nbsp;
                <i class="bi bi-clock"></i> {{ resto.deliveryTime }} &nbsp;|&nbsp;
                {{ (resto.eligibleMenu || resto.menu || []).length }} eligible items
              </div>
              <span v-for="cuisine in resto.cuisines" :key="cuisine" class="badge bg-light text-dark border me-1" style="font-size:0.7rem;">
                {{ cuisine }}
              </span>
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
            <span class="small text-muted">
              <i class="bi bi-geo-alt"></i> {{ tempDistanceKm }}km away &nbsp;|&nbsp;
              ETA: {{ tempETA }} mins
            </span>
          </div>
          <button class="btn-close" @click="showMenu = false"></button>
        </div>

        <!-- Preference filter notice -->
        <div v-if="currentOrderingPref && currentOrderingPref !== 'Any'" class="px-3 pt-2">
          <div class="alert alert-info py-2 mb-0 small">
            <i class="bi bi-funnel-fill me-1"></i>
            Showing items safe for <strong>{{ currentOrderingPref }}</strong> preference
          </div>
        </div>

        <ul class="list-group list-group-flush" style="max-height:360px; overflow-y:auto;">
          <li
            v-for="(item, idx) in tempMenuSelection"
            :key="idx"
            class="list-group-item d-flex justify-content-between align-items-center py-3">
            <div>
              <div class="fw-semibold">{{ item.name }}</div>
              <div class="small text-muted">₹{{ item.price }}</div>
              <div class="d-flex gap-1 mt-1">
                <span v-if="item.isVeg" class="badge bg-success bg-opacity-10 text-success" style="font-size:0.65rem;">Veg</span>
                <span v-if="item.isJainCompatible" class="badge bg-warning bg-opacity-10 text-warning" style="font-size:0.65rem;">Jain</span>
                <span v-if="item.isDiabeticFriendly" class="badge bg-info bg-opacity-10 text-info" style="font-size:0.65rem;">Diabetic OK</span>
              </div>
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

    <!-- ===== MODAL 3: Late Order Scheduling Confirmation ===== -->
    <div v-if="showLateSchedule" class="vue-modal-backdrop" @click.self="showLateSchedule = false">
      <div class="vue-modal-box p-4">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <h5 class="fw-bold mb-0"><i class="bi bi-clock-history text-warning me-2"></i>Scheduling Late Order</h5>
          <button class="btn-close" @click="showLateSchedule = false"></button>
        </div>
        <div v-if="lateScheduleLoading" class="text-center py-4">
          <div class="spinner-border text-orange mb-3" role="status"></div>
          <p class="text-muted">Groq AI computing optimal order time...</p>
        </div>
        <div v-else>
          <div class="alert alert-warning">
            <strong>{{ lateScheduleData.guest_name }}</strong> is arriving
            <strong>{{ lateScheduleData.late_minutes }} mins</strong> late.
          </div>
          <div class="bg-light rounded p-3 mb-3">
            <div class="d-flex justify-content-between mb-2">
              <span class="text-muted small">Party starts at</span>
              <strong>{{ partyTime }}</strong>
            </div>
            <div class="d-flex justify-content-between mb-2">
              <span class="text-muted small">Guest arrives at</span>
              <strong>{{ lateScheduleData.arrival_time }}</strong>
            </div>
            <div class="d-flex justify-content-between mb-2">
              <span class="text-muted small">Restaurant delivery time</span>
              <strong>{{ lateScheduleData.delivery_mins }} mins</strong>
            </div>
            <div class="d-flex justify-content-between border-top pt-2 mt-2">
              <span class="fw-bold">🚀 Order fires at</span>
              <strong class="text-orange fs-5">{{ lateScheduleData.fire_at }}</strong>
            </div>
          </div>
          <p class="text-muted small fst-italic mb-3">
            <i class="bi bi-robot me-1"></i> {{ lateScheduleData.reasoning }}
          </p>
          <button class="btn btn-orange w-100" @click="confirmLateSchedule">
            <i class="bi bi-check-circle me-1"></i> Confirm Scheduled Order
          </button>
        </div>
      </div>
    </div>

    <!-- ===== MODAL 4: Budget Guardian ===== -->
    <div v-if="showBudgetGuard" class="vue-modal-backdrop" @click.self="showBudgetGuard = false">
      <div class="vue-modal-box p-4">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <h5 class="fw-bold mb-0">
            <i class="bi bi-shield-exclamation me-2" :class="budgetGuardData.status === 'exceeded' ? 'text-danger' : 'text-success'"></i>
            Budget Guardian
          </h5>
          <button class="btn-close" @click="showBudgetGuard = false"></button>
        </div>

        <div v-if="budgetGuardLoading" class="text-center py-4">
          <div class="spinner-border text-orange mb-3" role="status"></div>
          <p class="text-muted">AI checking your budget...</p>
        </div>

        <div v-else>
          <!-- EXCEEDED -->
          <div v-if="budgetGuardData.status === 'exceeded'">
            <div class="alert alert-danger">
              <i class="bi bi-exclamation-triangle-fill me-2"></i>
              Cart exceeds budget by <strong>₹{{ budgetGuardData.exceeded_by }}</strong>. Remove items to proceed.
            </div>
            <div v-if="budgetGuardData.remove_suggestions && budgetGuardData.remove_suggestions.length">
              <p class="fw-bold small mb-2">AI suggests removing:</p>
              <ul class="list-group list-group-flush mb-3">
                <li v-for="item in budgetGuardData.remove_suggestions" :key="item" class="list-group-item small py-2">
                  <i class="bi bi-dash-circle text-danger me-2"></i>{{ item }}
                </li>
              </ul>
            </div>
            <button class="btn btn-secondary w-100" @click="showBudgetGuard = false">Go Back & Edit Orders</button>
          </div>

          <!-- OK with upsells -->
          <div v-else>
            <div class="alert alert-success">
              <i class="bi bi-check-circle-fill me-2"></i>
              Budget on track! <strong>₹{{ budgetGuardData.remaining }}</strong> remaining.
            </div>
            <div v-if="budgetGuardData.suggestions && budgetGuardData.suggestions.length">
              <p class="fw-bold small mb-2">🎉 Add something extra before you go?</p>
              <div class="d-flex flex-column gap-2 mb-3">
                <div
                  v-for="sugg in budgetGuardData.suggestions"
                  :key="sugg.name"
                  class="border rounded p-2 d-flex justify-content-between align-items-center">
                  <div>
                    <span class="fw-semibold small">{{ sugg.name }}</span>
                    <span class="text-muted small ms-2">₹{{ sugg.price }}</span>
                    <div class="text-muted" style="font-size:0.75rem;">{{ sugg.reason }}</div>
                  </div>
                  <button class="btn btn-sm btn-outline-orange" @click="addUpsellItem(sugg)">Add</button>
                </div>
              </div>
            </div>
            <button class="btn btn-orange w-100" @click="proceedToPayment">
              Continue to Payment <i class="bi bi-arrow-right ms-1"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ===== MODAL 5: Smart Merge ===== -->
    <div v-if="showMerge" class="vue-modal-backdrop" @click.self="showMerge = false">
      <div class="vue-modal-box p-4">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <h5 class="fw-bold mb-0"><i class="bi bi-diagram-2-fill text-orange me-2"></i>Smart Order Merge</h5>
          <button class="btn-close" @click="showMerge = false"></button>
        </div>
        <div v-if="mergeLoading" class="text-center py-4">
          <div class="spinner-border text-orange mb-3" role="status"></div>
          <p class="text-muted">AI scanning for merge opportunities...</p>
        </div>
        <div v-else>
          <div v-if="!mergeData.has_merges" class="text-center py-3">
            <i class="bi bi-check-circle-fill text-success fs-2 mb-2 d-block"></i>
            <p class="text-muted">No merge opportunities found. All orders look optimal!</p>
            <button class="btn btn-orange w-100 mt-2" @click="runBudgetCheck">
              Continue to Budget Check <i class="bi bi-arrow-right ms-1"></i>
            </button>
          </div>
          <div v-else>
            <div class="alert alert-info small">
              <i class="bi bi-lightbulb-fill me-1"></i>
              Found guests with same restaurant ordering similar items. Merging saves delivery fees!
            </div>
            <div v-for="(merge, idx) in mergeData.merges" :key="idx" class="border rounded p-3 mb-2">
              <div class="fw-bold mb-1">
                <i class="bi bi-people-fill text-orange me-1"></i>
                {{ merge.guests.join(' + ') }}
              </div>
              <div class="small text-muted mb-1"><i class="bi bi-shop me-1"></i>{{ merge.restaurant }}</div>
              <div class="small mb-1">Shared items: <span class="fw-semibold">{{ merge.shared_items.join(', ') }}</span></div>
              <span class="badge bg-success bg-opacity-10 text-success">{{ merge.savings_note }}</span>
            </div>
            <div class="d-flex gap-2 mt-3">
              <button class="btn btn-outline-secondary flex-fill" @click="skipMerge">
                Skip, Keep Separate
              </button>
              <button class="btn btn-orange flex-fill" @click="runBudgetCheck">
                Noted, Continue
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ===== MODAL 6: Checkout ===== -->
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
          <div class="border rounded p-3 mb-3 d-flex align-items-center justify-content-between hover-lift"
            style="cursor:pointer;" @click="processPayment">
            <div class="d-flex align-items-center gap-3">
              <i class="bi bi-credit-card fs-4 text-secondary"></i>
              <span class="fw-semibold">Credit / Debit Cards</span>
            </div>
            <i class="bi bi-chevron-right text-muted"></i>
          </div>
          <!-- Cancel button -->
          <button class="btn btn-outline-danger w-100" @click="showCheckout = false">
            <i class="bi bi-x-circle me-1"></i> Cancel & Go Back
          </button>
        </div>

        <div v-else class="text-center py-4">
          <div class="spinner-border text-orange mb-3" role="status"></div>
          <h6 class="fw-bold">Processing securely...</h6>
        </div>
      </div>
    </div>

    <!-- ===== MODAL 7: Success ===== -->
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
              rows="10" readonly style="resize:none; font-family:monospace;">
            </textarea>
          </div>
          <div class="d-flex gap-2">
            <button class="btn btn-outline-success w-50" @click="copyShareText">
              <i class="bi bi-copy me-1"></i>{{ copied ? 'Copied!' : 'Copy' }}
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
import { apiRequest } from '@/api/client'

export default {
  name: 'OrchestratorView',

  data() {
    return {
      budget: Number(this.$route.query.budget) || 4000,
      hostName: this.$route.query.hostName || '',
      occasion: this.$route.query.occasion || '',
      strategy: 'member',
      partySize: Number(this.$route.query.guestCount) || 4,
      hostPref: 'Any Preference',
      copied: false,
      partyTime: '20:00',

      location: {
        address: 'A-Block, Room 504, Signature Heights',
        city: 'Kondapur',
        pin: '500084'
      },

      members: [
        { id: 'm0', name: this.$route.query.hostName || 'Host', pref: 'Any', late: false, lateMinutes: 30, isHost: true },
      ],

      orders: [],
      scheduledOrders: [],  // late arrival schedule results from backend

      foodCategories: [
        { name: 'Pizza', emoji: '🍕', rating: 4.2, time: 35 },
        { name: 'Burgers', emoji: '🍔', rating: 4.5, time: 25 },
        { name: 'Biryani', emoji: '🍗', rating: 4.1, time: 40 },
        { name: 'Chinese', emoji: '🍝', rating: 4.3, time: 30 }
      ],

      // Modal states
      showAddGuest: false,
      newGuest: { name: '', pref: 'Any', late: false, lateMinutes: 30 },
      showAiScan: false,
      isScanning: false,
      scannedRestaurants: [],
      scanWidened: false,
      currentCategory: null,
      showMenu: false,
      showLateSchedule: false,
      lateScheduleLoading: false,
      lateScheduleData: {},
      showBudgetGuard: false,
      budgetGuardLoading: false,
      budgetGuardData: {},
      showMerge: false,
      mergeLoading: false,
      mergeData: { has_merges: false, merges: [] },
      showCheckout: false,
      showSuccess: false,
      isProcessing: false,

      // Temp order state
      currentOrderingForId: null,
      currentOrderingFor: '',
      currentOrderingPref: '',
      currentIsLate: false,
      currentLateMinutes: 30,
      tempRestaurantObj: null,
      tempRestaurant: null,
      tempETA: 0,
      tempDistanceKm: 0,
      tempMenuSelection: [],

      whatsappMessage: '',
      pendingLateOrder: null,  // holds order data while waiting for schedule confirm
      partyCode: this.$route.query.partyCode || '',
      joinLink: '',
      saveError: '',
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

  async mounted() {
    await this.ensureParty()
  },

  methods: {
    // ── Helpers ──
    hasOrdered(name) {
      return this.orders.some(o => o.who === name)
    },
    getScheduledOrder(name) {
      return this.scheduledOrders.find(s => s.guest_name === name) || null
    },
    orderItemsLabel(order) {
      return order.items.map(item => `${item.qty}x ${item.name}`).join(', ')
    },
    prefKey(pref) {
      const map = {
        'Any': 'Any', 'any': 'Any', 'Any Preference': 'Any',
        'Veg': 'Veg', 'Pure Veg': 'Veg',
        'Vegan': 'Vegan',
        'Non-Veg': 'Non-Veg',
        'Jain': 'Jain',
        'Diabetic': 'Diabetic'
      }
      return map[pref] || 'Any'
    },

    dietaryValue(pref) {
      return { Any: 'any', Veg: 'veg', Vegan: 'vegan', 'Non-Veg': 'non_veg', Jain: 'jain', Diabetic: 'diabetic' }[pref] || 'any'
    },

    async ensureParty() {
      if (this.partyCode) return
      try {
        const party = await apiRequest('/parties/', {
          method: 'POST',
          body: {
            mode: 'food_delivery',
            strategy: this.strategy,
            occasion: this.occasion || 'House Party',
            budget: this.budget,
            expected_guest_count: this.partySize,
            delivery_address: `${this.location.address}, ${this.location.city} ${this.location.pin}`,
            status: 'active'
          }
        })
        this.partyCode = party.code
        this.joinLink = party.join_link
        await this.syncHostGuest()
      } catch (e) {
        this.saveError = e.message
      }
    },

    async syncHostGuest() {
      if (!this.partyCode || !this.hostName) return
      const host = this.members.find(m => m.isHost)
      if (host?.backendId) return
      try {
        const guest = await apiRequest(`/parties/${this.partyCode}/guests/`, { method: 'POST', body: { name: this.hostName, dietary_pref: 'any' } })
        if (host) host.backendId = guest.id
      } catch {
        // Guest may already exist from an earlier draft; continue locally.
      }
    },

    async persistGuest(member) {
      if (!this.partyCode || member.backendId) return
      const guest = await apiRequest(`/parties/${this.partyCode}/guests/`, {
        method: 'POST',
        body: {
          name: member.name,
          dietary_pref: this.dietaryValue(member.pref),
          is_late: member.late,
          late_offset_minutes: member.late ? member.lateMinutes : null
        }
      })
      member.backendId = guest.id
    },

    addGuest() {
      // Reset form and open modal
      this.newGuest = { name: '', pref: 'Any', late: false, lateMinutes: 30 }
      this.showAddGuest = true
    },

    confirmAddGuest() {
      if (!this.newGuest.name.trim()) return
      this.members.push({
        id: 'm' + Date.now(),
        name: this.newGuest.name.trim(),
        pref: this.newGuest.pref,
        late: this.newGuest.late,
        lateMinutes: this.newGuest.lateMinutes,
        isHost: false
      })
      this.showAddGuest = false
    },
    removeMember(id) {
      const member = this.members.find(m => m.id === id)
      if (member) this.orders = this.orders.filter(o => o.who !== member.name)
      this.members = this.members.filter(m => m.id !== id)
    },

    // ── Feature 1: Start Order Flow with real backend restaurant fetch ──
    async startOrderFlow(id, name, pref, isLate, lateMinutes, category) {
      this.currentOrderingForId = id
      this.currentOrderingFor = name
      this.currentOrderingPref = pref || 'Any'
      this.currentCategory = category || null
      this.currentIsLate = isLate || false
      this.currentLateMinutes = lateMinutes || 30
      this.isScanning = true
      this.scannedRestaurants = []
      this.scanWidened = false
      this.showAiScan = true

      try {
        const data = await apiRequest('/ai/restaurants/', {
          method: 'POST',
          body: {
            pref: this.prefKey(this.currentOrderingPref),
            category: category || null,
            guest_name: name
          }
        })
        this.scannedRestaurants = data.restaurants || []
        this.scanWidened = data.widened || false
      } catch {
        // Fallback: complete restaurant + menu data, filter by pref locally
        const allFallback = [
          {
            id: 'rest_001', name: 'Punjab Grill', distanceKm: 1.2, rating: 4.3,
            deliveryTime: '30-35 mins', deliveryMins: 33, cuisines: ['North Indian', 'Punjabi'],
            menu: [
              { id: 'item_001', name: 'Paneer Butter Masala', price: 280, qty: 0, isVeg: true, isJainCompatible: true, isDiabeticFriendly: false },
              { id: 'item_002', name: 'Dal Makhani', price: 220, qty: 0, isVeg: true, isJainCompatible: true, isDiabeticFriendly: true },
              { id: 'item_003', name: 'Chicken Tikka', price: 320, qty: 0, isVeg: false, isJainCompatible: false, isDiabeticFriendly: true },
              { id: 'item_004', name: 'Tandoori Roti', price: 40, qty: 0, isVeg: true, isJainCompatible: true, isDiabeticFriendly: true },
              { id: 'item_005', name: 'Jeera Rice', price: 160, qty: 0, isVeg: true, isJainCompatible: true, isDiabeticFriendly: false },
            ]
          },
          {
            id: 'rest_002', name: 'Barbeque Nation', distanceKm: 2.8, rating: 4.5,
            deliveryTime: '45-50 mins', deliveryMins: 48, cuisines: ['Barbecue', 'Multi-Cuisine'],
            menu: [
              { id: 'item_007', name: 'Veg Seekh Kebab', price: 260, qty: 0, isVeg: true, isJainCompatible: false, isDiabeticFriendly: true },
              { id: 'item_008', name: 'Mutton Seekh Kebab', price: 380, qty: 0, isVeg: false, isJainCompatible: false, isDiabeticFriendly: true },
              { id: 'item_009', name: 'Paneer Tikka', price: 300, qty: 0, isVeg: true, isJainCompatible: true, isDiabeticFriendly: true },
              { id: 'item_010', name: 'Fish Tikka', price: 350, qty: 0, isVeg: false, isJainCompatible: false, isDiabeticFriendly: true },
            ]
          },
          {
            id: 'rest_003', name: 'Satvic Jain Kitchen', distanceKm: 0.9, rating: 4.1,
            deliveryTime: '25-30 mins', deliveryMins: 28, cuisines: ['Jain', 'Pure Veg'],
            menu: [
              { id: 'item_011', name: 'Jain Dal Baati', price: 240, qty: 0, isVeg: true, isJainCompatible: true, isDiabeticFriendly: false },
              { id: 'item_012', name: 'Jain Paneer Sabzi', price: 210, qty: 0, isVeg: true, isJainCompatible: true, isDiabeticFriendly: true },
              { id: 'item_013', name: 'Jain Khichdi', price: 150, qty: 0, isVeg: true, isJainCompatible: true, isDiabeticFriendly: true },
              { id: 'item_014', name: 'Jain Chapati (4 pcs)', price: 60, qty: 0, isVeg: true, isJainCompatible: true, isDiabeticFriendly: true },
            ]
          },
          {
            id: 'rest_004', name: 'Green Bowl Vegan Co.', distanceKm: 1.8, rating: 4.2,
            deliveryTime: '35-40 mins', deliveryMins: 38, cuisines: ['Vegan', 'Healthy'],
            menu: [
              { id: 'item_015', name: 'Vegan Buddha Bowl', price: 290, qty: 0, isVeg: true, isJainCompatible: true, isDiabeticFriendly: true },
              { id: 'item_016', name: 'Tofu Stir Fry', price: 260, qty: 0, isVeg: true, isJainCompatible: true, isDiabeticFriendly: true },
              { id: 'item_017', name: 'Multigrain Wrap', price: 180, qty: 0, isVeg: true, isJainCompatible: false, isDiabeticFriendly: true },
            ]
          },
          {
            id: 'rest_005', name: 'Spice Route Non-Veg', distanceKm: 3.5, rating: 4.4,
            deliveryTime: '40-45 mins', deliveryMins: 42, cuisines: ['Mughlai', 'Non-Veg'],
            menu: [
              { id: 'item_019', name: 'Butter Chicken', price: 340, qty: 0, isVeg: false, isJainCompatible: false, isDiabeticFriendly: false },
              { id: 'item_020', name: 'Mutton Biryani', price: 420, qty: 0, isVeg: false, isJainCompatible: false, isDiabeticFriendly: false },
              { id: 'item_021', name: 'Egg Curry', price: 220, qty: 0, isVeg: false, isJainCompatible: false, isDiabeticFriendly: true },
              { id: 'item_022', name: 'Rumali Roti', price: 35, qty: 0, isVeg: true, isJainCompatible: true, isDiabeticFriendly: true },
            ]
          },
          {
            id: 'rest_006', name: 'DiabEats Health Kitchen', distanceKm: 2.2, rating: 4.0,
            deliveryTime: '30-35 mins', deliveryMins: 32, cuisines: ['Healthy', 'Low GI'],
            menu: [
              { id: 'item_023', name: 'Millets Bowl', price: 200, qty: 0, isVeg: true, isJainCompatible: true, isDiabeticFriendly: true },
              { id: 'item_024', name: 'Grilled Chicken Salad', price: 280, qty: 0, isVeg: false, isJainCompatible: false, isDiabeticFriendly: true },
              { id: 'item_025', name: 'Quinoa Khichdi', price: 220, qty: 0, isVeg: true, isJainCompatible: true, isDiabeticFriendly: true },
            ]
          },
        ]

        // ── Correct preference filtering ──
        const prefLower = (this.currentOrderingPref || 'any').toLowerCase().trim()

        const filterMenu = (menu) => {
          if (prefLower === 'jain') return menu.filter(i => i.isJainCompatible)
          if (prefLower === 'veg' || prefLower === 'pure veg') return menu.filter(i => i.isVeg)
          if (prefLower === 'vegan') return menu.filter(i => i.isVeg)
          if (prefLower === 'diabetic') return menu.filter(i => i.isDiabeticFriendly)
          // Non-Veg, Any → all items allowed
          return menu
        }

        this.scannedRestaurants = allFallback
          .map(r => {
            const eligible = filterMenu(r.menu)
            return eligible.length > 0 ? { ...r, eligibleMenu: eligible } : null
          })
          .filter(Boolean)
          .sort((a, b) => a.distanceKm - b.distanceKm)
      } finally {
        this.isScanning = false
      }
    },

    selectRestaurant(resto) {
      this.showAiScan = false
      this.tempRestaurantObj = resto
      this.tempRestaurant = resto.name
      this.tempETA = resto.deliveryMins || 35
      this.tempDistanceKm = resto.distanceKm
      // Use eligibleMenu (preference-filtered) if available, else full menu
      const menuSource = (resto.eligibleMenu && resto.eligibleMenu.length) ? resto.eligibleMenu : resto.menu
      this.tempMenuSelection = (menuSource || []).map(item => ({ ...item, qty: 0 }))
      setTimeout(() => { this.showMenu = true }, 300)
    },

    updateMenuQty(idx, change) {
      const newQty = this.tempMenuSelection[idx].qty + change
      if (newQty >= 0) {
        this.tempMenuSelection[idx] = { ...this.tempMenuSelection[idx], qty: newQty }
        this.tempMenuSelection = [...this.tempMenuSelection]
      }
    },

    // ── Feature 2: Confirm menu — if late, call schedule endpoint ──
    async confirmMenuSelection() {
      const selected = this.tempMenuSelection.filter(i => i.qty > 0)
      if (selected.length === 0) { alert('Please add at least one item.'); return }

      const itemTotal = selected.reduce((sum, i) => sum + i.price * i.qty, 0)
      const orderData = {
        id: Date.now(),
        who: this.currentOrderingFor,
        restaurant: this.tempRestaurant,
        restaurant_id: this.tempRestaurantObj?.id,
        eta: this.tempETA,
        distanceKm: this.tempDistanceKm,
        items: selected,
        itemTotal,
        isLate: this.currentIsLate,
      }

      if (this.currentIsLate) {
        // Hold order data and show scheduling modal
        this.pendingLateOrder = orderData
        this.showMenu = false
        await this.computeLateSchedule(orderData)
      } else {
        this.orders = this.orders.filter(o => o.who !== this.currentOrderingFor)
        this.orders.push(orderData)
        this.showMenu = false
      }
    },

    async computeLateSchedule(orderData) {
      this.lateScheduleLoading = true
      this.showLateSchedule = true

      try {
        const data = await apiRequest('/ai/schedule-late-order/', {
          method: 'POST',
          body: {
            guest_name: orderData.who,
            pref: this.currentOrderingPref,
            late_minutes: this.currentLateMinutes,
            party_time: this.partyTime,
            restaurant_id: orderData.restaurant_id,
            items: orderData.items.map(i => ({ id: i.id, qty: i.qty }))
          }
        })
        // Compute arrival time display
        const [h, m] = this.partyTime.split(':').map(Number)
        const arrivalDate = new Date(2000, 0, 1, h, m + this.currentLateMinutes)
        const arrivalStr = `${String(arrivalDate.getHours()).padStart(2,'0')}:${String(arrivalDate.getMinutes()).padStart(2,'0')}`

        this.lateScheduleData = {
          ...data,
          arrival_time: arrivalStr,
          late_minutes: this.currentLateMinutes
        }
      } catch {
        // Fallback computation
        const [h, m] = this.partyTime.split(':').map(Number)
        const arrivalDate = new Date(2000, 0, 1, h, m + this.currentLateMinutes)
        const fireDate = new Date(2000, 0, 1, arrivalDate.getHours(), arrivalDate.getMinutes() - (this.tempETA || 35))
        this.lateScheduleData = {
          guest_name: orderData.who,
          late_minutes: this.currentLateMinutes,
          fire_at: `${String(fireDate.getHours()).padStart(2,'0')}:${String(fireDate.getMinutes()).padStart(2,'0')}`,
          reasoning: `Order fires ${this.tempETA} mins before ${orderData.who} arrives.`,
          delivery_mins: this.tempETA,
          arrival_time: `${String(arrivalDate.getHours()).padStart(2,'0')}:${String(arrivalDate.getMinutes()).padStart(2,'0')}`
        }
      } finally {
        this.lateScheduleLoading = false
      }
    },

    confirmLateSchedule() {
      if (this.pendingLateOrder) {
        this.orders = this.orders.filter(o => o.who !== this.pendingLateOrder.who)
        this.orders.push(this.pendingLateOrder)
        // Store schedule locally too
        this.scheduledOrders = this.scheduledOrders.filter(s => s.guest_name !== this.lateScheduleData.guest_name)
        this.scheduledOrders.push(this.lateScheduleData)
        this.pendingLateOrder = null
      }
      this.showLateSchedule = false
    },

    // ── Feature 4: Merge check THEN Feature 3: Budget check, in sequence ──
    async openCheckout() {
      if (this.orders.length === 0) {
        alert('Please add some orders before checking out!')
        return
      }
      // Step 1: Run merge check first
      await this.runMergeCheck()
    },

    async runMergeCheck() {
      this.mergeLoading = true
      this.showMerge = true
      try {
        const data = await apiRequest('/ai/merge-check/', {
          method: 'POST',
          body: { orders: this.orders }
        })
        this.mergeData = { has_merges: data.has_merges || false, merges: data.merges || [] }
      } catch {
        this.mergeData = { has_merges: false, merges: [] }
      } finally {
        this.mergeLoading = false
      }
    },

    skipMerge() {
      this.showMerge = false
      this.runBudgetCheck()
    },

    // ── Feature 3: Budget Guardian ──
    async runBudgetCheck() {
      this.showMerge = false
      this.budgetGuardLoading = true
      this.showBudgetGuard = true

      try {
        const data = await apiRequest('/ai/budget-check/', {
          method: 'POST',
          body: {
            budget: this.budget,
            current_total: this.billFinalTotal,
            guests: this.members.map(m => ({ name: m.name, pref: m.pref })),
            current_orders: this.orders
          }
        })
        this.budgetGuardData = data
      } catch {
        // Fallback: simple local check
        this.budgetGuardData = {
          status: this.isOverBudget ? 'exceeded' : 'ok',
          remaining: this.budgetLeft,
          exceeded_by: this.isOverBudget ? Math.abs(this.budgetLeft) : 0,
          suggestions: []
        }
      } finally {
        this.budgetGuardLoading = false
      }
    },

    addUpsellItem(sugg) {
      // Add upsell to first order's items as a bonus item (host's order)
      if (this.orders.length > 0) {
        const firstOrder = this.orders[0]
        firstOrder.items.push({ name: sugg.name, price: sugg.price, qty: 1 })
        firstOrder.itemTotal += sugg.price
      }
      // Remove from suggestions
      this.budgetGuardData.suggestions = this.budgetGuardData.suggestions.filter(s => s.name !== sugg.name)
      this.budgetGuardData.remaining -= sugg.price
    },

    proceedToPayment() {
      this.showBudgetGuard = false
      this.isProcessing = false
      this.showCheckout = true
    },

    async savePartyOrders() {
      await this.ensureParty()
      if (!this.partyCode) return
      for (const member of this.members.filter(m => !m.isHost)) {
        await this.persistGuest(member).catch(() => null)
      }
      for (const order of this.orders) {
        if (order.backendId) continue
        const member = this.members.find(m => m.name === order.who)
        const items = order.items.map(i => ({
          external_item_id: String(i.id || i.external_item_id || i.name),
          name: i.name,
          unit_price: Number(i.price || i.unit_price || 0),
          quantity: Number(i.qty || i.quantity || 1),
          is_veg: Boolean(i.isVeg || i.is_veg),
          is_jain_compatible: Boolean(i.isJainCompatible || i.is_jain_compatible),
          is_diabetic_friendly: Boolean(i.isDiabeticFriendly || i.is_diabetic_friendly),
        }))
        const saved = await apiRequest(`/parties/${this.partyCode}/orders/`, {
          method: 'POST',
          body: {
            guest: member?.backendId || null,
            placed_by: 'host',
            restaurant_id: String(order.restaurant_id || order.restaurant),
            restaurant_name: order.restaurant,
            payment_method: order.isLate ? 'online' : null,
            items
          }
        }).catch(() => null)
        if (saved?.id) order.backendId = saved.id
      }
    },

    async processPayment() {
      this.isProcessing = true
      await this.savePartyOrders()
      setTimeout(() => {
        this.showCheckout = false
        this.generateWhatsAppMessage()
        this.showSuccess = true
        this.isProcessing = false
      }, 800)
    },

    generateWhatsAppMessage() {
      let msg = `🎉 *PARTY DETAILS* 🎉\n\n`
      if (this.hostName) msg += `👑 *Host:* ${this.hostName}\n`
      if (this.occasion) msg += `🎊 *Occasion:* ${this.occasion}\n`
      msg += `📍 *Venue:*\n${this.location.address}, ${this.location.city}\n\n`
      msg += `🍕 *Orders:*\n`
      this.orders.forEach(o => {
        const itemsStr = o.items.map(i => i.name).join(', ')
        const lateTag = o.isLate ? ' ⏰ (Scheduled)' : ''
        msg += `• ${o.who}${lateTag} → ${itemsStr} (${o.restaurant})\n`
      })

      const lateMembers = this.members.filter(m => m.late).map(m => m.name)
      if (this.strategy === 'member' && lateMembers.length > 0) {
        msg += `\n⏰ *Late Arrivals (AI Scheduled):*\n`
        lateMembers.forEach(name => {
          const sched = this.getScheduledOrder(name)
          if (sched) msg += `  • ${name} — Order fires at ${sched.fire_at}\n`
          else msg += `  • ${name}\n`
        })
      }

      const maxEta = Math.max(...this.orders.map(o => o.eta))
      msg += `\n🚴 *Max ETA:* ${maxEta} mins\n`
      msg += `\n💰 *Total:* ₹${this.billFinalTotal}`
      const perHead = this.members.length > 0 ? Math.round(this.billFinalTotal / this.members.length) : 0
      msg += `\n🔗 *UPI Split (₹${perHead}/person):*\nupi://pay?pa=host@upi&pn=${this.hostName || 'Host'}&am=${perHead}\n`
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
      this.scheduledOrders = []
      this.$router.push('/')
    }
  }
}
</script>

<style scoped>
.main-content-area { padding-bottom: 100px; }
.sticky-summary { position: sticky; top: 90px; z-index: 10; }
.bottom-action-bar {
  position: fixed; bottom: 0; left: 0; width: 100%;
  background: white; box-shadow: 0 -4px 20px rgba(0,0,0,0.08);
  z-index: 1050; padding: 1rem 0;
}
</style>