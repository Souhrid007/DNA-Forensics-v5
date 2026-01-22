from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test


from cases.models import Sample
from strprofiles.models import STRProfile
from matching.utils import compare_loci
from .utils import render_to_pdf
from django.contrib.auth.decorators import login_required
from auditlog.utils import log_action

def is_analyst(user):
    return (
        user.is_superuser
        or user.is_staff
        or user.groups.filter(name="Analyst").exists()
    )

@login_required
@user_passes_test(is_analyst)
def generate_report_view(request, query_sample_id, target_sample_id):
    """
    Generate a PDF forensic report comparing two samples and return it as a download.
    Nothing is stored in MinIO.
    """
    query_sample = get_object_or_404(Sample, id=query_sample_id)
    target_sample = get_object_or_404(Sample, id=target_sample_id)

    try:
        query_profile = query_sample.str_profile
        target_profile = target_sample.str_profile
    except STRProfile.DoesNotExist:
        messages.error(request, "Both samples must have STR profiles to generate a report.")
        return redirect('search_matches')

    # Compare STR profiles
    overall_score, locus_results = compare_loci(
        query_profile.loci_json,
        target_profile.loci_json,
    )

    case = query_sample.case  # treat query sample's case as main case

    context = {
        "case": case,
        "query_sample": query_sample,
        "target_sample": target_sample,
        "query_profile": query_profile,
        "target_profile": target_profile,
        "overall_score": overall_score,
        "locus_results": locus_results,
        "user": request.user if request.user.is_authenticated else None,
    }

    pdf_bytes = render_to_pdf("reporting/report_template.html", context)
    if pdf_bytes is None:
        messages.error(request, "Error generating PDF report.")
        return redirect('search_matches')

    filename = f"report_{case.case_id}_{query_sample.sample_id}_vs_{target_sample.sample_id}.pdf"

    # Audit log
    log_action(
        request,
        action="GENERATE_REPORT",
        resource_type="SamplePair",
        resource_id=f"{query_sample.sample_id},{target_sample.sample_id}",
        description=f"Generated PDF report, similarity={overall_score:.2f}"
    )


    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
