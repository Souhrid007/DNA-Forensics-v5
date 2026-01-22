from django.db import models


class Case(models.Model):
    """
    Represents a forensic case.
    Example: CASE2025-001
    """
    case_id = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('OPEN', 'Open'),
            ('IN_PROGRESS', 'In Progress'),
            ('CLOSED', 'Closed'),
        ],
        default='OPEN',
    )

    def __str__(self):
        return f"{self.case_id} - {self.title}"


class Sample(models.Model):
    """
    Represents a DNA sample associated with a case.
    """
    SAMPLE_STATUS_CHOICES = [
        ('UPLOADED', 'Uploaded'),
        ('STR_PENDING', 'STR Pending'),
        ('STR_GENERATED', 'STR Generated'),
        ('MATCHED', 'Matched'),
    ]

    sample_id = models.CharField(max_length=50, unique=True)
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='samples')

    # Optional fingerprint / person link (string for now)
    fingerprint_id = models.CharField(max_length=100, blank=True, null=True)

    # Where file is stored in MinIO (we will fill this later)
    raw_storage_key = models.CharField(max_length=255, blank=True, null=True)

    # Integrity / tamper detection
    checksum = models.CharField(max_length=128, blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=SAMPLE_STATUS_CHOICES,
        default='UPLOADED',
    )

    collected_at = models.DateTimeField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.sample_id} ({self.case.case_id})"
