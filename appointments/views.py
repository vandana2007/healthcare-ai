"""
appointments/views.py
==============================================
Patient-facing appointment booking, editing, and management.
Features:
- Hospital -> Specialization -> Doctor selection
- Auto-calculated available time slots (AJAX endpoints)
- Full editing support (patient name, hospital, doctor, date, time, reason)
- Full ownership/privacy enforcement (patients only see their own)
- Database-level conflict protection via IntegrityError handling
==============================================
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import IntegrityError
from datetime import datetime

from .models import Appointment
from doctors.models import Doctor
from hospitals.models import Hospital
from .services.slot_service import get_available_slots


@login_required
def appointment_list_view(request):
    """
    Shows this patient's appointments AND the booking form.
    Pre-fills hospital/doctor if arriving from a "Book Appointment"
    link on a specific doctor's card (via ?hospital=X&doctor=Y).
    """
    appointments = Appointment.objects.filter(user=request.user)
    hospitals = Hospital.objects.all()

    # --------------------------------------------------
    # Pre-selection support: read optional query params
    # --------------------------------------------------
    preselected_hospital_id = request.GET.get("hospital")
    preselected_doctor_id = request.GET.get("doctor")

    context = {
        "appointments": appointments,
        "hospitals": hospitals,
        "preselected_hospital_id": preselected_hospital_id,
        "preselected_doctor_id": preselected_doctor_id,
    }
    return render(request, "appointment.html", context)


def get_doctors_for_hospital(request):
    """
    AJAX endpoint: given a hospital_id, returns JSON list of
    active doctors there (id, name, specialization) — used to
    populate the doctor dropdown dynamically after hospital
    selection, without a full page reload.
    """
    hospital_id = request.GET.get("hospital_id")
    doctors = Doctor.objects.filter(hospital_id=hospital_id, is_active=True)

    data = [
        {
            "id": doc.id,
            "label": f"Dr. {doc.full_name} — {doc.get_specialization_display()}",
        }
        for doc in doctors
    ]
    return JsonResponse({"doctors": data})


def get_available_slots_view(request):
    """
    AJAX endpoint: given a doctor_id and date, returns JSON
    list of genuinely available time slots — used to populate
    the time dropdown after doctor + date are chosen.

    exclude_appointment_id (optional): when editing an existing
    appointment, its own current slot is excluded from the
    "booked" check so it doesn't incorrectly appear as taken.
    """
    doctor_id = request.GET.get("doctor_id")
    date_str = request.GET.get("date")
    exclude_id = request.GET.get("exclude_appointment_id")

    try:
        doctor = Doctor.objects.get(id=doctor_id)
        appointment_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        slots = get_available_slots(doctor, appointment_date, exclude_appointment_id=exclude_id)
        return JsonResponse({"slots": slots})
    except (Doctor.DoesNotExist, ValueError):
        return JsonResponse({"slots": [], "error": "Invalid doctor or date."})


@login_required
def book_appointment_view(request):
    """
    Handles the actual booking submission.
    """
    if request.method == "POST":
        patient_name = request.POST.get("patient_name", "").strip()
        doctor_id = request.POST.get("doctor")
        appointment_date = request.POST.get("appointment_date")
        appointment_time = request.POST.get("appointment_time")
        reason = request.POST.get("reason", "").strip()

        if not all([patient_name, doctor_id, appointment_date, appointment_time, reason]):
            messages.error(request, "Please fill in all fields.")
            return redirect("appointment_list_view")

        doctor = get_object_or_404(Doctor, id=doctor_id)

        try:
            Appointment.objects.create(
                user=request.user,
                doctor=doctor,
                patient_name=patient_name,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                reason=reason,
            )
            messages.success(request, "Appointment booked successfully!")
        except IntegrityError:
            # --------------------------------------------------
            # This fires if our database constraint catches a
            # conflict (e.g., two tabs booking the same slot
            # at the exact same moment — a race condition our
            # slot-checking UI can't fully prevent on its own).
            # --------------------------------------------------
            messages.error(
                request,
                "Sorry, this slot is no longer available. Please choose another time."
            )

        return redirect("appointment_list_view")

    return redirect("appointment_list_view")


@login_required
def appointment_edit_view(request, appointment_id):
    """
    Allows editing patient name, hospital, doctor, date, time,
    and reason — with the same conflict-safe slot checking used
    during booking (excluding this appointment's own current slot).
    """
    appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)
    hospitals = Hospital.objects.all()

    if request.method == "POST":
        patient_name = request.POST.get("patient_name", "").strip()
        doctor_id = request.POST.get("doctor")
        appointment_date = request.POST.get("appointment_date")
        appointment_time = request.POST.get("appointment_time")
        reason = request.POST.get("reason", "").strip()

        if not all([patient_name, doctor_id, appointment_date, appointment_time, reason]):
            messages.error(request, "Please fill in all fields.")
            return redirect("appointment_edit_view", appointment_id=appointment.id)

        doctor = get_object_or_404(Doctor, id=doctor_id)

        appointment.patient_name = patient_name
        appointment.doctor = doctor
        appointment.appointment_date = appointment_date
        appointment.appointment_time = appointment_time
        appointment.reason = reason

        try:
            appointment.save()
            messages.success(request, "Appointment updated successfully!")
        except IntegrityError:
            messages.error(request, "That slot is no longer available. Please choose another time.")
            return redirect("appointment_edit_view", appointment_id=appointment.id)

        return redirect("appointment_list_view")

    context = {
        "appointment": appointment,
        "hospitals": hospitals,
        "preselected_hospital_id": appointment.doctor.hospital_id,
        "preselected_doctor_id": appointment.doctor_id,
    }
    return render(request, "appointment_edit.html", context)


@login_required
def appointment_delete_view(request, appointment_id):
    """
    Deletes/cancels an appointment. Only accepts POST requests —
    destructive actions should never be triggerable via a simple
    GET link or browser prefetch.
    """
    appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)

    if request.method == "POST":
        appointment.delete()
        messages.success(request, "Appointment cancelled successfully.")
        return redirect("appointment_list_view")

    return redirect("appointment_list_view")