"""
core app — DRF serializers.

"""

from rest_framework import serializers

from .models import GroqCallLog, Notification


class GroqCallLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroqCallLog
        fields = [
            "id",
            "party",
            "call_type",
            "prompt_template_version",
            "request_payload",
            "response_raw",
            "response_parsed",
            "success",
            "error_message",
            "latency_ms",
            "created_at",
        ]
        read_only_fields = fields  # internal audit trail — write-side is the Groq wrapper itself, not the API


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id",
            "party",
            "recipient_type",
            "recipient_user",
            "recipient_guest",
            "notification_type",
            "message",
            "is_read",
            "created_at",
        ]
        # is_read is the only field a client should ever be able to write
        # (e.g. PATCH to mark as read) — everything else is server-generated.
        read_only_fields = [
            "id",
            "party",
            "recipient_type",
            "recipient_user",
            "recipient_guest",
            "notification_type",
            "message",
            "created_at",
        ]