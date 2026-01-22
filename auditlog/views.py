from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import AuditLog


from django.contrib.auth.decorators import login_required, user_passes_test

@login_required
@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def audit_log_list(request):
    """
    Show recent audit log entries (latest 200).
    Only staff/superusers can view.
    """
    logs = AuditLog.objects.select_related('user').all()[:200]
    return render(request, "auditlog/audit_log_list.html", {"logs": logs})
