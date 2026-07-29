"""
accounts app — DRF serializers.

"""

from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):

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
# ---------------------------------------------------------------------------

class PhoneSignupSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    password = serializers.CharField(min_length=8, write_only=True)
    name = serializers.CharField(max_length=100)

    def validate_phone_number(self, value):
        
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError(
                "An account with this phone number already exists."
            )
        return value


class PhoneLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    password = serializers.CharField(write_only=True)
    

class ProfileUpdateSerializer(serializers.ModelSerializer):
    

    backup_password = serializers.CharField(
        write_only=True, required=False, min_length=8
    )

    class Meta:
        model = User
        fields = ["name", "phone_number", "backup_password"]

    def validate_phone_number(self, value):
        
        if User.objects.filter(phone_number=value).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError("This phone number is already in use.")
        return value

    def update(self, instance, validated_data):
        backup_password = validated_data.pop("backup_password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if backup_password:
            
            instance.set_backup_password(backup_password)

        return instance