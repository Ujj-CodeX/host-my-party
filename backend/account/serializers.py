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
 

 