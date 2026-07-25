"""
party app — DRF authentication for guest-session-token endpoints.

A host authenticates with "Authorization: Bearer <jwt>" (Section 4.3).
A guest who joined via link authenticates with a DIFFERENT scheme:
    Authorization: GuestSession <raw_token>

Using a distinct scheme name (not "Bearer") is deliberate — it stops a
guest token and a host's JWT access token from ever being confused with
each other in logs, in a browser's dev tools, or by a developer copy-
pasting the wrong header while debugging.

"""

from rest_framework import authentication, exceptions

from .services import get_guest_from_token


class GuestSessionAuthentication(authentication.BaseAuthentication):
    keyword = "GuestSession"

    def authenticate(self, request):
        auth_header = authentication.get_authorization_header(request).decode("utf-8")

        if not auth_header or not auth_header.startswith(self.keyword):
            
            return None

        raw_token = auth_header[len(self.keyword):].strip()
        guest = get_guest_from_token(raw_token)

        if guest is None:
            raise exceptions.AuthenticationFailed("Invalid or expired guest session.")

        
        return (None, guest)