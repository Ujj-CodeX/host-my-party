"""
party app — realtime notification helper (Section 5.3.3).


"""

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def notify_party(party_code, event_type, payload):
    """
    
    """
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return

    async_to_sync(channel_layer.group_send)(
        f"party_{party_code}",
        {
            
            "type": "party.update",
            "event_type": event_type,
            "payload": payload,
        },
    )