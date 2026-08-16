"""
healthcare_project/context_processors.py
==============================================
Makes the VAPID public key available to every template
automatically, without each view needing to pass it manually.
==============================================
"""

from django.conf import settings


def vapid_key(request):
    return {"vapid_public_key": settings.VAPID_PUBLIC_KEY}