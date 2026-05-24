from django.urls import path
from . import views

urlpatterns = [
    # Legacy
    path('plan-party/', views.plan_party),

    # Feature 1 — Distance-based restaurant recommendations
    path('restaurants/', views.get_restaurants),

    # Feature 2 — Late arrival scheduling
    path('schedule-order/', views.schedule_late_order),
    path('scheduled-orders/', views.get_scheduled_orders),

    # Feature 3 — Budget guardian
    path('budget-check/', views.budget_check),

    # Feature 4 — Shared preference merger
    path('merge-check/', views.merge_check),
]