"""
party app — DRF serializers.
"""

from rest_framework import serializers

from account.serializers import UserSummarySerializer

from .models import Guest, Party


class GuestSerializer(serializers.ModelSerializer):
    has_ordered = serializers.SerializerMethodField()

    class Meta:
        model = Guest
        fields = [
            "id",
            "party",
            "name",
            "phone_number",
            "dietary_pref",
            "is_late",
            "late_offset_minutes",
            "payment_method",
            "has_ordered",
            "created_at",
        ]
        read_only_fields = ["id", "party", "has_ordered", "created_at"]

    def get_has_ordered(self, obj):
        return obj.orders.exists()

    def validate(self, attrs):
        # payment_method only makes sense for a late guest (Section 5.3.6) —
        # their order is decoupled from the group's shared payment flow.
        is_late = attrs.get("is_late", getattr(self.instance, "is_late", False))
        payment_method = attrs.get(
            "payment_method", getattr(self.instance, "payment_method", None)
        )
        late_offset = attrs.get(
            "late_offset_minutes", getattr(self.instance, "late_offset_minutes", None)
        )

        if not is_late and payment_method:
            raise serializers.ValidationError(
                "payment_method should only be set for a late guest."
            )
        if is_late and not late_offset:
            raise serializers.ValidationError(
                "late_offset_minutes is required when is_late is true."
            )
        return attrs


class PartyListSerializer(serializers.ModelSerializer):
    """Lean representation for list/index views — no nested guests, so
    fetching a host's party history stays cheap regardless of guest count."""

    host = UserSummarySerializer(read_only=True)

    class Meta:
        model = Party
        fields = [
            "id",
            "host",
            "code",
            "mode",
            "strategy",
            "occasion",
            "budget",
            "expected_guest_count",
            "status",
            "party_start_time",
            "created_at",
        ]
        read_only_fields = ["id", "host", "code", "created_at"]


class PartyDetailSerializer(serializers.ModelSerializer):
    """Full representation for a single party's dashboard — includes guests.
    Orders/Booking are deliberately NOT nested here: they live in the
    orders app, and party must not import from orders (models.py already
    establishes orders -> party as the one-way dependency direction;
    serializers mirror that)."""

    host = UserSummarySerializer(read_only=True)
    guests = GuestSerializer(many=True, read_only=True)
    join_link = serializers.SerializerMethodField()

    class Meta:
        model = Party
        fields = [
            "id",
            "host",
            "code",
            "join_link",
            "mode",
            "strategy",
            "occasion",
            "budget",
            "expected_guest_count",
            "veg_count",
            "non_veg_count",
            "jain_count",
            "vegan_count",
            "diabetic_count",
            "delivery_address",
            "delivery_lat",
            "delivery_lng",
            "party_start_time",
            "status",
            "guests",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "host", "code", "guests", "created_at", "updated_at"]

    def get_join_link(self, obj):
        request = self.context.get("request")
        path = f"/join/{obj.code}"
        return request.build_absolute_uri(path) if request else path

    def validate(self, attrs):
        mode = attrs.get("mode", getattr(self.instance, "mode", None))
        strategy = attrs.get("strategy", getattr(self.instance, "strategy", None))

        if mode == Party.Mode.DINEOUT and strategy:
            raise serializers.ValidationError(
                "strategy is only applicable to food_delivery parties."
            )
        if mode == Party.Mode.FOOD_DELIVERY and not strategy:
            raise serializers.ValidationError(
                "strategy is required for food_delivery parties."
            )
        return attrs
    
