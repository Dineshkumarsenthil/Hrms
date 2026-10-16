from django.utils import timezone
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.permissions import IsAdmin, IsAdminOrHR
from audit.utils import log_action
from .inapp import send_broadcast
from .models import Broadcast, EmailLog, EmailTemplate, Notification, NotificationPreference
from .serializers import (BroadcastSerializer, EmailLogSerializer, EmailTemplateSerializer, NotificationSerializer, PreferenceSerializer)


class EmailLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EmailLog.objects.all()
    serializer_class = EmailLogSerializer
    permission_classes = [IsAdminOrHR]
    filterset_fields = ["template_code", "status", "to_email"]


class EmailTemplateViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = EmailTemplate.objects.all().order_by("code")
    serializer_class = EmailTemplateSerializer
    permission_classes = [IsAdmin]
    http_method_names = ["get", "put", "patch", "head", "options"]

    def perform_update(self, serializer):
        obj = serializer.save()
        log_action(self.request, "EMAIL_TEMPLATE_UPDATE", "EmailTemplate", obj.id, {"code": obj.code})


class NotificationViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """Every user only ever sees their own notifications."""
    serializer_class = NotificationSerializer
    filterset_fields = ["is_read", "kind"]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=False, methods=["get"], url_path="unread-count")
    def unread_count(self, request):
        return Response({"unread": self.get_queryset().filter(is_read=False).count()})

    @action(detail=True, methods=["post"], url_path="mark-read")
    def mark_read(self, request, pk=None):
        n = self.get_object()
        if not n.is_read:
            n.is_read, n.read_at = True, timezone.now()
            n.save(update_fields=["is_read", "read_at"])
        return Response(NotificationSerializer(n).data)

    @action(detail=False, methods=["post"], url_path="mark-all-read")
    def mark_all_read(self, request):
        n = self.get_queryset().filter(is_read=False).update(is_read=True, read_at=timezone.now())
        return Response({"marked": n})

    @action(detail=False, methods=["get", "put"])
    def preferences(self, request):
        if request.method == "PUT":
            items = request.data if isinstance(request.data, list) else [request.data]
            s = PreferenceSerializer(data=items, many=True)
            s.is_valid(raise_exception=True)
            for item in s.validated_data:
                NotificationPreference.objects.update_or_create(user=request.user, kind=item["kind"], defaults={"enabled": item["enabled"]})
        saved = dict(NotificationPreference.objects.filter(user=request.user).values_list("kind", "enabled"))
        return Response([{"kind": k, "label": label, "enabled": saved.get(k, True)} for k, label in Notification.Kind.choices])


class BroadcastViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    """Admin announcements to everyone or to one department."""
    queryset = Broadcast.objects.select_related("department", "sent_by")
    serializer_class = BroadcastSerializer
    permission_classes = [IsAdmin]

    def perform_create(self, s):
        d = s.validated_data
        b = send_broadcast(self.request.user, d["title"], d["message"], d.get("department"))
        s.instance = b
        log_action(self.request, "BROADCAST_SEND", "Broadcast", b.id, {"title": b.title, "department": b.department.name if b.department else "All", "recipients": b.recipient_count})
