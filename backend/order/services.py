"""
orders app — order-firing service layer (Section 5.3.6).

"""

from datetime import timedelta

from django.utils import timezone

from ai.food_delivery_provider import get_food_delivery_provider
from party.realtime import notify_party

from .models import Order

DEFAULT_PREP_TIME_MINUTES = 35  # fallback if restaurant lookup fails


def compute_fire_time(party, guest, restaurant_id):
   
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
    
    from .tasks import fire_order

    now = timezone.now()
    if order.fire_time and order.fire_time > now:
        order.status = Order.Status.SCHEDULED
        order.save(update_fields=["status"])
        fire_order.apply_async(args=[order.id], eta=order.fire_time)
    else:
        fire_order_now(order)


def fire_order_now(order):
    
    provider = get_food_delivery_provider()
    result = provider.place_order(
        restaurant_id=order.restaurant_id,
        items=[
            {"external_item_id": i.external_item_id, "name": i.name, "unit_price": i.unit_price, "quantity": i.quantity}
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
