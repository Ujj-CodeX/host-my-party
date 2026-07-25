from django.urls import path
from . import views

urlpatterns = [
    path('restaurants/', views.get_restaurants),
    path('guest/restaurants/', views.guest_get_restaurants),
    path('schedule-late-order/', views.schedule_late_order),
    path('scheduled-orders/', views.get_scheduled_orders),
    path('budget-check/', views.budget_check),
    path('merge-check/', views.merge_check),
    path('plan-party/', views.plan_party),  # legacy, kept for compatibility
]