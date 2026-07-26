<template>
  <div>
    <div v-if="loadingParty" class="text-center py-5"><div class="spinner-border text-orange"></div></div>

    <template v-else-if="party">
      <!-- Dashboard Header -->
      <div class="bg-white border-bottom py-4 mb-4">
        <div class="container">
          <div class="row align-items-center">
            <div class="col-md-8">
              <p class="text-orange fw-bold mb-1 small text-uppercase">
                Food Delivery Orchestration Active
                <span v-if="party.occasion" class="ms-2 badge bg-light text-dark border">{{ party.occasion }}</span>
              </p>
              <h2 class="fw-bold mb-0">
                {{ hostName }}'s Party
                <span class="text-orange">Not the chaos.</span>
              </h2>
              <button class="btn btn-sm btn-outline-orange mt-2" @click="copyJoinLink">
                <i class="bi bi-link-45deg me-1"></i>{{ linkCopied ? 'Copied!' : 'Copy Guest Join Link' }}
              </button>
            </div>
            <div class="col-md-4 text-md-end mt-3 mt-md-0">
              <div class="glass-card py-2 px-3 d-inline-block bg-light border">
                <span class="text-muted small d-block">Party Budget</span>
                <div class="d-flex align-items-center gap-2">
                  <span class="fs-4 fw-bold">₹</span>
                  <input
                    type="number"
                    v-model.number="budget"
                    @change="saveBudget"
                    class="form-control form-control-sm fw-bold fs-4 border-0 bg-transparent p-0 w-auto"
                    style="max-width: 80px;"
                  />
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
                  <div class="strategy-card p-3 h-100" :class="{ selected: strategy === 'member' }" @click="setStrategy('member')">
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
                  <div class="strategy-card p-3 h-100" :class="{ selected: strategy === 'whole' }" @click="setStrategy('whole')">
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

            <!-- Host / Shared Preferences + Order -->
            <div class="glass-card mb-4">
              <div class="d-flex justify-content-between align-items-center mb-4">
                <h5 class="fw-bold mb-0">{{ strategy === 'member' ? 'Host Order' : 'Shared Party Order' }}</h5>
                <span class="badge bg-light text-dark border">
                  <i class="bi bi-person-fill text-orange me-1"></i>{{ hostName }}
                </span>
              </div>
              <div class="row flex-nowrap overflow-auto pb-2" style="scrollbar-width: thin;">
                <div class="col-5 col-md-4 col-lg-3" v-for="cat in foodCategories" :key="cat.name">
                  <div class="card h-100 border-0 shadow-sm text-center p-2 hover-lift">
                    <div class="fs-1 mb-2">{{ cat.emoji }}</div>
                    <h6 class="mb-1 fw-bold">{{ cat.name }}</h6>
                    <span class="small text-muted d-block mb-2">★ {{ cat.rating }} | {{ cat.time }}m</span>
                    <button class="btn btn-sm btn-outline-orange w-100" @click="startOrderFlow(null, hostName, 'Any', false, 0, cat.name)">
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
                <button class="btn btn-sm btn-orange" @click="addGuestOpen">
                  <i class="bi bi-plus-lg"></i> Add Guest
                </button>
              </div>

              <div class="d-flex flex-column gap-3">
                <div v-for="member in guests" :key="member.id" class="border rounded p-3 bg-white hover-lift">
                  <div class="d-flex justify-content-between align-items-start mb-3">
                    <div class="d-flex align-items-center gap-2">
                      <div class="bg-light rounded-circle d-flex align-items-center justify-content-center fw-bold text-orange"
                        style="width:40px; height:40px;">
                        {{ member.name.charAt(0) }}
                      </div>
                      <div>
                        <h6 class="fw-bold mb-0">{{ member.name }}</h6>
                        <span class="small text-muted">
                          <span v-if="hasOrdered(member.id)">
                            <i class="bi bi-check-circle-fill text-success"></i> Ordered
                          </span>
                          <span v-else-if="member.is_late && getScheduledOrder(member.id)" class="text-warning">
                            <i class="bi bi-clock-history"></i>
                            Fires at {{ formatFireTime(getScheduledOrder(member.id).fire_time) }}
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
                    <div class="col-4">
                      <select :value="prefLabel(member.dietary_pref)" @change="onGuestPrefChange(member, $event.target.value)" class="form-select form-select-sm">
                        <option>Any</option>
                        <option>Veg</option>
                        <option>Non-Veg</option>
                        <option>Vegan</option>
                        <option>Jain</option>
                        <option>Diabetic</option>
                      </select>
                    </div>
                    <div class="col-5 d-flex align-items-center gap-2">
                      <div class="form-check form-switch m-0">
                        <input class="form-check-input" type="checkbox" :checked="member.is_late" @change="toggleLate(member, $event.target.checked)" :id="'late-' + member.id" />
                        <label class="form-check-label small" :for="'late-' + member.id">Late</label>
                      </div>
                      <div v-if="member.is_late" class="d-flex align-items-center gap-1">
                        <input
                          type="number"
                          :value="member.late_offset_minutes || 30"
                          @change="setLateMinutes(member, $event.target.value)"
                          class="form-control form-control-sm"
                          style="width:54px;"
                          min="5" max="120"
                        />
                        <span class="small text-muted">min</span>
                      </div>
                    </div>
                    <div class="col-3 d-flex justify-content-end">
                      <button
                        class="btn btn-sm"
                        :class="hasOrdered(member.id) ? 'btn-outline-success' : 'btn-outline-orange'"
                        @click="startOrderFlow(member.id, member.name, prefLabel(member.dietary_pref), member.is_late, member.late_offset_minutes || 30)">
                        {{ hasOrdered(member.id) ? 'Edit' : 'Order' }}
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
                      <i class="bi bi-person-fill text-muted"></i> {{ order.guest_name || hostName }}
                      <span v-if="order.status === 'scheduled'" class="badge bg-warning text-dark ms-1" style="font-size:0.65rem;">
                        <i class="bi bi-clock"></i> Late
                      </span>
                    </span>
                    <span class="fw-bold">₹{{ order.total }}</span>
                  </div>
                  <div class="text-muted" style="font-size:0.75rem;">
                    <i class="bi bi-shop"></i> {{ order.restaurant_name }}
                  </div>
                  <div class="text-muted fst-italic" style="font-size:0.75rem;">
                    {{ order.items.map(i => `${i.quantity}x ${i.name}`).join(', ') }}
                  </div>
                </div>
              </div>

              <!-- Bill Breakdown -->
              <div class="border-top pt-3 mb-4">
                <div class="d-flex justify-content-between small mb-2 text-muted">
                  <span>Item Total</span><span>₹{{ billItemTotal }}</span>
                </div>
                <div class="d-flex justify-content-between small mb-2 text-muted">
                  <span>Delivery Fee</span><span>₹{{ billDelivery }}</span>
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
    </template>

    <!-- ===== MODAL 0: Add Guest ===== -->
    <div v-if="showAddGuest" class="vue-modal-backdrop" @click.self="showAddGuest = false">
      <div class="vue-modal-box p-4" style="max-width: 420px;">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h5 class="fw-bold mb-0"><i class="bi bi-person-plus-fill text-orange me-2"></i>Add Guest</h5>
          <button class="btn-close" @click="showAddGuest = false"></button>
        </div>
        <div class="mb-3">
          <label class="form-label fw-semibold small">Guest Name</label>
          <input type="text" class="form-control" v-model="newGuest.name" placeholder="e.g. Rahul, Priya..." @keyup.enter="confirmAddGuest" autofocus />
        </div>
        <div class="mb-3">
          <label class="form-label fw-semibold small">Dietary Preference</label>
          <select v-model="newGuest.pref" class="form-select">
            <option>Any</option><option>Veg</option><option>Non-Veg</option><option>Vegan</option><option>Jain</option><option>Diabetic</option>
          </select>
        </div>
        <div class="mb-4 d-flex align-items-center gap-3">
          <div class="form-check form-switch m-0">
            <input class="form-check-input" type="checkbox" v-model="newGuest.late" id="newGuestLate" />
            <label class="form-check-label fw-semibold small" for="newGuestLate">Arriving Late?</label>
          </div>
          <div v-if="newGuest.late" class="d-flex align-items-center gap-2">
            <input type="number" v-model.number="newGuest.lateMinutes" class="form-control form-control-sm" style="width:64px;" min="5" max="120" />
            <span class="small text-muted">mins late</span>
          </div>
        </div>
        <div v-if="guestError" class="alert alert-danger py-2 small">{{ guestError }}</div>
        <div class="d-flex gap-2">
          <button class="btn btn-outline-secondary flex-fill" @click="showAddGuest = false">Cancel</button>
          <button class="btn btn-orange flex-fill" :disabled="!newGuest.name.trim() || savingGuest" @click="confirmAddGuest">
            <i class="bi bi-plus-lg me-1"></i> Add to Party
          </button>
        </div>
      </div>
    </div>

    <!-- ===== MODAL 1: AI Scan ===== -->
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
        </div>
        <div v-else>
          <div class="p-3 border-bottom d-flex justify-content-between align-items-center">
            <div>
              <h6 class="fw-bold mb-0">
                Nearest Matches for {{ currentOrderingFor }}
                <span v-if="currentCategory" class="badge bg-orange ms-1" style="font-size:0.7rem;">{{ currentCategory }}</span>
              </h6>
              <span v-if="scanWidened" class="small text-warning d-block">
                <i class="bi bi-info-circle"></i> AI response fell back to local filtering
              </span>
            </div>
            <button class="btn-close" @click="showAiScan = false"></button>
          </div>
          <div class="p-3 bg-light" style="max-height:420px; overflow-y:auto;">
            <div v-if="scannedRestaurants.length === 0" class="text-center text-muted py-4">
              No restaurants found nearby. Try changing preference.
            </div>
            <div v-for="resto in scannedRestaurants" :key="resto.id" class="restaurant-item bg-white p-3 mb-2" @click="selectRestaurant(resto)">
              <div class="d-flex justify-content-between align-items-start">
                <h6 class="fw-bold mb-1">{{ resto.name }}</h6>
                <span class="badge bg-success bg-opacity-10 text-success small">
                  <i class="bi bi-geo-alt"></i> {{ resto.distanceKm }}km
                </span>
              </div>
              <div class="small text-muted mb-1">
                ★ {{ resto.rating }} &nbsp;|&nbsp; <i class="bi bi-clock"></i> {{ resto.deliveryTime }} &nbsp;|&nbsp;
                {{ (resto.eligibleMenu || []).length }} eligible items
              </div>
              <span v-for="cuisine in resto.cuisines" :key="cuisine" class="badge bg-light text-dark border me-1" style="font-size:0.7rem;">{{ cuisine }}</span>
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
            <span class="small text-muted"><i class="bi bi-geo-alt"></i> {{ tempDistanceKm }}km away &nbsp;|&nbsp; ETA: {{ tempETA }} mins</span>
          </div>
          <button class="btn-close" @click="showMenu = false"></button>
        </div>
        <ul class="list-group list-group-flush" style="max-height:360px; overflow-y:auto;">
          <li v-for="(item, idx) in tempMenuSelection" :key="idx" class="list-group-item d-flex justify-content-between align-items-center py-3">
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
              <button v-if="item.qty > 0" class="btn btn-sm btn-outline-danger" @click="updateMenuQty(idx, -1)"><i class="bi bi-dash"></i></button>
              <span v-if="item.qty > 0" class="fw-bold mx-2">{{ item.qty }}</span>
              <button class="btn btn-sm btn-outline-success" @click="updateMenuQty(idx, 1)"><i class="bi bi-plus"></i> {{ item.qty === 0 ? 'ADD' : '' }}</button>
            </div>
          </li>
        </ul>
        <div class="p-3 bg-light d-flex justify-content-between align-items-center">
          <div><span class="text-muted small">Cart Total</span><h5 class="fw-bold mb-0">₹{{ menuTempTotal }}</h5></div>
          <button class="btn btn-orange px-4" :disabled="placingOrder" @click="confirmMenuSelection">{{ placingOrder ? 'Placing…' : 'Done' }}</button>
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
            <strong>{{ lateScheduleData.guest_name }}</strong> is arriving <strong>{{ lateScheduleData.late_minutes }} mins</strong> late.
          </div>
          <div class="bg-light rounded p-3 mb-3">
            <div class="d-flex justify-content-between mb-2"><span class="text-muted small">Restaurant delivery time</span><strong>{{ lateScheduleData.delivery_mins }} mins</strong></div>
            <div class="d-flex justify-content-between border-top pt-2 mt-2"><span class="fw-bold">🚀 Order fires at</span><strong class="text-orange fs-5">{{ lateScheduleData.fire_at }}</strong></div>
          </div>
          <p class="text-muted small fst-italic mb-3"><i class="bi bi-robot me-1"></i> {{ lateScheduleData.reasoning }}</p>
          <button class="btn btn-orange w-100" :disabled="placingOrder" @click="confirmLateSchedule">
            <i class="bi bi-check-circle me-1"></i> {{ placingOrder ? 'Placing…' : 'Confirm Scheduled Order' }}
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
          <div v-else>
            <div class="alert alert-success">
              <i class="bi bi-check-circle-fill me-2"></i>
              Budget on track! <strong>₹{{ budgetGuardData.remaining }}</strong> remaining.
            </div>
            <div v-if="budgetGuardData.suggestions && budgetGuardData.suggestions.length">
              <p class="fw-bold small mb-2">🎉 Add something extra before you go?</p>
              <div class="d-flex flex-column gap-2 mb-3">
                <div v-for="sugg in budgetGuardData.suggestions" :key="sugg.name" class="border rounded p-2 d-flex justify-content-between align-items-center">
                  <div>
                    <span class="fw-semibold small">{{ sugg.name }}</span>
                    <span class="text-muted small ms-2">₹{{ sugg.price }}</span>
                    <div class="text-muted" style="font-size:0.75rem;">{{ sugg.reason }}</div>
                  </div>
                </div>
              </div>
            </div>
            <button class="btn btn-orange w-100" @click="proceedToPayment">Continue to Payment <i class="bi bi-arrow-right ms-1"></i></button>
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
            <button class="btn btn-orange w-100 mt-2" @click="runBudgetCheck">Continue to Budget Check <i class="bi bi-arrow-right ms-1"></i></button>
          </div>
          <div v-else>
            <div class="alert alert-info small">
              <i class="bi bi-lightbulb-fill me-1"></i>
              Found guests with same restaurant ordering similar items. Merging saves delivery fees!
            </div>
            <div v-for="(merge, idx) in mergeData.merges" :key="idx" class="border rounded p-3 mb-2">
              <div class="fw-bold mb-1"><i class="bi bi-people-fill text-orange me-1"></i>{{ merge.guests.join(' + ') }}</div>
              <div class="small text-muted mb-1"><i class="bi bi-shop me-1"></i>{{ merge.restaurant }}</div>
              <div class="small mb-1">Shared items: <span class="fw-semibold">{{ merge.shared_items.join(', ') }}</span></div>
              <span class="badge bg-success bg-opacity-10 text-success">{{ merge.savings_note }}</span>
            </div>
            <div class="d-flex gap-2 mt-3">
              <button class="btn btn-outline-secondary flex-fill" @click="skipMerge">Skip, Keep Separate</button>
              <button class="btn btn-orange flex-fill" @click="runBudgetCheck">Noted, Continue</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ===== MODAL 6: Checkout ===== -->
    <div v-if="showCheckout" class="vue-modal-backdrop" @click.self="showCheckout = false">
      <div class="vue-modal-box p-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h5 class="fw-bold mb-0">Confirm & Share</h5>
          <button class="btn-close" @click="showCheckout = false"></button>
        </div>
        <div v-if="!isProcessing">
          <p class="text-muted small">
            Per the payment philosophy (Section 6), Host My Party never routes payments — settlement is
            trust-based and happens outside the app. Confirming below just finalizes the plan for sharing.
          </p>
          <button class="btn btn-orange w-100 py-2" @click="processPayment">
            <i class="bi bi-check-circle me-1"></i> Finalize Plan
          </button>
        </div>
        <div v-else class="text-center py-4">
          <div class="spinner-border text-orange mb-3" role="status"></div>
          <h6 class="fw-bold">Wrapping up...</h6>
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
            <textarea :value="whatsappMessage" class="form-control border-0 bg-transparent p-0 text-dark small" rows="10" readonly style="resize:none; font-family:monospace;"></textarea>
          </div>
          <div class="d-flex gap-2">
            <button class="btn btn-outline-success w-50" @click="copyShareText"><i class="bi bi-copy me-1"></i>{{ copied ? 'Copied!' : 'Copy' }}</button>
            <button class="btn btn-success w-50" @click="resetAll"><i class="bi bi-whatsapp me-1"></i> Done</button>
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
      loadingParty: true,
      party: null,
      budget: 0,
      strategy: 'member',
      partySize: 4,
      linkCopied: false,

      guests: [],
      orders: [],

      foodCategories: [
        { name: 'Pizza', emoji: '🍕', rating: 4.2, time: 35 },
        { name: 'Burgers', emoji: '🍔', rating: 4.5, time: 25 },
        { name: 'Biryani', emoji: '🍗', rating: 4.1, time: 40 },
        { name: 'Chinese', emoji: '🍝', rating: 4.3, time: 30 }
      ],

      // Modal states
      showAddGuest: false,
      newGuest: { name: '', pref: 'Any', late: false, lateMinutes: 30 },
      guestError: '', savingGuest: false,

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
      placingOrder: false,

      // Temp order state
      currentOrderingForId: null, // null = host
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
    hostName() { return this.party?.host?.name || 'Host' },
    billItemTotal() { return this.orders.reduce((sum, o) => sum + o.item_total, 0) },
    billDelivery() { return this.orders.reduce((sum, o) => sum + o.delivery_fee, 0) },
    billTaxes() { return this.orders.reduce((sum, o) => sum + o.taxes, 0) },
    billFinalTotal() { return this.billItemTotal + this.billDelivery + this.billTaxes },
    budgetLeft() { return this.budget - this.billFinalTotal },
    isOverBudget() { return this.billFinalTotal > this.budget },
    budgetPercent() { return this.budget ? Math.min((this.billFinalTotal / this.budget) * 100, 100) : 0 },
    budgetBarClass() {
      if (this.isOverBudget) return 'bg-danger'
      if (this.budgetPercent > 85) return 'bg-warning'
      return 'progress-bar-swiggy'
    },
    menuTempTotal() { return this.tempMenuSelection.reduce((sum, i) => sum + i.price * i.qty, 0) }
  },

  async mounted() {
    const code = this.$route.query.code
    if (!code) { this.$router.push('/selection'); return }
    await this.loadParty(code)
  },

  async mounted() {
    await this.ensureParty()
  },

  methods: {
    async loadParty(code) {
      this.loadingParty = true
      try {
        const [party, guests, orders] = await Promise.all([
          getParty(code), listGuests(code), listOrders(code),
        ])
        this.party = party
        this.budget = party.budget
        this.strategy = party.strategy || 'member'
        this.guests = guests
        this.orders = orders
      } catch {
        this.$router.push('/selection')
      } finally {
        this.loadingParty = false
      }
    },

    prefLabel(code) { return CODE_TO_PREF[code] || 'Any' },

    async saveBudget() {
      try { await updateParty(this.party.code, { budget: this.budget }) } catch { /* keep local value */ }
    },

    async setStrategy(next) {
      if (this.strategy === next) return
      this.strategy = next
      try { await updateParty(this.party.code, { strategy: next }) } catch { /* non-fatal */ }
    },

    copyJoinLink() {
      if (!this.party?.join_link) return
      navigator.clipboard.writeText(this.party.join_link)
      this.linkCopied = true
      setTimeout(() => { this.linkCopied = false }, 2000)
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
      this.guestError = ''
      this.showAddGuest = true
    },

    async confirmAddGuest() {
      if (!this.newGuest.name.trim()) return
      this.savingGuest = true
      this.guestError = ''
      try {
        const guest = await addGuest(this.party.code, {
          name: this.newGuest.name.trim(),
          dietary_pref: PREF_TO_CODE[this.newGuest.pref],
          is_late: this.newGuest.late,
          late_offset_minutes: this.newGuest.late ? this.newGuest.lateMinutes : null,
        })
        this.guests.push(guest)
        this.showAddGuest = false
      } catch (e) {
        this.guestError = e.body?.non_field_errors?.[0] || 'Could not add guest.'
      } finally {
        this.savingGuest = false
      }
    },

    async removeMember(id) {
      try {
        await removeGuest(this.party.code, id)
        this.guests = this.guests.filter(m => m.id !== id)
        this.orders = this.orders.filter(o => o.guest !== id)
      } catch { /* non-fatal */ }
    },

    async onGuestPrefChange(member, label) {
      member.dietary_pref = PREF_TO_CODE[label]
      try { await updateGuest(this.party.code, member.id, { dietary_pref: member.dietary_pref }) } catch { /* non-fatal */ }
    },
    async toggleLate(member, checked) {
      member.is_late = checked
      if (checked && !member.late_offset_minutes) member.late_offset_minutes = 30
      try {
        await updateGuest(this.party.code, member.id, {
          is_late: member.is_late, late_offset_minutes: member.late_offset_minutes,
        })
      } catch { /* non-fatal */ }
    },
    async setLateMinutes(member, value) {
      member.late_offset_minutes = Number(value)
      try { await updateGuest(this.party.code, member.id, { late_offset_minutes: member.late_offset_minutes }) } catch { /* non-fatal */ }
    },

    // ── Restaurant scan (Groq-filtered, via /api/ai/restaurants/) ──
    async startOrderFlow(guestId, name, pref, isLate, lateMinutes, category) {
      this.currentOrderingForId = guestId
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
      this.tempMenuSelection = (resto.eligibleMenu || []).map(item => ({ ...item, qty: 0 }))
      setTimeout(() => { this.showMenu = true }, 250)
    },

    updateMenuQty(idx, change) {
      const newQty = this.tempMenuSelection[idx].qty + change
      if (newQty >= 0) {
        this.tempMenuSelection[idx] = { ...this.tempMenuSelection[idx], qty: newQty }
        this.tempMenuSelection = [...this.tempMenuSelection]
      }
    },

    buildOrderPayload(selected) {
      const itemTotal = selected.reduce((s, i) => s + i.price * i.qty, 0)
      return {
        guest: this.currentOrderingForId,
        placed_by: 'host',
        restaurant_id: this.tempRestaurantObj?.id || '',
        restaurant_name: this.tempRestaurant,
        delivery_fee: 30,
        taxes: Math.round(itemTotal * 0.05),
        items: selected.map(i => ({
          external_item_id: String(i.id),
          name: i.name,
          unit_price: i.price,
          quantity: i.qty,
          is_veg: !!i.isVeg,
          is_jain_compatible: !!i.isJainCompatible,
          is_diabetic_friendly: !!i.isDiabeticFriendly,
        })),
      }
    },

    async confirmMenuSelection() {
      const selected = this.tempMenuSelection.filter(i => i.qty > 0)
      if (selected.length === 0) { alert('Please add at least one item.'); return }

      const payload = this.buildOrderPayload(selected)

      if (this.currentIsLate) {
        this.pendingOrderPayload = payload
        this.showMenu = false
        await this.computeLateSchedule()
      } else {
        await this.placeOrder(payload)
        this.showMenu = false
      }
    },

    async placeOrder(payload) {
      this.placingOrder = true
      try {
        const order = await createOrder(this.party.code, payload)
        this.orders = [order, ...this.orders.filter(o => o.id !== order.id)]
        return order
      } catch (e) {
        alert(e.body?.detail || 'Could not place the order.')
        return null
      } finally {
        this.placingOrder = false
      }
    },

    async computeLateSchedule() {
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

    async confirmLateSchedule() {
      if (!this.pendingOrderPayload) { this.showLateSchedule = false; return }
      const [hh, mm] = (this.lateScheduleData.fire_at || '00:00').split(':').map(Number)
      const fireDate = new Date(this.party.party_start_time || Date.now())
      if (!Number.isNaN(hh)) fireDate.setHours(hh, mm || 0, 0, 0)

      const payload = { ...this.pendingOrderPayload, status: 'scheduled', fire_time: fireDate.toISOString() }
      await this.placeOrder(payload)
      this.pendingOrderPayload = null
      this.showLateSchedule = false
    },

    // ── Checkout: merge check -> budget check -> finalize ──
    async openCheckout() {
      await this.runMergeCheck()
    },

    ordersForAi() {
      return this.orders.map(o => ({
        who: o.guest_name || this.hostName,
        restaurant: o.restaurant_name,
        items: o.items.map(i => ({ name: i.name, price: i.unit_price, qty: i.quantity })),
        itemTotal: o.item_total,
      }))
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

    skipMerge() { this.showMerge = false; this.runBudgetCheck() },

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
          remaining: this.budgetLeft, exceeded_by: this.isOverBudget ? Math.abs(this.budgetLeft) : 0, suggestions: [],
        }
      } finally {
        this.budgetGuardLoading = false
      }
    },

    proceedToPayment() { this.showBudgetGuard = false; this.isProcessing = false; this.showCheckout = true },

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
      msg += `👑 *Host:* ${this.hostName}\n`
      if (this.party.occasion) msg += `🎊 *Occasion:* ${this.party.occasion}\n\n`
      msg += `🍕 *Orders:*\n`
      this.orders.forEach(o => {
        const itemsStr = o.items.map(i => i.name).join(', ')
        const lateTag = o.status === 'scheduled' ? ' ⏰ (Scheduled)' : ''
        msg += `• ${o.guest_name || this.hostName}${lateTag} → ${itemsStr} (${o.restaurant_name})\n`
      })
      msg += `\n💰 *Total:* ₹${this.billFinalTotal}`
      const headcount = this.guests.length + 1
      const perHead = headcount > 0 ? Math.round(this.billFinalTotal / headcount) : 0
      msg += `\n🔗 *Split (₹${perHead}/person):* settle up outside the app — Host My Party never touches payments.\n`
      if (this.party.join_link) msg += `\n🔗 Join link for late-comers: ${this.party.join_link}\n`
      this.whatsappMessage = msg
    },

    copyShareText() {
      navigator.clipboard.writeText(this.whatsappMessage)
      this.copied = true
      setTimeout(() => { this.copied = false }, 2000)
    },

    resetAll() {
      this.showSuccess = false
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