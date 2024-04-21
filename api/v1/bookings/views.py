import requests
import json
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication

from django.utils import timezone
from accounts.models import User, OtpRecord
from general.models import Country
from bookings.models import Station, Trip, Booking
from .serializers import StationsListSerializer
# from general.encryption import encrypt, decrypt
# from api.v1.general.functions import generate_serializer_errors, randomnumber, generate_unique_id, random_password


class StationsListView(APIView):
    permission_class = [IsAuthenticated]
    def get(self, request):
        start_station = request.GET.get('start_station')
        try:
            stations = Station.objects.filter(is_deleted=False).order_by('order_id')
            
            if start_station:
                start_station_id = stations.get(slug=start_station).order_id
                end_station_order_ids = stations.exclude(slug=start_station).values_list('order_id', flat=True)
                ids = [s for s in end_station_order_ids if s > start_station_id]
                stations = stations.filter(order_id__in=ids)
            serializer = StationsListSerializer(stations, many=True, context={"request": request})
            response_data = {
                "StatusCode": 6000,
                "data": {
                    "title": "Success",
                    "data": serializer.data
                }
            }
        except Station.DoesNotExist:
            response_data = {
                "StatusCode": 6001,
                "data": {
                    "title": "Failed",
                    "message": "Station not found"
                }
            }
            
        return Response(response_data, status=status.HTTP_200_OK)
    

class BookTicketView(APIView):
    permission_class = [IsAuthenticated]
    def post(self, request):
        start_station = request.data.get('start_station')
        end_station = request.data.get('end_station')
        
        try:
            user = User.objects.get(pk=request.user.pk, is_deleted=False)
            trip = Trip.objects.get(start_point__slug=start_station, end_point__slug=end_station, is_deleted=False)

            booking = Booking.objects.create(
                user=user,
                trip=trip,
            )
            
            response_data = {
                "StatusCode": 6000,
                "data": {
                    "title": "Success",
                    "message": "Congratulation! Your booking is confirmed"
                }
            }
        except Trip.DoesNotExist:
            response_data = {
                "StatusCode": 6001,
                "data": {
                    "title": "Failed",
                    "message": "Trip not found"
                }
            }
            
        return Response(response_data, status=status.HTTP_201_CREATED)