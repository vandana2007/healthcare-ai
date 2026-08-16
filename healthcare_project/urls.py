"""
healthcare_project/urls.py
==============================================
The project's root URL configuration. Routes requests
to the correct app based on the URL path.
==============================================
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
# --------------------------------------------------
# Customize Django Admin branding to match our app
# --------------------------------------------------
admin.site.site_header = "AI Healthcare Assistant — Admin"
admin.site.site_title = "AI Healthcare Admin"
admin.site.index_title = "Welcome to the Healthcare Assistant Admin Panel"
urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("chat/", include("chatbot.urls")),
    path("appointments/", include("appointments.urls")),
    path("hospitals/", include("hospitals.urls")),
    path("doctors/", include("doctors.urls")),
    path("reminders/", include("reminders.urls")),
    path("reports/", include("reports.urls")),
]

# Serve uploaded media files (reports) during development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)