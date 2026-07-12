"""
orders app — Food Delivery orders and Dineout bookings.

 
Imports Guest.PaymentMethod from the party app rather than redefining it,
since "how does a late guest pay" is conceptually owned by Guest.
"""

from  django.db import models
from party.models import Guest , Party

class Order(models.Model):
    """A Food Delivery order — either a guest's individual order (Member-wise)
    or the host's single combined order (Whole-Sum)."""

    class PlacedBy(models.TextChoices):
        HOST = "host", "Host"
        GUEST = "guest", "Guest"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SCHEDULED = "scheduled", "Scheduled"   # late-arrival: waiting for Celery fire_time
        FIRED = "fired", "Fired"               # sent to Swiggy provider
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"
    

    party = models.ForeignKey(Party, on_delete=models.CASCADE, related_name="orders")
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE, related_name="orders", null=True, blank=True)
 
    placed_by = models.CharField(max_length=10, choices=PlacedBy.choices)
    last_modified_by = models.CharField(max_length=10, choices=PlacedBy.choices)

    # External (mock today, real Swiggy tomorrow) restaurant reference —
    # intentionally a plain string, not a FK, since this app doesn't own
    # the restaurant catalog.

    restaurant_id = models.CharField(max_length=100)
    restaurant_name = models.CharField(max_length=100)

    item_total = models.PositiveIntegerField(default=0)
    delivery_fee = models.PositiveIntegerField(default=0)
    taxes = models.PositiveIntegerField(default=0)


    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)

    # Late-arrival scheduling (Section 5.3.6):
    # fire_time = party_start_time + guest_late_offset - restaurant_avg_prep_time
    fire_time = models.DateTimeField(null=True, blank=True)
    payment_method = models.CharField(
        max_length=10, choices=Guest.PaymentMethod.choices, null=True, blank=True
    )
 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["party", "status"]),
            models.Index(fields=["fire_time"]),
        ]
 
    @property
    def total(self):
        return self.item_total + self.delivery_fee + self.taxes
 
    def __str__(self):
        who = self.guest.name if self.guest_id else "Host (whole-party)"
        return f"Order #{self.pk} — {who} @ {self.restaurant_name}"



class OrderItem(models.Model):
    """
    Individual line item within an Order. Kept relational (not JSON) so
    per-item / per-restaurant reporting is queryable later without a
    migration — e.g. most-ordered item, revenue by restaurant.
    """
 
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    external_item_id = models.CharField(max_length=100)  # Swiggy/mock menu item id
    name = models.CharField(max_length=150)
    unit_price = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField(default=1)
 
    # Snapshot of dietary tags at order time, so historical orders remain
    # accurate even if the upstream menu item's tags change later.
    is_veg = models.BooleanField(default=False)
    is_jain_compatible = models.BooleanField(default=False)
    is_diabetic_friendly = models.BooleanField(default=False)
 
    @property
    def line_total(self):
        return self.unit_price * self.quantity
 
    def __str__(self):
        return f"{self.quantity}x {self.name} (order #{self.order_id})"
 
 
class Booking(models.Model):
    """Dineout table reservation (Section 5.4)."""
 
    class Status(models.TextChoices):
        REQUESTED = "requested", "Requested"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"
 
    party = models.OneToOneField(Party, on_delete=models.CASCADE, related_name="booking")
 
    restaurant_id = models.CharField(max_length=100)
    restaurant_name = models.CharField(max_length=150)
    seating_capacity_required = models.PositiveIntegerField()
 
    arrival_time = models.DateTimeField()
    special_request = models.TextField(blank=True)
 
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.REQUESTED)
 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
 
    def __str__(self):
        return f"Booking @ {self.restaurant_name} for party {self.party.code}"