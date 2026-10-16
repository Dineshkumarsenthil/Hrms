from decimal import Decimal
from django.conf import settings
from django.db import models
from django.db.models import Q


class Shift(models.Model):
    class Kind(models.TextChoices):
        GENERAL = "GENERAL", "General"
        NIGHT = "NIGHT", "Night"
        FLEXIBLE = "FLEXIBLE", "Flexible"
        REMOTE = "REMOTE", "Remote"

    name = models.CharField(max_length=60, unique=True)
    kind = models.CharField(max_length=10, choices=Kind.choices, default=Kind.GENERAL)
    start_time = models.TimeField()
    end_time = models.TimeField()
    grace_minutes = models.PositiveSmallIntegerField(default=10, help_text="Check-in allowed this many minutes after start without being late")
    work_hours = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal("8"), help_text="Expected working hours per day. Less than half of this is a half day")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["start_time", "name"]

    @property
    def is_overnight(self):
        return self.end_time <= self.start_time

    @property
    def scheduled_hours(self):
        """Length of the shift window, e.g. 09:00-18:00 = 9 hours. Overtime starts after this."""
        start = self.start_time.hour * 60 + self.start_time.minute
        end = self.end_time.hour * 60 + self.end_time.minute
        minutes = end - start if end > start else end + 24 * 60 - start
        return Decimal(minutes) / 60

    def __str__(self):
        return f"{self.name} ({self.start_time:%H:%M}-{self.end_time:%H:%M})"


class ShiftAssignment(models.Model):
    """One row per period an employee (or a whole department) works a shift. Old rows are kept as shift history."""
    shift = models.ForeignKey(Shift, on_delete=models.PROTECT, related_name="assignments")
    employee = models.ForeignKey("employees.Employee", null=True, blank=True, on_delete=models.CASCADE, related_name="shift_assignments")
    department = models.ForeignKey("employees.Department", null=True, blank=True, on_delete=models.CASCADE, related_name="shift_assignments")
    start_date = models.DateField(db_index=True)
    end_date = models.DateField(null=True, blank=True)
    assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-start_date", "-id"]
        constraints = [
            # an assignment belongs to an employee OR a department, never both and never neither
            models.CheckConstraint(
                condition=(Q(employee__isnull=False, department__isnull=True) | Q(employee__isnull=True, department__isnull=False)),
                name="assignment_employee_xor_department",
            ),
        ]
        indexes = [models.Index(fields=["employee", "start_date"]), models.Index(fields=["department", "start_date"])]
