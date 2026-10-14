import calendar
from datetime import date
from decimal import Decimal
from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAdminOrHR, IsEmployee
from attendance.models import Attendance
from attendance.services import month_summary, working_dates
from audit.utils import log_action
from employees.models import Employee
from leaves.models import LeaveRequest
from leaves.services import ensure_balances
from payroll.models import Payroll
from .exporters import respond


def _date(request, name):
    v = request.query_params.get(name)
    if not v:
        return None
    try:
        return date.fromisoformat(v)
    except ValueError:
        raise ValidationError({name: "Use YYYY-MM-DD."})


class BaseReport(APIView):
    permission_classes = [IsAdminOrHR]
    title = ""
    slug = ""

    def get(self, request):
        columns, rows = self.build(request)
        fmt = request.query_params.get("format", "json")
        if fmt in ("csv", "pdf"):
            log_action(request, "REPORT_EXPORT", "Report", self.slug, {"format": fmt, "filters": dict(request.query_params)})
        return respond(fmt, self.title, columns, rows, f"{self.slug}_report")


class AttendanceReport(BaseReport):
    title, slug = "Attendance Report", "attendance"

    def build(self, request):
        qs = Attendance.objects.select_related("employee__user", "employee__department").order_by("date", "employee__employee_code")
        f, t = _date(request, "date_from"), _date(request, "date_to")
        if f: qs = qs.filter(date__gte=f)
        if t: qs = qs.filter(date__lte=t)
        if request.query_params.get("department"): qs = qs.filter(employee__department_id=request.query_params["department"])
        if request.query_params.get("employee"): qs = qs.filter(employee_id=request.query_params["employee"])
        cols = ["Emp Code", "Name", "Department", "Date", "Check-in", "Check-out", "Hours", "Status", "Overridden"]
        rows = [[a.employee.employee_code, a.employee.full_name, a.employee.department.name if a.employee.department else "-", a.date,
                 timezone.localtime(a.check_in).strftime("%H:%M") if a.check_in else "-",
                 timezone.localtime(a.check_out).strftime("%H:%M") if a.check_out else "-", a.working_hours, a.status, "Yes" if a.is_overridden else "No"] for a in qs]
        return cols, rows


class LeaveReport(BaseReport):
    title, slug = "Leave Report", "leave"

    def build(self, request):
        qs = LeaveRequest.objects.select_related("employee__user", "employee__department", "leave_type").order_by("start_date")
        f, t = _date(request, "date_from"), _date(request, "date_to")
        if f: qs = qs.filter(end_date__gte=f)
        if t: qs = qs.filter(start_date__lte=t)
        if request.query_params.get("department"): qs = qs.filter(employee__department_id=request.query_params["department"])
        if request.query_params.get("status"): qs = qs.filter(status=request.query_params["status"])
        cols = ["Emp Code", "Name", "Department", "Leave Type", "From", "To", "Days", "LOP Days", "Status"]
        rows = [[r.employee.employee_code, r.employee.full_name, r.employee.department.name if r.employee.department else "-", r.leave_type.name,
                 r.start_date, r.end_date, r.days, r.lop_days, r.status] for r in qs]
        return cols, rows


class PayrollReport(BaseReport):
    title, slug = "Payroll Summary", "payroll"

    def build(self, request):
        qs = Payroll.objects.select_related("employee__user", "employee__department").order_by("year", "month", "employee__employee_code")
        f, t = _date(request, "date_from"), _date(request, "date_to")
        if f: qs = qs.filter(year__gte=f.year).exclude(year=f.year, month__lt=f.month)
        if t: qs = qs.filter(year__lte=t.year).exclude(year=t.year, month__gt=t.month)
        if request.query_params.get("department"): qs = qs.filter(employee__department_id=request.query_params["department"])
        cols = ["Period", "Emp Code", "Name", "Department", "Gross", "LOP Days", "LOP Ded.", "PF", "Tax", "Adjust.", "Net", "Status"]
        rows, tot = [], Decimal("0")
        for p in qs:
            rows.append([f"{calendar.month_abbr[p.month]} {p.year}", p.employee.employee_code, p.employee.full_name,
                         p.employee.department.name if p.employee.department else "-", p.gross_salary, p.lop_days, p.lop_deduction,
                         p.pf_deduction, p.tax_deduction, p.adjustment, p.net_salary, p.status])
            tot += p.net_salary
        if rows:
            rows.append(["TOTAL", "", "", "", "", "", "", "", "", "", tot, ""])
        return cols, rows


class AdminDashboard(APIView):
    permission_classes = [IsAdminOrHR]

    def get(self, request):
        today = timezone.localdate()
        emps = Employee.objects.all()
        active = emps.filter(is_active=True)
        checked_in = Attendance.objects.filter(date=today, check_in__isnull=False).count()
        on_leave = LeaveRequest.objects.filter(status="APPROVED", start_date__lte=today, end_date__gte=today).count()
        is_workday = today.weekday() in (0, 1, 2, 3, 4)
        last = Payroll.objects.order_by("-year", "-month").first()
        payroll = None
        if last:
            agg = Payroll.objects.filter(year=last.year, month=last.month).aggregate(n=Count("id"), net=Sum("net_salary"))
            payroll = {"period": f"{calendar.month_name[last.month]} {last.year}", "employees_paid": agg["n"], "total_net": agg["net"],
                       "credited": Payroll.objects.filter(year=last.year, month=last.month, status="CREDITED").count()}
        return Response({
            "employees": {"total": emps.count(), "active": active.count(), "inactive": emps.filter(is_active=False).count(),
                          "by_department": list(active.values("department__name").annotate(count=Count("id")).order_by("-count"))},
            "attendance_today": {"checked_in": checked_in, "on_leave": on_leave,
                                 "not_checked_in": max(0, active.count() - checked_in - on_leave) if is_workday else 0, "is_workday": is_workday},
            "leaves": {"pending": LeaveRequest.objects.filter(status="PENDING").count(),
                       "approved_this_month": LeaveRequest.objects.filter(status="APPROVED", start_date__year=today.year, start_date__month=today.month).count()},
            "payroll": payroll,
        })


class EmployeeDashboard(APIView):
    permission_classes = [IsEmployee]

    def get(self, request):
        emp, today = request.user.employee, timezone.localdate()
        rec = Attendance.objects.filter(employee=emp, date=today).first()
        last = Payroll.objects.filter(employee=emp).order_by("-year", "-month").first()
        from leaves.serializers import LeaveBalanceSerializer
        return Response({
            "today": {"checked_in": bool(rec and rec.check_in), "checked_out": bool(rec and rec.check_out),
                      "check_in": rec.check_in if rec else None, "check_out": rec.check_out if rec else None},
            "month": month_summary(emp, today.year, today.month),
            "leave_balances": LeaveBalanceSerializer(ensure_balances(emp, today.year), many=True).data,
            "pending_leaves": LeaveRequest.objects.filter(employee=emp, status="PENDING").count(),
            "last_payroll": {"id": last.id, "period": f"{calendar.month_name[last.month]} {last.year}", "net": last.net_salary} if last else None,
        })
