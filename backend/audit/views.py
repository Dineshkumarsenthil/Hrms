from rest_framework import viewsets
from accounts.permissions import IsAdminOrHR
from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only: no create/update/delete routes exist."""
    queryset = AuditLog.objects.select_related("user")
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdminOrHR]
    filterset_fields = {"action": ["exact"], "entity": ["exact"], "user": ["exact"], "created_at": ["date__gte", "date__lte"]}
    search_fields = ["username", "action", "entity"]
