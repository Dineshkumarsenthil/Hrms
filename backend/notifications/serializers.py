from rest_framework import serializers
from .models import EmailLog, EmailTemplate


LOG_FIELDS = ["id", "template_code", "to_email", "subject", "body", "status", "error", "created_at"]


class EmailLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailLog
        fields = LOG_FIELDS
        read_only_fields = LOG_FIELDS


class EmailTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTemplate
        fields = "__all__"
