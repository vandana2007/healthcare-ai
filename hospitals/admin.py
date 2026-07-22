"""
hospitals/admin.py
==============================================
Registers Hospital with Django Admin, and auto-geocodes
the address into lat/long when a new hospital is saved —
so you never have to manually look up coordinates.
==============================================
"""

from django.contrib import admin
from django.contrib import messages
from .models import Hospital
from .services.geocoding_service import geocode_location


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "address", "latitude", "longitude")
    search_fields = ("name", "city", "address")

    # --------------------------------------------------
    # Hide latitude/longitude from the add/edit form —
    # they're calculated automatically, not typed manually.
    # --------------------------------------------------
    exclude = ("latitude", "longitude")

    def save_model(self, request, obj, form, change):
        """
        Called automatically by Django Admin whenever a
        Hospital is saved. We use this hook to auto-geocode
        the full address BEFORE saving to the database.
        """
        full_address = f"{obj.address}, {obj.city}"
        coordinates = geocode_location(full_address)

        if coordinates:
            obj.latitude, obj.longitude = coordinates
        else:
            messages.warning(
                request,
                f"Could not find coordinates for '{full_address}'. "
                "Hospital saved WITHOUT location data — nearby search won't find it."
            )
            obj.latitude, obj.longitude = 0.0, 0.0  # fallback placeholder

        super().save_model(request, obj, form, change)