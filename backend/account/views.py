import requests

from cryptography.fernet import InvalidToken
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseRedirect
from django.utils import timezone
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

from .models import SwiggyUserCredential
from .swiggy_crypto import decrypt_secret, encrypt_secret
from .swiggy_oauth import ( consume_swiggy_oauth_attempt, start_swiggy_authorization)
from datetime import timedelta







@api_view(["POST"])
@permission_classes([AllowAny])
def signup_phone(request):
    phone_number = request.data.get("phone_number", "")

    
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
    
    raw_token = request.data.get("id_token")
    if not raw_token:
        return Response(
            {"detail": "id_token is required."}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        
        idinfo = google_id_token.verify_oauth2_token(
            raw_token, google_requests.Request(), settings.GOOGLE_CLIENT_ID
        )
    except ValueError:
        
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


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def swiggy_callback(request):
    """Handle Swiggy's OAuth redirect securely."""

    state = request.query_params.get("state", "")
    attempt = consume_swiggy_oauth_attempt(state)

    if attempt is None:
        return _swiggy_callback_redirect("invalid_state")

    if request.query_params.get("error"):
        return _swiggy_callback_redirect("denied")

    code = request.query_params.get("code")
    if not code:
        return _swiggy_callback_redirect("failed")

    try:
        verifier = decrypt_secret(
            attempt.code_verifier_ciphertext
        )

        response = requests.post(
            f"{settings.SWIGGY_OAUTH_BASE_URL.rstrip('/')}/auth/token",
            json={
                "grant_type": "authorization_code",
                "code": code,
                "code_verifier": verifier,
                "client_id": attempt.client_id,
                "redirect_uri": attempt.redirect_uri,
            },
            timeout=(5, 15),
        )
        response.raise_for_status()
        token_data = response.json()

        access_token = token_data.get("access_token")
        expires_in = int(token_data.get("expires_in", 0))

        if not isinstance(access_token, str) or not access_token:
            raise ValueError("Missing access token.")

        if expires_in <= 0:
            raise ValueError("Invalid token lifetime.")

        now = timezone.now()

        SwiggyUserCredential.objects.update_or_create(
            user=attempt.user,
            defaults={
                "client_id": attempt.client_id,
                "access_token_ciphertext": encrypt_secret(
                    access_token
                ),
                "token_type": str(
                    token_data.get("token_type", "Bearer")
                )[:20],
                "scope": str(
                    token_data.get("scope", "")
                )[:255],
                "expires_at": now + timedelta(
                    seconds=expires_in
                ),
                "connected_at": now,
                "revoked_at": None,
            },
        )

    except (
        requests.RequestException,
        ValueError,
        TypeError,
        InvalidToken,
    ):
        return _swiggy_callback_redirect("failed")

    return _swiggy_callback_redirect("success")


def _swiggy_callback_redirect(result):
    app_url = settings.PARTYNOSH_APP_URL.rstrip("/")
    return HttpResponseRedirect(
        f"{app_url}/?swiggy_connection={result}"
    )

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def swiggy_connect(request):
    """Start Swiggy OAuth for the authenticated HMP user."""

    try:
        authorization_url = start_swiggy_authorization(
            request.user
        )
    except ImproperlyConfigured:
        return Response(
            {"detail": "Swiggy OAuth is not configured."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    return Response({
        "authorization_url": authorization_url,
        "expires_in_seconds": 300,
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def swiggy_status(request):
    """Return Swiggy connection status without exposing tokens."""

    credential = SwiggyUserCredential.objects.filter(
        user=request.user
    ).first()

    now = timezone.now()

    expired = bool(
        credential and credential.expires_at <= now
    )

    connected = bool(
        credential
        and credential.revoked_at is None
        and not expired
    )

    return Response({
        "connected": connected,
        "expired": expired,
        "expires_at": (
            credential.expires_at.isoformat()
            if credential else None
        ),
    })