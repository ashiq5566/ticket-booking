from django.db import models
from general.models import WebBaseModel
from api.v1.general.functions import get_auto_id

STATUS = {
    ('pending', "Pending"),
    ('success', 'Success'),
    ('failed', 'Failed'),
}

class Station(WebBaseModel):
    name = models.CharField(max_length=128, null=True, blank=True)
    slug = models.CharField(max_length=128, null=True, blank=True)
    order_id = models.IntegerField()

    def save(self, *args, **kwargs):
        if self._state.adding:
            auto_id = get_auto_id(Station)
            self.auto_id = auto_id

        super(Station, self).save(*args, **kwargs)
    
    class Meta:
        db_table = 'bookings_station'
        verbose_name = 'station'
        verbose_name_plural = 'Stations'
        ordering = ('-name',)

    def __str__(self):
        return self.name


class Trip(WebBaseModel):
    start_point = models.ForeignKey(Station, on_delete=models.CASCADE, null=True, blank=True, related_name="starting_station")
    end_point = models.ForeignKey(Station, on_delete=models.CASCADE, null=True, blank=True, related_name="ending_station")
    amount = models.IntegerField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if self._state.adding:
            auto_id = get_auto_id(Trip)
            self.auto_id = auto_id

        super(Trip, self).save(*args, **kwargs)
    
    class Meta:
        db_table = 'bookings_trip'
        verbose_name = 'trip'
        verbose_name_plural = 'Trips'
        ordering = ('-start_point',)

    def __str__(self):
        return f"starting-{self.start_point.name} - ending-{self.end_point.name}"
    
    
class Booking(WebBaseModel):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    status = models.CharField(max_length=128, choices=STATUS, default="pending")
    
    def save(self, *args, **kwargs):
        if self._state.adding:
            auto_id = get_auto_id(Booking)
            self.auto_id = auto_id

        super(Booking, self).save(*args, **kwargs)
    
    class Meta:
        db_table = 'bookings_booking'
        verbose_name = 'booking'
        verbose_name_plural = 'Bookings'
        ordering = ('-user',)

    def __str__(self):
        return self.user.first_name