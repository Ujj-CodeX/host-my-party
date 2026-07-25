from django.shortcuts import render

# Create your views here.
"""
accounts app — auth endpoints (Section 4 of the project docs).

Every endpoint here is AllowAny (no login required to reach it) EXCEPT
profile update and logout, which require an already-valid access token.
"""

from django.conf import settings
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .models import AuthAttemptLog, User
from .serializers import (
    PhoneLoginSerializer,
    PhoneSignupSerializer,
    ProfileUpdateSerializer,
    UserSerializer,
)
from .services import is_rate_limited, issue_tokens_response, log_auth_attempt


@api_view(["POST"])
@permission_classes([AllowAny])
def signup_phone(request):
    phone_number = request.data.get("phone_number", "")

    # Rate limiting (Section 4.4 / roadmap) — checked before touching the
    # serializer, so a flood of signup attempts against one number/IP
    # can't even reach validation or DB uniqueness checks.
    if is_rate_limited(request, identifier=phone_number, attempt_type=AuthAttemptLog.AttemptType.SIGNUP):
        log_auth_attempt(
            request,
            identifier=phone_number,
            identifier_type=AuthAttemptLog.IdentifierType.PHONE,
            attempt_type=AuthAttemptLog.AttemptType.SIGNUP,
            auth_provider=AuthAttemptLog.AuthProvider.LOCAL,
            status=AuthAttemptLog.Status.FAILED,
            failure_reason="rate_limited",
        )
        return Response(
            {"detail": "Too many attempts. Please try again later."},
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )

    serializer = PhoneSignupSerializer(data=request.data)

    if not serializer.is_valid():
        # Logged even on a validation failure (e.g. "phone already
        # registered") — that's still a signup *attempt*, and repeated
        # attempts against the same phone number from different IPs is
        # exactly the pattern Section 4.4's audit table exists to catch.
        log_auth_attempt(
            request,
            identifier=phone_number,
            identifier_type=AuthAttemptLog.IdentifierType.PHONE,
            attempt_type=AuthAttemptLog.AttemptType.SIGNUP,
            auth_provider=AuthAttemptLog.AuthProvider.LOCAL,
            status=AuthAttemptLog.Status.FAILED,
            failure_reason=str(serializer.errors)[:100],
        )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    user = User.objects.create_user(
        phone_number=data["phone_number"],
        password=data["password"],
        name=data["name"],
        auth_provider=User.AuthProvider.LOCAL,
    )

    log_auth_attempt(
        request,
        identifier=data["phone_number"],
        identifier_type=AuthAttemptLog.IdentifierType.PHONE,
        attempt_type=AuthAttemptLog.AttemptType.SIGNUP,
        auth_provider=AuthAttemptLog.AuthProvider.LOCAL,
        status=AuthAttemptLog.Status.SUCCESS,
    )

    return issue_tokens_response(user)


@api_view(["POST"])
@permission_classes([AllowAny])
def login_phone(request):
    serializer = PhoneLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    phone_number = serializer.validated_data["phone_number"]
    password = serializer.validated_data["password"]

    # Rate limiting (Section 4.4 / roadmap) — this is the primary
    # brute-force target, so it's checked before the password is even
    # compared, not just before issuing tokens.
    if is_rate_limited(request, identifier=phone_number, attempt_type=AuthAttemptLog.AttemptType.LOGIN):
        log_auth_attempt(
            request,
            identifier=phone_number,
            identifier_type=AuthAttemptLog.IdentifierType.PHONE,
            attempt_type=AuthAttemptLog.AttemptType.LOGIN,
            auth_provider=AuthAttemptLog.AuthProvider.LOCAL,
            status=AuthAttemptLog.Status.FAILED,
            failure_reason="rate_limited",
        )
        return Response(
            {"detail": "Too many attempts. Please try again later."},
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )

    user = User.objects.filter(phone_number=phone_number).first()

    # Deliberately the SAME error message and status code whether the
    # phone number doesn't exist at all, or it exists but the password is
    # wrong. Distinguishing the two ("no such account" vs "wrong
    # password") would let an attacker enumerate which phone numbers have
    # accounts just by trying logins.
    if user is None or not user.check_password(password):
        log_auth_attempt(
            request,
            identifier=phone_number,
            identifier_type=AuthAttemptLog.IdentifierType.PHONE,
            attempt_type=AuthAttemptLog.AttemptType.LOGIN,
            auth_provider=AuthAttemptLog.AuthProvider.LOCAL,
            status=AuthAttemptLog.Status.FAILED,
            failure_reason="invalid_credentials",
        )
        return Response(
            {"detail": "Invalid phone number or password."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    log_auth_attempt(
        request,
        identifier=phone_number,
        identifier_type=AuthAttemptLog.IdentifierType.PHONE,
        attempt_type=AuthAttemptLog.AttemptType.LOGIN,
        auth_provider=AuthAttemptLog.AuthProvider.LOCAL,
        status=AuthAttemptLog.Status.SUCCESS,
    )

    return issue_tokens_response(user)


@api_view(["POST"])
@permission_classes([AllowAny])
def google_auth(request):
    """
    Accepts a Google ID token (obtained client-side via Google Sign-In),
    verifies it against Google's servers, and either logs in an existing
    Google user or creates a new one — first-time Google sign-in doubles
    as signup (Section 4.5).
    """
    raw_token = request.data.get("id_token")
    if not raw_token:
        return Response(
            {"detail": "id_token is required."}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # This call hits Google's servers to verify the token's signature
        # and audience — it's what makes this trustworthy rather than
        # just decoding a JWT blindly and believing whatever email it claims.
        idinfo = google_id_token.verify_oauth2_token(
            raw_token, google_requests.Request(), settings.GOOGLE_CLIENT_ID
        )
    except ValueError:
        # verify_oauth2_token raises ValueError for basically any problem:
        # expired token, wrong audience, bad signature, malformed token.
        log_auth_attempt(
            request,
            identifier="",
            identifier_type=AuthAttemptLog.IdentifierType.EMAIL,
            attempt_type=AuthAttemptLog.AttemptType.LOGIN,
            auth_provider=AuthAttemptLog.AuthProvider.GOOGLE,
            status=AuthAttemptLog.Status.FAILED,
            failure_reason="invalid_google_token",
        )
        return Response(
            {"detail": "Invalid or expired Google token."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    email = idinfo["email"]
    name = idinfo.get("name", "")

    user, created = User.objects.get_or_create(
        email=email,
        defaults={"name": name, "auth_provider": User.AuthProvider.GOOGLE},
    )

    log_auth_attempt(
        request,
        identifier=email,
        identifier_type=AuthAttemptLog.IdentifierType.EMAIL,
        attempt_type=(
            AuthAttemptLog.AttemptType.SIGNUP if created
            else AuthAttemptLog.AttemptType.LOGIN
        ),
        auth_provider=AuthAttemptLog.AuthProvider.GOOGLE,
        status=AuthAttemptLog.Status.SUCCESS,
    )

    return issue_tokens_response(user, extra_data={"created": created})


@api_view(["POST"])
@permission_classes([AllowAny])
def refresh_token_view(request):
    """
    Reads the refresh token from the httpOnly cookie (not the request
    body — the whole point of httpOnly is that JavaScript, and therefore
    the frontend's own request-building code, can never read it; only the
    browser attaches it automatically). Rotates it: the old refresh token
    is blacklisted and a new one issued, so a stolen refresh token that
    gets used once becomes worthless (Section 4.3).
    """
    raw_refresh = request.COOKIES.get("refresh_token")
    if not raw_refresh:
        return Response(
            {"detail": "Refresh token missing."}, status=status.HTTP_401_UNAUTHORIZED
        )

    try:
        old_refresh = RefreshToken(raw_refresh)
    except TokenError:
        return Response(
            {"detail": "Refresh token invalid or expired."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    user_id = old_refresh["user_id"]
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {"detail": "User no longer exists."}, status=status.HTTP_401_UNAUTHORIZED
        )

    # Blacklist the old token before issuing a new one — requires the
    # rest_framework_simplejwt.token_blacklist app installed and migrated.
    # If that app isn't set up yet, .blacklist() doesn't exist and we skip
    # it rather than hard-crashing the refresh flow over a missing table.
    if hasattr(old_refresh, "blacklist"):
        old_refresh.blacklist()

    return issue_tokens_response(user)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Blacklists the current refresh token server-side (Section 4.5) —
    just clearing the cookie client-side wouldn't stop the same token
    being replayed by whoever's holding it."""
    raw_refresh = request.COOKIES.get("refresh_token")
    if raw_refresh:
        try:
            token = RefreshToken(raw_refresh)
            if hasattr(token, "blacklist"):
                token.blacklist()
        except TokenError:
            pass  # already invalid/expired — nothing to blacklist

    response = Response({"detail": "Logged out."})
    response.delete_cookie("refresh_token", path="/api/auth/")
    return response


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_profile(request):
    serializer = ProfileUpdateSerializer(request.user, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(UserSerializer(request.user).data)
