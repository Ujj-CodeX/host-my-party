

from rest_framework import generics, mixins, permissions, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from core.permissions import IsValidGuestSession, get_owned_party
from party.authentication import GuestSessionAuthentication
from party.models import Party
from party.realtime import notify_party

from .models import Booking, Order
from .serializers import BookingSerializer, OrderCreateSerializer, OrderSerializer
from .services import compute_fire_time, schedule_order_firing


class OrderListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        party = get_owned_party(self.request, self.kwargs["party_code"])
        return party.orders.all().order_by("-created_at")

    def get_serializer_class(self):
        return OrderSerializer if self.request.method == "GET" else OrderCreateSerializer

    def perform_create(self, serializer):
        party = get_owned_party(self.request, self.kwargs["party_code"])
        serializer.save(party=party)
        order = serializer.instance

        # Section 5.3.6 — compute fire_time if this order belongs to a
        # late guest, then dispatch (Celery-scheduled if late, immediate
        # otherwise). This was previously built but never called anywhere.
        fire_time = compute_fire_time(party, order.guest, order.restaurant_id)
        if fire_time:
            order.fire_time = fire_time
            order.save(update_fields=["fire_time"])
            schedule_order_firing(order)
            notify_party(party.code, "order_created", OrderSerializer(order).data)
        else:
            # Immediate path — schedule_order_firing fires it right away
            # and sends its own notify_party("order_fired"/... ) call, so
            # we don't send a second, redundant "order_created" event.
            schedule_order_firing(order)


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        party = get_owned_party(self.request, self.kwargs["party_code"])
        return party.orders.all()

    def get_serializer_class(self):
        # GET returns the full read shape (nested items, computed total).
        # PATCH/PUT use OrderCreateSerializer so a host edit can replace the
        # item list wholesale (Section 5.3.4's override), not just tweak
        # top-level fields like restaurant_name.
        if self.request.method == "GET":
            return OrderSerializer
        return OrderCreateSerializer

    def perform_update(self, serializer):
        # Any edit reaching this endpoint is, by definition, a host edit —
        # flip last_modified_by so the "Edited by host" badge (Section
        # 5.3.4) stays accurate. Guest-originated edits go through the
        # guest-session-authenticated endpoint added in the auth stage,
        # which will set this to GUEST instead.
        serializer.save(last_modified_by=Order.PlacedBy.HOST)
        notify_party(
            self.kwargs["party_code"], "order_updated",
            OrderSerializer(serializer.instance).data,
        )

    def update(self, request, *args, **kwargs):
        # OrderCreateSerializer's own .data is write-shaped (items is
        # write_only, no computed total) — re-serialize with OrderSerializer
        # so the response actually reflects the updated order.
        super().update(request, *args, **kwargs)
        instance = self.get_object()
        return Response(OrderSerializer(instance).data)


class BookingDetailView(mixins.CreateModelMixin, generics.RetrieveUpdateAPIView):
    """
    Booking is one-per-party (OneToOneField), so this single view/URL
    handles all three actions: POST creates the booking, GET/PATCH read
    and edit the one that exists. There's no "list" — a party has at most
    one Booking, so a separate ListCreateAPIView would be overkill.
    """

    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        party = get_owned_party(self.request, self.kwargs["party_code"])
        return get_object_or_404(Booking, party=party)

    def post(self, request, *args, **kwargs):
        party = get_owned_party(request, self.kwargs["party_code"])

        # A Booking only makes sense for a dineout party — food_delivery
        # parties place Orders instead (Section 5.4 vs 5.3).
        if party.mode != Party.Mode.DINEOUT:
            return Response(
                {"detail": "A booking can only be created for a dineout party."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # OneToOneField already enforces this at the DB level, but
        # catching it here gives a clear message instead of a raw
        # IntegrityError bubbling up as a 500.
        if Booking.objects.filter(party=party).exists():
            return Response(
                {"detail": "This party already has a booking. Use PATCH to edit it."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        party = get_owned_party(self.request, self.kwargs["party_code"])
        serializer.save(party=party)


# ---------------------------------------------------------------------------
# Guest self-service order placement (Section 5.3.2) — the counterpart to
# party app's join_party. A guest who joined via link places their OWN
# order here, using their GuestSession token instead of a host's JWT.
# ---------------------------------------------------------------------------

class GuestOrderCreateView(generics.CreateAPIView):
    """IsValidGuestSession (core/permissions.py) gates this now — replaces
    an earlier inline isinstance(request.auth, Guest) check that lived
    directly in perform_create as a base-functionality stand-in."""

    authentication_classes = [GuestSessionAuthentication]
    permission_classes = [IsValidGuestSession]
    serializer_class = OrderCreateSerializer

    def perform_create(self, serializer):
        guest = self.request.auth
        # party and guest are both taken from the authenticated session,
        # never from the request body — a guest can only ever place an
        # order for the party their own token belongs to.
        serializer.save(
            party=guest.party,
            guest=guest,
            placed_by=Order.PlacedBy.GUEST,
            last_modified_by=Order.PlacedBy.GUEST,
        )
        order = serializer.instance

        fire_time = compute_fire_time(guest.party, guest, order.restaurant_id)
        if fire_time:
            order.fire_time = fire_time
            order.save(update_fields=["fire_time"])
            schedule_order_firing(order)
            notify_party(guest.party.code, "order_created", OrderSerializer(order).data)
        else:
            # Immediate path — schedule_order_firing fires it right away
            # and sends its own notify_party call already.
            schedule_order_firing(order)