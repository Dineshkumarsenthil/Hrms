from .models import AuditLog


def _ip(request):
    if request is None:
        return None
    fwd = request.META.get("HTTP_X_FORWARDED_FOR")
    return fwd.split(",")[0].strip() if fwd else request.META.get("REMOTE_ADDR")


def log_action(request, action, entity, entity_id="", details=None, user=None):
    """Write one audit record. `request` may be None (e.g. management commands)."""
    actor = user or (getattr(request, "user", None) if request else None)
    if actor is not None and not getattr(actor, "is_authenticated", False):
        actor = None
    AuditLog.objects.create(
        user=actor,
        username=getattr(actor, "username", "") or "",
        action=action,
        entity=entity,
        entity_id=str(entity_id or ""),
        details=details or {},
        ip_address=_ip(request),
    )
