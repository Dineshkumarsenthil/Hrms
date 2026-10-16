"""Small helpers shared by the test files of the new modules."""
from datetime import date
from decimal import Decimal
from itertools import count

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from employees.models import Department, Employee

User = get_user_model()
_ids = count(1)


def make_user(role="EMPLOYEE", **extra):
    n = next(_ids)
    return User.objects.create_user(username=f"{role.lower()}{n}", email=f"{role.lower()}{n}@test.local", password="Test@12345", role=role, **extra)


def make_employee(role="EMPLOYEE", department=None, region="", joining=date(2026, 1, 1), basic="30000", hra="10000", allowances="0", pf="12", tax="0"):
    user = make_user(role)
    n = next(_ids)
    return Employee.objects.create(user=user, employee_code=f"T{n:03d}", department=department, designation="Tester", joining_date=joining, region=region,
                                   basic_salary=Decimal(basic), hra=Decimal(hra), allowances=Decimal(allowances), pf_percent=Decimal(pf), tax_deduction=Decimal(tax))


def make_department(name="QA"):
    return Department.objects.get_or_create(name=name)[0]


def client_for(user):
    c = APIClient()
    c.force_authenticate(user)
    return c
