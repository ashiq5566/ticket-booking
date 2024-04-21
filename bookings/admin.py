from django.contrib import admin
from .models import Station, Trip, Booking

class StationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'is_deleted')
    search_fields = ('name', 'slug')

admin.site.register(Station, StationAdmin)


class TripAdmin(admin.ModelAdmin):
    list_display = ('id', 'start_point', 'end_point', 'amount', 'is_deleted')
    search_fields = ('start_point__name', 'end_point__name', 'amount')

admin.site.register(Trip, TripAdmin)



class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'trip', 'status', 'is_deleted')
    search_fields = ('start_point__name', 'end_point__name', 'amount')

admin.site.register(Booking, BookingAdmin)