from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect


def staff_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(), login_url="login")

        if not request.user.is_staff or request.user.is_superuser:
            return redirect("customer_dashboard")

        return view_func(request, *args, **kwargs)

    return wraps(view_func)(_wrapped_view)


def admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(), login_url="login")

        if not request.user.is_superuser:
            return redirect("dashboard")

        return view_func(request, *args, **kwargs)

    return wraps(view_func)(_wrapped_view)