"""
chatbot/views.py
==============================================
Handles the chat feature, now tied to real user accounts
for both persistence (history survives logout/login) and
privacy (each patient only sees their own conversation).
==============================================
"""

from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import ChatHistory
from .services.ai_service import get_ai_response


def build_gemini_history(user) -> list:
    """
    Converts this user's stored ChatHistory rows into the
    format Gemini's SDK expects for conversation memory.
    """
    past_messages = ChatHistory.objects.filter(user=user).order_by("created_at")

    history = []
    for entry in past_messages:
        history.append({"role": "user", "parts": [{"text": entry.user_message}]})
        history.append({"role": "model", "parts": [{"text": entry.ai_response}]})

    return history


@login_required
def chat_view(request):
    """
    Main chat view. Requires login — chat history is now
    tied to the account, not an anonymous browser session.
    """

    # --------------------------------------------------
    # Handle language selection
    # --------------------------------------------------
    if request.method == "POST" and "language" in request.POST:
        selected_language = request.POST.get("language")
        if selected_language in settings.SUPPORTED_LANGUAGES:
            request.session["language"] = selected_language

    current_language = request.session.get("language", "en")

    # --------------------------------------------------
    # Handle a new chat message
    # --------------------------------------------------
    if request.method == "POST" and "user_message" in request.POST:
        user_message = request.POST.get("user_message", "").strip()

        if user_message:
            gemini_history = build_gemini_history(request.user)

            ai_reply, is_emergency = get_ai_response(
                user_message=user_message,
                language_code=current_language,
                conversation_history=gemini_history,
            )

            ChatHistory.objects.create(
                user=request.user,   # <-- ties this message to the logged-in patient
                user_message=user_message,
                ai_response=ai_reply,
                language=current_language,
                is_emergency=is_emergency,
            )

            if is_emergency:
                messages.warning(request, "⚠️ Emergency detected — please seek immediate medical help.")

        return redirect("chat_view")

    # --------------------------------------------------
    # GET: show only THIS user's conversation history
    # --------------------------------------------------
    conversation = ChatHistory.objects.filter(user=request.user).order_by("created_at")

    context = {
        "conversation": conversation,
        "current_language": current_language,
        "supported_languages": settings.SUPPORTED_LANGUAGES,
    }
    return render(request, "chat.html", context)