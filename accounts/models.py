"""
accounts/models.py
==============================================
Extends the built-in User model with a Profile holding
extra contact details (phone number, profile picture).
==============================================
"""

from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone_number = models.CharField(max_length=15, blank=True)
    profile_picture = models.ImageField(upload_to="profile_pics/", blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s profile"