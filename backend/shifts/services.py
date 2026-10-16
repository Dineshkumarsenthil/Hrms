from datetime import datetime, time, timedelta
from decimal import Decimal

from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from .models import Shift, ShiftAssignment

OVERTIME_MIN_HOURS = Decimal("0.5")  # ignore less than 30 minutes of extra work


def default_shift():
    shift, _ = Shift.objects.get_or_create(
        name="General Shift",
        defaults={"kind": Shift.Kind.GENERAL, "start_time": time(9, 0), "end_time": time(18, 0), "grace_minutes": 15, "work_hours": Decimal("8")},
    )
    return shift


def _active_on(qs, day):
    return qs.filter(start_date__lte=day).filter(Q(end_date__isnull=True) | Q(end_date__gte=day)).order_by("-start_date", "-id")


def assignment_for(employee, day):
    """Employee-level assignment wins over department-level."""
    found = _active_on(ShiftAssignment.objects.filter(employee=employee), day).select_related("shift").first()
    if not found and employee.department_id:
        found = _active_on(ShiftAssignment.objects.filter(department_id=employee.department_id), day).select_related("shift").first()
    return found


def shift_for(employee, day):
    found = assignment_for(employee, day)
    return found.shift if found else default_shift()


def _at(day, t):
    return timezone.make_aware(datetime.combine(day, t))


def shift_window(shift, day):
    """(start, end) datetimes of the shift that begins on `day`; night shifts end the next morning."""
    end_day = day + timedelta(days=1) if shift.is_overnight else day
    return _at(day, shift.start_time), _at(end_day, shift.end_time)


def late_minutes_for(check_in, shift, day):
    if shift.kind == Shift.Kind.FLEXIBLE:
        return 0
    start, _ = shift_window(shift, day)
    late_by = (check_in - start).total_seconds() / 60
    return int(late_by) if late_by > shift.grace_minutes else 0


def shift_metrics(check_in, check_out, shift, day, hours):
    """Early exit minutes and overtime hours for a finished day."""
    early = 0
    if shift.kind != Shift.Kind.FLEXIBLE:
        _, end = shift_window(shift, day)
        if check_out < end:
            early = int((end - check_out).total_seconds() / 60)
    extra = Decimal(hours) - shift.scheduled_hours
    overtime = extra.quantize(Decimal("0.01")) if extra >= OVERTIME_MIN_HOURS else Decimal("0")
    return {"early_exit_minutes": early, "overtime_hours": overtime}


@transaction.atomic
def assign_shift(shift, start_date, user, employee=None, department=None, end_date=None):
    """Create an assignment and close the previous open one, so history stays clean."""
    if not shift.is_active:
        raise ValidationError("This shift is inactive.")
    target = {"employee": employee} if employee else {"department": department}
    existing = ShiftAssignment.objects.filter(**target)
    if existing.filter(start_date__gte=start_date).exists():
        raise ValidationError("This target already has an assignment starting on or after that date.")
    # close whatever is still running when the new shift starts
    existing.filter(Q(end_date__isnull=True) | Q(end_date__gte=start_date)).update(end_date=start_date - timedelta(days=1))
    return ShiftAssignment.objects.create(shift=shift, start_date=start_date, end_date=end_date, assigned_by=user, **target)
