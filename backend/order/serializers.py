"""
orders app — DRF serializers.
"""

from django.db import transaction
from rest_framework import serializers

from .models import Booking, Order, OrderItem
from .services import compute_fire_time, schedule_order_firing


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
        # (order/services.py) — never directly settable via raw client input.
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


class OrderItemWriteSerializer(serializers.Serializer):
    """Plain (non-Model) serializer for the nested items[] payload on
    create — kept separate from OrderItemSerializer since that one is
    read-only and includes server-computed fields like line_total."""

    external_item_id = serializers.CharField(max_length=100)
    name = serializers.CharField(max_length=150)
    unit_price = serializers.IntegerField(min_value=0)
    quantity = serializers.IntegerField(min_value=1, default=1)
    is_veg = serializers.BooleanField(default=False)
    is_jain_compatible = serializers.BooleanField(default=False)
    is_diabetic_friendly = serializers.BooleanField(default=False)


class OrderCreateSerializer(serializers.ModelSerializer):
    """
    Write-side serializer for placing an order. Accepts a nested items[]
    payload and computes item_total server-side from it — the client never
    gets to send a total directly, so there's no way to under-report a bill
    by tampering with the request.

    Also owns the Section 5.3.6 fire_time wiring: on create, if the order
    belongs to a late guest, fire_time is computed and the order is handed
    to order/services.py to be scheduled (Celery ETA) or fired immediately.
    This lives here rather than in the views so both the host-facing
    OrderListCreateView and the guest-facing GuestOrderCreateView — which
    both save() through this same serializer — get identical behavior for
    free, without either view needing to know about scheduling at all.
    """

    items = OrderItemWriteSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "party",
            "guest",
            "placed_by",
            "restaurant_id",
            "restaurant_name",
            "delivery_fee",
            "taxes",
            "payment_method",
            "items",
        ]
        read_only_fields = ["id" , "party" ]

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError("An order needs at least one item.")
        return items

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        item_total = sum(item["unit_price"] * item.get("quantity", 1) for item in items_data)

        validated_data["item_total"] = item_total
        # Whoever places the order is, by definition, the last modifier at
        # creation time (Section 5.3.4's last_modified_by tracking starts here).
        validated_data["last_modified_by"] = validated_data.get("placed_by", Order.PlacedBy.HOST)

        party = validated_data.get("party")
        guest = validated_data.get("guest")
        restaurant_id = validated_data.get("restaurant_id")
        validated_data["fire_time"] = compute_fire_time(party, guest, restaurant_id)

        with transaction.atomic():
            order = Order.objects.create(**validated_data)
            OrderItem.objects.bulk_create(
                [OrderItem(order=order, **item) for item in items_data]
            )
            # on_commit so the Celery task (which may run near-instantly on
            # a fast broker) never sees a row that isn't actually committed
            # to the DB yet.
            transaction.on_commit(lambda: schedule_order_firing(order))

        return order

    def update(self, instance, validated_data):
        """
        Host-override edit (Section 5.3.4): replaces the item list wholesale
        rather than diffing, since partial item edits from the frontend
        already send the full desired cart, not a delta.

        Deliberately does NOT recompute or reschedule fire_time — an edit
        to an already-scheduled late order (e.g. changing items) shouldn't
        silently change when it fires; that's a separate future action
        (explicit reschedule/cancel), not implied by an item edit.
        """
        items_data = validated_data.pop("items", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if items_data is not None:
            instance.item_total = sum(
                item["unit_price"] * item.get("quantity", 1) for item in items_data
            )
            with transaction.atomic():
                instance.items.all().delete()
                OrderItem.objects.bulk_create(
                    [OrderItem(order=instance, **item) for item in items_data]
                )
                instance.save()
        else:
            instance.save()

        return instance


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
        read_only_fields = ["id", "party", "status", "created_at", "updated_at"]