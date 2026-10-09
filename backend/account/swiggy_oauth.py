import base64
import hashlib
import secrets 

from datetime import timedelta
from urllib.parse import urlencode, urlparse

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import transaction
from django.utils import timezone

from .models import SwiggyOAuthAttempt
from .swiggy_crypto import encrypt_secret

def hash_state(state: str) -> str:
    return hashlib.sha256(state.encode("utf-8")).hexdigest()

def start_swiggy_authorization(user) -> str:
    client_id = getattr(settings, "SWIGGY_CLIENT_ID","")
    redirect_uri = getattr(settings, "SWIGGY_REDIRECT_URI","")
    base_url = settings.SWIGGY_OAUTH_BASE_URI.rstrip("/")

    if not client_id or not redirect_uri:
        raise ImproperlyConfigured(
            "SWIGGY_CLIENT_ID and SWIGGY_REDIRECT_URI must be configured."
        )

    parsed = urlparse(redirect_uri)
    is_local_http = (
        parsed.scheme == "http" and parsed.hostname in ("localhost", "127.0.0.1")
    )

    if parsed.scheme != "https" and not is_local_http:
        raise ImproperlyConfigured(
            "Swiggy redirect URI must use HTTPS outside localhost."
        )
    state = secrets.token_urlsafe(32)
    verifier = secrets.token_urlsafe(48)

    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode("ascii")).digest()
    ).rstrip(b"=").decode("ascii")

    SwiggyOAuthAttempt.objects.create(
        user=user,
        client_id=client_id,
        state_hash=hash_state(state),
        code_verifier_ciphertext=encrypt_secret(verifier),
        redirect_uri=redirect_uri,
        expires_at=timezone.now() + timedelta(minutes=5),
    )

    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "state": state,
        "scope": "mcp:tools",
    }

    return f"{base_url}/auth/authorize?{urlencode(params)}"


def consume_swiggy_oauth_attempt(state: str):
    if not state:
        return None
    with transaction.atomic():
        attempt = (
            
            SwiggyOAuthAttempt.objects.select_for_update()
            .filter(state_hash=hash_state(state), consumed_at__isnull=True)
            .first()
        )

        if attempt is None:
            return None
        attempt.consumed_at = timezone.now()
        attempt.save(update_fields=["consumed_at"])
    return attempt




