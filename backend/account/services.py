"""
accounts app — shared helpers for the auth endpoints.

Two repeated jobs live here so every auth view doesn't reimplement them:
1. Writing an AuthAttemptLog row (Section 4.4) — every signup/login attempt,
   success or failure, gets logged.
2. Issuing JWT tokens the same way every time — access token in the
   response body, refresh token in an httpOnly cookie (Section 4.3).
"""

from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import AuthAttemptLog
from .serializers import UserSerializer

# Rate limiting (Section 4.4)
RATE_LIMIT_WINDOW = timedelta(minutes=15)
RATE_LIMIT_MAX_FAILURES = 5  # per identifier OR per IP within the window


def get_client_ip(request):
    """
    Reads the real client IP, accounting for a reverse proxy (nginx, a
    load balancer, etc.) that sets X-Forwarded-For. Without this, every
    AuthAttemptLog row would show the proxy's IP instead of the actual
    caller's — useless for the "same IP across many accounts" brute-force
    pattern the log is meant to catch (Section 4.4).
    """
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        # X-Forwarded-For can be a chain "client, proxy1, proxy2" —
        # the first entry is the original client.
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def log_auth_attempt(request, *, identifier, identifier_type, attempt_type,
                      auth_provider, status, failure_reason=""):
    """Thin wrapper around AuthAttemptLog.objects.create — exists so every
    call site doesn't have to repeat get_client_ip() and the user_agent
    truncation."""
    AuthAttemptLog.objects.create(
        identifier=identifier or "",
        identifier_type=identifier_type,
        ip_address=get_client_ip(request),
        attempt_type=attempt_type,
        auth_provider=auth_provider,
        status=status,
        failure_reason=failure_reason[:100],
        # user_agent field is max_length=255 — truncate defensively so a
        # weird/oversized header never causes a DB error on what should be
        # a best-effort audit log.
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:255],
    )


def is_rate_limited(request, *, identifier, attempt_type):
    """
    Blocks if EITHER the identifier or the calling IP has racked up
    RATE_LIMIT_MAX_FAILURES failed attempts of this type within
    RATE_LIMIT_WINDOW — checking both angles because brute force can come
    from either direction (same IP hammering many accounts, or many IPs
    hammering one account), same reasoning Section 4.4 gives for indexing
    AuthAttemptLog by both fields independently.

    Deliberately counts FAILED attempts only — a person who gets their
    password right on the 4th try shouldn't stay locked out because of
    3 earlier typos.
    """
    window_start = timezone.now() - RATE_LIMIT_WINDOW
    ip = get_client_ip(request)

    identifier_failures = AuthAttemptLog.objects.filter(
        identifier=identifier,
        attempt_type=attempt_type,
        status=AuthAttemptLog.Status.FAILED,
        timestamp__gte=window_start,
    ).count()
    if identifier_failures >= RATE_LIMIT_MAX_FAILURES:
        return True

    ip_failures = AuthAttemptLog.objects.filter(
        ip_address=ip,
        attempt_type=attempt_type,
        status=AuthAttemptLog.Status.FAILED,
        timestamp__gte=window_start,
    ).count()
    return ip_failures >= RATE_LIMIT_MAX_FAILURES


def issue_tokens_response(user, extra_data=None):
    """
    Builds the standard success response for signup/login/Google-auth:
    - access token goes in the JSON body (frontend keeps it in memory,
      attaches it as "Authorization: Bearer <token>" on every request)
    - refresh token goes in an httpOnly, Secure, SameSite cookie (never
      touchable by JavaScript, so an XSS bug can't steal it — Section 4.3)
    """
    refresh = RefreshToken.for_user(user)
    access = refresh.access_token

    response = Response({
        "access": str(access),
        "user": UserSerializer(user).data,
        **(extra_data or {}),
    })

    response.set_cookie(
        "refresh_token",
        str(refresh),
        httponly=True,
        # secure=True means the browser only ever sends this cookie over
        # HTTPS. In local dev (DEBUG=True) that would block the cookie
        # entirely since dev usually runs on plain http — so it's tied to
        # DEBUG here. In real production, DEBUG must be False anyway.
        secure=not settings.DEBUG,
        samesite="Strict",
        max_age=int(timedelta(days=7).total_seconds()),
        path="/api/auth/",  # cookie only sent to auth endpoints, not every request
    )
    return response
