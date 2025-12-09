from rest_framework.authentication import SessionAuthentication
from django.utils.deprecation import MiddlewareMixin


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """Session authentication without CSRF enforcement for API"""
    
    def enforce_csrf(self, request):
        return  # Skip CSRF check


class DisableCSRFForAPI(MiddlewareMixin):
    """Middleware to disable CSRF for API endpoints"""
    
    def process_request(self, request):
        if request.path.startswith('/api/'):
            setattr(request, '_dont_enforce_csrf_checks', True)
