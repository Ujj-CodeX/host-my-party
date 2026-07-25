from django.urls import path

from . import views

urlpatterns = [
    path("parties/<str:party_code>/orders/", views.OrderListCreateView.as_view(), name="order-list-create"),
    path("parties/<str:party_code>/orders/<int:pk>/", views.OrderDetailView.as_view(), name="order-detail"),
    path("parties/<str:party_code>/booking/", views.BookingDetailView.as_view(), name="booking-detail"),
    path("guest/orders/", views.GuestOrderCreateView.as_view(), name="guest-order-create"),
]