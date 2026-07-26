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

              <div class="glass-card py-2 px-3 d-inline-block bg-light border mt-2">
    <span class="text-muted small d-block">Party Start Time</span>
    <input
      type="datetime-local"
      v-model="partyStartTimeLocal"
      @change="savePartyStartTime"
      class="form-control form-control-sm border-0 bg-transparent p-0"
    />
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
                    <button v-if="strategy === 'whole'" class="btn btn-orange w-100 mt-3" @click="runWholeSumOptimize">
  <i class="bi bi-stars me-1"></i> AI Optimize Whole-Party Order
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
                <div v-for="order in orders" :key="order.id" class="border-bottom pb-2 mb-2">
                  <div class="d-flex justify-content-between gap-2">
                    <span class="fw-semibold">{{ order.guest_name || hostName }}</span>
                    <span class="text-muted">₹{{ order.total }}</span>
                  </div>
                  <div class="text-muted fst-italic" style="font-size:0.75rem;">
                    {{ orderItemsLabel(order) }}
                  </div>
                  <div class="text-muted" style="font-size:0.72rem;">
                    {{ order.restaurant_name }}
                    <span v-if="order.last_modified_by === 'host' && order.guest" class="badge bg-light text-dark border ms-1">Edited by host</span>
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
import { API_BASE, apiRequest, getAccessToken } from '@/api/client'

const PREF_TO_CODE = {
  Any: 'any',
  Veg: 'veg',
  'Non-Veg': 'non_veg',
  Vegan: 'vegan',
  Jain: 'jain',
  Diabetic: 'diabetic',
}

const CODE_TO_PREF = Object.fromEntries(
  Object.entries(PREF_TO_CODE).map(([label, code]) => [code, label]),
)

export default {
  name: 'OrchestratorView',

  data() {
    return {
      loadingParty: true,
      party: null,
      partyCode: this.$route.query.partyCode || this.$route.query.code || '',
      budget: 0,
      strategy: 'member',
      partySize: 1,
      linkCopied: false,
      copied: false,

      guests: [],
      orders: [],

      foodCategories: [
        { name: 'Pizza', emoji: '🍕', rating: 4.2, time: 35 },
        { name: 'Burgers', emoji: '🍔', rating: 4.5, time: 25 },
        { name: 'Biryani', emoji: '🍗', rating: 4.1, time: 40 },
        { name: 'Chinese', emoji: '🍝', rating: 4.3, time: 30 },
      ],

      showAddGuest: false,
      newGuest: { name: '', pref: 'Any', late: false, lateMinutes: 30 },
      guestError: '',
      savingGuest: false,

      showAiScan: false,
      isScanning: false,
      scannedRestaurants: [],
      scanWidened: false,
      currentCategory: null,

      showMenu: false,
      showLateSchedule: false,
      lateScheduleLoading: false,
      lateScheduleData: {},
      pendingOrderPayload: null,

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

      currentOrderingForId: null,
      currentOrderingFor: '',
      currentOrderingPref: 'Any',
      currentIsLate: false,
      currentLateMinutes: 30,
      editingOrderId: null,

      tempRestaurantObj: null,
      tempRestaurant: '',
      tempETA: 0,
      tempDistanceKm: 0,
      tempMenuSelection: [],

      whatsappMessage: '',

      socket: null,
      socketRetryTimer: null,
      socketRetryCount: 0,
      destroyed: false,

      partyStartTimeLocal: '',
    }
  },

  computed: {
    hostName() {
      return this.party?.host?.name || this.party?.host?.username || 'Host'
    },

    billItemTotal() {
      return this.orders.reduce((sum, order) => sum + Number(order.item_total || 0), 0)
    },

    billDelivery() {
      return this.orders.reduce((sum, order) => sum + Number(order.delivery_fee || 0), 0)
    },

    billTaxes() {
      return this.orders.reduce((sum, order) => sum + Number(order.taxes || 0), 0)
    },

    billFinalTotal() {
      return this.billItemTotal + this.billDelivery + this.billTaxes
    },

    budgetLeft() {
      return Number(this.budget || 0) - this.billFinalTotal
    },

    isOverBudget() {
      return this.billFinalTotal > Number(this.budget || 0)
    },

    budgetPercent() {
      if (!Number(this.budget)) return 0
      return Math.min((this.billFinalTotal / Number(this.budget)) * 100, 100)
    },

    budgetBarClass() {
      if (this.isOverBudget) return 'bg-danger'
      if (this.budgetPercent > 85) return 'bg-warning'
      return 'progress-bar-swiggy'
    },

    menuTempTotal() {
      return this.tempMenuSelection.reduce(
        (sum, item) => sum + Number(item.price || 0) * Number(item.qty || 0),
        0,
      )
    },
  },

  async mounted() {
    if (!this.partyCode) {
      await this.$router.replace('/selection')
      return
    }

    await this.loadParty()
    if (this.party) this.connectWebSocket()
  },

  beforeUnmount() {
    this.destroyed = true
    if (this.socketRetryTimer) clearTimeout(this.socketRetryTimer)
    if (this.socket) {
      this.socket.onclose = null
      this.socket.close()
    }
  },

  methods: {
    async loadParty() {
      this.loadingParty = true
      try {
        await this.refreshAuthoritativeState()
      } catch (error) {
        console.error('Unable to load party:', error)
        await this.$router.replace('/selection')
      } finally {
        this.loadingParty = false
      }
    },

    async refreshAuthoritativeState() {
      const code = this.partyCode
      const [party, guests, orders] = await Promise.all([
        apiRequest(`/parties/${code}/`),
        apiRequest(`/parties/${code}/guests/`),
        apiRequest(`/parties/${code}/orders/`),
      ])

      this.party = party
      this.guests = Array.isArray(guests) ? guests : []
      this.orders = Array.isArray(orders) ? orders : []
      this.budget = Number(party.budget || 0)
      this.strategy = party.strategy || 'member'
      this.partySize = Number(party.expected_guest_count || Math.max(this.guests.length + 1, 1))

      this.partyStartTimeLocal = party.party_start_time
  ? new Date(party.party_start_time).toISOString().slice(0, 16)
  : ''
    },

    connectWebSocket() {
      const token = getAccessToken()
      if (!token || !this.partyCode || this.destroyed) return

      if (this.socket && [WebSocket.OPEN, WebSocket.CONNECTING].includes(this.socket.readyState)) {
        return
      }

      const apiUrl = new URL(API_BASE, window.location.origin)
      const protocol = apiUrl.protocol === 'https:' ? 'wss:' : 'ws:'
      const wsUrl =
        `${protocol}//${apiUrl.host}/ws/party/${encodeURIComponent(this.partyCode)}/` +
        `?token=${encodeURIComponent(token)}`

      this.socket = new WebSocket(wsUrl)

      this.socket.onopen = async () => {
        this.socketRetryCount = 0
        // REST remains the source of truth after reconnect.
        try {
          await this.refreshAuthoritativeState()
        } catch (error) {
          console.error('Post-WebSocket reconnect refresh failed:', error)
        }
      }

      this.socket.onmessage = async () => {
        // Socket events are invalidation signals; authoritative state comes from REST.
        try {
          await this.refreshAuthoritativeState()
        } catch (error) {
          console.error('Realtime refresh failed:', error)
        }
      }

      this.socket.onerror = () => {
        if (this.socket) this.socket.close()
      }

      this.socket.onclose = () => {
        if (this.destroyed) return
        const delay = Math.min(1000 * (2 ** this.socketRetryCount), 30000)
        this.socketRetryCount += 1
        this.socketRetryTimer = setTimeout(() => this.connectWebSocket(), delay)
      }
    },

    prefLabel(code) {
      return CODE_TO_PREF[code] || 'Any'
    },

    prefKey(label) {
      return PREF_TO_CODE[label] || 'any'
    },

    async saveBudget() {
      const nextBudget = Number(this.budget)
      if (!Number.isFinite(nextBudget) || nextBudget <= 0) {
        this.budget = Number(this.party?.budget || 0)
        return
      }

      try {
        this.party = await apiRequest(`/parties/${this.partyCode}/`, {
          method: 'PATCH',
          body: { budget: nextBudget },
        })
        this.budget = Number(this.party.budget)
      } catch (error) {
        this.budget = Number(this.party?.budget || 0)
        alert(error.message || 'Could not update budget.')
      }
    },

    async savePartyStartTime() {
  if (!this.partyStartTimeLocal) return
  try {
    this.party = await apiRequest(`/parties/${this.partyCode}/`, {
      method: 'PATCH',
      body: { party_start_time: new Date(this.partyStartTimeLocal).toISOString() },
    })
  } catch (error) {
    alert(error.message || 'Could not update party start time.')
  }
},

    async setStrategy(next) {
      if (!['member', 'whole'].includes(next) || this.strategy === next) return

      const previous = this.strategy
      this.strategy = next

      try {
        this.party = await apiRequest(`/parties/${this.partyCode}/`, {
          method: 'PATCH',
          body: { strategy: next },
        })
      } catch (error) {
        this.strategy = previous
        alert(error.message || 'Could not update strategy.')
      }
    },

    async copyJoinLink() {
  if (!this.partyCode) return

  const joinUrl = `${window.location.origin}/join/${this.partyCode}`

  try {
    await navigator.clipboard.writeText(joinUrl)

    this.linkCopied = true

    setTimeout(() => {
      this.linkCopied = false
    }, 2000)
  } catch (error) {
    console.error('Could not copy join link:', error)
    alert('Could not copy join link.')
  }
},

    addGuestOpen() {
      this.guestError = ''
      this.newGuest = { name: '', pref: 'Any', late: false, lateMinutes: 30 }
      this.showAddGuest = true
    },

    async confirmAddGuest() {
      const name = this.newGuest.name.trim()
      if (!name) return

      this.savingGuest = true
      this.guestError = ''

      try {
        const payload = {
          name,
          dietary_pref: this.prefKey(this.newGuest.pref),
          is_late: Boolean(this.newGuest.late),
          late_offset_minutes: this.newGuest.late ? Number(this.newGuest.lateMinutes || 30) : null,
        }

        const guest = await apiRequest(`/parties/${this.partyCode}/guests/`, {
          method: 'POST',
          body: payload,
        })

        this.guests.push(guest)
        this.showAddGuest = false
      } catch (error) {
        this.guestError = error.message || 'Could not add guest.'
      } finally {
        this.savingGuest = false
      }
    },

    async removeMember(id) {
      try {
        await apiRequest(`/parties/${this.partyCode}/guests/${id}/`, { method: 'DELETE' })
        this.guests = this.guests.filter((guest) => guest.id !== id)
        this.orders = this.orders.filter((order) => order.guest !== id)
      } catch (error) {
        alert(error.message || 'Could not remove guest.')
      }
    },

    async onGuestPrefChange(member, label) {
      const previous = member.dietary_pref
      member.dietary_pref = this.prefKey(label)

      try {
        const updated = await apiRequest(
          `/parties/${this.partyCode}/guests/${member.id}/`,
          { method: 'PATCH', body: { dietary_pref: member.dietary_pref } },
        )
        Object.assign(member, updated)
      } catch (error) {
        member.dietary_pref = previous
        alert(error.message || 'Could not update preference.')
      }
    },

    async toggleLate(member, checked) {
      const previous = {
        is_late: member.is_late,
        late_offset_minutes: member.late_offset_minutes,
        payment_method: member.payment_method,
      }

      member.is_late = checked
      member.late_offset_minutes = checked ? Number(member.late_offset_minutes || 30) : null

      try {
        const updated = await apiRequest(
          `/parties/${this.partyCode}/guests/${member.id}/`,
          {
            method: 'PATCH',
            body: {
              is_late: member.is_late,
              late_offset_minutes: member.late_offset_minutes,
              payment_method: checked ? (member.payment_method || null) : null,
            },
          },
        )
        Object.assign(member, updated)
      } catch (error) {
        Object.assign(member, previous)
        alert(error.message || 'Could not update late-arrival setting.')
      }
    },

    async setLateMinutes(member, value) {
      const minutes = Math.max(5, Math.min(120, Number(value) || 30))
      const previous = member.late_offset_minutes
      member.late_offset_minutes = minutes

      try {
        const updated = await apiRequest(
          `/parties/${this.partyCode}/guests/${member.id}/`,
          { method: 'PATCH', body: { late_offset_minutes: minutes } },
        )
        Object.assign(member, updated)
      } catch (error) {
        member.late_offset_minutes = previous
        alert(error.message || 'Could not update late-arrival time.')
      }
    },

    hasOrdered(guestId) {
      return this.orders.some((order) => order.guest === guestId)
    },

    getScheduledOrder(guestId) {
      return this.orders.find(
        (order) => order.guest === guestId && order.fire_time &&
          ['pending', 'scheduled'].includes(order.status),
      ) || null
    },

    formatFireTime(value) {
      if (!value) return '—'
      const date = new Date(value)
      if (Number.isNaN(date.getTime())) return value
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    },

    orderItemsLabel(order) {
      return (order?.items || [])
        .map((item) => `${item.quantity || item.qty || 1}x ${item.name}`)
        .join(', ')
    },

    normalizeRestaurant(resto) {
      const menu = resto.eligibleMenu || resto.eligible_menu || resto.menu || []
      return {
        ...resto,
        id: resto.id ?? resto.restaurant_id,
        name: resto.name ?? resto.restaurant_name,
        distanceKm: resto.distanceKm ?? resto.distance_km ?? 0,
        rating: resto.rating ?? '—',
        deliveryTime: resto.deliveryTime ?? resto.delivery_time ?? `${resto.deliveryMins || resto.delivery_mins || 35} mins`,
        deliveryMins: resto.deliveryMins ?? resto.delivery_mins ?? 35,
        cuisines: resto.cuisines || [],
        eligibleMenu: menu.map((item) => ({
          ...item,
          id: item.id ?? item.external_item_id,
          price: Number(item.price ?? item.unit_price ?? 0),
          qty: 0,
          isVeg: Boolean(item.isVeg ?? item.is_veg),
          isJainCompatible: Boolean(item.isJainCompatible ?? item.is_jain_compatible),
          isDiabeticFriendly: Boolean(item.isDiabeticFriendly ?? item.is_diabetic_friendly),
        })),
      }
    },

    async startOrderFlow(guestId, name, pref, isLate, lateMinutes, category = null) {
      this.currentOrderingForId = guestId
      this.currentOrderingFor = name
      this.currentOrderingPref = pref || 'Any'
      this.currentCategory = category
      this.currentIsLate = Boolean(isLate)
      this.currentLateMinutes = Number(lateMinutes || 30)
      this.editingOrderId = null
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
            guest_name: name,
          },
        })

        this.scannedRestaurants = (data?.restaurants || []).map(this.normalizeRestaurant)
        this.scanWidened = Boolean(data?.widened)
      } catch (error) {
        console.error('Restaurant scan failed:', error)
        this.scanWidened = true
        this.scannedRestaurants = []
      } finally {
        this.isScanning = false
      }
    },

    selectRestaurant(resto) {
      const normalized = this.normalizeRestaurant(resto)

      this.editingOrderId = this.currentOrderingForId == null
    ? (this.orders.find(
        (o) => !o.guest && o.restaurant_name === normalized.name
      )?.id || null)
    : (this.orders.find((o) => o.guest === this.currentOrderingForId)?.id || null)


      this.showAiScan = false
      this.tempRestaurantObj = normalized
      this.tempRestaurant = normalized.name
      this.tempETA = Number(normalized.deliveryMins || 35)
      this.tempDistanceKm = normalized.distanceKm
      this.tempMenuSelection = normalized.eligibleMenu.map((item) => ({ ...item, qty: 0 }))
      this.showMenu = true
    },

    updateMenuQty(index, change) {
      const item = this.tempMenuSelection[index]
      if (!item) return
      const qty = Math.max(0, Number(item.qty || 0) + change)
      this.tempMenuSelection[index] = { ...item, qty }
      this.tempMenuSelection = [...this.tempMenuSelection]
    },

    buildOrderPayload(selected) {
      const itemTotal = selected.reduce(
        (sum, item) => sum + Number(item.price) * Number(item.qty),
        0,
      )

      return {
        guest: this.currentOrderingForId,
        placed_by: 'host',
        restaurant_id: String(this.tempRestaurantObj?.id || ''),
        restaurant_name: this.tempRestaurant,
        delivery_fee: 30,
        taxes: Math.round(itemTotal * 0.05),
        payment_method: this.currentIsLate ? 'online' : null,
        items: selected.map((item) => ({
          external_item_id: String(item.id),
          name: item.name,
          unit_price: Number(item.price),
          quantity: Number(item.qty),
          is_veg: Boolean(item.isVeg),
          is_jain_compatible: Boolean(item.isJainCompatible),
          is_diabetic_friendly: Boolean(item.isDiabeticFriendly),
        })),
      }
    },

    async confirmMenuSelection() {
      const selected = this.tempMenuSelection.filter((item) => Number(item.qty) > 0)
      if (!selected.length) {
        alert('Please add at least one item.')
        return
      }

      const payload = this.buildOrderPayload(selected)

      if (this.currentIsLate) {
        this.pendingOrderPayload = payload
        this.showMenu = false
        await this.computeLateSchedule()
        return
      }

      const saved = await this.placeOrder(payload)
      if (saved) this.showMenu = false
    },

    async placeOrder(payload) {
      this.placingOrder = true

      try {
        let order
        if (this.editingOrderId) {
          order = await apiRequest(
            `/parties/${this.partyCode}/orders/${this.editingOrderId}/`,
            { method: 'PATCH', body: payload },
          )
        } else {
          order = await apiRequest(`/parties/${this.partyCode}/orders/`, {
            method: 'POST',
            body: payload,
          })
        }

        await this.refreshAuthoritativeState()
        this.editingOrderId = null
        return order
      } catch (error) {
        alert(error.message || 'Could not place the order.')
        return null
      } finally {
        this.placingOrder = false
      }
    },

    partyClock() {
      const source = this.party?.party_start_time
      if (!source) return null
      const date = new Date(source)
      if (Number.isNaN(date.getTime())) return null
      return `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
    },

    async computeLateSchedule() {
      this.lateScheduleLoading = true
      this.showLateSchedule = true

      const partyTime = this.partyClock()
      const guestName = this.currentOrderingFor

      try {
        if (!partyTime) throw new Error('Party start time is not set.')

        const data = await apiRequest('/ai/schedule-late-order/', {
          method: 'POST',
          body: {
            guest_name: guestName,
            pref: this.currentOrderingPref,
            late_minutes: this.currentLateMinutes,
            party_time: partyTime,
            restaurant_id: this.pendingOrderPayload?.restaurant_id,
            items: (this.pendingOrderPayload?.items || []).map((item) => ({
              id: item.external_item_id,
              qty: item.quantity,
            })),
          },
        })

        this.lateScheduleData = {
          ...data,
          guest_name: data?.guest_name || guestName,
          late_minutes: data?.late_minutes ?? this.currentLateMinutes,
          delivery_mins: data?.delivery_mins ?? this.tempETA,
        }
      } catch (error) {
        const start = this.party?.party_start_time
          ? new Date(this.party.party_start_time)
          : new Date()
        const arrival = new Date(start.getTime() + this.currentLateMinutes * 60000)
        const fire = new Date(arrival.getTime() - Number(this.tempETA || 35) * 60000)

        this.lateScheduleData = {
          guest_name: guestName,
          late_minutes: this.currentLateMinutes,
          delivery_mins: Number(this.tempETA || 35),
          fire_at: fire.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          reasoning: this.party?.party_start_time
            ? `Order is timed ${this.tempETA || 35} minutes before the guest's expected arrival.`
            : 'Party start time is not set yet; backend scheduling will remain authoritative.',
        }
      } finally {
        this.lateScheduleLoading = false
      }
    },

    async confirmLateSchedule() {
      if (!this.pendingOrderPayload) {
        this.showLateSchedule = false
        return
      }

      // fire_time/status are server-controlled. The backend derives them from
      // party_start_time + guest late offset + restaurant preparation time.
      const saved = await this.placeOrder(this.pendingOrderPayload)
      if (saved) {
        this.pendingOrderPayload = null
        this.showLateSchedule = false
      }
    },

    async runMergeCheck() {
      this.mergeLoading = true
      this.showMerge = true

      try {
        const data = await apiRequest('/ai/merge-check/', {
          method: 'POST',
          body: { orders: this.ordersForAi() },
        })
        this.mergeData = {
          has_merges: Boolean(data?.has_merges),
          merges: data?.merges || [],
        }
      } catch (error) {
        console.error('Merge check failed:', error)
        this.mergeData = { has_merges: false, merges: [] }
      } finally {
        this.mergeLoading = false
      }
    },

    ordersForAi() {
      return this.orders.map((order) => ({
        who: order.guest_name || this.hostName,
        restaurant: order.restaurant_name,
        restaurant_id: order.restaurant_id,
        items: (order.items || []).map((item) => ({
          name: item.name,
          price: item.unit_price,
          qty: item.quantity,
        })),
        itemTotal: order.item_total,
      }))
    },

    async openCheckout() {
      if (!this.orders.length) {
        alert('Place at least one order before checkout.')
        return
      }
      await this.runMergeCheck()
    },

    skipMerge() {
      this.showMerge = false
      this.runBudgetCheck()
    },

    async runBudgetCheck() {
      this.showMerge = false
      this.budgetGuardLoading = true
      this.showBudgetGuard = true

      try {
        const data = await apiRequest('/ai/budget-check/', {
          method: 'POST',
          body: {
            budget: Number(this.budget),
            current_total: this.billFinalTotal,
            guests: this.guests.map((guest) => ({
              name: guest.name,
              pref: this.prefLabel(guest.dietary_pref),
            })),
            current_orders: this.ordersForAi(),
          },
        })
        this.budgetGuardData = data || {}
      } catch (error) {
        console.error('Budget check failed:', error)
        this.budgetGuardData = {
          status: this.isOverBudget ? 'exceeded' : 'ok',
          remaining: Math.max(this.budgetLeft, 0),
          exceeded_by: this.isOverBudget ? Math.abs(this.budgetLeft) : 0,
          suggestions: [],
        }
      } finally {
        this.budgetGuardLoading = false
      }
    },

    proceedToPayment() {
      this.showBudgetGuard = false
      this.showCheckout = true
    },

    async savePartyOrders() {
      // Orders are persisted at placement time. "Save Draft" therefore only
      // refreshes from Django so the UI cannot drift from server state.
      try {
        await this.refreshAuthoritativeState()
      } catch (error) {
        alert(error.message || 'Could not refresh the saved party.')
      }
    },

    async processPayment() {
      this.isProcessing = true
      try {
        await this.refreshAuthoritativeState()
        this.generateWhatsAppMessage()
        this.showCheckout = false
        this.showSuccess = true
      } catch (error) {
        alert(error.message || 'Could not finalize the party plan.')
      } finally {
        this.isProcessing = false
      }
    },

    async runWholeSumOptimize() {
  this.isScanning = true
  this.showAiScan = true
  try {
    const splits = {}
    this.guests.forEach(g => { splits[g.dietary_pref] = (splits[g.dietary_pref] || 0) + 1 })
    const data = await apiRequest('/ai/whole-sum-optimize/', {
      method: 'POST',
      body: { guest_count: this.partySize, budget: this.budget, dietary_splits: splits },
    })
    const payload = {
      guest: null, placed_by: 'host', restaurant_id: data.restaurant_id,
      restaurant_name: data.restaurant_name, delivery_fee: 30,
      taxes: Math.round(data.items.reduce((s,i)=>s+i.price*i.quantity,0)*0.05),
      items: data.items.map(i => ({
        external_item_id: String(i.item_id), name: i.name,
        unit_price: Number(i.price), quantity: Number(i.quantity),
        is_veg: false, is_jain_compatible: false, is_diabetic_friendly: false,
      })),
    }
    await this.placeOrder(payload)
  } catch (e) {
    alert(e.message || 'Whole-sum optimization failed.')
  } finally {
    this.isScanning = false
    this.showAiScan = false
  }
},

    generateWhatsAppMessage() {
      let message = `🎉 *PARTY DETAILS* 🎉\n\n`
      message += `👑 *Host:* ${this.hostName}\n`
      if (this.party?.occasion) message += `🎊 *Occasion:* ${this.party.occasion}\n`
      message += `\n🍕 *Orders:*\n`

      this.orders.forEach((order) => {
        const items = (order.items || [])
          .map((item) => `${item.quantity}x ${item.name}`)
          .join(', ')
        const scheduled = order.fire_time ? ' ⏰' : ''
        message += `• ${order.guest_name || this.hostName}${scheduled} → ${items} (${order.restaurant_name})\n`
      })

      message += `\n💰 *Total:* ₹${this.billFinalTotal}`
      const headcount = Math.max(this.guests.length + 1, 1)
      message += `\n🔗 *Split (~₹${Math.round(this.billFinalTotal / headcount)}/person):* settle outside the app.`
      if (this.party?.join_link) message += `\n\n👥 Join link: ${this.party.join_link}`

      this.whatsappMessage = message
    },

    async copyShareText() {
      await navigator.clipboard.writeText(this.whatsappMessage)
      this.copied = true
      setTimeout(() => { this.copied = false }, 2000)
    },

    resetAll() {
      this.showSuccess = false
      this.$router.push('/')
    },
  },
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