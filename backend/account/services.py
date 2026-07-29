"""
accounts app — shared helpers for the auth endpoints.

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
    
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
       
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def log_auth_attempt(request, *, identifier, identifier_type, attempt_type,
                      auth_provider, status, failure_reason=""):
    
    AuthAttemptLog.objects.create(
        identifier=identifier or "",
        identifier_type=identifier_type,
        ip_address=get_client_ip(request),
        attempt_type=attempt_type,
        auth_provider=auth_provider,
        status=status,
        failure_reason=failure_reason[:100],
        
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:255],
    )


def is_rate_limited(request, *, identifier, attempt_type):
    
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
        
        secure=not settings.DEBUG,
        samesite="Strict",
        max_age=int(timedelta(days=7).total_seconds()),
        path="/api/auth/",  # cookie only sent to auth endpoints, not every request
    )
    return response
