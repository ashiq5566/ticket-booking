from rest_framework import serializers
from bookings.models import Station


class StationsListSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Station
        fields = ('id', 'name', 'slug')