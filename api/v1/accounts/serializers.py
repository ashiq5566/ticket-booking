from rest_framework import serializers

from accounts.models import User


class PhoneSerializer(serializers.Serializer):
    country = serializers.CharField()
    phone = serializers.CharField()
    
class OTPSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=128)
    phone = serializers.CharField(max_length=16)
    otp = serializers.IntegerField()
    country = serializers.CharField()
    
class LoginOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=16)
    otp = serializers.IntegerField()
    country = serializers.CharField()