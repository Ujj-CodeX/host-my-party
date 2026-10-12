
from abc import ABC, abstractmethod
from copy import deepcopy
import secrets

from django.core.cache import cache
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


MOCK_ADDRESS_CACHE_TTL = 30 * 24 * 60 * 60


class AddressProviderError(Exception):
    """Raised when the address provider cannot complete an operation."""


class SwiggyAddressProvider(ABC):

    requires_swiggy_auth = True

    @abstractmethod
    def get_addresses(self, user):
        """Return saved addresses belonging to the host."""

    @abstractmethod
    def create_address(self, user, address_data):
        """Create and return a normalized address representation."""


class MockSwiggyAddressProvider(SwiggyAddressProvider):
    """Development-only provider. It does not call live Swiggy MCP."""

    requires_swiggy_auth = False

    def _cache_key(self, user):
        return f"mock-swiggy-addresses:v1:{user.pk}"

    def get_addresses(self, user):
        key = self._cache_key(user)
        addresses = cache.get(key)

        if addresses is None:
            addresses = [
                {
                    "address_id": f"mock-{user.pk}-home",
                    "label": "Demo Home",
                    "formatted_address": (
                        "Mock saved address — development only"
                    ),
                    "city": "Demo City",
                    "state": "Demo State",
                    "postal_code": "000000",
                    "latitude": None,
                    "longitude": None,
                },
                {
                    "address_id": f"mock-{user.pk}-work",
                    "label": "Demo Work",
                    "formatted_address": (
                        "Mock work address — development only"
                    ),
                    "city": "Demo City",
                    "state": "Demo State",
                    "postal_code": "000000",
                    "latitude": None,
                    "longitude": None,
                },
            ]

            cache.set(
                key,
                addresses,
                timeout=MOCK_ADDRESS_CACHE_TTL,
            )

        return deepcopy(addresses)

    def create_address(self, user, address_data):
        addresses = self.get_addresses(user)

        address_parts = [
            address_data.get("address_line1", ""),
            address_data.get("address_line2", ""),
            address_data.get("landmark", ""),
            address_data.get("city", ""),
            address_data.get("state", ""),
            address_data.get("postal_code", ""),
        ]

        formatted_address = ", ".join(
            part.strip()
            for part in address_parts
            if isinstance(part, str) and part.strip()
        )

        address = {
            **address_data,
            "address_id": (
                f"mock-{user.pk}-{secrets.token_hex(6)}"
            ),
            "formatted_address": formatted_address,
        }

        addresses.append(address)

        cache.set(
            self._cache_key(user),
            addresses,
            timeout=MOCK_ADDRESS_CACHE_TTL,
        )

        return deepcopy(address)

def get_swiggy_address_provider() -> SwiggyAddressProvider:
    if not settings.DEBUG:
        raise ImproperlyConfigured(
            "Mock address provider is development-only. "
            "Configure the real provider before production use."
        )

    return MockSwiggyAddressProvider()