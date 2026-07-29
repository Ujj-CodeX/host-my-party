"""
ai app — Food Delivery provider adapter (Section 3.6, mirrors
dineout_provider.py). The AI Layer (Groq filtering in views.py) sits
ABOVE this adapter and consumes raw restaurant/menu data from it — Groq
ranking logic itself is not part of this layer, matching the same
separation dineout_provider.py already has (adapter = raw data + order
placement, AI ranking = layer above).


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

    @abstractmethod
    def get_avg_prep_time_minutes(self, restaurant_id):
        """Average prep/delivery time in minutes for a restaurant — used
        by late-arrival scheduling (Section 5.3.6) to compute fire_time.
        Returns None if the restaurant isn't found, so callers can apply
        their own fallback default."""


class MockFoodDeliveryProvider(FoodDeliveryProvider):
    def get_restaurants(self):
        return RESTAURANTS

    def get_avg_prep_time_minutes(self, restaurant_id):
        restaurant = next((r for r in RESTAURANTS if r["id"] == restaurant_id), None)
        return restaurant["deliveryMins"] if restaurant else None

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

    @abstractmethod
    def get_avg_prep_time_minutes(self, restaurant_id):
        """Average prep/delivery time in minutes for a restaurant — used
        by late-arrival scheduling (Section 5.3.6) to compute fire_time.
        Returns None if the restaurant isn't found, so callers can apply
        their own fallback default."""


class MockFoodDeliveryProvider(FoodDeliveryProvider):
    def get_restaurants(self):
        return RESTAURANTS

    def get_avg_prep_time_minutes(self, restaurant_id):
        restaurant = next((r for r in RESTAURANTS if r["id"] == restaurant_id), None)
        return restaurant["deliveryMins"] if restaurant else None

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