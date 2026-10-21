"""Deterministic hard filters for party-order merge candidates."""

import math

from .mock_swiggy import RESTAURANTS


def _normalize_preferences(order):
    raw = order.get(
        "dietary_prefs",
        order.get("dietary_pref", order.get("pref", "any")),
    )

    if isinstance(raw, str):
        raw = [raw]

    if not isinstance(raw, list):
        return ["__invalid__"]

    return [
        str(pref).strip().lower().replace("-", "_").replace(" ", "_")
        for pref in raw
    ]


def _matches_preference(item, preference):
    if preference in ("", "any", "non_veg", "nonveg"):
        return True

    if preference == "jain":
        return item.get("isJainCompatible") is True

    if preference in ("veg", "pure_veg", "vegan"):
        return item.get("isVeg") is True

    if preference == "diabetic":
        return item.get("isDiabeticFriendly") is True

    # Unknown preferences fail closed.
    return False


def _eligible_items_for_order(menu, order):
    preferences = _normalize_preferences(order)

    return [
        item
        for item in menu
        if all(
            _matches_preference(item, preference)
            for preference in preferences
        )
    ]


def build_merge_candidates(
    orders,
    max_distance_km=5.0,
    min_rating=4.0,
):
    """Return restaurants passing deterministic distance, rating,
    availability, and per-order dietary filters.

    Missing dietary preferences default to 'any' for compatibility.
    """
    if not isinstance(orders, list) or len(orders) < 2:
        return []

    try:
        max_distance_km = float(max_distance_km)
        min_rating = float(min_rating)
    except (TypeError, ValueError):
        raise ValueError("Distance and minimum rating must be numeric.")

    if (
        not math.isfinite(max_distance_km)
        or max_distance_km < 0
        or not math.isfinite(min_rating)
        or not 0 <= min_rating <= 5
    ):
        raise ValueError("Invalid distance or rating threshold.")

    candidates = []

    for restaurant in RESTAURANTS:
        if restaurant.get("availabilityStatus") != "OPEN":
            continue

        try:
            distance = float(restaurant["distanceKm"])
            rating = float(restaurant["rating"])
        except (KeyError, TypeError, ValueError):
            continue

        if not math.isfinite(distance) or not math.isfinite(rating):
            continue

        if distance > max_distance_km or rating < min_rating:
            continue

        menu = restaurant.get("menu", [])
        if not isinstance(menu, list):
            continue

        eligible_menus_by_guest = []
        all_guests_supported = True

        for order in orders:
            if not isinstance(order, dict):
                all_guests_supported = False
                break

            eligible_items = _eligible_items_for_order(menu, order)

            if not eligible_items:
                all_guests_supported = False
                break

            eligible_menus_by_guest.append({
                "guest": order.get("who", "Guest"),
                "preferences": _normalize_preferences(order),
                "eligible_items": [
                    {
                        "id": item.get("id"),
                        "name": item.get("name"),
                        "price": item.get("price"),
                    }
                    for item in eligible_items
                ],
            })

        if not all_guests_supported:
            continue

        candidates.append({
            "id": restaurant["id"],
            "name": restaurant["name"],
            "distanceKm": distance,
            "rating": rating,
            "cuisines": restaurant.get("cuisines", []),
            "eligible_menus_by_guest": eligible_menus_by_guest,
        })

    candidates.sort(
        key=lambda restaurant: (
            restaurant["distanceKm"],
            -restaurant["rating"],
        )
    )

    return candidates