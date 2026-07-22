"""
hospitals/services/geocoding_service.py
==============================================
ISOLATED geocoding logic. This is the ONLY file in the
whole project that talks to the geocoding provider
(currently Nominatim/OpenStreetMap, free & no API key).

If we ever switch providers later (e.g., to Google Maps
Geocoding API or LocationIQ for better reliability at
scale), we ONLY need to edit the two functions below —
nothing else in the project needs to change.
==============================================
"""

from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from django.conf import settings

# --------------------------------------------------
# Nominatim requires a descriptive User-Agent per their
# usage policy — using our app name identifies our traffic.
# --------------------------------------------------
geolocator = Nominatim(user_agent=settings.GEOCODING_USER_AGENT)


def geocode_location(location_text: str):
    """
    Converts a typed location (e.g., "Nellore" or
    "Nellore, Andhra Pradesh") into (latitude, longitude).

    Returns a tuple (lat, lon) or None if the location
    couldn't be found.
    """
    try:
        result = geolocator.geocode(location_text, timeout=10)
        if result:
            return (result.latitude, result.longitude)
        return None
    except Exception as e:
        print(f"[geocoding_service.py] Geocoding error: {e}")
        return None


def calculate_distance_km(point_a: tuple, point_b: tuple) -> float:
    """
    Calculates real-world distance in kilometers between
    two (latitude, longitude) points using the geodesic
    (great-circle) distance formula — accurate for Earth's
    curvature, unlike simple Pythagorean distance.
    """
    return round(geodesic(point_a, point_b).km, 2)