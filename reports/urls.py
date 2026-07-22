"""
reports/urls.py
==============================================
Maps URL paths to report views.
==============================================
"""

from django.urls import path
from . import views

urlpatterns = [
    path("", views.report_list_view, name="report_list_view"),
    path("<int:report_id>/", views.report_detail_view, name="report_detail_view"),
    path("<int:report_id>/delete/", views.report_delete_view, name="report_delete_view"),
]