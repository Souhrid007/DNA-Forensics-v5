from django.db import models
from cases.models import Sample


class STRProfile(models.Model):
    """
    STR profile linked to a DNA sample.

    Stores:
    - loci_json: JSON of loci -> alleles
    - storage_key: where JSON is stored in MinIO
    - hash: checksum of JSON (tamper detection)
    """
    sample = models.OneToOneField(
        Sample,
        on_delete=models.CASCADE,
        related_name='str_profile'
    )

    loci_json = models.JSONField()  # requires Django 3.1+; else use TextField
    storage_key = models.CharField(max_length=255)
    hash = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"STR Profile for {self.sample.sample_id}"
