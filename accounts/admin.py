from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin import AdminSite
from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from django.template.response import TemplateResponse
from .models import User


class LibraryAdminSite(AdminSite):
    site_header = 'Library Management System'
    site_title = 'Library Admin'
    index_title = 'Administration'

    def has_permission(self, request):
        """
        Only allow admin users to access the admin panel.
        Students and faculty are blocked.
        """
        if not request.user.is_authenticated:
            return False
        
        # Superusers always have access
        if request.user.is_superuser:
            return True
        
        # Only users with ADMIN role can access
        return hasattr(request.user, 'role') and request.user.role == User.Role.ADMIN

    def login(self, request, extra_context=None):
        """
        Custom login that redirects non-admin users away from admin panel.
        """
        if request.user.is_authenticated:
            # If user is authenticated but not admin, redirect them away
            if not self.has_permission(request):
                from django.contrib import messages
                messages.error(request, 'You do not have permission to access the admin panel.')
                return redirect('/accounts/dashboard/')
        
        return super().login(request, extra_context)

    def admin_view(self, view, cacheable=False):
        """
        Override admin_view to add additional permission checks.
        """
        def inner(request, *args, **kwargs):
            if request.user.is_authenticated and not self.has_permission(request):
                from django.contrib import messages
                messages.error(request, 'Access denied. Admin privileges required.')
                return redirect('/accounts/dashboard/')
            return view(request, *args, **kwargs)
        
        return super().admin_view(inner, cacheable)


# Create custom admin site instance
admin_site = LibraryAdminSite(name='library_admin')


@admin.register(User, site=admin_site)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

    fieldsets = UserAdmin.fieldsets + (
        ('Library Info', {'fields': ('role', 'phone', 'address')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Library Info', {'fields': ('role', 'phone', 'address')}),
    )
