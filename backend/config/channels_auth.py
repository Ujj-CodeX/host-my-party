"""
config — Channels middleware authenticating WebSocket connections with
the SAME JWT access tokens the REST API already uses (Section 4.3).

WHY THIS FILE EXISTS: Channels' built-in AuthMiddlewareStack expects
Django's session-based auth (a login cookie) — this project has no
sessions at all, only JWT. And browsers can't attach a custom
Authorization header to a WebSocket handshake the way fetch() can attach
one to an HTTP request — so instead, the frontend connects like:

    ws://app.com/ws/party/XJ9K2A/?token=<access_token>


"""

from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken


@database_sync_to_async
def _get_user_from_token(raw_token):
    from account.models import User

    try:
        validated = AccessToken(raw_token)
        return User.objects.get(id=validated["user_id"])
    except (TokenError, InvalidToken, User.DoesNotExist):
        return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode()
        token = parse_qs(query_string).get("token", [None])[0]

        scope["user"] = await _get_user_from_token(token) if token else AnonymousUser()

        return await super().__call__(scope, receive, send)