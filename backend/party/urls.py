from django.urls import path

from . import views

urlpatterns = [
    path("parties/", views.PartyListCreateView.as_view(), name="party-list-create"),
    path("parties/<str:party_code>/", views.PartyDetailView.as_view(), name="party-detail"),
    path("parties/<str:party_code>/guests/", views.GuestListCreateView.as_view(), name="guest-list-create"),
    path("parties/<str:party_code>/guests/<int:pk>/", views.GuestDetailView.as_view(), name="guest-detail"),
    # Deliberately NOT under parties/<code>/ — this is the public join
    # link a host shares (e.g. https://app.com/join/XJ9K2A), so it reads
    # as its own top-level path, not nested under the host-only prefix.
    path("join/<str:party_code>/", views.join_party, name="join-party"),
]