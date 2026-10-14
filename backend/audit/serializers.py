from rest_framework import serializers
from .models import AuditLog

FIELDS = ["id", "user", "username", "action", "entity", "entity_id", "details", "ip_address", "created_at"]


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = FIELDS
        read_only_fields = FIELDS
