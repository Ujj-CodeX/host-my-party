
"""
party app — party setup and guest management.

"""

import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone




def generate_party_code():
    return uuid.uuid4().hex[:6].upper()

class Party(models.Model):
    class Mode(models.TextChoices):
        FOOD_DELIVERY = "food_delivery", "Food Delivery"
        DINEOUT = "dineout", "Dineout"
    class Strategy(models.TextChoices):
        MEMBER_WISE = "member", "Member-wise"
        WHOLE_SUM = "whole", "Whole Party"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"
    

    host = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="parties")
    code = models.CharField(max_length=12, unique=True, default=generate_party_code, editable=False)
 
    mode = models.CharField(max_length=15, choices=Mode.choices)

    mode = models.CharField(max_length=15, choices=Mode.choices)
    # Only meaningful when mode == FOOD_DELIVERY; null for Dineout.
    strategy = models.CharField(max_length=10, choices=Strategy.choices, null=True, blank=True)
 
    occasion = models.CharField(max_length=100, blank=True)
    budget = models.PositiveIntegerField()


    expected_guest_count = models.PositiveIntegerField()


    # Aggregate dietary counters — used directly by Dineout
    # and by the Whole-Sum Groq prompt. For Member-wise,
    # this is derived from Guest rows rather than authoritative.

    veg_count = models.PositiveIntegerField(default=0)
    non_veg_count = models.PositiveIntegerField(default=0)
    jain_count = models.PositiveIntegerField(default=0)
    vegan_count = models.PositiveIntegerField(default=0)
    diabetic_count = models.PositiveIntegerField(default=0)

    # Location (Food Delivery distance-sorting;)
    delivery_address = models.CharField(max_length=255, blank=True)
    delivery_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    delivery_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
 
    party_start_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["code"]),
           
        ]

    def __str__(self):
        return f"Party {self.code} ({self.mode}) — host {self.host_id}"

class Guest(models.Model):

    """
    A party-scoped participant. Deliberately NOT a User account — guests
    joining via link are frictionless, one-time participants
    
    """

    class DietaryPref(models.TextChoices):
        ANY = "any", "Any"
        VEG = "veg", "Veg"
        NON_VEG = "non_veg", "Non-Veg"
        VEGAN = "vegan", "Vegan"
        JAIN = "jain", "Jain"
        DIABETIC = "diabetic", "Diabetic"

    class PaymentMethod(models.TextChoices):
        ONLINE = "online", "Online"
        COD = "cod", "Cash on Delivery"
    
    party = models.ForeignKey(Party, on_delete=models.CASCADE, related_name="guests")
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, blank=True)
    dietary_pref = models.CharField(max_length=10, choices=DietaryPref.choices, default=DietaryPref.ANY)
 
    is_late = models.BooleanField(default=False)
    late_offset_minutes = models.PositiveIntegerField(null=True, blank=True)

    # Only set/relevant when is_late=True — late orders are decoupled from
    # the group's shared flow and must be resolved upfront

    payment_method = models.CharField(
        max_length=10, choices=PaymentMethod.choices, null=True, blank=True
    )
 
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["party", "name"]),
        ]

    def __str__(self):
        return f"{self.name} @ {self.party.code}"

class GuestSession(models.Model):
    """
    Short-lived, party-scoped session for a Guest who joined via link
    . The raw token is handed to the guest's browser once and
    never stored — only its hash. Not a full auth session; scoped to a
    single Guest within a single Party.
    """

    guest = models.OneToOneField(Guest, on_delete=models.CASCADE, related_name="session")
    token_hash = models.CharField(max_length=128, unique=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["token_hash"]),
        ]

    def is_valid(self):
        return self.expires_at > timezone.now()

    def __str__(self):
        return f"Session for {self.guest.name} (expires {self.expires_at:%Y-%m-%d %H:%M})"
 