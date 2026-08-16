"""
reminders/views.py
==============================================
Handles reminder CRUD, now supporting multiple times per
reminder, plus a JSON endpoint the browser polls to check
for due reminders (powers real notifications).
==============================================
"""
import json

from django.views.decorators.csrf import csrf_exempt
from .models import PushSubscription
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from datetime import datetime
from pywebpush import webpush, WebPushException
from django.conf import settings
from .models import Reminder
from django.core.mail import send_mail
@csrf_exempt
@login_required
def save_subscription(request):
    if request.method == "POST":
        data = json.loads(request.body)

        PushSubscription.objects.update_or_create(
            user=request.user,
            endpoint=data["endpoint"],
            defaults={
                "p256dh_key": data["keys"]["p256dh"],
                "auth_key": data["keys"]["auth"]
            }
        )

        return JsonResponse({"status":"saved"})

@login_required
def reminder_list_view(request):
    if request.method == "POST":
        medicine_name = request.POST.get("medicine_name", "").strip()
        dosage = request.POST.get("dosage", "").strip()
        frequency = request.POST.get("frequency", "daily")
        notes = request.POST.get("notes", "").strip()

        # --------------------------------------------------
        # Collect however many time inputs were submitted
        # (the form sends multiple fields all named "times").
        # --------------------------------------------------
        times_list = [t for t in request.POST.getlist("times") if t]
        times_string = ",".join(times_list)

        if medicine_name and times_list:
            Reminder.objects.create(
                user=request.user,
                medicine_name=medicine_name,
                dosage=dosage,
                frequency=frequency,
                times=times_string,
                notes=notes,
            )
            messages.success(request, "Reminder added successfully!")
        else:
            messages.error(request, "Medicine name and at least one time are required.")

        return redirect("reminder_list_view")

    reminders = Reminder.objects.filter(user=request.user)
    context = {"reminders": reminders}
    return render(request, "reminder.html", context)


@login_required
def reminder_toggle_view(request, reminder_id):
    reminder = get_object_or_404(Reminder, id=reminder_id, user=request.user)
    if request.method == "POST":
        reminder.is_active = not reminder.is_active
        reminder.save()
        status_text = "activated" if reminder.is_active else "paused"
        messages.success(request, f"Reminder {status_text}.")
    return redirect("reminder_list_view")


@login_required
def reminder_delete_view(request, reminder_id):
    reminder = get_object_or_404(Reminder, id=reminder_id, user=request.user)
    if request.method == "POST":
        reminder.delete()
        messages.success(request, "Reminder deleted.")
    return redirect("reminder_list_view")


@login_required
def active_reminder_times_view(request):
    """
    JSON endpoint polled by JavaScript (in base.html) every
    30 seconds. Returns this patient's active reminders with
    their medicine name and times, so the browser can check
    if any match the current time and fire a notification.
    """
    reminders = Reminder.objects.filter(user=request.user, is_active=True)

    data = [
        {
            "medicine_name": r.medicine_name,
            "dosage": r.dosage,
            "times": r.get_times_list(),
        }
        for r in reminders
    ]
    return JsonResponse({"reminders": data})
def send_push_notifications(request):
    now = datetime.now()
    current_time = now.strftime("%H:%M")

    active_reminders = Reminder.objects.filter(is_active=True)
    sent_count = 0

    for reminder in active_reminders:
        if current_time in reminder.get_times_list():
            subject = "💊 Medicine Reminder"
            body = f"Time to take {reminder.medicine_name}" + (f" ({reminder.dosage})" if reminder.dosage else "")

            # --- Push notification (existing) ---
            subscriptions = PushSubscription.objects.filter(user=reminder.user)
            for sub in subscriptions:
                try:
                    webpush(
                        subscription_info={
                            "endpoint": sub.endpoint,
                            "keys": {"p256dh": sub.p256dh_key, "auth": sub.auth_key}
                        },
                        data=json.dumps({"title": subject, "body": body}),
                        vapid_private_key=settings.VAPID_PRIVATE_KEY_FILE,
                        vapid_claims={"sub": settings.VAPID_CLAIMS_EMAIL},
                    )
                    sent_count += 1
                except WebPushException as e:
                    print(f"[send_push_notifications] Push failed: {e}")
                    if "410" in str(e) or "404" in str(e):
                        sub.delete()

            # --- Email notification (NEW) ---
            if reminder.user.email:
                try:
                    send_mail(
                        subject=subject,
                        message=body,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[reminder.user.email],
                        fail_silently=False,
                    )
                except Exception as e:
                    print(f"[send_push_notifications] Email failed: {e}")

    return JsonResponse({"status": "checked", "sent": sent_count, "time_checked": current_time})