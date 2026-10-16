from rest_framework import serializers
from .models import Broadcast, EmailLog, EmailTemplate, Notification


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


class NotificationSerializer(serializers.ModelSerializer):
    kind_label = serializers.CharField(source="get_kind_display", read_only=True)

    class Meta:
        model = Notification
        fields = ["id", "kind", "kind_label", "title", "message", "link", "is_read", "read_at", "created_at"]
        read_only_fields = fields


class PreferenceSerializer(serializers.Serializer):
    kind = serializers.ChoiceField(choices=Notification.Kind.choices)
    enabled = serializers.BooleanField()


class BroadcastSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source="department.name", read_only=True, default="Whole organization")
    sent_by_name = serializers.CharField(source="sent_by.username", read_only=True, default="")

    class Meta:
        model = Broadcast
        fields = ["id", "title", "message", "department", "department_name", "sent_by_name", "recipient_count", "created_at"]
        read_only_fields = ["id", "recipient_count", "created_at"]

    def validate_title(self, v):
        if not v.strip():
            raise serializers.ValidationError("Title cannot be empty.")
        return v.strip()

    def validate_message(self, v):
        if not v.strip():
            raise serializers.ValidationError("Message cannot be empty.")
        return v.strip()
