"""Deterministic combo optimizer.

Only explicit serving metadata is accepted.
No price-based serving-size estimation is allowed.
"""

def _positive_integer(value):
    """Return a positive integer, or None for invalid/missing values."""
    if isinstance(value, bool) or value is None:
        return None

    try:
        number = float(value)
    except (TypeError, ValueError):
        return None

    if not number.is_integer() or number <= 0:
        return None

    return int(number)

def _valid_price(value):
    """Return a finite, non-negative price, or None."""

    if isinstance(value, bool) or value is None:
        return None

    try:
        price = float(value)

    except (TypeError, ValueError):
        return None

    if price < 0 or price != price or price == float("inf"):

        return None

    if price == float("-inf"):
        return None

    return price

def _meets_dietary_requirements(combo, preferences):
    for preference in preferences:
        pref = str(preference).strip().lower().replace("-", "_").replace(" ", "_")

        if pref in ("", "any", "non_veg", "nonveg"):
            continue

        if pref in ("jain",):
            if combo.get("isJainCompatible") is not True:
                return False

            elif pref in ("veg", "pure_veg", "vegan"):
                if combo.get("isVeg") is not True:
                    return False

            elif pref == "diabetic":

                if combo.get("isDiabeticFriendly") is not True:
                    return False
            else:
                return False

        return True

def evaluate_combo_option(
    combo,
    required_servings,
    individual_total_cost,
    required_preferences=None,
):
    """Compare an eligible combo against an individual-item plan.

    Args:
        combo: Menu item with price and explicit servesCount/serves_count.
        required_servings: Exact number of servings needed.
        individual_total_cost: Total cost of an alternative plan that
            covers the same number of servings and meets the requirements.
        required_preferences: Dietary requirements that this combo must meet.

    Returns:
        A dictionary containing the recommendation and comparison details.
    """

    if not isinstance(combo, dict):
        return {
            "recommended": False,
            "reason": "Invalid combo data.",
        }

    servings_needed = _positive_integer(required_servings)

    if servings_needed is None:
        return {
            "recommended": False,
            "reason": "A valid positive required_servings value is required.",
        }
    serves_count = _positive_integer(
        combo.get("servesCount", combo.get("serves_count"))
    )

    if serves_count is None:
        return {
           "recommended": False,
            "reason": "Explicit serving metadata is missing or invalid.", 
        }

    combo_price = _valid_price(combo.get("price"))

    if combo_price is None:
        return {
            "recommended": False,
            "reason": "A valid combo price is required.",
        }

    individual_cost = _valid_price(individual_total_cost)
    if individual_cost is None:
        return {
            "recommended": False,
            "reason": "A valid individual-plan total cost is required.",
        }

    preferences = required_preferences or []
    if not _meets_dietary_requirements(combo, preferences):
        return {
            "recommended": False,
            "reason": "The combo does not satisfy all specified dietary requirements.",
        }

    # Do not recommend a combo that leaves excess servings or fails
    # to cover the required servings exactly.
    if servings_needed % serves_count != 0:
        return {
            "recommended": False,
            "reason": (
                "The combo quantity cannot cover the required servings "
                "exactly without excess."
            ),
        }

    combo_quantity = servings_needed // serves_count
    combo_total_cost = combo_price * combo_quantity

    combo_cost_per_head = combo_total_cost / servings_needed
    individual_cost_per_head = individual_cost / servings_needed
    savings = individual_cost - combo_total_cost

    recommended = savings > 0

    return {
        "recommended": recommended,
        "reason": (
            "Combo is cheaper per head."
            if recommended
            else "The combo does not cost less than the individual-item plan."
        ),
        "combo_id": combo.get("id"),
        "combo_name": combo.get("name"),
        "combo_quantity": combo_quantity,
        "serves_count_per_combo": serves_count,
        "total_servings": servings_needed,
        "combo_total_cost": round(combo_total_cost, 2),
        "combo_cost_per_head": round(combo_cost_per_head, 2),
        "individual_total_cost": round(individual_cost, 2),
        "individual_cost_per_head": round(individual_cost_per_head, 2),
        "estimated_savings": round(savings, 2),
    } 
    