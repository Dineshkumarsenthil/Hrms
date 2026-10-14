from decimal import Decimal
from django.conf import settings
from django.db import models


class LeaveType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    annual_quota = models.DecimalField(max_digits=5, decimal_places=1, default=Decimal("0"))
    is_paid = models.BooleanField(default=True, help_text="Unpaid types (e.g. Loss of Pay) are always LOP")

    def __str__(self):
        return self.name


class LeaveBalance(models.Model):
    employee = models.ForeignKey("employees.Employee", on_delete=models.CASCADE, related_name="leave_balances")
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    year = models.PositiveIntegerField()
    allocated = models.DecimalField(max_digits=5, decimal_places=1, default=Decimal("0"))
    used = models.DecimalField(max_digits=5, decimal_places=1, default=Decimal("0"))

    class Meta:
        constraints = [models.UniqueConstraint(fields=["employee", "leave_type", "year"], name="uniq_balance")]

    @property
    def remaining(self):
        return self.allocated - self.used


class LeaveRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
        CANCELLED = "CANCELLED", "Cancelled"

    employee = models.ForeignKey("employees.Employee", on_delete=models.CASCADE, related_name="leave_requests")
    leave_type = models.ForeignKey(LeaveType, on_delete=models.PROTECT)
    start_date = models.DateField(db_index=True)
    end_date = models.DateField()
    days = models.DecimalField(max_digits=5, decimal_places=1)
    lop_days = models.DecimalField(max_digits=5, decimal_places=1, default=Decimal("0"))
    reason = models.CharField(max_length=500)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING, db_index=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    reviewed_at = models.DateTimeField(null=True, blank=True)
    remarks = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-applied_at"]
