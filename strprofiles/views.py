from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test


from cases.models import Sample
from .models import STRProfile


from auditlog.utils import log_action

import csv
import io
from .forms import STRUploadForm

import json, hashlib
from storageapp.minio_client import upload_str_profile_json

def is_technician(user):
    return (
        user.is_superuser
        or user.is_staff
        or user.groups.filter(name="Technician").exists()
    )


def is_lab_user(user):
    return (
        user.is_superuser
        or user.is_staff
        or user.groups.filter(name__in=["Technician", "Analyst"]).exists()
    )


@login_required
@user_passes_test(is_technician)
def upload_str_profile_csv(request, sample_id):
    sample = get_object_or_404(Sample, id=sample_id)

    if request.method == "POST":
        form = STRUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data["file"]
            decoded = file.read().decode("utf-8")
            reader = csv.DictReader(io.StringIO(decoded))

            loci = {}
            for row in reader:
                locus = row.get("locus")
                a1 = row.get("allele1")
                a2 = row.get("allele2")
                if locus and a1 and a2:
                    loci[locus] = [a1.strip(), a2.strip()]

            if not loci:
                messages.error(request, "No valid STR data found in CSV.")
                return redirect("sample_list")

            # Remove old profile if exists
            STRProfile.objects.filter(sample=sample).delete()

            loci_json_str = json.dumps(loci, sort_keys=True)
            sha256_hash = hashlib.sha256(loci_json_str.encode()).hexdigest()

            storage_key, checksum = upload_str_profile_json(sample, loci)

            str_profile = STRProfile.objects.create(
                sample=sample,
                loci_json=loci,
                storage_key=storage_key,
                hash=checksum
            )

            sample.status = "STR_GENERATED"
            sample.save()

            log_action(
                request,
                action="UPLOAD_STR_PROFILE",
                resource_type="Sample",
                resource_id=sample.sample_id,
                description="Uploaded STR profile via CSV"
            )

            messages.success(request, "STR profile uploaded successfully from CSV.")
            return redirect("view_str_profile", sample_id=sample.id)
    else:
        form = STRUploadForm()

    return render(request, "strprofiles/upload_str_csv.html", {
        "form": form,
        "sample": sample,
    })



@login_required
@user_passes_test(is_lab_user)
def view_str_profile(request, sample_id):
    """
    Show STR profile (loci table) for a sample.
    """
    sample = get_object_or_404(Sample, id=sample_id)

    try:
        str_profile = sample.str_profile
    except STRProfile.DoesNotExist:
        messages.warning(request, "No STR profile exists for this sample. Generate one first.")
        return redirect('sample_list')

    context = {
        "sample": sample,
        "str_profile": str_profile,
        "loci_items": str_profile.loci_json.items(),  # for table
    }
    return render(request, "strprofiles/str_profile_detail.html", context)
