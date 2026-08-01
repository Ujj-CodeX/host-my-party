"""
core app — shared permission helpers used across party/orders views.

"""

from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import BasePermission

from party.models import Guest, Party


def get_owned_party(request, party_code):
    """
    Fetch a Party by its shareable code, restricted to the requesting user
    as host. 404s if the party doesn't exist at all, 403s if it exists but
    belongs to someone else.
    """
    party = get_object_or_404(Party, code=party_code)
    if party.host_id != request.user.id:
        raise PermissionDenied("You do not host this party.")
    return party


class IsValidGuestSession(BasePermission):
    """
    Grants access only if GuestSessionAuthentication succeeded for this
    request.

    WHY THIS CLASS EXISTS: DRF's built-in IsAuthenticated checks
    request.user.is_authenticated — but Guest was deliberately never made
    a User account, so under GuestSessionAuthentication, request.user
    stays Django's AnonymousUser no matter how valid the guest token was.
    The actual Guest rides along as request.auth instead (see
    party/authentication.py's docstring). IsAuthenticated would therefore
    reject every valid guest, permanently — this class checks the right
    thing instead of assuming "authenticated" always means "has a User".

    This replaces the inline `if not isinstance(request.auth, Guest):`
    checks that were written directly into guest_get_restaurants and
    GuestOrderCreateView as a base-functionality stand-in — same check,
    now reusable and declared as normal DRF permission_classes.
    """

    def has_permission(self, request, view):
        return isinstance(request.auth, Guest)


class IsHostOrValidGuestSession(BasePermission):
    """
    Grants access to EITHER a JWT-authenticated host OR a valid guest
    session — for any future endpoint genuinely meant to serve both (e.g.
    a shared "view this order" endpoint the host and the guest who placed
    it can both hit). Not used by any current view — guest_get_restaurants
    and GuestOrderCreateView are guest-only, so they use IsValidGuestSession
    directly. This exists ready for when a shared-access endpoint is needed,
    rather than being built retroactively at that point.
    """

    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            return True
        return isinstance(request.auth, Guest)