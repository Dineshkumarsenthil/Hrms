from datetime import timedelta
from decimal import Decimal
from django.conf import settings

from holidays.services import holiday_dates
from .models import LeaveBalance, LeaveRequest, LeaveType


def working_days_between(start, end, region=""):
    """Mon-Fri dates in the range that are not holidays for the given region."""
    off_days = holiday_dates(start, end, region)
    d, out = start, []
    while d <= end:
        if d.weekday() in settings.WORKDAYS and d not in off_days:
            out.append(d)
        d += timedelta(days=1)
    return out


def ensure_balances(employee, year):
    for lt in LeaveType.objects.all():
        LeaveBalance.objects.get_or_create(employee=employee, leave_type=lt, year=year, defaults={"allocated": lt.annual_quota})
    return LeaveBalance.objects.filter(employee=employee, year=year).select_related("leave_type")


def leave_days_in_month(employee, year, month):
    """(paid_days, lop_days) of APPROVED leave falling on working dates of the month.
    Within a request, paid days come first and LOP days are the last `lop_days` working dates."""
    from datetime import date
    import calendar
    first, last = date(year, month, 1), date(year, month, calendar.monthrange(year, month)[1])
    reqs = LeaveRequest.objects.filter(employee=employee, status="APPROVED", start_date__lte=last, end_date__gte=first)
    paid = lop = Decimal("0")
    for r in reqs:
        dates = working_days_between(r.start_date, r.end_date, employee.region)
        split = len(dates) - int(r.lop_days)
        for i, d in enumerate(dates):
            if first <= d <= last:
                if i < split:
                    paid += 1
                else:
                    lop += 1
    return paid, lop
