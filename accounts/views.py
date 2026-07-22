"""
accounts/views.py
==============================================
Handles signup, login, and a two-step logout flow:
1. User clicks "Logout" -> shown a confirmation page
2. User chooses "Keep data" or "Clear data" -> then actually logged out

We use Django's BUILT-IN User model (django.contrib.auth.models.User)
rather than creating our own — it already handles password hashing,
authentication, and sessions securely. No need to reinvent this.
==============================================
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Import models from other apps so we can delete a user's data
# when they choose "Clear data" on logout.
from chatbot.models import ChatHistory
from appointments.models import Appointment
# NOTE: reminders and reports imports will be added once those
# apps exist (later files) — for now we guard with try/except
# so this file doesn't break before those apps are built.
from doctors.models import Doctor
from hospitals.models import Hospital
def signup_view(request):
    """
    Unified signup for BOTH patients and doctors.
    The 'role' field from the form determines which type
    of account gets created.
    """
    hospitals = Hospital.objects.all()  # needed if role=doctor

    if request.method == "POST":
        role = request.POST.get("role")  # "patient" or "doctor"
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        # --------------------------------------------------
        # Shared validation for both roles
        # --------------------------------------------------
        if not username or not password:
            messages.error(request, "Username and password are required.")
            return render(request, "signup.html", {"hospitals": hospitals})

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "signup.html", {"hospitals": hospitals})

        if User.objects.filter(username=username).exists():
            messages.error(request, "That username is already taken.")
            return render(request, "signup.html", {"hospitals": hospitals})

        if role == "doctor":
            # --------------------------------------------------
            # Doctor-specific fields
            # --------------------------------------------------
            full_name = request.POST.get("full_name", "").strip()
            specialization = request.POST.get("specialization")
            hospital_id = request.POST.get("hospital")
            available_from = request.POST.get("available_from")
            available_to = request.POST.get("available_to")
            years_of_experience = request.POST.get("years_of_experience", 0)
            available_days_list = request.POST.getlist("available_days")

            # --------------------------------------------------
            # VALIDATION FIX: previously, if no day checkboxes
            # were selected, we silently defaulted to Mon-Fri.
            # That's misleading — a doctor might genuinely intend
            # to select their own days and just miss it by mistake.
            # Now we explicitly require at least one day and show
            # a clear error instead of guessing on their behalf.
            # --------------------------------------------------
            if not all([full_name, specialization, hospital_id, available_from, available_to]) or not available_days_list:
                messages.error(request, "Please fill in all doctor details, including at least one available day.")
                return render(request, "signup.html", {"hospitals": hospitals})

            available_days = ",".join(available_days_list)
            user = User.objects.create_user(username=username, password=password)
            hospital = Hospital.objects.get(id=hospital_id)

            Doctor.objects.create(
                user=user,
                full_name=full_name,
                specialization=specialization,
                hospital=hospital,
                available_from=available_from,
                available_to=available_to,
                available_days=available_days,
                years_of_experience=years_of_experience or 0,
            )

            login(request, user)
            messages.success(request, f"Welcome, Dr. {full_name}! Your profile has been created.")
            return redirect("doctor_dashboard_view")

        else:
            # --------------------------------------------------
            # Patient signup (default/fallback role)
            # --------------------------------------------------
            user = User.objects.create_user(username=username, password=password)
            login(request, user)
            messages.success(request, f"Welcome, {username}! Your account has been created.")
            return redirect("chat_view")

    return render(request, "signup.html", {"hospitals": hospitals})
def login_view(request):
    """
    Handles user login.
    """
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        # authenticate() checks the username/password against
        # the hashed password in the database — returns the
        # User object if valid, or None if invalid.
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {username}!")
            return redirect("chat_view")
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, "login.html")

    return render(request, "login.html")


@login_required
def logout_confirm_view(request):
    """
    STEP 1 of logout: show the confirmation page asking
    whether to keep or clear their data.
    Only accessible to logged-in users (@login_required
    redirects anonymous visitors to the login page automatically).
    """
    return render(request, "logout_confirm.html")


@login_required
def logout_process_view(request):
    """
    STEP 2 of logout: actually process their choice, then log out.
    """
    if request.method == "POST":
        choice = request.POST.get("data_choice")  # "keep" or "clear"
        user = request.user

        if choice == "clear":
            # --------------------------------------------------
            # Delete ONLY this user's data across every app.
            # Using .filter(user=user) ensures we NEVER touch
            # another patient's records.
            # --------------------------------------------------
            ChatHistory.objects.filter(user=user).delete()
            Appointment.objects.filter(user=user).delete()
            # Reminder.objects.filter(user=user).delete()   # added once reminders app exists
            # Report.objects.filter(user=user).delete()     # added once reports app exists

            messages.info(request, "Your data has been cleared.")
        else:
            messages.info(request, "Your data has been kept for next time.")

        logout(request)  # ends the Django session
        return redirect("login_view")

    # If someone GETs this URL directly without submitting the form,
    # send them back to the confirmation page instead of processing anything.
    return redirect("logout_confirm_view")
