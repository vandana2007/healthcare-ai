"""
hospitals/urls.py
==============================================
Maps URL paths to hospital search views.
==============================================
"""

from django.urls import path
from . import views

urlpatterns = [
    path("", views.hospital_search_view, name="hospital_search_view"),
]