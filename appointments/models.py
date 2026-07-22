"""
appointments/models.py
==============================================
Rebuilt to use REAL relationships to Doctor and Hospital
instead of free-text fields. This is what enables:
- Patients picking from an actual doctor list
- Automatic slot-conflict checking (no double-booking)
- Doctors seeing only their own real appointments
==============================================
"""

from django.db import models
from django.contrib.auth.models import User
from doctors.models import Doctor


class Appointment(models.Model):

    # --------------------------------------------------
    # The patient who booked this appointment.
    # --------------------------------------------------
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="appointments",
        help_text="The patient account that booked this appointment."
    )

    # --------------------------------------------------
    # REPLACES the old free-text 'doctor_name' field.
    # Now a real link to a Doctor profile — this is what
    # makes slot-checking and doctor dashboards possible.
    # --------------------------------------------------
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name="appointments",
        help_text="The doctor this appointment is booked with."
    )

    # --------------------------------------------------
    # Patient's display name for this booking (kept as a
    # simple text field — lets a patient book on behalf of
    # a family member without needing separate accounts).
    # --------------------------------------------------
    patient_name = models.CharField(
        max_length=150,
        help_text="Name of the person the appointment is for."
    )

    appointment_date = models.DateField(
        help_text="Date of the appointment."
    )
    appointment_time = models.TimeField(
        help_text="Time of the appointment."
    )

    reason = models.TextField(
        help_text="Reason for the appointment (e.g., symptoms, checkup)."
    )

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        help_text="Current status of this appointment."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["appointment_date", "appointment_time"]
        verbose_name = "Appointment"
        verbose_name_plural = "Appointments"

        # --------------------------------------------------
        # DATABASE-LEVEL SAFETY NET: prevents two appointments
        # existing for the same doctor at the same date+time,
        # EXCEPT if one is cancelled (cancelled slots free up).
        # This is a backup to our view-level check — even if
        # application code had a bug, the database itself
        # would reject a duplicate booking.
        # --------------------------------------------------
        constraints = [
            models.UniqueConstraint(
                fields=["doctor", "appointment_date", "appointment_time"],
                condition=models.Q(status__in=["pending", "confirmed"]),
                name="unique_active_doctor_slot",
            )
        ]

    def __str__(self):
        return f"{self.patient_name} with Dr. {self.doctor.full_name} on {self.appointment_date} at {self.appointment_time}"