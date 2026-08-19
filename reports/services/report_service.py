"""
reports/services/report_service.py
==============================================
Handles extracting text from uploaded medical reports
(PDF or image) and getting a simplified explanation from
Gemini. Isolated here — same pattern as ai_service.py and
geocoding_service.py — so extraction logic stays in ONE place.
==============================================
"""

import os
import re
import PyPDF2
import pytesseract
from PIL import Image
from google import genai
from groq import Groq
# --------------------------------------------------
# Reuse the same Gemini client setup as ai_service.py
# --------------------------------------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)
MODEL_NAME = "openai/gpt-oss-120b"


def clean_extracted_text(text: str) -> str:
    print(f"extract_text() called for: {filename}")
    """
    Removes lines that are almost certainly OCR garbage —
    short, mostly non-alphanumeric fragments produced by
    misread logos, borders, or decorative elements.

    Heuristic: a line is kept if it contains at least one
    digit OR is reasonably long with real words. Very short,
    letter-salad lines (typical OCR noise) are dropped.
    """
    cleaned_lines = []

    for line in text.split("\n"):
        stripped = line.strip()

        if not stripped:
            continue

        # Keep lines with digits (values, dates, ranges — almost
        # always real report content, not OCR noise).
        has_digit = bool(re.search(r"\d", stripped))

        # Count "real" words (3+ letters) vs total tokens.
        words = stripped.split()
        real_words = [w for w in words if len(re.sub(r"[^a-zA-Z]", "", w)) >= 3]

        # Keep if it has a digit, OR has at least 2 real words,
        # OR is a reasonably long line (likely a real sentence).
        if has_digit or len(real_words) >= 2 or len(stripped) > 25:
            cleaned_lines.append(stripped)

    return "\n".join(cleaned_lines)


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts all text from a PDF file using PyPDF2.
    Works well for PDFs with actual text content (not
    scanned image-only PDFs — those would need OCR instead).
    """
    text = ""
    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"[report_service.py] PDF extraction error: {e}")
    return text.strip()


def extract_text_from_image(file_path: str) -> str:
    """
    Extracts text from an image file using Tesseract OCR,
    then filters out likely garbage lines from decorative
    elements (logos, borders, stamps).

    Uses PSM 6 (Page Segmentation Mode 6): treats the image as
    a single uniform block of text, which preserves line-by-line
    structure much better than the default mode — important for
    tabular/structured documents like lab reports.
    """
    text = ""
    try:
        image = Image.open(file_path)
        custom_config = r"--oem 3 --psm 6"
        raw_text = pytesseract.image_to_string(image, config=custom_config)
        print("=" * 50)
        print("RAW OCR TEXT:")
        print(raw_text)
        print("=" * 50)
        text = clean_extracted_text(raw_text)
    except Exception as e:
        print(f"[report_service.py] OCR extraction error: {e}")
    return text.strip()


def extract_text(file_path: str, filename: str) -> str:
    """
    Detects the file type by extension and routes to the
    correct extraction method.
    """
    extension = filename.lower().split(".")[-1]

    if extension == "pdf":
        return extract_text_from_pdf(file_path)
    elif extension in ["jpg", "jpeg", "png", "bmp", "tiff"]:
        return extract_text_from_image(file_path)
    else:
        return ""


def get_report_explanation(extracted_text: str) -> str:
    """
    Sends the extracted report text to Gemini and asks for
    a simple, patient-friendly, well-formatted explanation.
    """

    if not extracted_text or len(extracted_text.strip()) < 10:
        return (
            "We couldn't extract readable text from this file. "
            "Please try uploading a clearer scan or a different file."
        )

    prompt = f"""You are a helpful medical assistant. A patient has uploaded a medical report.
Explain the following report content in SIMPLE, non-technical language that a general patient can understand.

Rules:
- Do NOT diagnose any disease.
- Use clear markdown formatting: ## for section headers, ** for bold key terms, bullet points for lists.
- Add ONE relevant emoji at the start of each section header (e.g., "## 🩸 Blood Counts", "## ⚠️ Abnormal Values", "## 👨‍⚕️ Next Steps").
- Highlight any values that appear abnormal or out of typical range, if mentioned, using an emoji flag like 🔴 or ⚠️.
- Use ✅ next to findings that are normal/healthy.
- Suggest the patient consult a doctor for proper interpretation.
- Keep the explanation clear and reasonably concise.
- End with this exact disclaimer on its own line: "This is a simplified explanation and not a medical diagnosis. Please consult a qualified doctor for proper interpretation of your report."

Report content:
{extracted_text}
"""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role":"user",
                    "content":prompt
                }
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"[report_service.py] Gemini explanation error: {e}")
        return (
            "Sorry, we couldn't generate an explanation right now. "
            "Please try again in a moment."
        )