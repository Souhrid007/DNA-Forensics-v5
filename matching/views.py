from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test


from cases.models import Sample
from strprofiles.models import STRProfile
from .forms import CompareSamplesForm, SearchMatchesForm
from .utils import compare_loci, search_matches
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
def compare_samples_view(request):
    """
    1:1 comparison of STR profiles between two samples.
    """
    if request.method == "POST":
        form = CompareSamplesForm(request.POST)
        if form.is_valid():
            sample_a = form.cleaned_data["sample_a"]
            sample_b = form.cleaned_data["sample_b"]

            # Ensure both have STR profiles
            try:
                profile_a = sample_a.str_profile
            except STRProfile.DoesNotExist:
                messages.error(request, f"Sample {sample_a.sample_id} has no STR profile.")
                profile_a = None

            try:
                profile_b = sample_b.str_profile
            except STRProfile.DoesNotExist:
                messages.error(request, f"Sample {sample_b.sample_id} has no STR profile.")
                profile_b = None

            if not profile_a or not profile_b:
                return render(request, "matching/compare_samples.html", {
                    "form": form,
                    "comparison_done": False,
                })

            overall_score, locus_results = compare_loci(
                profile_a.loci_json,
                profile_b.loci_json,
            )

            # Audit log
            log_action(
                request,
                action="COMPARE_SAMPLES",
                resource_type="SamplePair",
                resource_id=f"{sample_a.sample_id},{sample_b.sample_id}",
                description=f"Compared {sample_a.sample_id} with {sample_b.sample_id}, score={overall_score:.2f}"
            )


            context = {
                "form": form,
                "comparison_done": True,
                "sample_a": sample_a,
                "sample_b": sample_b,
                "profile_a": profile_a,
                "profile_b": profile_b,
                "overall_score": overall_score,
                "locus_results": locus_results,
            }
            return render(request, "matching/compare_samples.html", context)
    else:
        form = CompareSamplesForm()

    return render(request, "matching/compare_samples.html", {
        "form": form,
        "comparison_done": False,
    })

@login_required
@user_passes_test(is_analyst)
def search_matches_view(request):
    """
    1:N search: query one sample against all other STR profiles.
    """
    if request.method == "POST":
        form = SearchMatchesForm(request.POST)
        if form.is_valid():
            query_sample = form.cleaned_data["query_sample"]

            try:
                query_profile = query_sample.str_profile
            except STRProfile.DoesNotExist:
                messages.error(request, f"Sample {query_sample.sample_id} has no STR profile.")
                return render(request, "matching/search_matches.html", {
                    "form": form,
                    "search_done": False,
                })

            match_results = search_matches(query_profile)

            # Audit log
            log_action(
                request,
                action="SEARCH_MATCHES",
                resource_type="Sample",
                resource_id=query_sample.sample_id,
                description=f"Ran 1:N search for {query_sample.sample_id} against {len(match_results)} candidates"
            )


            context = {
                "form": form,
                "search_done": True,
                "query_sample": query_sample,
                "query_profile": query_profile,
                "match_results": match_results,
            }
            return render(request, "matching/search_matches.html", context)
    else:
        form = SearchMatchesForm()

    return render(request, "matching/search_matches.html", {
        "form": form,
        "search_done": False,
    })
