"""
party app — host-facing CRUD endpoints for Party and Guest.

Scope note: all endpoints here are host-authenticated (JWT). The
guest-facing self-service flow (join via link, guest places their own
order) needs a separate GuestSession-token authentication class and is
deferred to the auth-endpoints stage — it's an auth mechanism, not CRUD.
"""

from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from core.permissions import get_owned_party

from .models import Guest, Party
from .serializers import (
    GuestSerializer,
    PartyDetailSerializer,
    PartyJoinInfoSerializer,
    PartyListSerializer,
    SwiggyAddressCreateSerializer,
)
from .services import issue_guest_session
from account.models import SwiggyUserCredential
from django.core.exceptions import ImproperlyConfigured

from ai.address_provider import (
    AddressProviderError,
    get_swiggy_address_provider,
)


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
    
    guest = serializer.save(party=party)

    raw_token = issue_guest_session(guest)

    return Response(
        {
            "guest": GuestSerializer(guest).data,
            
            "session_token": raw_token,
            "expires_in_hours": 12,
        },
        status=status.HTTP_201_CREATED,
    )




@api_view(["GET", "POST", "PATCH"])
@permission_classes([permissions.IsAuthenticated])
def party_address(request, party_code):
    """Manage the authenticated host's addresses for a party."""

    party = get_owned_party(request, party_code)

    # Get the configured address provider.
    try:
        provider = get_swiggy_address_provider()
    except ImproperlyConfigured:
        return Response(
            {
                "code": "address_provider_unavailable",
                "detail": "Address provider is not configured.",
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    # Mock provider works without Swiggy OAuth.
    # A real provider must require a valid Swiggy credential.
    if provider.requires_swiggy_auth:
        credential = SwiggyUserCredential.objects.filter(
            user=request.user
        ).first()

        if credential is None or credential.revoked_at is not None:
            return Response(
                {
                    "code": "swiggy_connection_required",
                    "detail": "Connect your Swiggy account first.",
                },
                status=status.HTTP_409_CONFLICT,
            )

        if credential.expires_at <= timezone.now():
            return Response(
                {
                    "code": "swiggy_reconnect_required",
                    "detail": "Your Swiggy connection has expired.",
                },
                status=status.HTTP_409_CONFLICT,
            )

    # Fetch addresses once, for GET and PATCH validation.
    try:
        addresses = provider.get_addresses(request.user)
    except AddressProviderError:
        return Response(
            {"detail": "Unable to retrieve saved addresses."},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    if request.method == "GET":
        selected_address = next(
            (
                address
                for address in addresses
                if str(address.get("address_id"))
                == str(party.swiggy_address_id)
            ),
            None,
        )

        return Response(
            {
                "party_code": party.code,
                "selected_address_id": party.swiggy_address_id,
                "selected_address": selected_address,
                "addresses": addresses,
            }
        )

    if request.method == "PATCH":
        address_id = request.data.get("address_id")

        if not isinstance(address_id, str) or not address_id.strip():
            return Response(
                {"detail": "address_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        selected_address = next(
            (
                address
                for address in addresses
                if str(address.get("address_id")) == address_id
            ),
            None,
        )

        if selected_address is None:
            return Response(
                {
                    "detail": (
                        "Address not found in this host's saved addresses."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        response_status = status.HTTP_200_OK

    else:
        serializer = SwiggyAddressCreateSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        try:
            selected_address = provider.create_address(
                request.user,
                serializer.validated_data,
            )
        except AddressProviderError:
            return Response(
                {"detail": "Unable to create the address."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        if (
            not isinstance(selected_address, dict)
            or not selected_address.get("address_id")
        ):
            return Response(
                {"detail": "Address provider returned no address ID."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        response_status = status.HTTP_201_CREATED

    # Save the selected address against this party.
    address_id = selected_address.get("address_id")

    if not address_id:
        return Response(
            {"detail": "Address provider returned no address ID."},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    party.swiggy_address_id = str(address_id)
    party.delivery_address = str(
        selected_address.get("formatted_address") or ""
    )[:255]
    party.delivery_lat = selected_address.get("latitude")
    party.delivery_lng = selected_address.get("longitude")

    party.save(
        update_fields=[
            "swiggy_address_id",
            "delivery_address",
            "delivery_lat",
            "delivery_lng",
            "updated_at",
        ]
    )

    return Response(
        {
            "party_code": party.code,
            "selected_address_id": party.swiggy_address_id,
            "selected_address": selected_address,
        },
        status=response_status,
    )
