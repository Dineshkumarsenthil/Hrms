from decimal import Decimal
from django.conf import settings
from django.db import models


class Payroll(models.Model):
    class Status(models.TextChoices):
        GENERATED = "GENERATED", "Generated"
        CREDITED = "CREDITED", "Credited (simulated)"

    employee = models.ForeignKey("employees.Employee", on_delete=models.PROTECT, related_name="payrolls")
    year = models.PositiveIntegerField(db_index=True)
    month = models.PositiveIntegerField(db_index=True)
    working_days = models.PositiveIntegerField()
    present_days = models.DecimalField(max_digits=5, decimal_places=1)
    paid_leave_days = models.DecimalField(max_digits=5, decimal_places=1, default=Decimal("0"))
    lop_days = models.DecimalField(max_digits=5, decimal_places=1, default=Decimal("0"))
    # earnings (full monthly structure)
    basic = models.DecimalField(max_digits=10, decimal_places=2)
    hra = models.DecimalField(max_digits=10, decimal_places=2)
    allowances = models.DecimalField(max_digits=10, decimal_places=2)
    gross_salary = models.DecimalField(max_digits=10, decimal_places=2)
    # deductions
    lop_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    pf_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    tax_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    adjustment = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"), help_text="+ bonus / - extra deduction")
    adjustment_note = models.CharField(max_length=255, blank=True)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.GENERATED, db_index=True)
    locked = models.BooleanField(default=True)
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="+")
    generated_at = models.DateTimeField(auto_now_add=True)
    credited_at = models.DateTimeField(null=True, blank=True)
    transaction_ref = models.CharField(max_length=40, blank=True)

    class Meta:
        ordering = ["-year", "-month", "employee__employee_code"]
        constraints = [models.UniqueConstraint(fields=["employee", "year", "month"], name="one_payroll_per_month")]


class SalarySlip(models.Model):
    payroll = models.OneToOneField(Payroll, on_delete=models.CASCADE, related_name="slip")
    file = models.FileField(upload_to="slips/")
    generated_at = models.DateTimeField(auto_now=True)
