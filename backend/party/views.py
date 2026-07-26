"""
party app — host-facing CRUD endpoints for Party and Guest.

Scope note: all endpoints here are host-authenticated (JWT). The
guest-facing self-service flow (join via link, guest places their own
order) needs a separate GuestSession-token authentication class and is
deferred to the auth-endpoints stage — it's an auth mechanism, not CRUD.
"""

from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from core.permissions import get_owned_party
from party.realtime import notify_party

from .models import Guest, Party
from .serializers import (
    GuestSerializer,
    PartyDetailSerializer,
    PartyJoinInfoSerializer,
    PartyListSerializer,
)
from .services import issue_guest_session


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



@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def join_party(request, party_code):
    """
    GET:  the join-link landing page's data — party's public info only.
    POST: guest submits name + dietary_pref, a Guest row is created, and a
          session token is issued (Section 5.3.2) — a lightweight,
          party-scoped credential, not a full account.
    """
    party = get_object_or_404(Party, code=party_code)

    if request.method == "GET":
        return Response(PartyJoinInfoSerializer(party).data)

    serializer = GuestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    # party is injected here, never trusted from the request body — same
    # principle as every other create() in this codebase (e.g. Booking's
    # perform_create).
    guest = serializer.save(party=party)

    raw_token = issue_guest_session(guest)

    notify_party(party.code, "guest_joined", GuestSerializer(guest).data)

    return Response(
        {
            "guest": GuestSerializer(guest).data,
            
            "session_token": raw_token,
            "expires_in_hours": 12,
        },
        status=status.HTTP_201_CREATED,
    )