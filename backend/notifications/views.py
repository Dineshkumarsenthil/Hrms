from rest_framework import mixins, viewsets
from accounts.permissions import IsAdmin, IsAdminOrHR
from audit.utils import log_action
from .models import EmailLog, EmailTemplate
from .serializers import EmailLogSerializer, EmailTemplateSerializer


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
