"""
accounts app — DRF serializers.

Only display-facing model serializers live here. Signup/login request and
response serializers (phone+password payload, Google ID-token payload, etc.)
belong with the auth endpoints themselves, since they represent actions
rather than this model's stored shape.
"""

from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Full, public-safe representation of a User — never includes the
    password hash (it isn't a model field DRF would auto-include, but
    called out here deliberately as a reminder)."""

    class Meta:
        model = User
        fields = [
            "id",
            "name",
            "phone_number",
            "email",
            "auth_provider",
            "has_backup_password",
            "date_joined",
        ]
        read_only_fields = fields  # display-only; profile updates get their own serializer with auth endpoints


class UserSummarySerializer(serializers.ModelSerializer):
    """Minimal nested representation — used when a User is embedded inside
    another object (e.g. Party.host) so we don't leak more than needed."""

    class Meta:
        model = User
        fields = ["id", "name"]
        read_only_fields = fields


# ---------------------------------------------------------------------------
# Action serializers — request-shape validation for the auth endpoints.
# These aren't ModelSerializers because they don't map 1:1 to a stored
# row: signup validates a password before hashing it, login validates
# credentials against an existing row rather than creating one.
# ---------------------------------------------------------------------------

class PhoneSignupSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    password = serializers.CharField(min_length=8, write_only=True)
    name = serializers.CharField(max_length=100)

    def validate_phone_number(self, value):
        # Checked here (not just relying on the DB's unique constraint) so
        # the view gets a clean validation error instead of having to
        # catch an IntegrityError after attempting the insert.
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError(
                "An account with this phone number already exists."
            )
        return value


class PhoneLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    password = serializers.CharField(write_only=True)
    # Deliberately NO validate_phone_number check for existence here —
    # unlike signup, login must not reveal via a validation error whether
    # a phone number is registered. That check happens in the view, where
    # a wrong phone and a wrong password produce the exact same generic
    # error message.


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Handles two distinct updates (Section 4.2):
    - A Google-signup user adding a phone number at checkout time.
    - A Google-only user opting in to a backup password for phone+password
      login as a fallback.
    backup_password is write_only and never round-trips in a GET — it's
    an action ("set/replace my backup password"), not stored data to display.
    """

    backup_password = serializers.CharField(
        write_only=True, required=False, min_length=8
    )

    class Meta:
        model = User
        fields = ["name", "phone_number", "backup_password"]

    def validate_phone_number(self, value):
        # exclude=self.instance.pk so a user PATCHing their own unchanged
        # phone number doesn't trip the uniqueness check against themselves.
        if User.objects.filter(phone_number=value).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError("This phone number is already in use.")
        return value

    def update(self, instance, validated_data):
        backup_password = validated_data.pop("backup_password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if backup_password:
            # set_backup_password() (on the User model) hashes the
            # password AND flips has_backup_password=True in one place —
            # calling it here instead of setting instance.password
            # directly means that flag can never drift out of sync with
            # whether a usable password actually exists.
            instance.set_backup_password(backup_password)

        return instance