"""
party app — host-facing CRUD endpoints for Party and Guest.

Scope note: all endpoints here are host-authenticated (JWT). The
guest-facing self-service flow (join via link, guest places their own
order) needs a separate GuestSession-token authentication class and is
deferred to the auth-endpoints stage — it's an auth mechanism, not CRUD.
"""

from rest_framework import generics, permissions

from core.permissions import get_owned_party

from .models import Guest, Party
from .serializers import GuestSerializer, PartyDetailSerializer, PartyListSerializer


class PartyListCreateView(generics.ListCreateAPIView):
    """GET: host's own parties (lean list). POST: create a new party,
    host is always the requesting user — never client-supplied."""

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Party.objects.filter(host=self.request.user).order_by("-created_at")

    def get_serializer_class(self):
        return PartyListSerializer if self.request.method == "GET" else PartyDetailSerializer

    def perform_create(self, serializer):
        serializer.save(host=self.request.user)


class PartyDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Looked up by the shareable `code`, not the numeric id — that's the
    identifier already used everywhere else (join links, guest views)."""

    serializer_class = PartyDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "code"
    lookup_url_kwarg = "party_code"

    def get_queryset(self):
        # Scoping the queryset to the requester's own parties means a
        # mismatched host gets a clean 404, not a 403 — no need for a
        # separate object-permission check here.
        return Party.objects.filter(host=self.request.user)


class GuestListCreateView(generics.ListCreateAPIView):
    """Host adding/viewing guests for a party they own. This is the
    "host orders on behalf of everyone, using each guest's stated
    preference" path (Section 5.3.1) — not the guest self-join-link flow."""

    serializer_class = GuestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        party = get_owned_party(self.request, self.kwargs["party_code"])
        return party.guests.all().order_by("created_at")

    def perform_create(self, serializer):
        party = get_owned_party(self.request, self.kwargs["party_code"])
        serializer.save(party=party)


class GuestDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = GuestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        party = get_owned_party(self.request, self.kwargs["party_code"])
        return party.guests.all()