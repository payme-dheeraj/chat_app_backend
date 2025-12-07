from rest_framework import serializers
from .models import User, OTPVerification


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'display_name', 'user_type', 'mobile_number', 
                  'avatar', 'bio', 'is_online', 'last_seen', 'created_at']
        read_only_fields = ['id', 'created_at', 'is_online', 'last_seen']


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new users"""
    
    password = serializers.CharField(write_only=True, min_length=6)
    
    class Meta:
        model = User
        fields = ['username', 'password', 'mobile_number', 'display_name']
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value
    
    def validate_mobile_number(self, value):
        if value and User.objects.filter(mobile_number=value).exists():
            raise serializers.ValidationError("Mobile number already registered")
        return value


class LoginSerializer(serializers.Serializer):
    """Serializer for login"""
    
    username = serializers.CharField()
    password = serializers.CharField()


class SignupSerializer(serializers.Serializer):
    """Serializer for signup with CAPTCHA"""
    
    username = serializers.CharField(min_length=3, max_length=150)
    password = serializers.CharField(min_length=6, write_only=True)
    mobile_number = serializers.CharField(min_length=10, max_length=15)
    captcha_token = serializers.CharField(required=True)
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value
    
    def validate_mobile_number(self, value):
        if User.objects.filter(mobile_number=value).exists():
            raise serializers.ValidationError("Mobile number already registered")
        return value


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""
    
    class Meta:
        model = User
        fields = ['display_name', 'bio', 'avatar']


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password"""
    
    old_password = serializers.CharField()
    new_password = serializers.CharField(min_length=6)
