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
from .serializers import PhoneSerializer, OTPSerializer, LoginOTPSerializer
from general.encryption import encrypt, decrypt
from api.v1.general.functions import generate_serializer_errors, randomnumber, generate_unique_id, random_password


class SignupPhoneView(APIView):
    permission_class = [AllowAny]
    
    def post(self, request):
        serialized = PhoneSerializer(data=request.data)
        if not serialized.is_valid():
            return Response({
                "StatusCode": 6001,
                "data": {
                    "title": "Validation Error",
                    "message": generate_serializer_errors(serialized.errors)
                }
            }, status=status.HTTP_200_OK)
            
        country_code = request.data['country']
        phone = request.data['phone']

        try:
            country = Country.objects.get(country_code=country_code)
        except Country.DoesNotExist:
            return Response({
                "StatusCode": 6001,
                "data": {
                    "title": "Failed",
                    "message": "Service not available in this country"
                }
            }, status=status.HTTP_200_OK)

        if len(phone) != country.phone_number_length:
            return Response({
                "StatusCode": 6001,
                "data": {
                    "title": "Failed",
                    "message": "Invalid phone number"
                }
            }, status=status.HTTP_200_OK)

        # Check if profile already exists
        if User.objects.filter(country__country_code=country_code, phone=phone).exists():
            return Response({
                "StatusCode": 6001,
                "data": {
                    "title": "Failed",
                    "message": "User with this phone already exists."
                }
            }, status=status.HTTP_200_OK)

        # Generate OTP
        otp = randomnumber(4)
        phone_code = country.phone_code
        phone_with_code = f'+{phone_code}{phone}'

        try:
            otp_record = OtpRecord.objects.filter(phone=phone, country=country, is_applied=False).latest("date_added")
            if otp_record.attempts <= 3:
                new_otp_record = OtpRecord.objects.create(
                    country=country,
                    phone=phone,
                    otp=otp,
                )
                message = f"iLM : {new_otp_record.otp} is your verification code. Please do not reveal it to anyone."

                return Response({
                    "StatusCode": 6000,
                    "data": {
                        "title": "Success",
                        "message": "OTP sent successfully"
                    }
                }, status=status.HTTP_200_OK)
    
            else:
                time_limit = otp_record.date_updated + timezone.timedelta(minutes=15)
                if time_limit <= timezone.now():
                    otp = randomnumber(4)
                    new_otp_record = OtpRecord.objects.create(
                        country=country,
                        phone=phone,
                        otp=otp,
                    )
                    message = f"iLM : {new_otp_record.otp} is your verification code. Please do not reveal it to anyone."

                    return Response({
                        "StatusCode": 6000,
                        "data": {
                            "title": "Success",
                            "message": "OTP sent successfully"
                        }
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        "StatusCode": 6001,
                        "data": {
                            "title": "Failed",
                            "message": "You crossed the maximum limit of OTPs."
                        }
                    }, status=status.HTTP_200_OK)
        except OtpRecord.DoesNotExist:
            # Handle case where no OTP record exists yet for the phone
            message = f"iLM : {otp} is your verification code. Please do not reveal it to anyone."
            OtpRecord.objects.create(
                country=country,
                phone=phone,
                otp=otp,
            )

        return Response({
            "StatusCode": 6000,
            "data": {
                "title": "Success",
                "message": "OTP sent successfully"
            }
        }, status=status.HTTP_200_OK)
        
        
class SignupVerifyPhoneView(APIView):
    permission_class = [IsAuthenticated]
    # authentication_classes = [TokenAuthentication]
    def post(self, request):
        email = None
        serialized = OTPSerializer(data=request.data)

        if not serialized.is_valid():
            response_data = {
                "StatusCode": 6001,
                "data": {
                    "title": "Failed",
                    "message": generate_serializer_errors(serialized._errors)
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)

        name = request.data['name']
        phone = request.data['phone']
        otp = int(request.data['otp'])
        country_code = request.data['country']
        
        try:
            country = Country.objects.get(country_code=country_code)
        except Country.DoesNotExist:
            response_data = {
                "StatusCode": 6001,
                "data": {
                    "title": "Failed",
                    "message": "Service not available in this country"
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)

        try:
            otp_record = OtpRecord.objects.filter(phone=phone, country=country, is_applied=False).latest('date_added')

            if otp_record.attempts > 3:
                response_data = {
                    "StatusCode": 6001,
                    "data": {
                        "title": "Failed!",
                        "message": "You crossed the maximum limit of OTPs."
                    }
                }
            elif otp_record.otp == otp:
                # Update OTP record instance
                otp_record.is_applied = True
                otp_record.date_updated = timezone.now()
                otp_record.save()

                username = generate_unique_id(size=20)
                password = random_password(12)
                
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    country = country,
                    first_name=name,
                    phone=phone,
                    encrypted_password=encrypt(password),
    
                )

                headers = {
                    "Content-Type": "application/json"
                }

                decrypted_password = decrypt(user.encrypted_password)
                data = {
                    "username": user.username,
                    "password": decrypted_password,
                }

                protocol = "http://"
                if request.is_secure():
                    protocol = "https://"

                host = request.get_host()

                url = protocol + host + "/api/v1/accounts/token/"
                response = requests.post(url, headers=headers, data=json.dumps(data))
                print(response.text)  # Print response content for debugging

                if response.status_code == 200:
                    token, created = Token.objects.get_or_create(user=user)

                    response_data = {
                        "StatusCode": 6000,
                        "data": {
                            "title": "Success",
                            "message": "Phone number verified successfully",
                            "phone": phone,
                            "refresh_token" : response.json()["refresh"],
                            "access_token" : response.json()["access"],
                            "name" : user.first_name,
                            "phone" : user.phone
                        }
                    }
        
                else:
                    response_data = {
                        "StatusCode": 6001,
                        "data": {
                            "title": "Failed",
                            "message": "Failed to generate token"
                        }
                    }
            else:
                # Set attempts
                otp_record.attempts += 1
                otp_record.date_updated = timezone.now()
                otp_record.save()

                response_data = {
                    "StatusCode": 6001,
                    "data": {
                        "title": "Failed!",
                        "message": "Invalid OTP."
                    }
                }
        except OtpRecord.DoesNotExist:
            response_data = {
                "StatusCode": 6001,
                "data": {
                    "title": "Failed!",
                    "message": "OTP Record not found."
                }
            }
        except Exception as e:
            response_data = {
                "StatusCode": 6001,
                "data": {
                    "title": "Failed!",
                    "message": str(e)  # Provide a more informative error message
                }
            }

        return Response(response_data, status=status.HTTP_200_OK)
    

class LoginPhoneView(APIView):
    def post(self, request):
        serialized = PhoneSerializer(data=request.data)
        if serialized.is_valid():
            
            country_code = request.data['country']
            phone = request.data['phone']
            
            # Check if profile already exists
            if not User.objects.filter(country__country_code=country_code, phone=phone, is_deleted=False).exists():
                return Response({
                    "StatusCode": 6001,
                    "data": {
                        "title": "Failed",
                        "message": "User with this phone not regsitered."
                    }
                }, status=status.HTTP_200_OK)

            try:
                country = Country.objects.get(country_code=country_code)
            except Country.DoesNotExist:
                return Response({
                    "StatusCode": 6001,
                    "data": {
                        "title": "Failed",
                        "message": "Service not available in this country"
                    }
                }, status=status.HTTP_200_OK)

            if len(phone) != country.phone_number_length:
                return Response({
                    "StatusCode": 6001,
                    "data": {
                        "title": "Failed",
                        "message": "Invalid phone number"
                    }
                }, status=status.HTTP_200_OK)

            # Generate OTP
            otp = randomnumber(4)
            phone_code = country.phone_code
            phone_with_code = f'+{phone_code}{phone}'

            try:
                otp_record = OtpRecord.objects.filter(phone=phone, country=country, is_applied=False).latest("date_added")
                if otp_record.attempts <= 3:

                    new_otp_record = OtpRecord.objects.create(
                        country=country,
                        phone=phone,
                        otp=otp,
                    )
                    message = f"iLM : {new_otp_record.otp} is your verification code. Please do not reveal it to anyone."

                    return Response({
                        "StatusCode": 6000,
                        "data": {
                            "title": "Success",
                            "message": "OTP send successfully"
                        }
                    }, status=status.HTTP_200_OK)
        
                else:
                    time_limit = otp_record.date_updated + timezone.timedelta(minutes=15)
                    if time_limit <= timezone.now():
                        otp = randomnumber(4)
                        new_otp_record = OtpRecord.objects.create(
                            country=country,
                            phone=phone,
                            otp=otp,
                        )
                        message = f"iLM : {new_otp_record.otp} is your verification code. Please do not reveal it to anyone."

                    else:
                        return Response({
                            "StatusCode": 6001,
                            "data": {
                                "title": "Failed",
                                "message": "You crossed the maximum limit of OTPs."
                            }
                        }, status=status.HTTP_200_OK)
            except OtpRecord.DoesNotExist:
                message = f"iLM : {otp} is your verification code. Please do not reveal it to anyone."

                OtpRecord.objects.create(
                    country=country,
                    phone=phone,
                    otp=otp,
                )

            return Response({
                "StatusCode": 6000,
                "data": {
                    "title": "Success",
                    "message": "OTP send successfully"
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "StatusCode": 6001,
                "data": {
                    "title": "Validation Error",
                    "message": generate_serializer_errors(serialized._errors)
                }
            }, status=status.HTTP_200_OK)
            

class LoginVerifyPhone(APIView):
    def post(self, request):
        serialized = LoginOTPSerializer(data=request.data)

        if not serialized.is_valid():
            response_data = {
                "StatusCode": 6001,
                "data": {
                    "title": "Failed",
                    "message": generate_serializer_errors(serialized._errors)
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)

        phone = request.data['phone']
        otp = int(request.data['otp'])
        country_code = request.data['country']

        try:
            country = Country.objects.get(country_code=country_code)
        except Country.DoesNotExist:
            response_data = {
                "StatusCode": 6001,
                "data": {
                    "title": "Failed",
                    "message": "Service not available in this country"
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)

        try:
            # Verification for test account of playstore
            if phone == "1234567890":
                otp_record = OtpRecord.objects.filter(phone=phone, country=country, is_applied=True).latest('date_added')
            else:
                otp_record = OtpRecord.objects.filter(phone=phone, country=country, is_applied=False).latest('date_added')

            if otp_record.attempts > 3:
                response_data = {
                    "StatusCode": 6001,
                    "data": {
                        "title": "Failed!",
                        "message": "You crossed the maximum limit of OTPs."
                    }
                }
            elif otp_record.otp == otp:
                # Update OTP record instance
                otp_record.is_applied = True
                otp_record.date_updated = timezone.now()
                otp_record.save()
                if User.objects.filter(country=country, phone=phone).exists():
                    user = User.objects.get(country=country, phone=phone)            

                    headers = {
                        "Content-Type": "application/json"
                    }

                    decrypted_password = decrypt(user.encrypted_password)

                    data = {
                        "username": user.username,
                        "password": decrypted_password,
                    }

                    protocol = "http://"
                    if request.is_secure():
                        protocol = "https://"

                    host = request.get_host()

                    url = protocol + host + "/api/v1/accounts/token/"
                    response = requests.post(url, headers=headers, data=json.dumps(data))

                    if response.status_code == 200:

                        token, created = Token.objects.get_or_create(user=user)

                        response_data = {
                            "StatusCode": 6000,
                            "data": {
                                "title": "Success",
                                "message": "Phone number verified successfully",
                                "phone": phone,
                                "refresh_token" : response.json()["refresh"],
                                "access_token" : response.json()["access"],
                                "name" : user.first_name,
                                "phone" : user.phone
                            }
                        }
                    else:
                        response_data = {
                            "StatusCode": 6001,
                            "data": {
                                "title": "Failed",
                                "message": "Failed to generate token"
                            }
                        }
            else:
                # Set attempts
                otp_record.attempts += 1
                otp_record.date_updated = timezone.now()
                otp_record.save()

                response_data = {
                    "StatusCode": 6001,
                    "data": {
                        "title": "Failed!",
                        "message": "Invalid OTP."
                    }
                }
        except OtpRecord.DoesNotExist:
            response_data = {
                "StatusCode": 6001,
                "data": {
                    "title": "Failed!",
                    "message": "OTP Record not found."
                }
            }
        except Exception as e:
            response_data = {
                "StatusCode": 6001,
                "data": {
                    "title": "Failed!",
                    "message": str(e)  # Provide a more informative error message
                }
            }

        return Response(response_data, status=status.HTTP_200_OK)
    

class ResendOtpVIew(APIView):
    def post(self, request):
        serialized = PhoneSerializer(data=request.data)

        if not serialized.is_valid():
            response_data = {
                "StatusCode": 6001,
                "data": {
                    "title": "Validation Error",
                    "message": generate_serializer_errors(serialized.errors)
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        country_code = request.data['country']
        phone = request.data['phone']

        try:
            country = Country.objects.get(country_code=country_code)
            phone_code = country.phone_code
        except Country.DoesNotExist:
            response_data = {
                "StatusCode": 6001,
                "data": {
                    "title": "Failed",
                    "message": "Service not available in selected Country."
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)

        otp_record = OtpRecord.objects.filter(
            phone=phone,
            country=country,
            is_applied=False,
            is_deleted=False
        ).order_by('-date_added').first()

        if not otp_record:
            response_data = {
                "StatusCode": 6001,
                "data": {
                    "title": "OTP not exists",
                    "message": "Please try again"
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        if otp_record.attempts > 3:
            time_limit = otp_record.date_updated + timezone.timedelta(seconds=30)
            if time_limit <= timezone.now():
                otp = randomnumber(4)
                OtpRecord.objects.create(
                    country=country,
                    phone=phone,
                    otp=otp,
                )
                message = "iLM : %s is your verification code. Please do not reveal it to anyone." % (otp)
            
                response_data = {
                    "StatusCode": 6000,
                    "data": {
                        "title": "Success",
                        "message": "successful",
                        "phone": phone,
                    }
                }
            else:
                response_data = {
                    "StatusCode": 6001,
                    "data": {
                        "title": "Failed!",
                        "message": "You crossed the maximum limit of OTPs."
                    }
                }
        else:
            otp_record.date_updated = timezone.now()
            otp_record.save()

            message = "iLM : %s is your verification code. Please do not reveal it to anyone." % (otp_record.otp)

            response_data = {
                "StatusCode": 6000,
                "data": {
                    "title": "Success",
                    "message": "successful",
                    "phone": phone,
                }
            }
        return Response(response_data, status=status.HTTP_200_OK)