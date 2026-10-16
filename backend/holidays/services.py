import calendar
from datetime import date

from .models import Holiday


def holiday_dates(start, end, region=""):
    """Dates between start and end (inclusive) that are NOT working days.

    Company holidays apply to everyone. Regional holidays apply only to employees
    of the same region. Optional holidays never remove a working day."""
    qs = Holiday.objects.filter(is_active=True, date__gte=start, date__lte=end)
    days = set()
    for h in qs:
        if h.kind == Holiday.Kind.COMPANY:
            days.add(h.date)
        elif h.kind == Holiday.Kind.REGIONAL and region and h.region.lower() == region.lower():
            days.add(h.date)
    return days


def month_holiday_dates(year, month, region=""):
    last = calendar.monthrange(year, month)[1]
    return holiday_dates(date(year, month, 1), date(year, month, last), region)
