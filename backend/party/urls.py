from django.urls import path

from . import views

urlpatterns = [
    path("parties/", views.PartyListCreateView.as_view(), name="party-list-create"),
    path("parties/<str:party_code>/", views.PartyDetailView.as_view(), name="party-detail"),
    path("parties/<str:party_code>/guests/", views.GuestListCreateView.as_view(), name="guest-list-create"),
    path("parties/<str:party_code>/guests/<int:pk>/", views.GuestDetailView.as_view(), name="guest-detail"),
]