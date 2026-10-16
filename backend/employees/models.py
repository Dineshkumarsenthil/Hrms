import os
import uuid
from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Employee(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="employee")
    employee_code = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, null=True, on_delete=models.SET_NULL, related_name="employees")
    designation = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    joining_date = models.DateField()
    region = models.CharField(max_length=50, blank=True, help_text="Work region, used for regional holidays")
    # salary structure (monthly)
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    hra = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    allowances = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    pf_percent = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal("12"), help_text="PF % of basic")
    tax_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["employee_code"]

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username

    @property
    def gross_salary(self):
        return self.basic_salary + self.hra + self.allowances

    def __str__(self):
        return f"{self.employee_code} - {self.full_name}"


def validate_upload(f):
    ext = os.path.splitext(f.name)[1].lower()
    if ext not in settings.ALLOWED_UPLOAD_EXTENSIONS:
        raise ValidationError(f"File type {ext or '(none)'} not allowed. Allowed: {', '.join(settings.ALLOWED_UPLOAD_EXTENSIONS)}")
    if f.size > settings.MAX_UPLOAD_MB * 1024 * 1024:
        raise ValidationError(f"File too large (max {settings.MAX_UPLOAD_MB} MB).")


def document_path(instance, filename):
    # random name: never trust the client's filename on disk
    ext = os.path.splitext(filename)[1].lower()
    return f"documents/{instance.employee_id}/{uuid.uuid4().hex}{ext}"


class EmployeeDocument(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="documents")
    title = models.CharField(max_length=100)
    original_name = models.CharField(max_length=255, blank=True)
    file = models.FileField(upload_to=document_path, validators=[validate_upload])
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]
