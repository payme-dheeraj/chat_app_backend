from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
import requests
import os
from .models import User, generate_random_id
from .serializers import (
    UserSerializer, LoginSerializer, SignupSerializer, 
    ProfileUpdateSerializer, ChangePasswordSerializer
)


def verify_recaptcha(token):
    """Verify reCAPTCHA token with Google"""
    secret_key = os.getenv('RECAPTCHA_SECRET_KEY', '')
    
    # For development, if no secret key is set, skip verification
    if not secret_key or secret_key == 'your-recaptcha-secret-key':
        return True
    
    try:
        response = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data={
                'secret': secret_key,
                'response': token
            },
            timeout=5
        )
        result = response.json()
        return result.get('success', False)
    except Exception:
        # If verification fails, allow in development
        return settings.DEBUG


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """Session authentication without CSRF enforcement for API"""
    def enforce_csrf(self, request):
        return  # Skip CSRF check


@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([AllowAny])
def generate_anonymous_user(request):
    """Generate a random anonymous user"""
    username = generate_random_id()
    
    # Ensure unique username
    while User.objects.filter(username=username).exists():
        username = generate_random_id()
    
    user = User.objects.create(
        username=username,
        display_name=username,
        user_type='anonymous',
    )
    user.set_unusable_password()
    user.save()
    
    # Log in the user
    login(request, user)
    
    return Response({
        'success': True,
        'message': 'Anonymous user created',
        'user': UserSerializer(user).data
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([AllowAny])
def user_login(request):
    """Login with username and password"""
    serializer = LoginSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(
        request,
        username=serializer.validated_data['username'],
        password=serializer.validated_data['password']
    )
    
    if user is not None:
        login(request, user)
        user.is_online = True
        user.save()
        
        return Response({
            'success': True,
            'message': 'Login successful',
            'user': UserSerializer(user).data
        })
    
    return Response({
        'success': False,
        'message': 'Invalid username or password'
    }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([AllowAny])
def user_signup(request):
    """Signup with username, password, and CAPTCHA verification"""
    serializer = SignupSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    
    # Verify CAPTCHA
    if not verify_recaptcha(data['captcha_token']):
        return Response({
            'success': False,
            'message': 'CAPTCHA verification failed. Please try again.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Create user directly
    user = User.objects.create_user(
        username=data['username'],
        password=data['password'],
        mobile_number=data['mobile_number'],
        display_name=data['username'],
        user_type='registered'
    )
    
    # Log in the user
    login(request, user)
    
    return Response({
        'success': True,
        'message': 'Account created successfully',
        'user': UserSerializer(user).data
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_recaptcha_site_key(request):
    """Get reCAPTCHA site key for frontend"""
    site_key = os.getenv('RECAPTCHA_SITE_KEY', '')
    return Response({
        'site_key': site_key,
        'enabled': bool(site_key and site_key != 'your-recaptcha-site-key')
    })


@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated])
def user_logout(request):
    """Logout user"""
    request.user.is_online = False
    request.user.save()
    logout(request)
    
    return Response({
        'success': True,
        'message': 'Logged out successfully'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    """Get current user profile"""
    return Response({
        'success': True,
        'user': UserSerializer(request.user).data
    })


@api_view(['PUT', 'PATCH'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """Update user profile"""
    serializer = ProfileUpdateSerializer(request.user, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response({
            'success': True,
            'message': 'Profile updated',
            'user': UserSerializer(request.user).data
        })
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Change user password"""
    serializer = ChangePasswordSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    
    if not request.user.check_password(data['old_password']):
        return Response({
            'success': False,
            'message': 'Current password is incorrect'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    request.user.set_password(data['new_password'])
    request.user.save()
    
    return Response({
        'success': True,
        'message': 'Password changed successfully'
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def check_auth(request):
    """Check if user is authenticated"""
    if request.user.is_authenticated:
        return Response({
            'authenticated': True,
            'user': UserSerializer(request.user).data
        })
    return Response({
        'authenticated': False
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_users(request):
    """Search users by username"""
    query = request.GET.get('q', '')
    
    if len(query) < 2:
        return Response({
            'success': True,
            'users': []
        })
    
    users = User.objects.filter(
        username__icontains=query
    ).exclude(id=request.user.id)[:20]
    
    return Response({
        'success': True,
        'users': UserSerializer(users, many=True).data
    })
