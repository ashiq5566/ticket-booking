import os
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Represents userprofile to store user basic details.
    """

    phone = models.CharField(max_length=20, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    email = models.EmailField(max_length=45, null=True,blank=True)
    encrypted_password = models.TextField(null=True, blank=True)
    country = models.ForeignKey('general.Country', on_delete=models.DO_NOTHING, null=True, blank=True)
    


class OtpRecord(models.Model):
    """
    Create OTP Record when user enters phone number
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date_added = models.DateTimeField(db_index=True,auto_now_add=True)
    date_updated = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    phone = models.CharField(max_length=16)
    otp = models.PositiveIntegerField()
    attempts = models.PositiveIntegerField(default=0)
    is_applied = models.BooleanField(default=False)
    country = models.ForeignKey('general.Country', on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = 'accounts_otp_record'
        verbose_name = ('Otp Record')
        verbose_name_plural = ('Otp Records')
        ordering = ('-date_added',)
        
    def __str__(self):
        return self.phone