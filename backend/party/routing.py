"""
party app — WebSocket routing. This is deliberately separate from
urls.py: Django's normal path()/urls.py only ever matches HTTP requests.
WebSocket connections are routed through this file instead, wired into
config/asgi.py.
"""

from django.urls import re_path

from .consumers import PartyConsumer

websocket_urlpatterns = [
    re_path(r"ws/party/(?P<party_code>\w+)/$", PartyConsumer.as_asgi()),
]