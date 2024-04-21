
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/accounts/', include('api.v1.accounts.urls')),
    path('api/v1/bookings/', include('api.v1.bookings.urls')),
   
]