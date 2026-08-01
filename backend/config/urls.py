
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('account.urls')),
    path('api/', include('party.urls')),
    path('api/', include('order.urls')),
    path('api/ai/', include('ai.urls')), 

]
