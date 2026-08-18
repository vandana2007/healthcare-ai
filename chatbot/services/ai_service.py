"""
chatbot/services/ai_service.py
==============================================
This file contains ALL logic for talking to the AI provider.
Switched from Google Gemini to Groq (Llama 3.3 70B) due to
Google's ongoing API key authentication rollout issues.

No other file needs to change — get_ai_response() keeps the
exact same function signature as before.
==============================================
"""

import os
import time
from pathlib import Path
from groq import Groq

# --------------------------------------------------
# STEP 1: Create the Groq client using our API key
# --------------------------------------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

# Fast, capable open-source model — good fit for chat +
# symptom-checking + multilingual responses.
MODEL_NAME = "openai/gpt-oss-120b"

# --------------------------------------------------
# STEP 2: Load the system prompt template from file
# --------------------------------------------------
PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "system_prompt.txt"

with open(PROMPT_PATH, "r", encoding="utf-8") as f:
    SYSTEM_PROMPT_TEMPLATE = f.read()

# --------------------------------------------------
# STEP 3: Map our short language codes to full names
# --------------------------------------------------
LANGUAGE_NAME_MAP = {
    "en": "English",
    "hi": "Hindi",
    "te": "Telugu",
}

# --------------------------------------------------
# STEP 4: Local emergency keyword safety net
# --------------------------------------------------
EMERGENCY_KEYWORDS = [
    "cannot breathe", "can't breathe", "difficulty breathing",
    "chest pain", "fainted", "unconscious", "severe bleeding",
    "heart attack", "stroke", "suicide", "kill myself",
    "want to die", "severe allergic reaction", "not breathing",
]

EMERGENCY_MESSAGE = {
    "en": "This may be a medical emergency. Please contact your local emergency medical services immediately or go to the nearest emergency department.",
    "hi": "यह एक चिकित्सा आपातकाल हो सकता है। कृपया तुरंत अपनी स्थानीय आपातकालीन चिकित्सा सेवाओं से संपर्क करें या निकटतम आपातकालीन विभाग जाएं।",
    "te": "ఇది వైద్య అత్యవసర పరిస్థితి కావచ్చు. దయచేసి వెంటనే మీ స్థానిక అత్యవసర వైద్య సేవలను సంప్రదించండి లేదా సమీప అత్యవసర విభాగానికి వెళ్లండి.",
}


def is_emergency_message(user_message: str) -> bool:
    lowered = user_message.lower()
    return any(keyword in lowered for keyword in EMERGENCY_KEYWORDS)


def build_system_prompt(language_code: str) -> str:
    language_name = LANGUAGE_NAME_MAP.get(language_code, "English")
    return SYSTEM_PROMPT_TEMPLATE.replace("{language}", language_name)


def get_ai_response(user_message: str, language_code: str, conversation_history: list) -> tuple:
    """
    Returns a tuple: (ai_reply_text: str, is_emergency: bool)

    conversation_history: list of dicts like
    [{"role": "user", "parts": [{"text": "..."}]},
     {"role": "model", "parts": [{"text": "..."}]}]
    (kept in this format since views.py already builds it this way —
    we convert it internally to Groq's expected format below.)
    """

    # --- Step A: Emergency check FIRST ---
    if is_emergency_message(user_message):
        message = EMERGENCY_MESSAGE.get(language_code, EMERGENCY_MESSAGE["en"])
        return message, True

    # --- Step B: Build language-specific system instruction ---
    system_instruction = build_system_prompt(language_code)

    # --------------------------------------------------
    # Step C: Convert conversation_history (Gemini-style) into
    # Groq/OpenAI-style messages list: [{"role": ..., "content": ...}]
    # --------------------------------------------------
    messages = [{"role": "system", "content": system_instruction}]

    for entry in conversation_history:
        role = "user" if entry["role"] == "user" else "assistant"
        text = entry["parts"][0]["text"]
        messages.append({"role": role, "content": text})

    messages.append({"role": "user", "content": user_message})

    # --- Step D: Call Groq (with retry for transient errors) ---
    max_retries = 3
    ai_reply = None

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
            )
            ai_reply = response.choices[0].message.content
            break
        except Exception as e:
            error_text = str(e)
            print(f"[ai_service.py] Groq API error (attempt {attempt + 1}/{max_retries}): {e}")

            if "429" in error_text or "rate_limit" in error_text.lower():
                ai_reply = (
                    "We've reached today's usage limit for the AI service. "
                    "Please try again after some time."
                )
                break

            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                ai_reply = (
                    "Sorry, I'm having trouble processing your request right now. "
                    "Please try again in a moment."
                )

    return ai_reply, False