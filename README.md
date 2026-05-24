# 🎉 Host My Party
### AI-Powered Party Planning Agent — Swiggy MCP Integration

> **One prompt. Every preference handled. Party sorted.**

Built for **Swiggy Builders Club** — integrating Swiggy Food MCP Server with Groq LLM to plan entire parties end-to-end, handling dietary conflicts, per-member ordering, late arrival scheduling, bill splitting, and WhatsApp-ready output.

---

## 🧠 What It Does

Host My Party is a Django + Vue.js AI agent that connects to Swiggy's Food MCP Server to plan a group party from scratch. The host inputs guest names, dietary preferences, budget, and party time — the AI handles everything else.

| Problem | How We Solve It |
|--------|----------------|
| Mixed dietary needs (Jain + Diabetic + Non-Veg) | Multi-constraint conflict detection via Groq LLM |
| Someone always arrives late | Task Scheduler auto-places late arrival orders |
| Bill splitting after ordering is painful | Per-person exact split with UPI deeplinks |
| Sharing the plan with the group | One-tap WhatsApp-ready message generated |

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Vue.js 3 + Bootstrap 5 |
| Backend | Django 6 + Django REST Framework |
| AI Engine | Groq API — Llama 3.3 70B (Free Tier) |
| MCP Integration | Swiggy Food MCP Server |
| Deployment | Vercel (Frontend) + Railway (Backend) |

---

## 🏗️ Architecture

```
User (Vue.js Frontend)
        ↓  REST API
Django Backend
        ↓
Groq LLM (Llama 3.3 70B) ← Brain / Orchestrator
        ↓  Tool Calling
Swiggy Food MCP Server
        ↓
Conflict Detection + Filtering
        ↓
WhatsApp-Ready Party Plan Output
```

---

## ✨ Core Features

### 1. Two Ordering Modes
- **Explicit Mode** — Host assigns dishes per guest individually
- **Wholesome Mode** — Host places one shared optimized order for everyone

### 2. Multi-Constraint Conflict Detection
Groq LLM filters restaurants satisfying ALL guest preferences simultaneously:
- Jain guests → `isJainCompatible: true`
- Diabetic guests → `isDiabeticFriendly: true`
- Veg/Non-Veg → handled in single pass

### 3. Distance-Based Restaurant Filter
Restaurants are sorted by proximity to host's address — ensuring all orders arrive at approximately the same time.

### 4. Late Arrival Scheduler
Flag individual guests as arriving late. Their order auto-schedules separately via task queue. Main order fires immediately.

### 5. Bill Split + UPI Deeplinks
Exact per-person amount calculated. Each person gets a direct UPI payment link in the final WhatsApp message.

### 6. WhatsApp-Ready Output
One-tap copy of complete party plan — venue, items, timings, per-person cost, UPI links — formatted for WhatsApp sharing.

---

## 🚀 Run Locally

### Prerequisites
- Python 3.10+
- Node.js 18+
- Groq API Key (free at [console.groq.com](https://console.groq.com))

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
echo "GROQ_API_KEY=your_key_here" > .env

python manage.py runserver
```

### Frontend Setup
```bash
cd frontend/host-my-party
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`
Backend runs at `http://localhost:8000`

---

## 📡 API Reference

### `POST /api/plan-party/`

**Request:**
```json
{
  "guests": [
    { "name": "Priya", "diet": "jain" },
    { "name": "Rahul", "diet": "non-veg" },
    { "name": "Arjun", "diet": "diabetic" }
  ],
  "budget": 5000,
  "time": "7:30 PM",
  "mode": "wholesome"
}
```

**Response:**
```json
{
  "plan": "🎉 Party Plan Ready!\n\nPunjab Grill...",
  "guests": [...]
}
```

---

## 🗂️ Project Structure

```
host-my-party/
│
├── backend/
│   ├── config/
│   │   ├── settings.py
│   │   └── urls.py
│   ├── party/
│   │   ├── views.py          ← API + Groq integration
│   │   ├── mock_swiggy.py    ← Swiggy MCP mock (pending credentials)
│   │   └── urls.py
│   └── requirements.txt
│
├── frontend/host-my-party/
│   ├── src/
│   │   ├── views/
│   │   │   ├── LandingView.vue       ← Mode selection
│   │   │   └── OrchestratorView.vue  ← Main dashboard
│   │   ├── router/index.js
│   │   └── App.vue
│   └── package.json
│
└── README.md
```

---

## 🔌 Swiggy MCP Integration

Currently using mock Swiggy Food MCP data that mirrors the exact production schema:

```python
# mock_swiggy.py — matches real Swiggy MCP response structure
{
  "success": True,
  "data": {
    "restaurants": [
      {
        "id": "rest_001",
        "name": "Punjab Grill",
        "distanceKm": 2.1,
        "menu": [
          {
            "name": "Dal Makhani",
            "price": 220,
            "isVeg": True,
            "isJainCompatible": True,
            "isDiabeticFriendly": True
          }
        ]
      }
    ]
  }
}
```

**Awaiting Swiggy Builders Club credentials** — one function swap and real data flows in.

---

## 🗓️ Build Timeline

| Day | Milestone |
|-----|-----------|
| Day 1-2 | OAuth 2.1 + MCP client setup + Groq integration ✅ |
| Day 3-4 | Conflict detection engine + per-member ordering logic ✅ |
| Day 5 | Late Arrival Mode + Budget Guard |
| Day 6 | Bill split + UPI deeplinks + WhatsApp generator |
| Day 7 | End-to-end demo video + deployment |

---

## 👨‍💻 Developer

| | |
|--|--|
| **Name** | Ujjawal Rauniyar |
| **Education** | BS Student — IIT Madras (Data Science & Applications) |
| **Stack** | Python, Django REST, PostgreSQL, Vue.js, Celery, Redis |
| **Production Project** | [JeevanDaan+](https://github.com/Ujj-CodeX) — Healthcare platform, 45+ REST API endpoints |
| **GitHub** | [github.com/Ujj-CodeX](https://github.com/Ujj-CodeX) |
| **LinkedIn** | [linkedin.com/in/ujjawal-rauniyar-21a34a272](https://linkedin.com/in/ujjawal-rauniyar-21a34a272) |

---

## 📬 Swiggy Builders Club

Built as part of **Swiggy Builders Club** application.
Demo video shared at [builders@swiggy.in](mailto:builders@swiggy.in) within 7 days of API access.

> *Happy to jump on a call to walk through the architecture.*

---

<p align="center">Made with ❤️ for Swiggy Builders Club</p>
