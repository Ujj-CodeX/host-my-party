"""
party app — WebSocket consumer for the host's live dashboard (Section 5.3.3).

    Host Dashboard --connects--> ws://app.com/ws/party/{party_code}/

Delivers live updates only. Per the docs' explicit design decision, the
socket is NOT the source of truth: on reconnect, the frontend must still
re-fetch authoritative state via a normal REST GET. This consumer only
pushes "something changed, go refetch" style events.
"""

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from .models import Party


class PartyConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.party_code = self.scope["url_route"]["kwargs"]["party_code"]
        self.group_name = f"party_{self.party_code}"

        # scope["user"] is populated by JWTAuthMiddleware (config/channels_auth.py)
        # reading the access token from the connection URL's query string —
        # WebSocket connections can't set a custom Authorization header the
        # way a normal fetch() can, so the token travels as ?token=... instead.
        user = self.scope.get("user")
        if user is None or not user.is_authenticated:
            # Reject BEFORE accept() — the connection is refused outright,
            # never even upgraded to a socket. Matches "only the host's
            # dashboard connects" from Section 5.3.3.
            await self.close(code=4401)
            return

        is_host = await self._is_host_of_this_party(user)
        if not is_host:
            await self.close(code=4403)
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # group_name only exists if connect() got far enough to set it —
        # a connection rejected early (bad/no auth) never joined a group,
        # so there's nothing to clean up in that case.
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def party_update(self, event):
        """
        Handles every message sent via channel_layer.group_send with
        "type": "party.update" (see party/realtime.py). The method name
        matching that type string (with the dot turned into an
        underscore) is a Channels convention, not a coincidence.
        """
        await self.send_json({
            "event_type": event["event_type"],
            "payload": event["payload"],
        })

    @database_sync_to_async
    def _is_host_of_this_party(self, user):
        # Wrapped in database_sync_to_async because this consumer runs in
        # an async context, but Django's ORM is synchronous — a plain
        # Party.objects.filter(...) call here would crash without this
        # wrapper bridging sync DB access into the async event loop.
        return Party.objects.filter(code=self.party_code, host=user).exists()