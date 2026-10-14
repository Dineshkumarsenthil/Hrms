from datetime import date
from decimal import Decimal
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.permissions import IsAdminOrHR, IsEmployee
from audit.utils import log_action
from employees.models import Employee
from .models import Attendance
from .serializers import AttendanceSerializer, OverrideSerializer
from .services import hours_and_status, month_summary


def _month_year(request):
    today = timezone.localdate()
    try:
        return int(request.query_params.get("year", today.year)), int(request.query_params.get("month", today.month))
    except ValueError:
        from rest_framework.exceptions import ValidationError
        raise ValidationError("year and month must be numbers.")


class AttendanceViewSet(viewsets.ReadOnlyModelViewSet):
    """HR/Admin see everyone; employees see only their own rows."""
    serializer_class = AttendanceSerializer
    filterset_fields = {"date": ["exact", "gte", "lte"], "employee": ["exact"], "employee__department": ["exact"], "status": ["exact"]}
    ordering_fields = ["date"]

    def get_queryset(self):
        qs = Attendance.objects.select_related("employee__user", "employee__department")
        u = self.request.user
        return qs if u.is_hr_or_admin else qs.filter(employee__user=u)

    @action(detail=False, methods=["get"], url_path="today")
    def today(self, request):
        rec = Attendance.objects.filter(employee__user=request.user, date=timezone.localdate()).first()
        return Response(AttendanceSerializer(rec).data if rec else {"status": None})

    @action(detail=False, methods=["post"], url_path="check-in", permission_classes=[IsEmployee])
    def check_in(self, request):
        emp, today = request.user.employee, timezone.localdate()
        if not emp.is_active:
            return Response({"error": "Inactive employee."}, status=403)
        try:
            with transaction.atomic():
                rec = Attendance.objects.create(employee=emp, date=today, check_in=timezone.now(), status="PRESENT")
        except IntegrityError:
            return Response({"error": "You have already checked in today."}, status=400)
        log_action(request, "CHECK_IN", "Attendance", rec.id)
        return Response(AttendanceSerializer(rec).data, status=201)

    @action(detail=False, methods=["post"], url_path="check-out", permission_classes=[IsEmployee])
    def check_out(self, request):
        rec = Attendance.objects.filter(employee__user=request.user, date=timezone.localdate()).first()
        if not rec or not rec.check_in:
            return Response({"error": "You have not checked in today."}, status=400)
        if rec.check_out:
            return Response({"error": "You have already checked out today."}, status=400)
        rec.check_out = timezone.now()
        rec.working_hours, rec.status = hours_and_status(rec.check_in, rec.check_out)
        rec.save()
        log_action(request, "CHECK_OUT", "Attendance", rec.id, {"hours": str(rec.working_hours)})
        return Response(AttendanceSerializer(rec).data)

    @action(detail=False, methods=["get"], url_path="my-summary", permission_classes=[IsEmployee])
    def my_summary(self, request):
        y, m = _month_year(request)
        return Response(month_summary(request.user.employee, y, m))

    @action(detail=False, methods=["get"], url_path="summary", permission_classes=[IsAdminOrHR])
    def summary(self, request):
        y, m = _month_year(request)
        emps = Employee.objects.filter(is_active=True).select_related("user", "department")
        if request.query_params.get("department"):
            emps = emps.filter(department_id=request.query_params["department"])
        return Response([month_summary(e, y, m) for e in emps])

    @action(detail=False, methods=["post"], url_path="override", permission_classes=[IsAdminOrHR])
    def override(self, request):
        s = OverrideSerializer(data=request.data); s.is_valid(raise_exception=True); d = s.validated_data
        emp = get_object_or_404(Employee, pk=d["employee"])
        ci, co = d.get("check_in"), d.get("check_out")
        if ci and co:
            hrs, auto_status = hours_and_status(ci, co)
        else:
            hrs, auto_status = Decimal("0"), None
        status = d.get("status") or auto_status
        if status == "ABSENT":
            ci = co = None; hrs = Decimal("0")
        rec, created = Attendance.objects.update_or_create(
            employee=emp, date=d["date"],
            defaults={"check_in": ci, "check_out": co, "working_hours": hrs, "status": status,
                      "is_overridden": True, "override_note": d["note"], "overridden_by": request.user})
        log_action(request, "ATTENDANCE_OVERRIDE", "Attendance", rec.id, {"employee": emp.employee_code, "date": str(d["date"]), "status": status, "note": d["note"]})
        return Response(AttendanceSerializer(rec).data, status=201 if created else 200)
