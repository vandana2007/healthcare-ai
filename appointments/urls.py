"""
appointments/urls.py
==============================================
Maps URL paths to appointment views, including 2 new
AJAX endpoints for dynamic doctor/slot loading.
==============================================
"""

from django.urls import path
from . import views

urlpatterns = [
    path("", views.appointment_list_view, name="appointment_list_view"),
    path("book/", views.book_appointment_view, name="book_appointment_view"),
    path("ajax/doctors/", views.get_doctors_for_hospital, name="get_doctors_for_hospital"),
    path("ajax/slots/", views.get_available_slots_view, name="get_available_slots_view"),
    path("<int:appointment_id>/edit/", views.appointment_edit_view, name="appointment_edit_view"),
    path("<int:appointment_id>/delete/", views.appointment_delete_view, name="appointment_delete_view"),
]