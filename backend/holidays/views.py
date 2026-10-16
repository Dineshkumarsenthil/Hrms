from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from django.db.models import Q

from accounts.permissions import IsAdminOrHR
from audit.utils import log_action
from .models import Holiday
from .serializers import HolidaySerializer


class HolidayViewSet(viewsets.ModelViewSet):
    """Everyone can read. Only Admin/HR can create, edit or delete.

    ?year=2026 gives the yearly view, ?year=2026&month=10 the monthly view."""
    serializer_class = HolidaySerializer
    pagination_class = None
    filterset_fields = ["kind", "region", "is_active"]

    def get_permissions(self):
        if self.request.method in ("GET", "HEAD", "OPTIONS"):
            return super().get_permissions()
        return [IsAdminOrHR()]

    def get_queryset(self):
        qs = Holiday.objects.all()
        user = self.request.user
        if not user.is_hr_or_admin:
            # employees see active company + optional holidays and the ones of their own region
            region = user.employee.region if hasattr(user, "employee") else ""
            qs = qs.filter(is_active=True).filter(Q(kind__in=["COMPANY", "OPTIONAL"]) | Q(kind="REGIONAL", region__iexact=region))

        p = self.request.query_params
        try:
            if p.get("year"):
                qs = qs.filter(date__year=int(p["year"]))
            if p.get("month"):
                qs = qs.filter(date__month=int(p["month"]))
        except ValueError:
            raise ValidationError("year and month must be numbers.")
        return qs

    def perform_create(self, s):
        h = s.save()
        log_action(self.request, "HOLIDAY_CREATE", "Holiday", h.id, {"name": h.name, "date": str(h.date), "kind": h.kind})

    def perform_update(self, s):
        h = s.save()
        log_action(self.request, "HOLIDAY_UPDATE", "Holiday", h.id, {"name": h.name, "date": str(h.date)})

    def perform_destroy(self, h):
        log_action(self.request, "HOLIDAY_DELETE", "Holiday", h.id, {"name": h.name, "date": str(h.date)})
        h.delete()
