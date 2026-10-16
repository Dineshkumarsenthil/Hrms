import calendar
from datetime import date, timedelta
from decimal import Decimal
from django.conf import settings
from django.db.models import F, Sum
from django.utils import timezone

from holidays.services import month_holiday_dates
from .models import Attendance


def working_dates(year, month, start_from=None, region=""):
    """Mon-Fri dates of a month, minus holidays (optionally only on/after a joining date)."""
    off_days = month_holiday_dates(year, month, region)
    last = calendar.monthrange(year, month)[1]
    out = []
    for d in range(1, last + 1):
        day = date(year, month, d)
        if day.weekday() not in settings.WORKDAYS or day in off_days:
            continue
        if start_from is None or day >= start_from:
            out.append(day)
    return out


def hours_and_status(check_in, check_out, shift=None):
    """Worked hours and Present / Half day. Half day = less than half of the shift's expected hours."""
    hrs = Decimal(str(round((check_out - check_in).total_seconds() / 3600, 2)))
    limit = (shift.work_hours / 2) if shift else Decimal(settings.HALF_DAY_HOURS)
    status = Attendance.Status.PRESENT if hrs >= limit else Attendance.Status.HALF_DAY
    return hrs, status


def open_record(employee):
    """The record still waiting for a check-out. Night shifts check out the next morning, so look back one day."""
    today = timezone.localdate()
    waiting = Attendance.objects.filter(employee=employee, check_in__isnull=False, check_out__isnull=True)
    rec = waiting.filter(date=today).first()
    if rec:
        return rec
    # yesterday only counts when it was an overnight shift (end time is earlier than start time)
    return waiting.filter(date=today - timedelta(days=1), shift__end_time__lte=F("shift__start_time")).first()


def attendance_counts(employee, year, month):
    qs = Attendance.objects.filter(employee=employee, date__year=year, date__month=month)
    present = qs.filter(status="PRESENT").count()
    half = qs.filter(status="HALF_DAY").count()
    totals = qs.aggregate(hours=Sum("working_hours"), overtime=Sum("overtime_hours"))
    return {"present_days": present, "half_days": half, "present_equivalent": Decimal(present) + Decimal(half) / 2,
            "total_hours": totals["hours"] or Decimal("0"), "overtime_hours": totals["overtime"] or Decimal("0"),
            "late_days": qs.filter(late_minutes__gt=0).count()}


def month_summary(employee, year, month):
    from leaves.services import leave_days_in_month
    wdays = working_dates(year, month, employee.joining_date, employee.region)
    weekday_holidays = [d for d in month_holiday_dates(year, month, employee.region) if d.weekday() in settings.WORKDAYS]
    c = attendance_counts(employee, year, month)
    paid, lop = leave_days_in_month(employee, year, month)
    unaccounted = max(Decimal("0"), Decimal(len(wdays)) - c["present_equivalent"] - paid)
    return {
        "employee": employee.id, "employee_code": employee.employee_code, "employee_name": employee.full_name,
        "year": year, "month": month, "working_days": len(wdays), "holidays": len(weekday_holidays),
        "present_days": c["present_days"], "half_days": c["half_days"],
        "paid_leave_days": paid, "lop_leave_days": lop,
        "absent_days": unaccounted, "total_hours": c["total_hours"],
        "late_days": c["late_days"], "overtime_hours": c["overtime_hours"],
    }
