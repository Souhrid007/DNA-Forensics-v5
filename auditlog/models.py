from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class AuditLog(models.Model):
    """
    Simple audit log entry.
    Records who did what, on which resource, when, and from which IP.
    """
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=100)        # e.g. UPLOAD_SAMPLE_FILE
    resource_type = models.CharField(max_length=50, blank=True)  # e.g. "Sample"
    resource_id = models.CharField(max_length=100, blank=True)   # e.g. "SAMP001"
    description = models.TextField(blank=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        user_str = self.user.username if self.user else "Anonymous"
        return f"[{self.timestamp}] {user_str} {self.action} {self.resource_type}:{self.resource_id}"
