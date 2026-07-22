"""
reports/models.py
==============================================
Defines the Report table — stores uploaded medical report
files (PDF/image) along with the AI-generated explanation.
Private per patient, same pattern as reminders/appointments.
==============================================
"""

from django.db import models
from django.contrib.auth.models import User


class Report(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reports",
        help_text="The patient who uploaded this report."
    )

    # --------------------------------------------------
    # Django's FileField handles the actual file storage.
    # Files are saved under MEDIA_ROOT/reports/ automatically.
    # --------------------------------------------------
    file = models.FileField(
        upload_to="reports/",
        help_text="The uploaded PDF or image file."
    )

    original_filename = models.CharField(
        max_length=255,
        help_text="Original name of the uploaded file."
    )

    extracted_text = models.TextField(
        blank=True,
        help_text="Raw text extracted from the file (via PyPDF2 or OCR)."
    )

    ai_explanation = models.TextField(
        blank=True,
        help_text="Gemini's simplified explanation of the report."
    )

    STATUS_CHOICES = [
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="processing",
        help_text="Processing status of this report."
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name = "Report"
        verbose_name_plural = "Reports"

    def __str__(self):
        return f"{self.original_filename} ({self.user.username})"