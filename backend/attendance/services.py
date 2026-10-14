import calendar
from datetime import date, timedelta
from decimal import Decimal
from django.conf import settings
from django.db.models import Sum

from .models import Attendance


def working_dates(year, month, start_from=None):
    """Mon-Fri dates of a month (optionally only on/after a joining date)."""
    last = calendar.monthrange(year, month)[1]
    out = []
    for d in range(1, last + 1):
        day = date(year, month, d)
        if day.weekday() in settings.WORKDAYS and (start_from is None or day >= start_from):
            out.append(day)
    return out


def hours_and_status(check_in, check_out):
    hrs = Decimal(str(round((check_out - check_in).total_seconds() / 3600, 2)))
    status = Attendance.Status.PRESENT if hrs >= settings.HALF_DAY_HOURS else Attendance.Status.HALF_DAY
    return hrs, status


def attendance_counts(employee, year, month):
    qs = Attendance.objects.filter(employee=employee, date__year=year, date__month=month)
    present = qs.filter(status="PRESENT").count()
    half = qs.filter(status="HALF_DAY").count()
    hours = qs.aggregate(t=Sum("working_hours"))["t"] or Decimal("0")
    return {"present_days": present, "half_days": half, "present_equivalent": Decimal(present) + Decimal(half) / 2, "total_hours": hours}


def month_summary(employee, year, month):
    from leaves.services import leave_days_in_month
    wdays = working_dates(year, month, employee.joining_date)
    c = attendance_counts(employee, year, month)
    paid, lop = leave_days_in_month(employee, year, month)
    unaccounted = max(Decimal("0"), Decimal(len(wdays)) - c["present_equivalent"] - paid)
    return {
        "employee": employee.id, "employee_code": employee.employee_code, "employee_name": employee.full_name,
        "year": year, "month": month, "working_days": len(wdays),
        "present_days": c["present_days"], "half_days": c["half_days"],
        "paid_leave_days": paid, "lop_leave_days": lop,
        "absent_days": unaccounted, "total_hours": c["total_hours"],
    }
