from django.contrib.auth.models import AbstractUser
from django.db import models
import random
import string


def generate_random_id():
    """Generate a random user ID like Anon12345"""
    return 'Anon' + ''.join(random.choices(string.digits, k=5))


def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))


class User(AbstractUser):
    """Custom User model with additional fields"""
    
    USER_TYPE_CHOICES = [
        ('anonymous', 'Anonymous'),
        ('registered', 'Registered'),
    ]
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='anonymous')
    display_name = models.CharField(max_length=100, blank=True)
    mobile_number = models.CharField(max_length=15, blank=True, null=True, unique=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.display_name:
            self.display_name = self.username
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.username


class OTPVerification(models.Model):
    """Store OTP for mobile verification"""
    
    mobile_number = models.CharField(max_length=15)
    otp = models.CharField(max_length=6)
    username = models.CharField(max_length=150)
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"OTP for {self.mobile_number}"
