"""
orders app — host-facing CRUD endpoints for Order and Booking.
 
Same scope note as party/views.py: guest self-service ordering (a guest
placing their own order via their join-link session) is deferred to the
auth-endpoints stage. These endpoints cover the host's dashboard — viewing
all orders in a party, and the "host orders on behalf of everyone" path.
"""

# Create your views here.


from rest_framework import generics, permissions
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response


from core.permissions import get_owned_party
from .models import Booking, Order
from .serializers import OrderSerializer,BookingSerializer, OrderCreateSerializer


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
 
    def update(self, request, *args, **kwargs):
        # OrderCreateSerializer's own .data is write-shaped (items is
        # write_only, no computed total) — re-serialize with OrderSerializer
        # so the response actually reflects the updated order.
        super().update(request, *args, **kwargs)
        instance = self.get_object()
        return Response(OrderSerializer(instance).data)
 
 
class BookingDetailView(generics.RetrieveUpdateAPIView):
    """
    One-to-one with Party, so there's no separate create endpoint here —
    creating a Party in dineout mode should create its Booking in the same
    request. That composite create belongs with the Dineout booking flow
    (not yet built). For now this supports read + host edits of an
    existing Booking.
    """
 
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
 
    def get_object(self):
        party = get_owned_party(self.request, self.kwargs["party_code"])
        return get_object_or_404(Booking, party=party)
