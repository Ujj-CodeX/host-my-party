"""
ai app — AI Layer (Section 3.4) + parts of Business Logic Layer (Section 3.3).


"""

import json
import math
from datetime import datetime, timedelta

from django.conf import settings
from django.core.cache import cache
from groq import Groq
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from .merge_optimizer import build_merge_candidates


from core.models import GroqCallLog
from core.permissions import IsValidGuestSession
from party.authentication import GuestSessionAuthentication
from party.models import Party
from rest_framework import status

from .dineout_provider import get_dineout_provider
from .groq_utils import call_groq_validated,GROQ_MODEL
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

from rest_framework.exceptions import NotFound , PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated

client = Groq(api_key=settings.GROQ_API_KEY)


def _get_required_owned_party(request):
    """Require a party and verify that the authenticated user hosts it."""

    if request.method in ("GET", "HEAD"):
        party_id = request.query_params.get("party_id")
    else:
        party_id = request.data.get("party_id")

    if not party_id:
        raise ValidationError({
            "party_id": "This field is required."
        })

    try:
        party = Party.objects.get(pk=party_id)
    except (Party.DoesNotExist, ValueError, TypeError):
        raise NotFound("Party not found.")

    if party.host_id != request.user.id:
        raise PermissionDenied(
            "You do not have permission to access this party."
        )

    return party


def _get_required_owned_party(request):
    """Require a party and verify that the authenticated user hosts it."""

    if request.method in ("GET", "HEAD"):
        party_id = request.query_params.get("party_id")
    else:
        party_id = request.data.get("party_id")

    if not party_id:
        raise ValidationError({
            "party_id": "This field is required."
        })

    try:
        party = Party.objects.get(pk=party_id)
    except (Party.DoesNotExist, ValueError, TypeError):
        raise NotFound("Party not found.")

    if party.host_id != request.user.id:
        raise PermissionDenied(
            "You do not have permission to access this party."
        )

    return party

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
@permission_classes([IsAuthenticated])
def get_restaurants(request):
    """
    Groq reads the mock data, filters by guest pref + category,
    and returns distance-sorted eligible restaurants with only safe menu items.
    """
    pref = request.data.get('pref', 'Any')
    category = request.data.get('category', None)
    guest_name = request.data.get('guest_name', 'Guest')

    party = _get_required_owned_party(request)
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
@permission_classes([IsAuthenticated])
def schedule_late_order(request):

    party = _get_required_owned_party(request)
    
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
    cache_key = f"scheduled_orders:{party.code}"
    scheduled = cache.get(cache_key, [])
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
     "status": "scheduled",
    }

    scheduled.append(order_entry)
    cache.set(cache_key, scheduled, timeout=3600)

    return Response({
        "success": True,
        "guest_name": guest_name,
        "fire_at": schedule_data.get("fire_at"),
        "reasoning": schedule_data.get("reasoning"),
        "delivery_mins": delivery_mins,
        "late_minutes": late_minutes
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_scheduled_orders(request):
    """Return scheduled orders belonging only to the host's party."""

    party = _get_required_owned_party(request)

    cache_key = f"scheduled_orders:{party.code}"
    scheduled = cache.get(cache_key, [])

    return Response({
        "success": True,
        "scheduled_orders": scheduled,
    })

# ─────────────────────────────────────────────
# 3. BUDGET GUARDIAN
# ─────────────────────────────────────────────
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def budget_check(request):
    """Evaluate the budget using the authoritative to_pay amount."""

    party = _get_required_owned_party(request)

    try:
        budget = float(request.data.get("budget", 0))
    except (TypeError, ValueError):
        raise ValidationError({"budget": "A valid numeric budget is required."})

    if not math.isfinite(budget) or budget < 0:
        raise ValidationError({"budget": "Budget must be finite and non-negative."})

    raw_to_pay = request.data.get("to_pay")

    if raw_to_pay is None or isinstance(raw_to_pay, bool):
        raise ValidationError({
            "to_pay": "The payable total is required."
        })

    try:
        to_pay = float(raw_to_pay)
    except (TypeError, ValueError):
        raise ValidationError({
            "to_pay": "A valid numeric payable total is required."
        })

    if not math.isfinite(to_pay) or to_pay < 0:
        raise ValidationError({
            "to_pay": "Payable total must be finite and non-negative."
        })

    guests = request.data.get("guests", [])
    current_orders = request.data.get("current_orders", [])

    # The provider's payable total is the decision input.
    # item_total, delivery_fee and taxes are display-only.
    remaining = budget - to_pay

    safe_upsells = get_upsell_items_for_guests(guests)
    affordable_upsells = [
        item for item in safe_upsells
        if item["price"] <= remaining
    ]

    if remaining < 0:
        prompt = budget_exceeded_prompt(
            budget,
            to_pay,
            remaining,
            json.dumps(current_orders),
        )
        template_key = "budget_exceeded"

    elif remaining >= 200 and affordable_upsells:
        upsell_list = [
            f"{item['name']} (₹{item['price']})"
            for item in affordable_upsells[:5]
        ]
        prompt = budget_headroom_prompt(
            budget,
            to_pay,
            remaining,
            upsell_list,
        )
        template_key = "budget_headroom"

    else:
        return Response({
            "success": True,
            "status": "ok",
            "to_pay": to_pay,
            "remaining": remaining,
            "suggestions": [],
            "message": "Budget on track. Nothing extra to recommend.",
        })

    result, used_fallback, _log = call_groq_validated(
        client,
        call_type=GroqCallLog.CallType.BUDGET_GUARDIAN,
        prompt=prompt,
        request_payload={
            "budget": budget,
            "to_pay": to_pay,
            "remaining": remaining,
            "guest_count": len(guests),
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
            "message": "Could not parse AI response.",
        }

    return Response({
        "success": True,
        "to_pay": to_pay,
        **result,
    })


# ─────────────────────────────────────────────
# 4. SHARED PREFERENCE MERGER
# ─────────────────────────────────────────────
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def merge_check(request):
    party = _get_required_owned_party(request)
    orders = request.data.get("orders", [])

    if not isinstance(orders, list):
        raise ValidationError({
            "orders": "Orders must be a list."
        })

    if len(orders) < 2:
        return Response({
            "success": True,
            "has_merges": False,
            "merges": [],
            "message": "Not enough orders to check for merges.",
        })

    for order in orders:
        if not isinstance(order, dict):
            raise ValidationError({
                "orders": "Every order must be an object."
            })

    # Step 1: Deterministic Python hard filters.
    try:
        candidates = build_merge_candidates(
            orders,
            max_distance_km=request.data.get("max_distance_km", 5.0),
            min_rating=request.data.get("min_rating", 4.0),
        )
    except ValueError as exc:
        raise ValidationError({"filters": str(exc)})

    if not candidates:
        return Response({
            "success": True,
            "has_merges": False,
            "merges": [],
            "message": "No restaurant passed the distance, rating, and dietary filters.",
        })

    # Step 2: Build concise order summaries.
    orders_summary = []

    for order in orders:
        items = order.get("items", [])
        if not isinstance(items, list):
            items = []

        item_names = []
        for item in items:
            if not isinstance(item, dict):
                continue

            name = item.get("name")
            if name:
                item_names.append(
                    f"{item.get('qty', 1)}x {name}"
                )

        orders_summary.append(
            f"{order.get('who', 'Guest')}: "
            f"{', '.join(item_names) or 'No item details'}"
        )

    # Step 3: Groq sees only Python-approved candidates.
    prompt = (
        merge_check_prompt(orders_summary)
        + "\n\nSTRICT CONSTRAINTS:\n"
        + "The following restaurants have already passed deterministic "
          "Python checks for distance, rating, and dietary compatibility.\n"
        + "Only recommend restaurants from this candidate list. "
          "Never invent or substitute a restaurant.\n"
        + "Use only menu items shown in the candidate data and respect "
          "each guest's eligible menu.\n"
        + "Do not invent numeric delivery savings; exact savings are "
          "not available from this input.\n\n"
        + "Hard-filtered candidates:\n"
        + json.dumps(candidates, ensure_ascii=False)
    )

    result, used_fallback, _log = call_groq_validated(
        client,
        call_type=GroqCallLog.CallType.MERGE_CHECK,
        prompt=prompt,
        request_payload={
            "order_count": len(orders),
            "candidate_restaurants": [
                candidate["id"] for candidate in candidates
            ],
            "guests": [
                order.get("who", "Guest") for order in orders
            ],
        },
        template_key="merge_check",
        party=party,
        max_tokens=400,
    )

    if used_fallback or result is None:
        return Response({
            "success": True,
            "has_merges": False,
            "merges": [],
            "message": "No validated merge recommendation is available.",
        })

    # Step 4: Never return a restaurant or shared item that failed
    # the deterministic candidate/menu checks.
    candidate_by_name = {
        candidate["name"]: candidate
        for candidate in candidates
    }

    known_guests = {
        str(order.get("who", "Guest"))
        for order in orders
    }

    safe_merges = []

    for merge in result.get("merges", []):
        if not isinstance(merge, dict):
            continue

        restaurant_name = merge.get("restaurant")
        candidate = candidate_by_name.get(restaurant_name)

        if candidate is None:
            continue

        guests = merge.get("guests", [])
        if (
            not isinstance(guests, list)
            or len(set(guests)) < 2
            or not set(guests).issubset(known_guests)
        ):
            continue

        # A shared item must be eligible for every order.
        eligible_sets = [
            {
                item["name"]
                for item in guest_menu["eligible_items"]
                if item.get("name")
            }
            for guest_menu in candidate["eligible_menus_by_guest"]
        ]

        common_items = (
            set.intersection(*eligible_sets)
            if eligible_sets
            else set()
        )

        proposed_items = merge.get("shared_items", [])
        if not isinstance(proposed_items, list):
            continue

        shared_items = [
            item for item in proposed_items
            if isinstance(item, str) and item in common_items
        ]

        if not shared_items:
            continue

        safe_merges.append({
            "guests": guests,
            "restaurant": restaurant_name,
            "shared_items": shared_items,
            "savings_note": (
                "Potential consolidation; exact delivery savings "
                "have not been calculated."
            ),
        })

    return Response({
        "success": True,
        "has_merges": bool(safe_merges),
        "merges": safe_merges,
        "message": (
            "Validated merge suggestions found."
            if safe_merges
            else "No merge recommendation passed final validation."
        ),
    })
# ─────────────────────────────────────────────
# 5. ORIGINAL PLAN PARTY (kept for compatibility)
# ─────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def plan_party(request):
    party = _get_required_owned_party(request)

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
        model=GROQ_MODEL,
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
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def dineout_restaurants(request):
    party = _get_required_owned_party(request)
    address_id = party.swiggy_address_id

    if not address_id:
        return Response(
            {
                "code": "party_address_required",
                "detail": "Select a saved address for this party first.",
            },
            status=status.HTTP_409_CONFLICT,
        )

    guest_count = int(request.data.get("guest_count") or 1)
    budget = float(request.data.get("budget") or 0)
    max_distance_km = float(request.data.get("max_distance_km") or 10)

    dietary_prefs = request.data.get("dietary_prefs") or []
    if isinstance(dietary_prefs, str):
        dietary_prefs = [dietary_prefs]

    normalized = {
        str(pref).lower().replace("-", "_")
        for pref in dietary_prefs
    }
    needs_veg = bool(normalized & {"veg", "vegan", "jain"})
    needs_jain = "jain" in normalized

    per_head_budget = budget / guest_count if guest_count else budget

    provider = get_dineout_provider()
    restaurants = provider.search_restaurants(
        address_id=address_id,
        guest_count=guest_count,
        needs_veg=needs_veg,
        needs_jain=needs_jain,
        max_distance_km=max_distance_km,
    )

    ranked = []
    for restaurant in restaurants:
        estimated_per_head = restaurant.get("avgCostForTwo", 0) / 2
        budget_status = (
            "ok"
            if not budget or estimated_per_head <= per_head_budget
            else "over_budget"
        )

        ranked.append({
            **restaurant,
            "estimatedPerHead": round(estimated_per_head),
            "estimatedTotal": round(estimated_per_head * guest_count),
            "budgetStatus": budget_status,
            "budgetNote": (
                "Fits group budget"
                if budget_status == "ok"
                else (
                    f"Approx ₹{round((estimated_per_head - per_head_budget) * guest_count)} "
                    "over budget"
                )
            ),
            "aiReason": (
                "Matches seating, distance, dietary needs, "
                "and mock Dineout availability."
            ),
        })

    ranked.sort(
        key=lambda item: (
            item["budgetStatus"] != "ok",
            item["distanceKm"],
            -item["rating"],
        )
    )

    return Response({
        "success": True,
        "restaurants": ranked,
    })

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def dineout_slots(request):
    _get_required_owned_party(request)

    provider = get_dineout_provider()
    result = provider.check_slots(
        request.data.get("restaurant_id"),
        request.data.get("date"),
        int(request.data.get("guest_count") or 1),
    )
    return Response(result)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def dineout_book(request):
    _get_required_owned_party(request)

    provider = get_dineout_provider()
    result = provider.book_table(
        request.data.get("restaurant_id"),
        request.data.get("date"),
        request.data.get("time"),
        int(request.data.get("guest_count") or 1),
        special_request=request.data.get("special_request", ""),
    )
    return Response(result)

