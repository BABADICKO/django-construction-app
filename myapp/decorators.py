from django.core.exceptions import PermissionDenied
from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse

def role_required(allowed_roles):
    """
    Decorator to check if user has one of the allowed roles
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(reverse('login'))
                
            if not hasattr(request.user, 'customuser'):
                raise PermissionDenied
                
            user_role = request.user.customuser.get_role()
            if user_role in allowed_roles or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied
        return _wrapped_view
    return decorator

def admin_required(view_func):
    """
    Decorator for views that require admin access
    """
    return role_required(['Admin'])(view_func)

def project_manager_required(view_func):
    """
    Decorator for views that require project manager access
    """
    return role_required(['Admin', 'Project Manager'])(view_func)

def worker_or_above_required(view_func):
    """
    Decorator for views that require worker or higher access
    """
    return role_required(['Admin', 'Project Manager', 'Worker'])(view_func)
