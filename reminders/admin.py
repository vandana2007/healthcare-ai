"""
reminders/admin.py
==============================================
Registers Reminder with Django Admin.
Updated to reference 'times' instead of the old
single 'reminder_time' field.
==============================================
"""

from django.contrib import admin
from .models import Reminder


@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = ("medicine_name", "user", "times", "frequency", "is_active")
    list_filter = ("frequency", "is_active")
    search_fields = ("medicine_name", "user__username")
    ordering = ("medicine_name",)