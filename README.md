# 🎉 Host My Party

### AI-Assisted Party Orchestration for Swiggy Food & Dineout

> Coordinate guests, dietary preferences, orders, budgets, arrival times, and dineout plans from one shared party experience.

**Host My Party** is a full-stack prototype developed as part of the **Swiggy Builders Club**. It explores how an orchestration layer can sit on top of Swiggy Food and Dineout experiences to simplify group food planning.

The current build uses a **mock Swiggy provider** while partner/MCP access is pending. The integration boundary is intentionally isolated so that the mock provider can later be replaced by real Swiggy capabilities without redesigning the core party workflow.

---

## 🎥 Demo

**Latest Product Walkthrough:**  
`https://drive.google.com/file/d/1S5fhYGIY0Ls6VljKWZLuTKsPtM3LdBJN/view?usp=drivesdk`

The demo covers the current end-to-end flow: party creation, Food Delivery orchestration, guest participation, dietary-aware recommendations, real-time synchronization, budget tracking, and late-arrival handling.

---

## 💡 The Problem

Group food planning becomes surprisingly complicated once multiple people are involved.

A host may need to coordinate:

- different dietary preferences
- individual vs shared ordering
- multiple restaurants and menus
- a fixed party budget
- guests arriving at different times
- real-time changes from multiple participants
- dineout restaurant selection and booking

**Host My Party turns these disconnected decisions into one coordinated party workflow.**

---

## ✨ Product Experience

### 🍱 Food Delivery

The host can choose between two orchestration strategies:

**Member-wise**

Each guest can have an independent dietary preference and order. Guests may order for themselves through a shareable party link, while the host retains visibility and override control.

**Whole-Sum**

The host manages one combined order optimized around the group's overall preferences and budget.

### 🍽️ Dineout

For dineout parties, the orchestration changes from individual ordering to group-level restaurant discovery.

The system considers:

- party size
- dietary requirements
- restaurant suitability
- estimated cost
- seating/capacity constraints
- available booking slots

---

## 🧠 Intelligent Orchestration

### Dietary-Aware Recommendations

The recommendation layer considers preferences such as:

- Vegetarian
- Non-Vegetarian
- Vegan
- Jain
- Diabetic-friendly

Groq is used for reasoning and recommendation assistance while deterministic backend validation protects important constraints.

### ⏰ Late-Arrival Scheduling

A guest can be marked as arriving late.

Instead of sending every order at the same time, Host My Party can calculate an appropriate order trigger time using:

```text
fire_time =
party_start_time
+ guest_late_offset
- estimated_restaurant_preparation_time
```

Background scheduling is handled using Celery and Redis.

### 💰 Budget Guardian

The party maintains a running total against the host's configured budget.

The orchestration layer can detect when the party is approaching or exceeding the available budget and surface adjustment suggestions.

### 🔀 Order Merge Detection

Compatible orders can be identified for consolidation where appropriate, reducing unnecessary fragmentation across the party.

### ⚡ Real-Time Party State

Guest activity is synchronized with the host dashboard using Django Channels and WebSockets.

REST remains the authoritative state, while WebSocket events trigger immediate UI synchronization.

---

## 👥 Frictionless Guest Flow

Guests do **not** need to create a permanent account.

```text
Host creates party
        ↓
Shareable /join/:code link
        ↓
Guest enters name + dietary preference
        ↓
Party-scoped guest session issued
        ↓
Guest explores recommendations
        ↓
Guest places/updates own order
        ↓
Host dashboard updates in real time
```

Guest sessions are restricted to the specific party and guest identity.

---

## 🏗️ Architecture

```text
┌──────────────────────────────────────┐
│             Vue.js 3 UI              │
│                                      │
│ Host Dashboard   Guest Flow   Dineout│
└───────────────────┬──────────────────┘
                    │
                 REST API
                    │
┌───────────────────▼──────────────────┐
│        Django + Django REST           │
│                                      │
│ Party / Guest / Order / Booking      │
│ Authentication & Authorization       │
└───────┬───────────┬───────────┬──────┘
        │           │           │
        │           │           └─────────────┐
        ▼           ▼                         ▼
     Groq AI    PostgreSQL              Celery + Redis
        │
        ▼
┌──────────────────────────────────────┐
│        Swiggy Provider Layer          │
│                                      │
│  Current: MockSwiggyProvider         │
│             ↓                        │
│  Target:  Real Swiggy MCP/API        │
└──────────────────────────────────────┘
```

---

## 🔌 Swiggy Integration Strategy

### Current State

The prototype currently runs against a local mock provider containing representative restaurant, menu, dietary, pricing, and dineout data.

```text
Application
     ↓
Swiggy Provider Interface
     ↓
Mock Provider
```

This allows the orchestration workflow to be developed and demonstrated independently of production credentials.

### Target State

Once the appropriate Swiggy partner/MCP capabilities are available:

```text
Application
     ↓
Swiggy Provider Interface
     ↓
Real Swiggy Food / Dineout Integration
```

The intention is to replace the provider implementation rather than rewrite the orchestration layer.

### Integration Capabilities Requested

For a complete integration, Host My Party would benefit from access to:

**Swiggy Food**
- restaurant discovery
- live menu/catalogue data
- dietary metadata where available
- pricing and delivery estimates
- sandbox/test order placement
- order status updates

**Swiggy Dineout**
- restaurant search and details
- availability/slot discovery
- booking creation
- booking confirmation/status

**Payment / Checkout**

Host My Party is designed as an **orchestration layer, not a payment processor**.

The intended production flow is:

```text
Host My Party
    ↓
coordinates party
    ↓
finalizes selected order / booking
    ↓
hands off to Swiggy
    ↓
Swiggy-native checkout & payment
    ↓
order / booking confirmation
    ↓
status reflected back in Host My Party
```

No independent payment gateway is intended to be introduced into Host My Party.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Vue.js 3, Bootstrap 5 |
| Backend | Django, Django REST Framework |
| Database | PostgreSQL / Supabase |
| AI | Groq |
| Authentication | JWT + Google OAuth |
| Realtime | Django Channels, WebSockets |
| Background Tasks | Celery + Redis |
| Deployment | Vercel + Railway |
| External Integration | Mock Swiggy Provider → Swiggy MCP/API |

---

## 🔐 Authentication & Security

Host and guest identities use separate authentication models.

### Host

```text
Login / Google OAuth
        ↓
JWT access + refresh tokens
        ↓
Authenticated Django REST endpoints
```

### Guest

```text
Party join link
        ↓
Guest created for specific party
        ↓
Opaque session token
        ↓
Party-scoped GuestSessionAuthentication
```

Additional safeguards include:

- host ownership checks
- guest-party isolation
- protected host routes
- server-controlled order totals/status
- server-side scheduling
- restricted guest mutation scope

---

## 📂 Project Structure

```text
host-my-party/
│
├── backend/
│   ├── config/
│   ├── accounts/
│   ├── party/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── consumers.py
│   │   ├── tasks.py
│   │   ├── mock_swiggy.py
│   │   └── urls.py
│   └── requirements.txt
│
├── frontend/
│   └── host-my-party/
│       ├── src/
│       │   ├── api/
│       │   ├── router/
│       │   ├── views/
│       │   │   ├── LandingView.vue
│       │   │   ├── SelectionView.vue
│       │   │   ├── OrchestratorView.vue
│       │   │   ├── JoinPartyView.vue
│       │   │   ├── GuestOrderView.vue
│       │   │   └── DineoutView.vue
│       │   └── App.vue
│       └── package.json
│
└── README.md
```

---

## 🚀 Running Locally

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL
- Redis
- Groq API key

### Backend

```bash
cd backend

python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt

python manage.py migrate
python manage.py runserver
```

### Frontend

```bash
cd frontend/host-my-party

npm install
npm run dev
```

Development URLs:

```text
Frontend: http://localhost:5173
Backend:  http://localhost:8000
```

Environment variables and credentials are intentionally excluded from the repository.

---

## 🗺️ Current Status

| Capability | Status |
|---|---:|
| Host authentication | ✅ Implemented |
| Party creation | ✅ Implemented |
| Member-wise orchestration | ✅ Implemented |
| Whole-Sum orchestration | ✅ Implemented |
| Guest invite/session flow | ✅ Implemented |
| Dietary-aware recommendations | ✅ Implemented |
| Real-time synchronization | ✅ Implemented |
| Budget tracking | ✅ Implemented |
| Late-arrival scheduling | ✅ Implemented |
| Dineout workflow | ✅ Prototype |
| Swiggy restaurant/menu data | 🧪 Mock provider |
| Real Swiggy Food MCP/API | ⏳ Awaiting access |
| Real Dineout integration | ⏳ Awaiting access |
| Swiggy-native checkout/payment | 🎯 Integration target |

---

## 🎯 Product Principle

Host My Party does not aim to replace Swiggy's ordering, booking, logistics, or payment infrastructure.

It acts as the **coordination layer before and around those capabilities**:

> **Plan together → orchestrate intelligently → execute through Swiggy.**

---

## 👨‍💻 Developer

**Ujjawal Rauniyar**  
BS — Data Science & Applications, IIT Madras

Python · Django · Django REST Framework · PostgreSQL · Vue.js · Celery · Redis

**GitHub:**  
https://github.com/Ujj-CodeX

**LinkedIn:**  
https://linkedin.com/in/ujjawal-rauniyar-21a34a272

---

## 🤝 Swiggy Builders Club

Host My Party is currently being developed as part of the **Swiggy Builders Club**.

The current prototype demonstrates the orchestration layer using mock integration data while awaiting the appropriate Swiggy capabilities required to move from simulation to real ordering, logistics, Dineout booking, and Swiggy-native checkout.

Feedback on the recommended MCP/API integration path is welcome.

---

<p align="center">
  <strong>Host My Party</strong><br>
  Plan together. Orchestrate intelligently. Execute through Swiggy.
</p>
