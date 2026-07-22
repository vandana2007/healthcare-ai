"""
chatbot/services/ai_service.py
==============================================
This file contains ALL logic for talking to Google Gemini.
Updated to use the new "google-genai" SDK (the old
"google-generativeai" package is now legacy/deprecated).
==============================================
"""

import os
from pathlib import Path
from google import genai

# --------------------------------------------------
# STEP 1: Create the Gemini client using our API key
# --------------------------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

# The current stable, auto-updating model alias.
# Using "gemini-flash-latest" means we automatically benefit
# from future model upgrades without changing this code.
MODEL_NAME = "gemini-flash-latest"

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
    """

    # --- Step A: Emergency check FIRST ---
    if is_emergency_message(user_message):
        message = EMERGENCY_MESSAGE.get(language_code, EMERGENCY_MESSAGE["en"])
        return message, True

    # --- Step B: Build language-specific system instruction ---
    system_instruction = build_system_prompt(language_code)

    # --- Step C: Build the full conversation contents for this call ---
    # The new SDK expects "contents" as a list of turns, ending with
    # the new user message.
    contents = conversation_history + [
        {"role": "user", "parts": [{"text": user_message}]}
    ]

    # --- Step D: Call Gemini ---
    # --- Step D: Call Gemini (with a simple retry for temporary overload) ---
    import time

    max_retries = 4
    ai_reply = None

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=contents,
                config={"system_instruction": system_instruction},
            )
            ai_reply = response.text
            break
        except Exception as e:
            error_text = str(e)
            print(f"[ai_service.py] Gemini API error (attempt {attempt + 1}/{max_retries}): {e}")

            # --------------------------------------------------
            # 429 = quota exhausted. Retrying won't help until
            # the daily quota resets, so fail immediately with a
            # clear message instead of wasting remaining attempts.
            # --------------------------------------------------
            if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:
                ai_reply = (
                    "We've reached today's usage limit for the AI service. "
                    "Please try again after some time, or come back tomorrow."
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