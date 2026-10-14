import random
from datetime import date, datetime, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from attendance.models import Attendance
from attendance.services import working_dates
from employees.models import Department, Employee
from leaves.models import LeaveType
from notifications.models import EmailTemplate
from notifications.templates_default import DEFAULT_TEMPLATES

User = get_user_model()

PEOPLE = [
    ("admin", "Admin", "User", "ADMIN", "Engineering", "System Administrator", 90000),
    ("hr", "Helen", "Roberts", "HR", "Human Resources", "HR Manager", 70000),
    ("dinesh", "Dinesh", "Kumar", "EMPLOYEE", "Engineering", "Software Engineer", 50000),
    ("priya", "Priya", "Sharma", "EMPLOYEE", "Engineering", "QA Engineer", 45000),
    ("arun", "Arun", "Raj", "EMPLOYEE", "Finance", "Accountant", 42000),
    ("meena", "Meena", "Iyer", "EMPLOYEE", "Human Resources", "Recruiter", 40000),
]


class Command(BaseCommand):
    help = "Create sample users, departments, leave types, templates and last month's attendance."

    def handle(self, *args, **opts):
        for name, quota, paid in [("Casual Leave", 12, True), ("Sick Leave", 10, True), ("Earned Leave", 15, True), ("Loss of Pay", 0, False)]:
            LeaveType.objects.get_or_create(name=name, defaults={"annual_quota": quota, "is_paid": paid})
        for code, (subj, body) in DEFAULT_TEMPLATES.items():
            EmailTemplate.objects.get_or_create(code=code, defaults={"subject": subj, "body": body})

        for i, (uname, fn, ln, role, dept, desig, basic) in enumerate(PEOPLE, start=1):
            d, _ = Department.objects.get_or_create(name=dept)
            pwd = {"admin": "Admin@123", "hr": "Hr@12345"}.get(uname, "Employee@123")
            user, created = User.objects.get_or_create(username=uname, defaults={"email": f"{uname}@hrms.local", "first_name": fn, "last_name": ln, "role": role})
            if created:
                user.set_password(pwd); user.save()
            if role == "ADMIN":
                user.is_staff = user.is_superuser = True; user.save()
            Employee.objects.get_or_create(user=user, defaults=dict(
                employee_code=f"EMP{i:03d}", department=d, designation=desig, joining_date=date(2025, 1, 15),
                basic_salary=Decimal(basic), hra=Decimal(basic) * Decimal("0.4"), allowances=Decimal(basic) * Decimal("0.2"), tax_deduction=Decimal("1000")))

        # last month's attendance so payroll can be generated immediately
        today = timezone.localdate()
        first_this = today.replace(day=1)
        last_month_end = first_this - timedelta(days=1)
        random.seed(7)
        tz = timezone.get_current_timezone()
        for emp in Employee.objects.all():
            for day in working_dates(last_month_end.year, last_month_end.month, emp.joining_date):
                if Attendance.objects.filter(employee=emp, date=day).exists():
                    continue
                if random.random() < 0.06:  # occasional absence -> LOP in payroll
                    continue
                ci = timezone.make_aware(datetime(day.year, day.month, day.day, 9, random.randint(0, 40)), tz)
                co = ci + timedelta(hours=8, minutes=random.randint(0, 45))
                Attendance.objects.create(employee=emp, date=day, check_in=ci, check_out=co, working_hours=Decimal(str(round((co - ci).total_seconds() / 3600, 2))), status="PRESENT")
        self.stdout.write(self.style.SUCCESS("Seed complete.\n  admin / Admin@123\n  hr / Hr@12345\n  dinesh, priya, arun, meena / Employee@123"))
