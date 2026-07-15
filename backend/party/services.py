"""
party app — Guest self-join-link session helpers (Section 5.3.2).

A guest joining via link gets a short-lived, party-scoped session token —
NOT a full User account (Guest was deliberately designed that way from
the start). This mirrors the accounts app's "never store the raw secret"
pattern, but is deliberately much lighter than JWT: no refresh rotation,
no blacklist, just one opaque token good for a fixed window. A one-time
party guest doesn't need the same machinery as a returning host.
"""

import hashlib
import secrets
from datetime import timedelta

from django.utils import timezone

from .models import GuestSession

SESSION_TOKEN_BYTES = 32
SESSION_LIFETIME = timedelta(hours=12)  # covers a full evening party, start to late-arrivals


def _hash_token(raw_token):
    return hashlib.sha256(raw_token.encode()).hexdigest()


def issue_guest_session(guest):
    """
    Generates a new raw token and stores only its hash. The raw token is
    returned so the CALLER (the join view) can hand it to the guest right
    now — it can never be retrieved again after this; only the hash
    exists in the DB from this point on.

    update_or_create means re-joining (e.g. guest refreshes the join page
    and submits again) simply issues a fresh token rather than erroring
    on GuestSession's OneToOneField.
    """
    raw_token = secrets.token_urlsafe(SESSION_TOKEN_BYTES)
    GuestSession.objects.update_or_create(
        guest=guest,
        defaults={
            "token_hash": _hash_token(raw_token),
            "expires_at": timezone.now() + SESSION_LIFETIME,
        },
    )
    return raw_token


def get_guest_from_token(raw_token):
    """
    Looks up the Guest owning a valid, non-expired token. Returns None
    for EVERY failure case (token doesn't exist, or exists but expired) —
    deliberately no way for a caller to distinguish "never existed" from
    "existed but expired", so that distinction can never leak to whoever
    is holding an invalid token.
    """
    if not raw_token:
        return None

    token_hash = _hash_token(raw_token)
    try:
        session = GuestSession.objects.select_related("guest").get(token_hash=token_hash)
    except GuestSession.DoesNotExist:
        return None

    if not session.is_valid():
        return None

    return session.guest