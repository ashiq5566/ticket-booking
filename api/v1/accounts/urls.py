from django.urls import path, re_path, include
from django.views.decorators.csrf import csrf_exempt

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    
)
from .views import SignupPhoneView, SignupVerifyPhoneView, LoginPhoneView, LoginVerifyPhone, ResendOtpVIew


app_name = "api_v1_accounts"

urlpatterns = [   
    # register & login with otp
    re_path(r'^signup/phone/$', SignupPhoneView.as_view()),
    re_path(r'^signup/verify/phone/$', SignupVerifyPhoneView.as_view()),
    re_path(r'^login/phone/$', LoginPhoneView.as_view()),
    re_path(r'^login/verify/phone/$', LoginVerifyPhone.as_view()),
    re_path(r'^resend/otp/$', ResendOtpVIew.as_view()),


    #token authentication
    re_path(r"^token/$", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    re_path(r"^token/refresh/$", TokenRefreshView.as_view(), name="token_refresh"),

]