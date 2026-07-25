"""
ai app — Food Delivery provider adapter (Section 3.6, mirrors
dineout_provider.py). The AI Layer (Groq filtering in views.py) sits
ABOVE this adapter and consumes raw restaurant/menu data from it — Groq
ranking logic itself is not part of this layer, matching the same
separation dineout_provider.py already has (adapter = raw data + order
placement, AI ranking = layer above).

Swap point: when real Swiggy Food MCP credentials arrive, write
RealSwiggyFoodDeliveryProvider(FoodDeliveryProvider) and change the
single line in get_food_delivery_provider(). Nothing above this file
changes.
"""

import secrets
from abc import ABC, abstractmethod

from .mock_swiggy import RESTAURANTS


class FoodDeliveryProvider(ABC):
    @abstractmethod
    def get_restaurants(self):
        """Raw restaurant+menu data — the AI Layer filters/ranks this,
        not this adapter."""

    @abstractmethod
    def place_order(self, restaurant_id, items, delivery_address=""):
        """Places an order with the restaurant. items is a list of
        {external_item_id, unit_price, quantity} dicts."""


class MockFoodDeliveryProvider(FoodDeliveryProvider):
    def get_restaurants(self):
        return RESTAURANTS

    def place_order(self, restaurant_id, items, delivery_address=""):
        restaurant = next((r for r in RESTAURANTS if r["id"] == restaurant_id), None)
        if restaurant is None:
            return {"success": False, "error": "restaurant_not_found"}

        item_total = sum(i["unit_price"] * i.get("quantity", 1) for i in items)
        return {
            "success": True,
            "order_reference": f"MOCK-FOOD-{restaurant_id}-{secrets.token_hex(4)}",
            "restaurant_id": restaurant_id,
            "restaurant_name": restaurant["name"],
            "item_total": item_total,
            "delivery_address": delivery_address,
            "status": "confirmed",
        }


def get_food_delivery_provider() -> FoodDeliveryProvider:
    return MockFoodDeliveryProvider()