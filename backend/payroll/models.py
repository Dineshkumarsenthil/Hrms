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
    # added with the advanced payroll module (old rows keep the default 0)
    variable_pay = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    overtime_hours = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("0"))
    overtime_pay = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    other_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"), help_text="Deduction components other than PF and tax")
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


class SalaryComponent(models.Model):
    """One line of a salary structure, e.g. Basic, HRA, Conveyance, Performance Bonus, PF."""
    class Kind(models.TextChoices):
        EARNING = "EARNING", "Earning"
        DEDUCTION = "DEDUCTION", "Deduction"

    class Calc(models.TextChoices):
        FIXED = "FIXED", "Fixed amount"
        PERCENT_OF_BASIC = "PERCENT_OF_BASIC", "% of basic"

    name = models.CharField(max_length=60, unique=True)
    code = models.CharField(max_length=20, unique=True)
    kind = models.CharField(max_length=10, choices=Kind.choices)
    calc_type = models.CharField(max_length=20, choices=Calc.choices, default=Calc.FIXED)
    is_variable = models.BooleanField(default=False, help_text="Amount is entered every month (bonus, incentive) instead of being part of the structure")
    is_system = models.BooleanField(default=False, help_text="Used by payroll rules, cannot be deleted")
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveSmallIntegerField(default=50)

    class Meta:
        ordering = ["kind", "display_order", "name"]

    def __str__(self):
        return self.name


class SalaryStructure(models.Model):
    """A version of an employee's salary. Revising pay adds a new row; old rows stay as history."""
    employee = models.ForeignKey("employees.Employee", on_delete=models.CASCADE, related_name="structures")
    effective_from = models.DateField(db_index=True)
    reason = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-effective_from", "-id"]
        constraints = [models.UniqueConstraint(fields=["employee", "effective_from"], name="one_structure_per_start_date")]


class SalaryStructureItem(models.Model):
    structure = models.ForeignKey(SalaryStructure, on_delete=models.CASCADE, related_name="items")
    component = models.ForeignKey(SalaryComponent, on_delete=models.PROTECT, related_name="+")
    value = models.DecimalField(max_digits=10, decimal_places=2, help_text="Amount, or percent when the component is % of basic")

    class Meta:
        constraints = [models.UniqueConstraint(fields=["structure", "component"], name="one_item_per_component")]


class MonthlyVariablePay(models.Model):
    """Bonus / incentive entered for one employee and one month, before payroll is generated."""
    employee = models.ForeignKey("employees.Employee", on_delete=models.CASCADE, related_name="variable_pay")
    year = models.PositiveIntegerField()
    month = models.PositiveIntegerField()
    component = models.ForeignKey(SalaryComponent, on_delete=models.PROTECT, related_name="+")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    note = models.CharField(max_length=255, blank=True)
    entered_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-year", "-month", "employee__employee_code"]
        constraints = [models.UniqueConstraint(fields=["employee", "year", "month", "component"], name="one_variable_pay_per_month")]


class PayrollLine(models.Model):
    """Snapshot of the breakdown shown on the pay slip. Copied at generation time so later salary revisions never change old slips."""
    payroll = models.ForeignKey(Payroll, on_delete=models.CASCADE, related_name="lines")
    name = models.CharField(max_length=80)
    code = models.CharField(max_length=20)
    kind = models.CharField(max_length=10, choices=SalaryComponent.Kind.choices)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["kind", "order", "id"]
