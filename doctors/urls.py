"""
doctors/urls.py
==============================================
Maps URL paths to doctor-facing views.
==============================================
"""

from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.doctor_dashboard_view, name="doctor_dashboard_view"),
    path("appointment/<int:appointment_id>/update/", views.update_appointment_status_view, name="update_appointment_status_view"),
    path("hospital/<int:hospital_id>/", views.hospital_doctors_view, name="hospital_doctors_view"),
]