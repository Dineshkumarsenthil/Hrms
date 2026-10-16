from datetime import date

from django.test import TestCase

from attendance.services import month_summary, working_dates
from config.testing import client_for, make_employee, make_user
from leaves.services import working_days_between
from .models import Holiday


class HolidayApiTests(TestCase):
    def setUp(self):
        self.admin = client_for(make_user("ADMIN"))
        self.hr = client_for(make_user("HR"))
        self.emp = client_for(make_employee().user)

    def create(self, client, **extra):
        body = {"name": "Founders Day", "date": "2026-08-14", "kind": "COMPANY", **extra}
        return client.post("/api/holidays/", body, format="json")

    def test_admin_and_hr_can_create_employee_cannot(self):
        self.assertEqual(self.create(self.admin).status_code, 201)
        self.assertEqual(self.create(self.hr, name="Another", date="2026-08-17").status_code, 201)
        self.assertEqual(self.create(self.emp, name="Nope", date="2026-08-18").status_code, 403)

    def test_everyone_can_read(self):
        self.create(self.admin)
        r = self.emp.get("/api/holidays/?year=2026&month=8")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json()), 1)

    def test_regional_holiday_needs_region(self):
        self.assertEqual(self.create(self.admin, kind="REGIONAL").status_code, 400)
        self.assertEqual(self.create(self.admin, kind="REGIONAL", region="Tamil Nadu").status_code, 201)

    def test_duplicate_is_rejected(self):
        self.create(self.admin)
        self.assertEqual(self.create(self.admin).status_code, 400)

    def test_employee_only_sees_own_region(self):
        self.create(self.admin, name="Pongal", date="2026-01-15", kind="REGIONAL", region="Tamil Nadu")
        self.create(self.admin, name="Onam", date="2026-08-26", kind="REGIONAL", region="Kerala")
        tn = client_for(make_employee(region="Tamil Nadu").user)
        names = [h["name"] for h in tn.get("/api/holidays/").json()]
        self.assertEqual(names, ["Pongal"])

    def test_delete_is_admin_or_hr_only(self):
        hid = self.create(self.admin).json()["id"]
        self.assertEqual(self.emp.delete(f"/api/holidays/{hid}/").status_code, 403)
        self.assertEqual(self.hr.delete(f"/api/holidays/{hid}/").status_code, 204)


class HolidayCalculationTests(TestCase):
    """Holidays must disappear from working days everywhere (attendance, leave, payroll)."""

    def test_company_holiday_removed_from_working_dates(self):
        before = len(working_dates(2026, 8))
        Holiday.objects.create(name="Company day", date=date(2026, 8, 14), kind="COMPANY")  # a Friday
        self.assertEqual(len(working_dates(2026, 8)), before - 1)

    def test_holiday_on_weekend_changes_nothing(self):
        before = len(working_dates(2026, 8))
        Holiday.objects.create(name="Independence Day", date=date(2026, 8, 15), kind="COMPANY")  # a Saturday
        self.assertEqual(len(working_dates(2026, 8)), before)

    def test_regional_holiday_only_for_that_region(self):
        Holiday.objects.create(name="Onam", date=date(2026, 8, 26), kind="REGIONAL", region="Kerala")
        self.assertEqual(len(working_dates(2026, 8, region="Kerala")), len(working_dates(2026, 8)) - 1)
        self.assertEqual(len(working_dates(2026, 8, region="Tamil Nadu")), len(working_dates(2026, 8)))

    def test_optional_and_inactive_holidays_do_not_count(self):
        Holiday.objects.create(name="Optional", date=date(2026, 8, 12), kind="OPTIONAL")
        Holiday.objects.create(name="Cancelled", date=date(2026, 8, 13), kind="COMPANY", is_active=False)
        self.assertEqual(len(working_dates(2026, 8)), 21)

    def test_leave_days_skip_holidays(self):
        Holiday.objects.create(name="Mid week", date=date(2026, 8, 12), kind="COMPANY")  # Wednesday
        days = working_days_between(date(2026, 8, 10), date(2026, 8, 14))  # Mon-Fri
        self.assertEqual(len(days), 4)

    def test_monthly_summary_shows_holiday_count(self):
        emp = make_employee()
        Holiday.objects.create(name="Mid week", date=date(2026, 8, 12), kind="COMPANY")
        s = month_summary(emp, 2026, 8)
        self.assertEqual(s["holidays"], 1)
        self.assertEqual(s["working_days"], 20)
