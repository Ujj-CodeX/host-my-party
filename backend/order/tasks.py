"""
orders app — Celery tasks (Section 5.3.6).

Only one task exists today: firing a late guest's order at its
Order.fire_time. Scheduled via Celery's `eta` kwarg (order/services.py's
schedule_order_firing), not celery-beat — there's nothing to poll for,
each order schedules its own one-off firing the moment it's created.
"""

from celery import shared_task


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def fire_order(self, order_id):
    from .models import Order
    from .services import fire_order_now

    try:
        order = Order.objects.select_related("party", "guest").get(id=order_id)
    except Order.DoesNotExist:
        return

    if order.status != Order.Status.SCHEDULED:
        
        return

    try:
        fire_order_now(order)
    except Exception as exc:
        raise self.retry(exc=exc)
