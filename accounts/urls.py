from django.urls import path
from . import views

urlpatterns = [
    path("signup/", views.signup_view, name="signup_view"),
    path("login/", views.login_view, name="login_view"),
    path("logout/", views.logout_confirm_view, name="logout_confirm_view"),
    path("logout/process/", views.logout_process_view, name="logout_process_view"),
    path("profile/", views.profile_view, name="profile_view"),
    path("profile/change-password/", views.change_password_view, name="change_password_view"),
]