from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect

def unauthenticated_only(view_func):
    """Для страниц входа/регистрации — только для неавторизованных"""
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/')
        return view_func(request, *args, **kwargs)
    return wrapper