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
from notifications.inapp import notify
from shifts.services import late_minutes_for, shift_for, shift_metrics
from .services import hours_and_status, month_summary, open_record


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
        if not rec and hasattr(request.user, "employee"):
            rec = open_record(request.user.employee)  # night shift that started yesterday
        return Response(AttendanceSerializer(rec).data if rec else {"status": None})

    @action(detail=False, methods=["post"], url_path="check-in", permission_classes=[IsEmployee])
    def check_in(self, request):
        emp, today = request.user.employee, timezone.localdate()
        if not emp.is_active:
            return Response({"error": "Inactive employee."}, status=403)
        now = timezone.now()
        shift = shift_for(emp, today)
        late = late_minutes_for(now, shift, today)
        try:
            with transaction.atomic():
                rec = Attendance.objects.create(employee=emp, date=today, check_in=now, status="PRESENT", shift=shift, late_minutes=late)
        except IntegrityError:
            return Response({"error": "You have already checked in today."}, status=400)
        log_action(request, "CHECK_IN", "Attendance", rec.id, {"shift": shift.name, "late_minutes": late})
        if late:
            notify(request.user, "ATTENDANCE", "Late check-in", f"You checked in {late} minutes after the start of {shift.name}.", "/attendance")
        return Response(AttendanceSerializer(rec).data, status=201)

    @action(detail=False, methods=["post"], url_path="check-out", permission_classes=[IsEmployee])
    def check_out(self, request):
        emp = request.user.employee
        rec = open_record(emp)
        if not rec:
            done = Attendance.objects.filter(employee=emp, date=timezone.localdate(), check_out__isnull=False).exists()
            return Response({"error": "You have already checked out today." if done else "You have not checked in today."}, status=400)
        rec.check_out = timezone.now()
        shift = rec.shift or shift_for(emp, rec.date)
        rec.working_hours, rec.status = hours_and_status(rec.check_in, rec.check_out, shift)
        extra = shift_metrics(rec.check_in, rec.check_out, shift, rec.date, rec.working_hours)
        rec.early_exit_minutes, rec.overtime_hours = extra["early_exit_minutes"], extra["overtime_hours"]
        rec.save()
        log_action(request, "CHECK_OUT", "Attendance", rec.id, {"hours": str(rec.working_hours), "overtime": str(rec.overtime_hours)})
        if rec.early_exit_minutes:
            notify(request.user, "ATTENDANCE", "Early check-out", f"You left {rec.early_exit_minutes} minutes before the end of {shift.name}.", "/attendance")
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
        shift = d.get("shift") or shift_for(emp, d["date"])  # admin may pick a different shift for this day
        late, early, overtime = 0, 0, Decimal("0")
        if ci and co:
            hrs, auto_status = hours_and_status(ci, co, shift)
            extra = shift_metrics(ci, co, shift, d["date"], hrs)
            early, overtime = extra["early_exit_minutes"], extra["overtime_hours"]
        else:
            hrs, auto_status = Decimal("0"), None
        if ci:
            late = late_minutes_for(ci, shift, d["date"])
        status = d.get("status") or auto_status
        if status == "ABSENT":
            ci = co = None; hrs = Decimal("0"); late = early = 0; overtime = Decimal("0")
        rec, created = Attendance.objects.update_or_create(
            employee=emp, date=d["date"],
            defaults={"check_in": ci, "check_out": co, "working_hours": hrs, "status": status,
                      "is_overridden": True, "override_note": d["note"], "overridden_by": request.user,
                      "shift": shift, "late_minutes": late, "early_exit_minutes": early, "overtime_hours": overtime})
        log_action(request, "ATTENDANCE_OVERRIDE", "Attendance", rec.id, {"employee": emp.employee_code, "date": str(d["date"]), "status": status, "shift": shift.name, "note": d["note"]})
        notify(emp.user, "ATTENDANCE", "Attendance corrected", f"Your attendance for {d['date']} was corrected by {request.user.username}.", "/attendance")
        return Response(AttendanceSerializer(rec).data, status=201 if created else 200)
