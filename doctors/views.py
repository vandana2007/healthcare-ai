"""
doctors/views.py
==============================================
Doctor-facing views: dashboard showing only THIS doctor's
appointments, with the ability to update status
(pending -> confirmed -> completed, or cancelled).
==============================================
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Doctor
from appointments.models import Appointment
from hospitals.models import Hospital


def hospital_doctors_view(request, hospital_id):
    """
    Shows all active doctors at a specific hospital —
    what the "View Doctors" link on hospital search points to.
    """
    hospital = get_object_or_404(Hospital, id=hospital_id)
    doctors = Doctor.objects.filter(hospital=hospital, is_active=True)

    context = {
        "hospital": hospital,
        "doctors": doctors,
    }
    return render(request, "hospital_doctors.html", context)

@login_required
def doctor_dashboard_view(request):
    """
    Shows all appointments booked with the logged-in doctor.
    Only accessible to users who have a linked Doctor profile.
    """

    # --------------------------------------------------
    # Safety check: make sure this user is actually a doctor.
    # hasattr() checks if the OneToOne relationship exists
    # without raising an error if it doesn't.
    # --------------------------------------------------
    if not hasattr(request.user, "doctor_profile"):
        messages.error(request, "This page is for doctors only.")
        return redirect("chat_view")

    doctor = request.user.doctor_profile

    # --------------------------------------------------
    # CRITICAL: only show appointments booked with THIS
    # doctor — never another doctor's patient list.
    # --------------------------------------------------
    appointments = Appointment.objects.filter(doctor=doctor).order_by(
        "appointment_date", "appointment_time"
    )

    context = {
        "doctor": doctor,
        "appointments": appointments,
    }
    return render(request, "doctor_dashboard.html", context)


@login_required
def update_appointment_status_view(request, appointment_id):
    """
    Lets a doctor update the status of ONE of their own
    appointments (e.g., pending -> confirmed).
    """

    if not hasattr(request.user, "doctor_profile"):
        messages.error(request, "This page is for doctors only.")
        return redirect("chat_view")

    doctor = request.user.doctor_profile

    # --------------------------------------------------
    # Ownership check: this appointment must belong to
    # THIS doctor. Prevents a doctor from editing another
    # doctor's appointments by guessing an ID in the URL.
    # --------------------------------------------------
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=doctor)

    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in dict(Appointment.STATUS_CHOICES):
            appointment.status = new_status
            appointment.save()
            messages.success(request, "Appointment status updated.")

    return redirect("doctor_dashboard_view")