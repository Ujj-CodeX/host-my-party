"""
ai app — versioned prompt templates (Section 3.4).

Every prompt sent to Groq is built here, not inline in views.py, and each
builder is tagged with a version key in PROMPT_VERSIONS. GroqCallLog has
always had a prompt_template_version column, but until now every call
site just hardcoded "v1" into it while the prompt text itself lived
inline in views.py and could drift without that column ever changing.
This file is what makes prompt_template_version mean something: bump the
version string here whenever a builder's wording changes materially, and
old GroqCallLog rows stay honest about which wording actually produced
them — useful when debugging "why did the AI suggest this" after a
prompt tweak (Section 3.4's stated reason GroqCallLog exists at all).
"""

PROMPT_VERSIONS = {
    "restaurant_filter": "v1",
    "scheduling": "v1",
    "budget_exceeded": "v1",
    "budget_headroom": "v1",
    "merge_check": "v1",
    "dineout_ranking" : "v1",
    "whole_sum_optimizer": "v1"
}


def restaurant_filter_prompt(pref, category, guest_name, restaurants_json):
    return (
        "You are a Swiggy restaurant filter engine.\n\n"
        f"Guest name: {guest_name}\n"
        f"Guest dietary preference: {pref}\n"
        f"Food category requested: {category or 'Any'}\n\n"
        f"Available restaurants and menus:\n{restaurants_json}\n\n"
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


def scheduling_prompt(guest_name, party_time_str, late_minutes, delivery_mins):
    return (
        f"Party starts at {party_time_str}. Guest {guest_name} will arrive {late_minutes} minutes late.\n"
        f"Restaurant delivery time is {delivery_mins} minutes.\n"
        f"When should we fire the order so food arrives just as {guest_name} arrives?\n"
        f"Reply with ONLY a JSON object: "
        f'{{ "fire_at": "HH:MM", "reasoning": "one sentence" }}'
    )


def budget_exceeded_prompt(budget, current_total, remaining, current_orders_json):
    return (
        f"Party budget is ₹{budget}. Current cart total is ₹{current_total} (over by ₹{abs(remaining)}).\n"
        f"Current orders: {current_orders_json}\n"
        f"Suggest which items to remove to bring total under budget.\n"
        f"Reply ONLY as JSON: "
        f'{{ "status": "exceeded", "exceeded_by": {abs(remaining)}, '
        f'"remove_suggestions": ["item name 1", "item name 2"] }}'
    )


def budget_headroom_prompt(budget, current_total, remaining, upsell_list):
    return (
        f"Party budget is ₹{budget}. Current cart total is ₹{current_total}. "
        f"Remaining: ₹{remaining}.\n"
        f"Available add-on items safe for all guests: {', '.join(upsell_list)}\n"
        f"Recommend 2-3 items to order before checkout.\n"
        f"Reply ONLY as JSON: "
        f'{{ "status": "ok", "remaining": {remaining}, '
        f'"suggestions": [{{"name": "item", "price": 0, "reason": "short reason"}}] }}'
    )


def merge_check_prompt(orders_summary_lines):
    return (
        "These are party food orders:\n"
        + "\n".join(orders_summary_lines)
        + "\n\nFind guests ordering from the SAME restaurant who have identical or very similar items. "
        "Suggest merging their orders into one cart to save on delivery fees.\n"
        "If no merge opportunity exists, say so.\n"
        "Reply ONLY as JSON:\n"
        '{ "has_merges": true/false, "merges": [{ "guests": ["Guest A", "Guest B"], '
        '"restaurant": "Name", "shared_items": ["Item 1"], "savings_note": "Save ₹X on delivery" }] }'
    )




def dineout_ranking_prompt(location, guest_count, budget, dietary_prefs, restaurants_json):
    return (
        f"User location: {location}\nGuest count: {guest_count}\nBudget: ₹{budget}\n"
        f"Dietary needs: {', '.join(dietary_prefs) or 'Any'}\n\n"
        f"Restaurants:\n{restaurants_json}\n\n"
        "Rank these restaurants best-fit first considering distanceKm (closer to "
        "user location is better), seatingCapacity vs guest_count, dietary match "
        "(servesVeg/servesNonVeg/hasJainOptions), and per-head budget fit.\n"
        "Reply ONLY as JSON array of objects: "
        '{ "id": "...", "aiReason": "one sentence why this fits" }'
    )

def whole_sum_optimizer_prompt(guest_count, dietary_splits, budget, restaurants_json):
    return (
        f"Total guests: {guest_count}\nDietary splits: {dietary_splits}\nBudget: ₹{budget}\n\n"
        f"Restaurants:\n{restaurants_json}\n\n"
        "Pick ONE restaurant and a shared item list (with quantities) that satisfies "
        "ALL dietary splits simultaneously, stays within budget, and covers guest_count "
        "people (assume ~1.5 items per person across shared platters).\n"
        "Reply ONLY as JSON: "
        '{ "restaurant_id": "...", "restaurant_name": "...", '
        '"items": [{"item_id": "...", "name": "...", "price": 0, "quantity": 0}], '
        '"reasoning": "one sentence" }'
    )