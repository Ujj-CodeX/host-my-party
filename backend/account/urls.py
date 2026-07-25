from django.urls import path

from . import views

urlpatterns = [
    path("auth/signup/phone/", views.signup_phone, name="signup-phone"),
    path("auth/login/phone/", views.login_phone, name="login-phone"),
    path("auth/google/", views.google_auth, name="google-auth"),
    path("auth/refresh/", views.refresh_token_view, name="token-refresh"),
    path("auth/logout/", views.logout_view, name="logout"),
    path("auth/profile/", views.update_profile, name="update-profile"),
]