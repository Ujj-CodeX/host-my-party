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

# Security backlog item: session expiry is tied to the party itself, not a
# flat window from whenever the guest happened to join. A guest who joins
# hours before the party starts shouldn't get logged out mid-party, and a
# guest shouldn't keep a valid session days after the party ended either.
# This buffer covers late arrivals + a reasonable afterparty window past
# the party's stated start time.
SESSION_BUFFER_AFTER_START = timedelta(hours=4)


def _hash_token(raw_token):
    return hashlib.sha256(raw_token.encode()).hexdigest()


def _compute_expiry(party):
    """
    If the party has a start time, the session is valid through
    party_start_time + SESSION_BUFFER_AFTER_START. If a guest somehow
    joins late enough that this window is already in the past (or the
    party hasn't set a start time yet, e.g. still being configured),
    fall back to the flat SESSION_LIFETIME measured from right now — a
    guest should never receive an already-expired token.
    """
    now = timezone.now()
    if party.party_start_time:
        tied_expiry = party.party_start_time + SESSION_BUFFER_AFTER_START
        return max(tied_expiry, now + SESSION_LIFETIME)
    return now + SESSION_LIFETIME


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
            "expires_at": _compute_expiry(guest.party),
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
