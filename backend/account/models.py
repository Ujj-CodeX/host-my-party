"""
accounts app — everything related to who a person is and how they log in.
Section 4 of the project docs.

"""

import uuid

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    """
    Creates users keyed by phone (local signup) or email (Google signup).
    `username` is never chosen by the person — it's an internal-only UUID
    hex string that exists purely to satisfy Django's auth machinery.
    """

    use_in_migrations = True

    def _create_user(self, *, phone_number=None, email=None, password=None,
                      name="", auth_provider="local", **extra_fields):
        if not phone_number and not email:
            raise ValueError("A user requires either a phone_number or an email.")

        email = self.normalize_email(email) if email else None
        user = self.model(
            username=uuid.uuid4().hex,
            phone_number=phone_number,
            email=email,
            name=name,
            auth_provider=auth_provider,
            **extra_fields,
        )
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_user(self, *, phone_number=None, email=None, password=None,
                     name="", auth_provider="local", **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(
            phone_number=phone_number, email=email, password=password,
            name=name, auth_provider=auth_provider, **extra_fields,
        )

    def create_superuser(self, *, email=None, phone_number=None, password=None,
                          name="Admin", **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(
            phone_number=phone_number, email=email, password=password,
            name=name, auth_provider="local", **extra_fields,
        )


class User(AbstractBaseUser, PermissionsMixin):
    class AuthProvider(models.TextChoices):
        LOCAL = "local", "Local"
        GOOGLE = "google", "Google"

    # Internal-only, never shown to or chosen by the person.
    username = models.CharField(max_length=32, unique=True, editable=False)

    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    name = models.CharField(max_length=100, blank=True)
    auth_provider = models.CharField(
        max_length=10, choices=AuthProvider.choices, default=AuthProvider.LOCAL
    )

    # Optional account-linking: a Google-only user may explicitly opt in to
    # a backup password (Section 4.2).
    has_backup_password = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []  # phone/email handled explicitly by signup views, not createsuperuser prompts

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(phone_number__isnull=False) | models.Q(email__isnull=False),
                name="phone_or_email_required",
            )
        ]
        indexes = [
            models.Index(fields=["phone_number"]),
            models.Index(fields=["email"]),
        ]

    def __str__(self):
        return self.name or self.phone_number or self.email or str(self.pk)

    def set_backup_password(self, raw_password):
        """Explicit opt-in path for Google users adding phone+password login."""
        self.password = make_password(raw_password)
        self.has_backup_password = True
        self.save(update_fields=["password", "has_backup_password"])


class AuthAttemptLog(models.Model):
    """
    Append-only audit trail for every signup/login attempt (success or
    failure). Doubles as the data source for future rate-limiting /
    lockout enforcement (Section 4.4) — no schema change needed later.
    """

    class IdentifierType(models.TextChoices):
        PHONE = "phone", "Phone"
        EMAIL = "email", "Email"

    class AttemptType(models.TextChoices):
        SIGNUP = "signup", "Signup"
        LOGIN = "login", "Login"

    class AuthProvider(models.TextChoices):
        LOCAL = "local", "Local"
        GOOGLE = "google", "Google"

    class Status(models.TextChoices):
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"

    identifier = models.CharField(max_length=100)
    identifier_type = models.CharField(max_length=10, choices=IdentifierType.choices)
    ip_address = models.GenericIPAddressField()
    attempt_type = models.CharField(max_length=10, choices=AttemptType.choices)
    auth_provider = models.CharField(max_length=10, choices=AuthProvider.choices)
    status = models.CharField(max_length=10, choices=Status.choices)
    failure_reason = models.CharField(max_length=100, blank=True, null=True)
    user_agent = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["identifier", "timestamp"]),
            models.Index(fields=["ip_address", "timestamp"]),
        ]

    def __str__(self):
        return f"{self.attempt_type}/{self.status} — {self.identifier} @ {self.timestamp:%Y-%m-%d %H:%M}"