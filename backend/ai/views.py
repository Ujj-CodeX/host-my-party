"""
ai app — AI Layer (Section 3.4) + parts of Business Logic Layer (Section 3.3).


"""

import json
from datetime import datetime, timedelta

from django.conf import settings
from django.core.cache import cache
from groq import Groq
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response

from core.models import GroqCallLog
from core.permissions import IsValidGuestSession
from party.authentication import GuestSessionAuthentication
from party.models import Party

from .dineout_provider import get_dineout_provider
from .groq_utils import call_groq_validated
from .mock_swiggy import (
    RESTAURANTS,
    get_mock_restaurants,
    get_upsell_items_for_guests,
)
from .prompt_templates import (
    budget_exceeded_prompt,
    budget_headroom_prompt,
    merge_check_prompt,
    restaurant_filter_prompt,
    scheduling_prompt,
)

client = Groq(api_key=settings.GROQ_API_KEY)


def _get_optional_party(request):
    
    party_id = request.data.get('party_id') if hasattr(request, 'data') else None
    if not party_id:
        return None
    return Party.objects.filter(id=party_id).first()


# ─────────────────────────────────────────────
# 1. RESTAURANT RECOMMENDATIONS
# ─────────────────────────────────────────────
def _filter_restaurants_via_ai(pref, category, guest_name, party=None):
    
    prompt = restaurant_filter_prompt(pref, category, guest_name, json.dumps(RESTAURANTS, indent=2))

    restaurants, used_fallback, _log = call_groq_validated(
        client,
        call_type=GroqCallLog.CallType.RESTAURANT_FILTER,
        prompt=prompt,
        request_payload={"pref": pref, "category": category, "guest_name": guest_name},
        template_key="restaurant_filter",
        party=party,
        max_tokens=2000,
    )

    if used_fallback or restaurants is None:
        # Hard fallback — pure Python filter, no Groq.
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
    else:
        widened = False

    return restaurants, widened


@api_view(['POST'])
def get_restaurants(request):
    """
    Groq reads the mock data, filters by guest pref + category,
    and returns distance-sorted eligible restaurants with only safe menu items.
    """
    pref = request.data.get('pref', 'Any')
    category = request.data.get('category', None)
    guest_name = request.data.get('guest_name', 'Guest')

    party = _get_optional_party(request)
    restaurants, widened = _filter_restaurants_via_ai(pref, category, guest_name, party=party)

    return restaurants, widened


@api_view(['POST'])
def get_restaurants(request):
    """
    Groq reads the mock data, filters by guest pref + category,
    and returns distance-sorted eligible restaurants with only safe menu items.
    """
    pref = request.data.get('pref', 'Any')
    category = request.data.get('category', None)
    guest_name = request.data.get('guest_name', 'Guest')

    party = _get_optional_party(request)
    restaurants, widened = _filter_restaurants_via_ai(pref, category, guest_name, party=party)

    return Response({
        "success": True,
        "pref": pref,
        "category": category,
        "widened": widened,
        "restaurants": restaurants,
        "message": f"Found {len(restaurants)} restaurants for {guest_name} ({pref})"
    })


@api_view(['GET'])
@authentication_classes([GuestSessionAuthentication])
@permission_classes([IsValidGuestSession])
def guest_get_restaurants(request):
    
    guest = request.auth

    restaurants, widened = _filter_restaurants_via_ai(
        pref=guest.dietary_pref,
        category=request.query_params.get("category"),
        guest_name=guest.name,
        party=guest.party,
    )

    return Response({
        "success": True,
        "pref": guest.dietary_pref,
        "widened": widened,
        "restaurants": restaurants,
        "message": f"Found {len(restaurants)} restaurants for {guest.name} ({guest.dietary_pref})"
    })


# ─────────────────────────────────────────────
# 2. LATE ARRIVAL SCHEDULING
# ─────────────────────────────────────────────
@api_view(['POST'])
def schedule_late_order(request):
    
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

    prompt = scheduling_prompt(guest_name, party_time_str, late_minutes, delivery_mins)

    party = _get_optional_party(request)
    schedule_data, used_fallback, _log = call_groq_validated(
        client,
        call_type=GroqCallLog.CallType.SCHEDULING,
        prompt=prompt,
        request_payload={
            "guest_name": guest_name, "pref": pref, "late_minutes": late_minutes,
            "party_time": party_time_str, "restaurant_id": restaurant_id,
        },
        template_key="scheduling",
        party=party,
        max_tokens=100,
    )

    if used_fallback or schedule_data is None:
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
        prompt = budget_exceeded_prompt(budget, current_total, remaining, json.dumps(current_orders))
        template_key = "budget_exceeded"
    elif remaining >= 200 and affordable_upsells:
        upsell_list = [f"{u['name']} (₹{u['price']})" for u in affordable_upsells[:5]]
        prompt = budget_headroom_prompt(budget, current_total, remaining, upsell_list)
        template_key = "budget_headroom"
    else:
        return Response({
            "success": True,
            "status": "ok",
            "remaining": remaining,
            "suggestions": [],
            "message": "Budget on track. Nothing extra to recommend."
        })

    party = _get_optional_party(request)
    result, used_fallback, _log = call_groq_validated(
        client,
        call_type=GroqCallLog.CallType.BUDGET_GUARDIAN,
        prompt=prompt,
        request_payload={
            "budget": budget, "current_total": current_total,
            "remaining": remaining, "guest_count": len(guests),
        },
        template_key=template_key,
        party=party,
        max_tokens=300,
    )

    if used_fallback or result is None:
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

    prompt = merge_check_prompt(orders_summary)

    party = _get_optional_party(request)
    result, used_fallback, _log = call_groq_validated(
        client,
        call_type=GroqCallLog.CallType.MERGE_CHECK,
        prompt=prompt,
        request_payload={
            "order_count": len(orders),
            "guests": [o.get("who") for o in orders],
            "restaurants": list({o.get("restaurant") for o in orders}),
        },
        template_key="merge_check",
        party=party,
        max_tokens=400,
    )

    if used_fallback or result is None:
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

# ─────────────────────────────────────────────
# 6. DINEOUT MOCK/GROQ-READY HELPERS
# ─────────────────────────────────────────────
@api_view(['POST'])
def dineout_restaurants(request):
    
    guest_count = int(request.data.get('guest_count') or 1)
    budget = float(request.data.get('budget') or 0)
    max_distance_km = float(request.data.get('max_distance_km') or 10)
    dietary_prefs = request.data.get('dietary_prefs') or []
    if isinstance(dietary_prefs, str):
        dietary_prefs = [dietary_prefs]

    normalized = {str(pref).lower().replace('-', '_') for pref in dietary_prefs}
    needs_veg = bool(normalized & {'veg', 'vegan', 'jain'})
    needs_jain = 'jain' in normalized
    per_head_budget = budget / guest_count if guest_count else budget

    provider = get_dineout_provider()
    restaurants = provider.search_restaurants(
        guest_count=guest_count,
        needs_veg=needs_veg,
        needs_jain=needs_jain,
        max_distance_km=max_distance_km,
    )

    ranked = []
    for restaurant in restaurants:
        estimated_per_head = restaurant.get('avgCostForTwo', 0) / 2
        budget_status = 'ok' if not budget or estimated_per_head <= per_head_budget else 'over_budget'
        ranked.append({
            **restaurant,
            'estimatedPerHead': round(estimated_per_head),
            'estimatedTotal': round(estimated_per_head * guest_count),
            'budgetStatus': budget_status,
            'budgetNote': (
                'Fits group budget' if budget_status == 'ok'
                else f"Approx ₹{round((estimated_per_head - per_head_budget) * guest_count)} over budget"
            ),
            'aiReason': 'Matches seating, distance, dietary needs, and mock Dineout availability.',
        })

    ranked.sort(key=lambda item: (item['budgetStatus'] != 'ok', item['distanceKm'], -item['rating']))
    return Response({'success': True, 'restaurants': ranked})


@api_view(['POST'])
def dineout_slots(request):
    provider = get_dineout_provider()
    result = provider.check_slots(
        request.data.get('restaurant_id'),
        request.data.get('date'),
        int(request.data.get('guest_count') or 1),
    )
    return Response(result)


@api_view(['POST'])
def dineout_book(request):
    provider = get_dineout_provider()
    result = provider.book_table(
        request.data.get('restaurant_id'),
        request.data.get('date'),
        request.data.get('time'),
        int(request.data.get('guest_count') or 1),
        special_request=request.data.get('special_request', ''),
    )
    return Response(result)
