from django.urls import path
from . import views

urlpatterns = [
    path('plan-party/', views.plan_party),

]