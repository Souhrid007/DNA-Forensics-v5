from django.conf import settings
from minio import Minio
from minio.error import S3Error
import hashlib
import io
import json



def get_minio_client():
    """
    Create and return a Minio client using Django settings.
    """
    return Minio(
        settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=settings.MINIO_USE_SSL,
    )


def ensure_bucket(client, bucket_name: str):
    """
    Ensure the given bucket exists. Create it if not.
    """
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)


def upload_raw_dna_file(sample, file_obj):
    """
    Upload a raw DNA file (FASTA/FASTQ/etc.) to MinIO.

    - sample: Sample instance (from cases.models)
    - file_obj: UploadedFile object from Django (request.FILES)

    Returns:
        object_name (str): key/name of the object in the bucket
        checksum (str): SHA-256 checksum of file content
    """
    client = get_minio_client()
    raw_bucket = settings.MINIO_RAW_BUCKET

    # Make sure bucket exists
    ensure_bucket(client, raw_bucket)

    # Read the file content into memory (OK for small/medium files for this project)
    data = file_obj.read()
    checksum = hashlib.sha256(data).hexdigest()

    # Object name structure: CASEID/SAMPLEID/original_filename
    object_name = f"{sample.case.case_id}/{sample.sample_id}/{file_obj.name}"

    # Upload to MinIO
    data_stream = io.BytesIO(data)
    data_length = len(data)

    try:
        client.put_object(
            raw_bucket,
            object_name,
            data_stream,
            length=data_length,
            content_type=file_obj.content_type or "application/octet-stream",
        )
    except S3Error as e:
        # For now, just re-raise. In production, you'd log this properly.
        raise e

    return object_name, checksum

def upload_str_profile_json(sample, profile_data: dict):
    """
    Upload STR profile JSON for a sample to MinIO.

    Returns:
        object_name (str): key in the STR bucket
        checksum (str): SHA-256 checksum of the JSON bytes
    """
    client = get_minio_client()
    str_bucket = settings.MINIO_STR_BUCKET

    # Ensure bucket exists
    ensure_bucket(client, str_bucket)

    # Convert dict to JSON bytes
    json_bytes = json.dumps(profile_data, indent=2).encode("utf-8")
    checksum = hashlib.sha256(json_bytes).hexdigest()

    # Object name structure: CASEID/SAMPLEID/str_profile.json
    object_name = f"{sample.case.case_id}/{sample.sample_id}/str_profile.json"

    data_stream = io.BytesIO(json_bytes)
    data_length = len(json_bytes)

    try:
        client.put_object(
            str_bucket,
            object_name,
            data_stream,
            length=data_length,
            content_type="application/json",
        )
    except S3Error as e:
        raise e

    return object_name, checksum
