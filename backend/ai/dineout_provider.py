"""
ai app — Dineout provider adapter (Section 3.6's adapter pattern, applied
specifically to Dineout).

WHY THIS FILE EXISTS:
Every other part of the codebase (views, future Celery tasks, etc.) should
call get_dineout_provider() and use whatever it returns — never import
mock_swiggy functions directly for Dineout. That's the whole point of an
adapter: today get_dineout_provider() returns MockDineoutProvider (backed
by static mock data); the day Swiggy Partner API / MCP credentials arrive,
it returns RealSwiggyDineoutProvider instead (backed by actual Swiggy MCP
tool calls) — and NOTHING above this file needs to change, because both
classes expose the exact same four methods.

The method names and shapes deliberately mirror the real Swiggy Dineout
MCP CLI (confirmed against Swiggy's own MCP server manifest):
    swiggy dineout search "<query>"
    swiggy dineout details <restaurant-id>
    swiggy dineout slots <restaurant-id> --date <date>
    swiggy dineout book <restaurant-id> --date --time --guests N --confirm
"""

from abc import ABC, abstractmethod

from .mock_swiggy import (
    book_dineout_table,
    check_dineout_slots,
    get_dineout_restaurants,
    get_restaurant_details,
)


class DineoutProvider(ABC):
    

    @abstractmethod
    def search_restaurants(self, guest_count, needs_veg=False, needs_jain=False,
                            max_distance_km=10.0):
        """Returns a list of restaurants that can seat guest_count people,
        filtered by dietary needs. Mirrors `swiggy dineout search`."""

    @abstractmethod
    def get_details(self, restaurant_id):
        """Returns full details for one restaurant. Mirrors `swiggy dineout details`."""

    @abstractmethod
    def check_slots(self, restaurant_id, date, guest_count):
        """Returns available time slots for a date + guest count. Mirrors
        `swiggy dineout slots`."""

    @abstractmethod
    def book_table(self, restaurant_id, date, time, guest_count, special_request=""):
        """Confirms a booking for a specific slot. Mirrors `swiggy dineout book --confirm`."""


class MockDineoutProvider(DineoutProvider):
    
    def search_restaurants(self, guest_count, needs_veg=False, needs_jain=False,
                            max_distance_km=10.0):
        return get_dineout_restaurants(
            guest_count, needs_veg=needs_veg, needs_jain=needs_jain,
            max_distance_km=max_distance_km,
        )

    def get_details(self, restaurant_id):
        return get_restaurant_details(restaurant_id)

    def check_slots(self, restaurant_id, date, guest_count):
        return check_dineout_slots(restaurant_id, date, guest_count)

    def book_table(self, restaurant_id, date, time, guest_count, special_request=""):
        return book_dineout_table(
            restaurant_id, date, time, guest_count, special_request=special_request,
        )




def get_dineout_provider() -> DineoutProvider:
    return MockDineoutProvider()