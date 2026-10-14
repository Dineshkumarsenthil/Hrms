from decimal import Decimal
from django.conf import settings
from django.db import models


class Attendance(models.Model):
    class Status(models.TextChoices):
        PRESENT = "PRESENT", "Present"
        HALF_DAY = "HALF_DAY", "Half day"
        ABSENT = "ABSENT", "Absent"

    employee = models.ForeignKey("employees.Employee", on_delete=models.CASCADE, related_name="attendance")
    date = models.DateField(db_index=True)
    check_in = models.DateTimeField(null=True, blank=True)
    check_out = models.DateTimeField(null=True, blank=True)
    working_hours = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0"))
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PRESENT)
    is_overridden = models.BooleanField(default=False)
    override_note = models.CharField(max_length=255, blank=True)
    overridden_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")

    class Meta:
        ordering = ["-date"]
        constraints = [models.UniqueConstraint(fields=["employee", "date"], name="one_attendance_per_day")]  # DB-level duplicate guard
        indexes = [models.Index(fields=["employee", "date"])]
