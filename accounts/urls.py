"""
accounts/urls.py
==============================================
Maps URL paths to authentication views.
==============================================
"""

from django.urls import path
from . import views

urlpatterns = [
    path("signup/", views.signup_view, name="signup_view"),
    path("login/", views.login_view, name="login_view"),
    path("logout/", views.logout_confirm_view, name="logout_confirm_view"),
    path("logout/process/", views.logout_process_view, name="logout_process_view"),
]