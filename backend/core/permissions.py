"""
core app — shared permission helpers used across party/orders views.
 
core already depends on party (GroqCallLog/Notification both FK into
Party/Guest), so this mirrors the same dependency direction rather than
introducing a new one.
"""


from rest_framework import PermissionDenied
from rest_framework.permissions import get_object_or_404


from party.models import Party

def get_owned_party(request, party_code):
    """
    Fetch a Party by its shareable code, restricted to the requesting user
    as host. 404s if the party doesn't exist at all, 403s if it exists but
    belongs to someone else.
    """

    party = get_object_or_404(Party, code=party_code)
    if party.host != request.user:
        raise PermissionDenied("You are not the host of this party.")
    return party

    