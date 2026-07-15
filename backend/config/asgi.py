"""
config — ASGI application entrypoint.

CRITICAL ORDERING: get_asgi_application() must run BEFORE anything below
it imports app code (routing -> consumers -> models). Django's app
registry isn't ready until get_asgi_application() has run once — importing
models before that raises AppRegistryNotReady. This is why the imports
below are split into two groups instead of one tidy alphabetical block.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Must happen before importing anything that touches models (directly or
# transitively) — see docstring above.
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402
from config.channels_auth import JWTAuthMiddleware  # noqa: E402
from party.routing import websocket_urlpatterns  # noqa: E402

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": JWTAuthMiddleware(URLRouter(websocket_urlpatterns)),
})