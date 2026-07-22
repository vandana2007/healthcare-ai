"""
hospitals/views.py
==============================================
Lets a patient type in their location (city/area) and see
all hospitals sorted by real distance, nearest first.
==============================================
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Hospital
from .services.geocoding_service import geocode_location, calculate_distance_km


@login_required
def hospital_search_view(request):
    """
    GET: shows the search form (empty results).
    POST: geocodes the typed location, calculates distance
    to every hospital, and shows them sorted nearest-first.
    """

    results = []
    searched_location = None

    if request.method == "POST":
        searched_location = request.POST.get("location", "").strip()

        if searched_location:
            # --------------------------------------------------
            # Step 1: Convert the typed location into coordinates
            # --------------------------------------------------
            patient_coords = geocode_location(searched_location)

            if patient_coords:
                # --------------------------------------------------
                # Step 2: Calculate distance to EVERY hospital
                # --------------------------------------------------
                all_hospitals = Hospital.objects.all()

                for hospital in all_hospitals:
                    hospital_coords = (hospital.latitude, hospital.longitude)
                    distance = calculate_distance_km(patient_coords, hospital_coords)
                    results.append({
                        "hospital": hospital,
                        "distance_km": distance,
                    })

                # --------------------------------------------------
                # Step 3: Sort nearest-first
                # --------------------------------------------------
                results.sort(key=lambda item: item["distance_km"])
            else:
                # Geocoding failed — location not recognized
                results = None

    context = {
        "results": results,
        "searched_location": searched_location,
    }
    return render(request, "hospital_search.html", context)