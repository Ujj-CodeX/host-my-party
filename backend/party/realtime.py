"""
party app — realtime notification helper (Section 5.3.3).

Regular DRF views are synchronous, but Django Channels' channel layer is
async-native — async_to_sync bridges the two. Every place in the codebase
that changes something the host's dashboard should know about (a guest's
order saved, a host editing an order, etc.) calls notify_party() instead
of talking to the channel layer directly, so "how do I reach the
dashboard" plumbing lives in exactly one place, not duplicated at every
call site.
"""

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def notify_party(party_code, event_type, payload):
    """
    Pushes a live update to whoever's connected to this party's dashboard
    channel. Fails SILENTLY if the channel layer isn't configured (e.g.
    Redis isn't running in a given environment) — realtime is explicitly
    a nice-to-have layered on top of the REST API (Section 5.3.3: "the
    socket is not the source of truth"), so a missing Redis should never
    break the HTTP request that triggered this notification.
    """
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return

    async_to_sync(channel_layer.group_send)(
        f"party_{party_code}",
        {
            # "type" is a Channels convention: dots become underscores to
            # find the handler method — "party.update" here routes to
            # PartyConsumer.party_update() below.
            "type": "party.update",
            "event_type": event_type,
            "payload": payload,
        },
    )