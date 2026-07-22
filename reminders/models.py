"""
reminders/models.py
==============================================
Reminder table — now stores MULTIPLE times per reminder
(e.g., "twice daily" needs 2 times, not 1), stored as a
comma-separated string of HH:MM values.
==============================================
"""

from django.db import models
from django.contrib.auth.models import User


class Reminder(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reminders",
        help_text="The patient this reminder belongs to."
    )

    medicine_name = models.CharField(
        max_length=150,
        help_text="Name of the medicine (e.g., Paracetamol)."
    )

    dosage = models.CharField(
        max_length=100,
        blank=True,
        help_text="Optional dosage info (e.g., '500mg', '1 tablet')."
    )

    FREQUENCY_CHOICES = [
        ("daily", "Daily (1 time)"),
        ("twice_daily", "Twice Daily (2 times)"),
        ("thrice_daily", "Thrice Daily (3 times)"),
    ]
    frequency = models.CharField(
        max_length=20,
        choices=FREQUENCY_CHOICES,
        default="daily",
        help_text="How often this medicine should be taken."
    )

    # --------------------------------------------------
    # Stores one or more times as comma-separated HH:MM
    # strings, e.g. "07:30" or "07:30,19:30" or "08:00,14:00,20:00".
    # The number of times here should match the frequency.
    # --------------------------------------------------
    times = models.CharField(
        max_length=100,
        help_text="Comma-separated reminder times (HH:MM), count matching frequency."
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Whether this reminder is currently active."
    )

    notes = models.TextField(
        blank=True,
        help_text="Optional notes (e.g., 'take with food')."
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["medicine_name"]
        verbose_name = "Reminder"
        verbose_name_plural = "Reminders"

    def get_times_list(self):
        """Returns the stored times as a clean Python list, e.g. ['07:30', '19:30']."""
        return [t.strip() for t in self.times.split(",") if t.strip()]

    def __str__(self):
        return f"{self.medicine_name} ({self.times}) - {self.user.username}"