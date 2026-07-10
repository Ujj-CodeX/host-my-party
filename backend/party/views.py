import json
from datetime import datetime, timedelta
from django.core.cache import cache
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
from groq import Groq
from .mock_swiggy import (
    get_mock_restaurants,
    get_restaurants_for_guest,
    get_upsell_items_for_guests,
    RESTAURANTS,
)

client = Groq(api_key=settings.GROQ_API_KEY)


# ─────────────────────────────────────────────
# 1. RESTAURANT RECOMMENDATIONS 
# ─────────────────────────────────────────────
@api_view(['POST'])
def get_restaurants(request):
    """
    Groq reads the mock data, filters by guest pref + category,
    and returns distance-sorted eligible restaurants with only safe menu items.
    """
    pref = request.data.get('pref', 'Any')
    category = request.data.get('category', None)
    guest_name = request.data.get('guest_name', 'Guest')

    prompt = (
        "You are a Swiggy restaurant filter engine.\n\n"
        f"Guest name: {guest_name}\n"
        f"Guest dietary preference: {pref}\n"
        f"Food category requested: {category or 'Any'}\n\n"
        f"Available restaurants and menus:\n{json.dumps(RESTAURANTS, indent=2)}\n\n"
        "Rules:\n"
        "1. Filter restaurants that have AT LEAST ONE menu item safe for the guest's preference:\n"
        "   - Jain: only isJainCompatible=true items\n"
        "   - Veg or Pure Veg: only isVeg=true items\n"
        "   - Vegan: only isVeg=true items\n"
        "   - Diabetic: only isDiabeticFriendly=true items\n"
        "   - Non-Veg or Any: all items are fine\n"
        "2. Sort restaurants by distanceKm ascending (nearest first)\n"
        "3. For each restaurant, only include eligible menu items (filtered by rule 1)\n"
        "4. If category is not 'Any', prefer restaurants whose cuisines match it, but still include others if no match\n"
        "5. Only include restaurants with availabilityStatus=OPEN\n\n"
        "Reply ONLY as a JSON array of restaurants, each with fields: "
        "id, name, cuisines, rating, deliveryTime, deliveryMins, distanceKm, eligibleMenu (array of safe items with id/name/price/isVeg/isJainCompatible/isDiabeticFriendly). "
        "No explanation, no markdown, just the JSON array."
    )

    groq_resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000
    )

    raw = groq_resp.choices[0].message.content.strip()
    try:
        clean = raw.replace("```json", "").replace("```", "").strip()
        restaurants = json.loads(clean)
        widened = False
    except Exception:
        # Hard fallback — pure Python filter, no Groq
        restaurants = []
        for r in RESTAURANTS:
            if r['availabilityStatus'] != 'OPEN':
                continue
            eligible = []
            for item in r['menu']:
                p = pref.lower()
                if p == 'jain' and not item['isJainCompatible']:
                    continue
                if p in ('veg', 'pure veg', 'vegan') and not item['isVeg']:
                    continue
                if p == 'diabetic' and not item['isDiabeticFriendly']:
                    continue
                eligible.append(item)
            if eligible:
                restaurants.append({**r, 'eligibleMenu': eligible})
        restaurants.sort(key=lambda x: x['distanceKm'])
        widened = True

    return Response({
        "success": True,
        "pref": pref,
        "category": category,
        "widened": widened,
        "restaurants": restaurants,
        "message": f"Found {len(restaurants)} restaurants for {guest_name} ({pref})"
    })


# ─────────────────────────────────────────────
# 2. LATE ARRIVAL SCHEDULING
# ─────────────────────────────────────────────
@api_view(['POST'])
def schedule_late_order(request):
    """
    POST {
        guest_name, pref, late_minutes, party_time (HH:MM),
        restaurant_id, items (list of item ids + qty)
    }
    Groq computes when to fire the order so it arrives on time.
    Stores scheduled order in Django cache.
    """
    guest_name = request.data.get('guest_name')
    pref = request.data.get('pref', 'Any')
    late_minutes = int(request.data.get('late_minutes', 30))
    party_time_str = request.data.get('party_time', '20:00')
    restaurant_id = request.data.get('restaurant_id')
    items = request.data.get('items', [])

    # Find restaurant delivery time
    restaurant = next((r for r in RESTAURANTS if r['id'] == restaurant_id), None)
    delivery_mins = restaurant['deliveryMins'] if restaurant else 35
    rest_name = restaurant['name'] if restaurant else 'Unknown'

    # Groq: compute ideal order fire time
    prompt = (
        f"Party starts at {party_time_str}. Guest {guest_name} will arrive {late_minutes} minutes late.\n"
        f"Restaurant delivery time is {delivery_mins} minutes.\n"
        f"When should we fire the order so food arrives just as {guest_name} arrives?\n"
        f"Reply with ONLY a JSON object: "
        f'{{ "fire_at": "HH:MM", "reasoning": "one sentence" }}'
    )

    groq_resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100
    )

    raw = groq_resp.choices[0].message.content.strip()
    try:
        # Strip markdown fences if present
        clean = raw.replace("```json", "").replace("```", "").strip()
        schedule_data = json.loads(clean)
    except Exception:
        # Fallback: compute manually
        party_dt = datetime.strptime(party_time_str, "%H:%M")
        arrival_dt = party_dt + timedelta(minutes=late_minutes)
        fire_dt = arrival_dt - timedelta(minutes=delivery_mins)
        schedule_data = {
            "fire_at": fire_dt.strftime("%H:%M"),
            "reasoning": f"Order fires {delivery_mins} mins before {guest_name} arrives."
        }

    # Store in cache (key: scheduled_orders list)
    scheduled = cache.get('scheduled_orders', [])
    order_entry = {
        "guest_name": guest_name,
        "pref": pref,
        "restaurant_id": restaurant_id,
        "restaurant_name": rest_name,
        "items": items,
        "late_minutes": late_minutes,
        "party_time": party_time_str,
        "fire_at": schedule_data.get("fire_at"),
        "reasoning": schedule_data.get("reasoning"),
        "status": "scheduled"
    }
    scheduled.append(order_entry)
    cache.set('scheduled_orders', scheduled, timeout=3600)

    return Response({
        "success": True,
        "guest_name": guest_name,
        "fire_at": schedule_data.get("fire_at"),
        "reasoning": schedule_data.get("reasoning"),
        "delivery_mins": delivery_mins,
        "late_minutes": late_minutes
    })


@api_view(['GET'])
def get_scheduled_orders(request):
    """Returns all scheduled late-arrival orders from cache."""
    scheduled = cache.get('scheduled_orders', [])
    return Response({"success": True, "scheduled_orders": scheduled})


# ─────────────────────────────────────────────
# 3. BUDGET GUARDIAN
# ─────────────────────────────────────────────
@api_view(['POST'])
def budget_check(request):
    """
    POST {
        budget: 4000,
        current_total: 3200,
        guests: [{name, pref}, ...],
        current_orders: [{who, restaurant, items: [{name, price, qty}], itemTotal}, ...]
    }
    Groq checks budget health and recommends upsell items if headroom > 200.
    """
    budget = float(request.data.get('budget', 0))
    current_total = float(request.data.get('current_total', 0))
    guests = request.data.get('guests', [])
    current_orders = request.data.get('current_orders', [])

    remaining = budget - current_total

    # Get safe upsell items for the guest group
    safe_upsells = get_upsell_items_for_guests(guests)
    affordable_upsells = [u for u in safe_upsells if u['price'] <= remaining]

    if remaining < 0:
        # EXCEEDED — ask Groq what to cut
        prompt = (
            f"Party budget is ₹{budget}. Current cart total is ₹{current_total} (over by ₹{abs(remaining)}).\n"
            f"Current orders: {json.dumps(current_orders)}\n"
            f"Suggest which items to remove to bring total under budget.\n"
            f"Reply ONLY as JSON: "
            f'{{ "status": "exceeded", "exceeded_by": {abs(remaining)}, '
            f'"remove_suggestions": ["item name 1", "item name 2"] }}'
        )
    elif remaining >= 200 and affordable_upsells:
        # HEADROOM — ask Groq to recommend upsells
        upsell_list = [f"{u['name']} (₹{u['price']})" for u in affordable_upsells[:5]]
        prompt = (
            f"Party budget is ₹{budget}. Current cart total is ₹{current_total}. "
            f"Remaining: ₹{remaining}.\n"
            f"Available add-on items safe for all guests: {', '.join(upsell_list)}\n"
            f"Recommend 2-3 items to order before checkout.\n"
            f"Reply ONLY as JSON: "
            f'{{ "status": "ok", "remaining": {remaining}, '
            f'"suggestions": [{{"name": "item", "price": 0, "reason": "short reason"}}] }}'
        )
    else:
        return Response({
            "success": True,
            "status": "ok",
            "remaining": remaining,
            "suggestions": [],
            "message": "Budget on track. Nothing extra to recommend."
        })

    groq_resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300
    )

    raw = groq_resp.choices[0].message.content.strip()
    try:
        clean = raw.replace("```json", "").replace("```", "").strip()
        result = json.loads(clean)
    except Exception:
        result = {
            "status": "exceeded" if remaining < 0 else "ok",
            "remaining": remaining,
            "suggestions": [],
            "message": "Could not parse AI response."
        }

    return Response({"success": True, **result})


# ─────────────────────────────────────────────
# 4. SHARED PREFERENCE MERGER
# ─────────────────────────────────────────────
@api_view(['POST'])
def merge_check(request):
    """
    POST {
        orders: [{who, restaurant, restaurant_id, items: [{name, price, qty}], itemTotal}, ...]
    }
    Groq finds guests with same restaurant + same/similar items and recommends merging.
    Returns merge suggestions for host to accept or skip.
    """
    orders = request.data.get('orders', [])

    if len(orders) < 2:
        return Response({
            "success": True,
            "has_merges": False,
            "merges": [],
            "message": "Not enough orders to check for merges."
        })

    orders_summary = []
    for o in orders:
        items_str = ", ".join([f"{i.get('qty', 1)}x {i['name']} (₹{i['price']})" for i in o['items']])
        orders_summary.append(f"{o['who']} from {o['restaurant']}: {items_str}")

    prompt = (
        "These are party food orders:\n"
        + "\n".join(orders_summary)
        + "\n\nFind guests ordering from the SAME restaurant who have identical or very similar items. "
        "Suggest merging their orders into one cart to save on delivery fees.\n"
        "If no merge opportunity exists, say so.\n"
        "Reply ONLY as JSON:\n"
        '{ "has_merges": true/false, "merges": [{ "guests": ["Guest A", "Guest B"], '
        '"restaurant": "Name", "shared_items": ["Item 1"], "savings_note": "Save ₹X on delivery" }] }'
    )

    groq_resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400
    )

    raw = groq_resp.choices[0].message.content.strip()
    try:
        clean = raw.replace("```json", "").replace("```", "").strip()
        result = json.loads(clean)
    except Exception:
        result = {"has_merges": False, "merges": []}

    return Response({"success": True, **result})


# ─────────────────────────────────────────────
# 5. ORIGINAL PLAN PARTY (kept for compatibility)
# ─────────────────────────────────────────────
@api_view(['POST'])
def plan_party(request):
    data = request.data
    guests = data.get('guests', [])
    budget = data.get('budget', 0)
    party_time = data.get('time', '')

    restaurants = get_mock_restaurants("party food", guests)

    prompt = (
        "You are a smart party planning assistant.\n\n"
        f"Guests and their dietary needs:\n{guests}\n\n"
        f"Total Budget: Rs.{budget}\n"
        f"Party Time: {party_time}\n\n"
        f"Available Swiggy restaurants and menu:\n{restaurants['data']}\n\n"
        "Your tasks:\n"
        "1. Filter items that are SAFE for ALL guests simultaneously\n"
        "   - Jain guests: only isJainCompatible=true items\n"
        "   - Veg guests: only isVeg=true items\n"
        "   - Diabetic guests: only isDiabeticFriendly=true items\n"
        "   - Non-veg guests: any item is fine\n"
        "2. Pick best restaurant within budget\n"
        "3. Assign items per guest\n"
        "4. Calculate per-person bill split\n"
        "5. Return WhatsApp-ready party plan with emojis\n\n"
        "Output: WhatsApp message only."
    )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000
    )

    return Response({
        "plan": response.choices[0].message.content,
        "guests": guests
    })