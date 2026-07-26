from django.urls import path
from . import views

urlpatterns = [
    path('restaurants/', views.get_restaurants),
    path('guest/restaurants/', views.guest_get_restaurants),
    path('schedule-late-order/', views.schedule_late_order),
    path('scheduled-orders/', views.get_scheduled_orders),
    path('budget-check/', views.budget_check),
    path('merge-check/', views.merge_check),
    path('dineout/restaurants/', views.dineout_restaurants),
    path('dineout/slots/', views.dineout_slots),
    path('dineout/book/', views.dineout_book),
    path('plan-party/', views.plan_party),  # legacy, kept for compatibility
    path('whole-sum-optimize/', views.whole_sum_optimize),
]