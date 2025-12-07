from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, OTPVerification


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'display_name', 'user_type', 'mobile_number', 'is_online', 'created_at']
    list_filter = ['user_type', 'is_online', 'created_at']
    search_fields = ['username', 'display_name', 'mobile_number']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'display_name', 'mobile_number', 'avatar', 'bio', 'is_online')}),
    )


@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ['mobile_number', 'username', 'otp', 'is_verified', 'attempts', 'created_at']
    list_filter = ['is_verified', 'created_at']
    search_fields = ['mobile_number', 'username']
