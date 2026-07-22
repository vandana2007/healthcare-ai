"""
chatbot/urls.py
==============================================
Maps URL paths to view functions for the chatbot app.
==============================================
"""

from django.urls import path
from . import views

urlpatterns = [
    path("", views.chat_view, name="chat_view"),
]