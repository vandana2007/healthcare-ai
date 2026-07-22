"""
hospitals/models.py
==============================================
Defines the Hospital table. Each hospital has a name,
address, city, and geographic coordinates (used to
calculate distance from a patient's searched location).
==============================================
"""

from django.db import models


class Hospital(models.Model):
    name = models.CharField(
        max_length=200,
        help_text="Official name of the hospital/clinic."
    )
    address = models.CharField(
        max_length=300,
        help_text="Street address."
    )
    city = models.CharField(
        max_length=100,
        help_text="City the hospital is located in."
    )

    # --------------------------------------------------
    # Coordinates — set ONCE when the hospital is added
    # (via geocoding the address), used later to calculate
    # distance from a patient's searched location.
    # --------------------------------------------------
    latitude = models.FloatField(
        help_text="Latitude coordinate (auto-filled via geocoding)."
    )
    longitude = models.FloatField(
        help_text="Longitude coordinate (auto-filled via geocoding)."
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Hospital"
        verbose_name_plural = "Hospitals"

    def __str__(self):
        return f"{self.name} ({self.city})"