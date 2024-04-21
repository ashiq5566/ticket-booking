from django.urls import path, re_path
from .views import StationsListView, BookTicketView

app_name = "api_v1_bookings"

urlpatterns = [
    re_path(r'^available-stations/$', StationsListView.as_view()),
    re_path(r'^book-ticket/$', BookTicketView.as_view()),
]