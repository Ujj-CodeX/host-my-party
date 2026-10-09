from cryptography.fernet import Fernet
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def _fernet():
    key = getattr(settings, "SWIGGY_TOKEN_ENCRYPTION_KEY", "")

    if not key:
        raise ImproperlyConfigured(
            "SWIGGY_TOKEN_ENCRYPTION_KEY is not configured."
        )

    return Fernet(key.encode("ascii"))


def encrypt_secret(value: str) -> str:
    return _fernet().encrypt(value.encode("utf-8")).decode("ascii")


def decrypt_secret(ciphertext: str) -> str:
    return _fernet().decrypt(ciphertext.encode("ascii")).decode("utf-8")