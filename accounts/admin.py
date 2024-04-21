from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, OtpRecord


class UserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password', 'is_deleted')}),
        ('Personal Info', {'fields': ('first_name', 'email', 'phone')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('username', 'first_name', 'email', 'phone', 'is_deleted')
admin.site.register(User, UserAdmin)


class OtpRecordAdmin(admin.ModelAdmin):
    # Define how user records are displayed in the admin interface
    list_display = ('phone', 'otp', 'attempts', 'is_applied', 'country')
    search_fields = ('phone', 'otp', 'country__name')

admin.site.register(OtpRecord, OtpRecordAdmin)