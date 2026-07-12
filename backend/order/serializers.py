"""
orders app — DRF serializers.
"""

from rest_framework import serializers

from .models import Booking, Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    line_total = serializers.IntegerField(read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "external_item_id",
            "name",
            "unit_price",
            "quantity",
            "line_total",
            "is_veg",
            "is_jain_compatible",
            "is_diabetic_friendly",
        ]
        read_only_fields = ["id", "line_total"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total = serializers.IntegerField(read_only=True)
    guest_name = serializers.CharField(source="guest.name", read_only=True, default=None)

    class Meta:
        model = Order
        fields = [
            "id",
            "party",
            "guest",
            "guest_name",
            "placed_by",
            "last_modified_by",
            "restaurant_id",
            "restaurant_name",
            "item_total",
            "delivery_fee",
            "taxes",
            "total",
            "status",
            "fire_time",
            "payment_method",
            "items",
            "created_at",
            "updated_at",
        ]
        # Money fields, status, last_modified_by, and fire_time are
        # server-computed/controlled by the order-placement service layer
        # (next stage) — never directly settable via raw client input.
        read_only_fields = [
            "id",
            "last_modified_by",
            "item_total",
            "delivery_fee",
            "taxes",
            "total",
            "status",
            "fire_time",
            "items",
            "created_at",
            "updated_at",
        ]


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            "id",
            "party",
            "restaurant_id",
            "restaurant_name",
            "seating_capacity_required",
            "arrival_time",
            "special_request",
            "status",
            "created_at",
            "updated_at",
        ]
        # status transitions (requested -> confirmed) are driven by the
        # Swiggy Dineout partner callback / service layer, not raw client PATCH.
        read_only_fields = ["id", "status", "created_at", "updated_at"]