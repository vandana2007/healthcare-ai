"""
reports/views.py
==============================================
Handles report upload, triggers text extraction + AI
explanation, and displays results. Private per patient.
==============================================
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Report
from .services.report_service import extract_text, get_report_explanation


@login_required
def report_list_view(request):
    """
    Shows this patient's uploaded reports and handles new uploads.
    """
    if request.method == "POST" and request.FILES.get("report_file"):
        uploaded_file = request.FILES["report_file"]

        # --------------------------------------------------
        # Basic validation: only accept PDF/image files, and
        # cap file size to avoid abuse (10 MB limit here).
        # --------------------------------------------------
        allowed_extensions = ["pdf", "jpg", "jpeg", "png", "bmp", "tiff"]
        extension = uploaded_file.name.lower().split(".")[-1]

        if extension not in allowed_extensions:
            messages.error(request, "Please upload a PDF or image file (jpg, png, etc.).")
            return redirect("report_list_view")

        if uploaded_file.size > 10 * 1024 * 1024:  # 10 MB
            messages.error(request, "File is too large. Please upload a file under 10MB.")
            return redirect("report_list_view")

        # --------------------------------------------------
        # Step 1: Save the report record (status=processing)
        # --------------------------------------------------
        report = Report.objects.create(
            user=request.user,
            file=uploaded_file,
            original_filename=uploaded_file.name,
            status="processing",
        )

        # --------------------------------------------------
        # Step 2: Extract text from the saved file
        # --------------------------------------------------
        extracted_text = extract_text(report.file.path, report.original_filename)

        if not extracted_text:
            report.status = "failed"
            report.extracted_text = ""
            report.ai_explanation = (
                "We couldn't extract any readable text from this file. "
                "It may be blank, corrupted, or an unsupported format."
            )
            report.save()
            messages.warning(request, "Report uploaded, but text extraction failed.")
            return redirect("report_list_view")

        # --------------------------------------------------
        # Step 3: Get Gemini's simplified explanation
        # --------------------------------------------------
        explanation = get_report_explanation(extracted_text)

        report.extracted_text = extracted_text
        report.ai_explanation = explanation
        report.status = "completed"
        report.save()

        messages.success(request, "Report uploaded and explained successfully!")
        return redirect("report_list_view")

    # Only this user's reports — private by design
    reports = Report.objects.filter(user=request.user)
    context = {"reports": reports}
    return render(request, "report.html", context)


@login_required
def report_detail_view(request, report_id):
    """
    Shows the full extracted text + AI explanation for one report.
    """
    report = get_object_or_404(Report, id=report_id, user=request.user)
    context = {"report": report}
    return render(request, "report_detail.html", context)


@login_required
def report_delete_view(request, report_id):
    """
    Deletes a report and its associated file.
    """
    report = get_object_or_404(Report, id=report_id, user=request.user)

    if request.method == "POST":
        report.file.delete()  # removes the actual file from disk
        report.delete()       # removes the database record
        messages.success(request, "Report deleted.")

    return redirect("report_list_view")