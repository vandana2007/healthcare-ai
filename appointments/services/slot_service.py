"""
appointments/services/slot_service.py
==============================================
Calculates which time slots are ACTUALLY available for a
given doctor on a given date — combining:
1. The doctor's working hours (available_from/to)
2. The doctor's working days (available_days)
3. Existing pending/confirmed appointments that day

This is the core logic that prevents double-booking and
lets patients see only genuinely open slots.
==============================================
"""

from datetime import datetime, timedelta, date as date_type
from doctors.models import Doctor
from appointments.models import Appointment

# Each appointment slot is 30 minutes long.
SLOT_DURATION_MINUTES = 30


def get_available_slots(doctor: Doctor, appointment_date: date_type, exclude_appointment_id: int = None) -> list:
    """
    Returns a list of available time strings for the given doctor
    on the given date.

    exclude_appointment_id: when editing an existing appointment,
    pass its ID so its OWN current slot doesn't incorrectly show
    as "taken" by itself.
    """

    weekday = str(appointment_date.weekday())
    working_days = doctor.available_days.split(",")

    if weekday not in working_days:
        return []

    all_slots = []
    current_time = datetime.combine(appointment_date, doctor.available_from)
    end_time = datetime.combine(appointment_date, doctor.available_to)

    while current_time < end_time:
        all_slots.append(current_time.time())
        current_time += timedelta(minutes=SLOT_DURATION_MINUTES)

    booked_query = Appointment.objects.filter(
        doctor=doctor,
        appointment_date=appointment_date,
        status__in=["pending", "confirmed"],
    )

    if exclude_appointment_id:
        booked_query = booked_query.exclude(id=exclude_appointment_id)

    booked_times = set(booked_query.values_list("appointment_time", flat=True))

    available_slots = [
        slot.strftime("%H:%M") for slot in all_slots if slot not in booked_times
    ]

    return available_slots