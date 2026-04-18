"""
Middleware to block admin panel access for non-admin users.
"""
from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from .models import User


class AdminAccessMiddleware:
    """
    Middleware that blocks access to admin panel for non-admin users.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if user is trying to access admin panel
        if request.path.startswith('/admin/'):
            if request.user.is_authenticated:
                # If user is not admin or superuser, block access
                if not (request.user.is_superuser or 
                       (hasattr(request.user, 'role') and 
                        request.user.role == User.Role.ADMIN and 
                        request.user.is_staff)):
                    return redirect('/accounts/dashboard/')
            # If not authenticated, let Django handle the login redirect
        
        response = self.get_response(request)
        return response