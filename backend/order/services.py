"""
orders app — order-firing service layer (Section 5.3.6).

Bridges Order.fire_time to actual dispatch: computing when a late
guest's order should fire, and handing off to the pluggable food-delivery
provider adapter (ai/food_delivery_provider.py) at that moment — whether
that moment is right now (a normal, non-late order) or a scheduled
Celery ETA (a late order).
"""

from datetime import timedelta

from django.utils import timezone

from ai.food_delivery_provider import get_food_delivery_provider
from party.realtime import notify_party

from .models import Order

DEFAULT_PREP_TIME_MINUTES = 35  # fallback if restaurant lookup fails


def compute_fire_time(party, guest, restaurant_id):
    """
    fire_time = party_start_time + guest_late_offset - restaurant_avg_prep_time
    (Section 5.3.6). Returns None if this isn't a late-guest order, or the
    party has no start time set yet — in either case the order fires
    immediately instead of being scheduled.
    """
    if guest is None or not guest.is_late or not guest.late_offset_minutes:
        return None
    if party is None or party.party_start_time is None:
        return None

    provider = get_food_delivery_provider()
    prep_minutes = provider.get_avg_prep_time_minutes(restaurant_id) or DEFAULT_PREP_TIME_MINUTES

    return (
        party.party_start_time
        + timedelta(minutes=guest.late_offset_minutes)
        - timedelta(minutes=prep_minutes)
    )


def schedule_order_firing(order):
    """
    Called right after an Order is committed. Two paths:
    - fire_time is set and still in the future -> Celery ETA task,
      status flips to SCHEDULED now and FIRED once the task runs.
    - otherwise -> fire immediately, synchronously, status goes straight
      to FIRED (or stays PENDING on a provider failure).
    The Celery task import is local to keep this module importable
    (e.g. by tests, or by the OrderCreateSerializer) without requiring a
    running Celery worker at import time.
    """
    from .tasks import fire_order

    now = timezone.now()
    if order.fire_time and order.fire_time > now:
        order.status = Order.Status.SCHEDULED
        order.save(update_fields=["status"])
        fire_order.apply_async(args=[order.id], eta=order.fire_time)
    else:
        fire_order_now(order)


def fire_order_now(order):
    """
    Synchronous fire path — used both for immediate (non-late) orders and
    as the body of the Celery task once its ETA arrives.
    """
    provider = get_food_delivery_provider()
    result = provider.place_order(
        restaurant_id=order.restaurant_id,
        items=[
            {"external_item_id": i.external_item_id, "name": i.name, "quantity": i.quantity}
            for i in order.items.all()
        ],
    )

    order.status = Order.Status.FIRED if result.get("success") else Order.Status.PENDING
    order.save(update_fields=["status"])

    is_late_fire = bool(order.guest_id and order.guest.is_late)
    notify_party(
        order.party.code,
        "late_order_fired" if is_late_fire else "order_fired",
        {"order_id": order.id, "status": order.status, "provider_result": result},
    )
    return result
