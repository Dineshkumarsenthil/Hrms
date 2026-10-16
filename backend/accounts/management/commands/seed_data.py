import random
from datetime import date, datetime, time, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from attendance.models import Attendance
from attendance.services import hours_and_status, working_dates
from employees.models import Department, Employee
from holidays.models import Holiday
from leaves.models import LeaveType
from notifications.inapp import send_broadcast
from notifications.models import EmailTemplate, Notification
from notifications.templates_default import DEFAULT_TEMPLATES
from payroll import services as payroll_services
from payroll.models import MonthlyVariablePay, SalaryComponent
from shifts.models import Shift
from shifts.services import assign_shift, default_shift, late_minutes_for, shift_for, shift_metrics

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

        self.seed_holidays()
        self.seed_shifts()
        self.seed_salary_structures()

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
                shift = shift_for(emp, day)
                start = timezone.make_aware(datetime.combine(day, shift.start_time), tz)
                ci = start + timedelta(minutes=random.randint(-10, 40))
                co = ci + timedelta(hours=float(shift.scheduled_hours), minutes=random.randint(-20, 60))
                hours, status = hours_and_status(ci, co, shift)
                extra = shift_metrics(ci, co, shift, day, hours)
                Attendance.objects.create(employee=emp, date=day, check_in=ci, check_out=co, working_hours=hours, status=status, shift=shift,
                                          late_minutes=late_minutes_for(ci, shift, day), **extra)
        self.seed_variable_pay(last_month_end)
        if not Notification.objects.exists():
            send_broadcast(User.objects.get(username="admin"), "Welcome to the new HRMS", "Holidays, shifts, notifications and a detailed payroll are now available.")
        self.stdout.write(self.style.SUCCESS("Seed complete.\n  admin / Admin@123\n  hr / Hr@12345\n  dinesh, priya, arun, meena / Employee@123"))

    def seed_holidays(self):
        year = timezone.localdate().year
        sample = [
            ("New Year's Day", date(year, 1, 1), "COMPANY", ""), ("Republic Day", date(year, 1, 26), "COMPANY", ""),
            ("Pongal", date(year, 1, 15), "REGIONAL", "Tamil Nadu"), ("Tamil New Year", date(year, 4, 14), "REGIONAL", "Tamil Nadu"),
            ("May Day", date(year, 5, 1), "COMPANY", ""), ("Independence Day", date(year, 8, 15), "COMPANY", ""),
            ("Gandhi Jayanti", date(year, 10, 2), "COMPANY", ""), ("Christmas", date(year, 12, 25), "COMPANY", ""),
            ("Good Friday", date(year, 4, 3), "OPTIONAL", ""), ("Raksha Bandhan", date(year, 8, 28), "OPTIONAL", ""),
        ]
        for name, day, kind, region in sample:
            Holiday.objects.get_or_create(date=day, name=name, defaults={"kind": kind, "region": region})

    def seed_shifts(self):
        default_shift()
        for name, kind, start, end, grace, hours in [("Night Shift", "NIGHT", time(21, 0), time(6, 0), 15, 8), ("Flexible Shift", "FLEXIBLE", time(10, 0), time(19, 0), 60, 8),
                                                     ("Remote Shift", "REMOTE", time(9, 30), time(18, 30), 30, 8)]:
            Shift.objects.get_or_create(name=name, defaults={"kind": kind, "start_time": start, "end_time": end, "grace_minutes": grace, "work_hours": hours})
        # Finance works the remote shift, so the sample data shows department-level assignment
        finance = Department.objects.filter(name="Finance").first()
        remote = Shift.objects.get(name="Remote Shift")
        if finance and not finance.shift_assignments.exists():
            assign_shift(remote, date(2025, 1, 15), User.objects.get(username="admin"), department=finance)

    def seed_salary_structures(self):
        comps = payroll_services.default_components()
        conveyance, _ = SalaryComponent.objects.get_or_create(code="CONVEYANCE", defaults={"name": "Conveyance Allowance", "kind": "EARNING", "display_order": 5})
        admin = User.objects.get(username="admin")
        for emp in Employee.objects.all():
            if emp.structures.exists():
                continue
            items = payroll_services.legacy_items(emp) + [(conveyance, Decimal("1600"))]
            payroll_services.create_structure(emp, emp.joining_date, "Initial salary structure", items, admin)

    def seed_variable_pay(self, month_end):
        emp = Employee.objects.filter(user__username="dinesh").first()
        bonus = SalaryComponent.objects.filter(code="BONUS").first()
        if emp and bonus:
            MonthlyVariablePay.objects.get_or_create(employee=emp, year=month_end.year, month=month_end.month, component=bonus,
                                                     defaults={"amount": Decimal("5000"), "note": "Sprint delivery bonus"})
