"""
party app — DRF authentication for guest-session-token endpoints.



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