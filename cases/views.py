from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test


from .models import Sample
from .forms import SampleFileUploadForm, SampleCreateForm
from storageapp.minio_client import upload_raw_dna_file
from django.contrib.auth.decorators import login_required
from auditlog.utils import log_action

from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Sample

@login_required
def global_search(request):
    query = request.GET.get("q", "").strip()
    results = []

    if query:
        results = Sample.objects.select_related("case").filter(
            Q(sample_id__icontains=query) |
            Q(case__case_id__icontains=query) |
            Q(status__icontains=query)
        )

    return render(request, "cases/search_results.html", {
        "query": query,
        "results": results
    })

def is_lab_user(user):
    # Can see samples (Technician, Analyst, Admin/staff)
    return (
        user.is_superuser
        or user.is_staff
        or user.groups.filter(name__in=["Technician", "Analyst"]).exists()
    )


def is_technician(user):
    # Can upload files / generate STR (Technician, Admin/staff)
    return (
        user.is_superuser
        or user.is_staff
        or user.groups.filter(name="Technician").exists()
    )

@login_required
@user_passes_test(is_lab_user)
def sample_list(request):
    """
    Simple page to list all samples.
    Visible to Technician, Analyst, Admin.
    """
    samples = Sample.objects.select_related('case').all().order_by('-uploaded_at')

    is_admin = request.user.is_superuser or request.user.is_staff
    is_analyst = request.user.groups.filter(name="Analyst").exists()
    is_technician = request.user.groups.filter(name="Technician").exists()

    return render(request, "cases/sample_list.html", {
        "samples": samples,
        "is_admin": is_admin,
        "is_analyst": is_analyst,
        "is_technician": is_technician,
    })

@login_required
@user_passes_test(is_technician)
def upload_sample_file(request, sample_id):
    """
    Upload a raw DNA file for a specific sample and store it in MinIO.
    """
    sample = get_object_or_404(Sample, id=sample_id)

    if request.method == "POST":
        form = SampleFileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            upload_file = form.cleaned_data['file']

            try:
                object_name, checksum = upload_raw_dna_file(sample, upload_file)
            except Exception as e:
                messages.error(request, f"Error uploading file to MinIO: {e}")
                return render(request, "cases/upload_sample_file.html", {
                    "sample": sample,
                    "form": form,
                })

            # Save storage key & checksum in the sample
            sample.raw_storage_key = object_name
            sample.checksum = checksum
            sample.status = "UPLOADED"  # ensure correct status
            sample.save()

            log_action(
                request,
                action="UPLOAD_SAMPLE_FILE",
                resource_type="Sample",
                resource_id=sample.sample_id,
                description=f"Uploaded DNA file '{upload_file.name}' stored at '{sample.raw_storage_key}'"
            )


            messages.success(request, "File uploaded successfully and stored securely.")
            return redirect("sample_list")
    else:
        form = SampleFileUploadForm()

    return render(request, "cases/upload_sample_file.html", {
        "sample": sample,
        "form": form,
    })

@login_required
@user_passes_test(is_technician)
def create_sample(request):
    """
    Technician creates a new DNA evidence sample linked to an existing case.
    After creation, redirect to file upload.
    """
    if request.method == "POST":
        form = SampleCreateForm(request.POST)
        if form.is_valid():
            sample = form.save(commit=False)
            # status will use default ('UPLOADED') defined in model, that's fine
            sample.save()

            # Audit log
            from auditlog.utils import log_action
            log_action(
                request,
                action="CREATE_SAMPLE",
                resource_type="Sample",
                resource_id=sample.sample_id,
                description=f"Created new DNA evidence sample linked to case {sample.case.case_id}"
            )

            messages.success(
                request,
                f"Sample {sample.sample_id} created. Now upload the DNA file."
            )
            # Redirect directly to upload file page for this new sample
            return redirect("upload_sample_file", sample_id=sample.id)
    else:
        form = SampleCreateForm()

    return render(request, "cases/create_sample.html", {"form": form})

@login_required
@user_passes_test(is_technician)
def generate_str_from_fastq(request, sample_id):
    """
    Trigger STR profile generation from an uploaded FASTQ file.
    This does NOT run STRaitRazor.
    It only marks the sample as pending for external processing.
    """
    sample = get_object_or_404(Sample, id=sample_id)

    if not sample.raw_storage_key:
        messages.error(request, "No FASTQ file uploaded for this sample.")
        return redirect("upload_sample_file", sample_id=sample.id)

    # Mark sample as waiting for STR generation
    sample.status = "STR_PENDING"
    sample.save()

    log_action(
        request,
        action="REQUEST_STR_GENERATION",
        resource_type="Sample",
        resource_id=sample.sample_id,
        description="STR generation requested from FASTQ (semi-automatic pipeline)"
    )

    messages.info(
        request,
        "STR generation requested. Run the STR processing worker to generate the profile."
    )

    return redirect("sample_list")
