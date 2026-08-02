"""
party app — Guest self-join-link session helpers (Section 5.3.2).

A guest joining via link gets a short-lived, party-scoped session token —
NOT a full User account (Guest was deliberately designed that way from
the start). This mirrors the accounts app's "never store the raw secret"
pattern, but is deliberately much lighter than JWT: no refresh rotation,
no blacklist, just one opaque token good for a fixed window.
"""

import hashlib
import secrets
from datetime import timedelta

from django.utils import timezone

from .models import GuestSession

SESSION_TOKEN_BYTES = 32
SESSION_LIFETIME = timedelta(hours=12)  # fallback: covers a full evening, start to late-arrivals


SESSION_BUFFER_AFTER_START = timedelta(hours=4)


def _hash_token(raw_token):
    return hashlib.sha256(raw_token.encode()).hexdigest()


def _compute_expiry(party):
    
    now = timezone.now()
    if party.party_start_time:
        tied_expiry = party.party_start_time + SESSION_BUFFER_AFTER_START
        return max(tied_expiry, now + SESSION_LIFETIME)
    return now + SESSION_LIFETIME


def issue_guest_session(guest):
    
    raw_token = secrets.token_urlsafe(SESSION_TOKEN_BYTES)
    GuestSession.objects.update_or_create(
        guest=guest,
        defaults={
            "token_hash": _hash_token(raw_token),
            "expires_at": _compute_expiry(guest.party),
        },
    )
    return raw_token


def get_guest_from_token(raw_token):
    
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
