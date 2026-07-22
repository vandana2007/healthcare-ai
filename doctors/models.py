"""
doctors/models.py
==============================================
Defines the Doctor table — links a Doctor's professional
profile to both a User account (for login) and a Hospital
(where they practice), plus their specialization and
working hours.
==============================================
"""

from django.db import models
from django.contrib.auth.models import User
from hospitals.models import Hospital


class Doctor(models.Model):
    """
    Represents a doctor's professional profile.
    Each Doctor is linked to exactly one User account
    (for login) via a OneToOne relationship — a doctor
    account IS a user account, just with extra fields.
    """

    # --------------------------------------------------
    # OneToOneField: each User can be linked to AT MOST
    # one Doctor profile (unlike ForeignKey, which allows
    # many-to-one). This is the correct relationship for
    # "this account IS this doctor."
    # --------------------------------------------------
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="doctor_profile",
        help_text="The login account associated with this doctor."
    )

    full_name = models.CharField(
        max_length=150,
        help_text="Doctor's full name (e.g., Dr. Ramesh Kumar)."
    )

    SPECIALIZATION_CHOICES = [
        ("general_physician", "General Physician"),
        ("cardiologist", "Cardiologist"),
        ("dermatologist", "Dermatologist"),
        ("pediatrician", "Pediatrician"),
        ("orthopedic", "Orthopedic"),
        ("ent", "ENT Specialist"),
        ("gynecologist", "Gynecologist"),
        ("neurologist", "Neurologist"),
        ("psychiatrist", "Psychiatrist"),
        ("dentist", "Dentist"),
    ]
    specialization = models.CharField(
        max_length=50,
        choices=SPECIALIZATION_CHOICES,
        help_text="Doctor's medical specialization."
    )

    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.CASCADE,
        related_name="doctors",
        help_text="The hospital this doctor practices at."
    )

    # --------------------------------------------------
    # Working hours — used later to generate available
    # time slots for patients to book.
    # --------------------------------------------------
    available_from = models.TimeField(
        help_text="Start of working hours (e.g., 09:00)."
    )
    available_to = models.TimeField(
        help_text="End of working hours (e.g., 17:00)."
    )

    # --------------------------------------------------
    # Which days of the week the doctor is available.
    # Stored as a comma-separated string of day numbers
    # (0=Monday ... 6=Sunday) for simplicity.
    # --------------------------------------------------
    available_days = models.CharField(
        max_length=20,
        default="0,1,2,3,4",
        help_text="Comma-separated weekday numbers doctor is available (0=Mon...6=Sun). Default: Mon-Fri."
    )

    years_of_experience = models.PositiveIntegerField(
        default=0,
        help_text="Years of professional experience."
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Whether this doctor is currently accepting appointments."
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["full_name"]
        verbose_name = "Doctor"
        verbose_name_plural = "Doctors"

    def __str__(self):
        return f"Dr. {self.full_name} ({self.get_specialization_display()}) - {self.hospital.name}"