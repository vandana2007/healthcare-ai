"""
accounts/management/commands/create_admin.py
==============================================
Custom management command that creates a superuser
automatically during deployment, using environment
variables. Safe to run on every deploy — checks if
the user already exists first (won't error or duplicate).
==============================================
"""

import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Creates a superuser from environment variables if one doesn't already exist."

    def handle(self, *args, **options):
        username = os.getenv("DJANGO_SUPERUSER_USERNAME")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL", "")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD")

        if not username or not password:
            self.stdout.write("Skipping superuser creation — env vars not set.")
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(f"Superuser '{username}' already exists. Skipping.")
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' created successfully."))
