"""
accounts/views.py
==============================================
Signup (patient/doctor), login, logout (keep/clear data),
and profile view/edit — now collecting email + phone number
at signup, used later for email reminders/report delivery.
==============================================
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Profile
from doctors.models import Doctor
from hospitals.models import Hospital
from chatbot.models import ChatHistory
from appointments.models import Appointment
from reminders.models import Reminder, PushSubscription
from reports.models import Report
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password
def signup_view(request):
    """
    Unified signup for BOTH patients and doctors, now also
    collecting email and phone number for every account.
    """
    hospitals = Hospital.objects.all()

    if request.method == "POST":
        role = request.POST.get("role")
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")
        email = request.POST.get("email", "").strip()
        phone_number = request.POST.get("phone_number", "").strip()

        if not username or not password or not email or not phone_number:
            messages.error(request, "Username, password, email, and phone number are all required.")
            return render(request, "signup.html", {"hospitals": hospitals})

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "signup.html", {"hospitals": hospitals})

        if User.objects.filter(username=username).exists():
            messages.error(request, "That username is already taken.")
            return render(request, "signup.html", {"hospitals": hospitals})

        if User.objects.filter(email=email).exists():
            messages.error(request, "That email is already registered.")
            return render(request, "signup.html", {"hospitals": hospitals})

        if role == "doctor":
            full_name = request.POST.get("full_name", "").strip()
            specialization = request.POST.get("specialization")
            hospital_id = request.POST.get("hospital")
            available_from = request.POST.get("available_from")
            available_to = request.POST.get("available_to")
            years_of_experience = request.POST.get("years_of_experience", 0)
            available_days_list = request.POST.getlist("available_days")

            if not all([full_name, specialization, hospital_id, available_from, available_to]) or not available_days_list:
                messages.error(request, "Please fill in all doctor details, including at least one available day.")
                return render(request, "signup.html", {"hospitals": hospitals})

            available_days = ",".join(available_days_list)

            user = User.objects.create_user(username=username, password=password, email=email)
            Profile.objects.create(user=user, phone_number=phone_number)

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
            user = User.objects.create_user(username=username, password=password, email=email)
            Profile.objects.create(user=user, phone_number=phone_number)

            login(request, user)
            messages.success(request, f"Welcome, {username}! Your account has been created.")
            return redirect("chat_view")

    return render(request, "signup.html", {"hospitals": hospitals})


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

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
    return render(request, "logout_confirm.html")


@login_required
def logout_process_view(request):
    if request.method == "POST":
        choice = request.POST.get("data_choice")
        user = request.user

        if choice == "clear":
            ChatHistory.objects.filter(user=user).delete()
            Appointment.objects.filter(user=user).delete()
            Reminder.objects.filter(user=user).delete()
            Report.objects.filter(user=user).delete()
            PushSubscription.objects.filter(user=user).delete()
            messages.info(request, "Your data has been cleared.")
        else:
            messages.info(request, "Your data has been kept for next time.")

        logout(request)
        return redirect("login_view")

    return redirect("logout_confirm_view")


@login_required
def profile_view(request):
    """
    Lets a patient/doctor view and update their email, phone
    number, and profile picture.
    """
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        phone_number = request.POST.get("phone_number", "").strip()

        if not email:
            messages.error(request, "Email cannot be empty.")
            return redirect("profile_view")

        if User.objects.filter(email=email).exclude(id=request.user.id).exists():
            messages.error(request, "That email is already used by another account.")
            return redirect("profile_view")

        request.user.email = email
        request.user.save()

        profile.phone_number = phone_number

        if request.FILES.get("profile_picture"):
            profile.profile_picture = request.FILES["profile_picture"]

        profile.save()

        messages.success(request, "Profile updated successfully.")
        return redirect("profile_view")

    return render(request, "profile.html", {"profile": profile})


@login_required
def change_password_view(request):
    """
    Lets a logged-in user change their password, without
    needing to log out/in afterward.
    """
    if request.method == "POST":
        current_password = request.POST.get("current_password", "")
        new_password = request.POST.get("new_password", "")
        confirm_password = request.POST.get("confirm_new_password", "")

        if not check_password(current_password, request.user.password):
            messages.error(request, "Current password is incorrect.")
            return redirect("profile_view")

        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return redirect("profile_view")

        if len(new_password) < 6:
            messages.error(request, "New password must be at least 6 characters.")
            return redirect("profile_view")

        request.user.set_password(new_password)
        request.user.save()

        # --------------------------------------------------
        # Keeps the user logged in after password change —
        # without this, Django invalidates the session and
        # forces an immediate re-login.
        # --------------------------------------------------
        update_session_auth_hash(request, request.user)

        messages.success(request, "Password changed successfully.")
        return redirect("profile_view")

    return redirect("profile_view")