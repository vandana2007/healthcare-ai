"""
appointments/admin.py
==============================================
Registers Appointment with Django's admin panel.
Updated to reference the new 'doctor' ForeignKey instead
of the old free-text 'doctor_name' field.
==============================================
"""

from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("patient_name", "doctor", "appointment_date", "appointment_time", "status")
    list_filter = ("status", "doctor", "appointment_date")
    search_fields = ("patient_name", "reason")
    list_editable = ("status",)
    ordering = ("-created_at",)