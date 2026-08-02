"""
party app — WebSocket consumer for the host's live dashboard (Section 5.3.3).

    Host Dashboard --connects--> ws://app.com/ws/party/{party_code}/


"""

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from .models import Party


class PartyConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.party_code = self.scope["url_route"]["kwargs"]["party_code"]
        self.group_name = f"party_{self.party_code}"

        
        user = self.scope.get("user")
        if user is None or not user.is_authenticated:
            
            await self.close(code=4401)
            return

        is_host = await self._is_host_of_this_party(user)
        if not is_host:
            await self.close(code=4403)
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
       
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def party_update(self, event):
        
        
        await self.send_json({
            "event_type": event["event_type"],
            "payload": event["payload"],
        })

    @database_sync_to_async
    def _is_host_of_this_party(self, user):
        
        return Party.objects.filter(code=self.party_code, host=user).exists()