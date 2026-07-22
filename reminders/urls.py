"""
reminders/urls.py
==============================================
Maps URL paths to reminder views, including the JSON
endpoint that powers browser notifications.
==============================================
"""

from django.urls import path
from . import views

urlpatterns = [
    path("", views.reminder_list_view, name="reminder_list_view"),
    path("<int:reminder_id>/toggle/", views.reminder_toggle_view, name="reminder_toggle_view"),
    path("<int:reminder_id>/delete/", views.reminder_delete_view, name="reminder_delete_view"),
    path("ajax/active-times/", views.active_reminder_times_view, name="active_reminder_times_view"),
]