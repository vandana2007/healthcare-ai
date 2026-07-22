"""
chatbot/models.py
==============================================
Defines the ChatHistory table using Django's ORM.
Now tied to real user accounts instead of anonymous
sessions — ensures chat history is private per patient
and persists correctly across login sessions.
==============================================
"""

from django.db import models
from django.contrib.auth.models import User


class ChatHistory(models.Model):

    # --------------------------------------------------
    # Links this message to the logged-in patient.
    # Replaces the old session_id approach — user accounts
    # are permanent, sessions are not.
    # --------------------------------------------------
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="chat_messages",
        help_text="The patient account this message belongs to."
    )

    user_message = models.TextField(
        help_text="The message sent by the user."
    )

    ai_response = models.TextField(
        help_text="The AI assistant's reply to the user."
    )

    LANGUAGE_CHOICES = [
        ("en", "English"),
        ("hi", "Hindi"),
        ("te", "Telugu"),
    ]
    language = models.CharField(
        max_length=5,
        choices=LANGUAGE_CHOICES,
        default="en",
        help_text="Language this conversation exchange was conducted in."
    )

    is_emergency = models.BooleanField(
        default=False,
        help_text="True if this message triggered emergency detection."
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "Chat History"
        verbose_name_plural = "Chat Histories"

    def __str__(self):
        preview = self.user_message[:40]
        return f"[{self.language}] {self.user.username}: {preview}..."