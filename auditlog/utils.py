from .models import AuditLog


def get_client_ip(request):
    """
    Extract client IP address from request.
    Handles reverse proxy headers if present.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # may contain multiple IPs, take first
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_action(request, action: str, resource_type: str = "", resource_id: str = "", description: str = ""):
    """
    Convenience wrapper to create an AuditLog entry.
    """
    user = request.user if request.user.is_authenticated else None
    ip_address = get_client_ip(request)

    AuditLog.objects.create(
        user=user,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        description=description,
        ip_address=ip_address,
    )
