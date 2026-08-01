"""
core app — cross-cutting concerns that don't belong to a single domain app.


"""

from django.conf import settings
from django.db import models

from party.models import Guest, Party


class GroqCallLog(models.Model):
    class CallType(models.TextChoices):
        RESTAURANT_FILTER = "restaurant_filter", "Restaurant Filter (Food Delivery)"
        WHOLE_SUM_OPTIMIZER = "whole_sum_optimizer", "Whole-Sum Quantity Optimizer"
        DINEOUT_RANKING = "dineout_ranking", "Dineout Restaurant Ranking"
        SCHEDULING = "scheduling", "Late-Arrival Scheduling Suggestion"
        MERGE_CHECK = "merge_check", "Order Merge Detection"
        BUDGET_GUARDIAN = "budget_guardian", "Budget Guardian"
        BUDGET_CHECK = "budget_check", "Budget Guardian Check"

    party = models.ForeignKey(
        Party, on_delete=models.CASCADE, related_name="groq_calls", null=True, blank=True
    )
    call_type = models.CharField(max_length=25, choices=CallType.choices)

    # Prompt templates are versioned and stored separately from view logic
    # (Section 3.4) — this just records which version was live for this call.
    prompt_template_version = models.CharField(max_length=20, default="v1")

    request_payload = models.JSONField()
    response_raw = models.TextField(blank=True)
    # Populated only after the response parser/validator (Section 3.4)
    # successfully enforces the strict JSON schema on Groq's output.
    response_parsed = models.JSONField(null=True, blank=True)

    success = models.BooleanField(default=False)
    error_message = models.CharField(max_length=255, blank=True)
    latency_ms = models.PositiveIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["call_type", "created_at"]),
            models.Index(fields=["party", "created_at"]),
        ]

    def __str__(self):
        status = "OK" if self.success else "FAILED"
        return f"[{status}] {self.call_type} @ {self.created_at:%Y-%m-%d %H:%M}"


class Notification(models.Model):
    class RecipientType(models.TextChoices):
        HOST = "host", "Host"
        GUEST = "guest", "Guest"

    class NotificationType(models.TextChoices):
        ORDER_EDITED_BY_HOST = "order_edited_by_host", "Order Edited by Host"
        GUEST_ORDER_PLACED = "guest_order_placed", "Guest Order Placed"
        MERGE_DETECTED = "merge_detected", "Order Merge Detected"
        BUDGET_WARNING = "budget_warning", "Budget Warning"
        LATE_ORDER_FIRED = "late_order_fired", "Late Order Auto-Fired"
        BOOKING_CONFIRMED = "booking_confirmed", "Dineout Booking Confirmed"

    party = models.ForeignKey(Party, on_delete=models.CASCADE, related_name="notifications")

    recipient_type = models.CharField(max_length=10, choices=RecipientType.choices)
    # Exactly one of these is set, matching recipient_type.
    recipient_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        null=True, blank=True, related_name="notifications",
    )
    recipient_guest = models.ForeignKey(
        Guest, on_delete=models.CASCADE,
        null=True, blank=True, related_name="notifications",
    )

    notification_type = models.CharField(max_length=25, choices=NotificationType.choices)
    message = models.CharField(max_length=255)

    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(recipient_type="host", recipient_user__isnull=False, recipient_guest__isnull=True)
                    | models.Q(recipient_type="guest", recipient_guest__isnull=False, recipient_user__isnull=True)
                ),
                name="notification_recipient_matches_type",
            )
        ]
        indexes = [
            models.Index(fields=["party", "is_read"]),
        ]

    def __str__(self):
        who = self.recipient_user or self.recipient_guest
        return f"{self.notification_type} → {who} ({'read' if self.is_read else 'unread'})"