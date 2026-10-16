from datetime import date, datetime, time
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from attendance.models import Attendance
from config.testing import client_for, make_department, make_employee, make_user
from .models import Shift, ShiftAssignment
from .services import assign_shift, default_shift, shift_for


def at(day, hh, mm=0):
    return timezone.make_aware(datetime.combine(day, time(hh, mm)))


class ShiftSetupTests(TestCase):
    def setUp(self):
        self.admin_user = make_user("ADMIN")
        self.admin = client_for(self.admin_user)
        self.emp = make_employee()
        self.emp_client = client_for(self.emp.user)

    def shift_body(self, **extra):
        return {"name": "Early", "kind": "GENERAL", "start_time": "07:00", "end_time": "15:00", "grace_minutes": 10, "work_hours": "8", **extra}

    def test_admin_creates_shift_employee_cannot(self):
        self.assertEqual(self.admin.post("/api/shifts/", self.shift_body(), format="json").status_code, 201)
        self.assertEqual(self.emp_client.post("/api/shifts/", self.shift_body(name="X"), format="json").status_code, 403)
        self.assertEqual(self.emp_client.get("/api/shifts/").status_code, 200)

    def test_validation(self):
        self.assertEqual(self.admin.post("/api/shifts/", self.shift_body(end_time="07:00"), format="json").status_code, 400)
        self.assertEqual(self.admin.post("/api/shifts/", self.shift_body(work_hours="20"), format="json").status_code, 400)
        self.assertEqual(self.admin.post("/api/shifts/", self.shift_body(grace_minutes=500), format="json").status_code, 400)

    def test_default_shift_is_used_when_nothing_assigned(self):
        self.assertEqual(shift_for(self.emp, date(2026, 9, 14)), default_shift())

    def test_employee_assignment_beats_department_assignment(self):
        dept = make_department()
        emp = make_employee(department=dept)
        night = Shift.objects.create(name="Night", kind="NIGHT", start_time=time(21), end_time=time(6))
        flex = Shift.objects.create(name="Flex", kind="FLEXIBLE", start_time=time(10), end_time=time(19))
        assign_shift(night, date(2026, 1, 1), self.admin_user, department=dept)
        self.assertEqual(shift_for(emp, date(2026, 9, 14)), night)
        assign_shift(flex, date(2026, 1, 1), self.admin_user, employee=emp)
        self.assertEqual(shift_for(emp, date(2026, 9, 14)), flex)

    def test_new_assignment_closes_old_one_and_keeps_history(self):
        a = Shift.objects.create(name="A", start_time=time(8), end_time=time(16))
        b = Shift.objects.create(name="B", start_time=time(12), end_time=time(20))
        assign_shift(a, date(2026, 1, 1), self.admin_user, employee=self.emp)
        assign_shift(b, date(2026, 6, 1), self.admin_user, employee=self.emp)
        self.assertEqual(ShiftAssignment.objects.filter(employee=self.emp).count(), 2)
        self.assertEqual(shift_for(self.emp, date(2026, 5, 31)), a)  # history still answers correctly
        self.assertEqual(shift_for(self.emp, date(2026, 6, 1)), b)

    def test_assign_via_api_needs_exactly_one_target(self):
        shift = Shift.objects.create(name="A", start_time=time(8), end_time=time(16))
        both = {"shift": shift.id, "employee": self.emp.id, "department": make_department().id, "start_date": "2026-09-01"}
        neither = {"shift": shift.id, "start_date": "2026-09-01"}
        self.assertEqual(self.admin.post("/api/shifts/assignments/", both, format="json").status_code, 400)
        self.assertEqual(self.admin.post("/api/shifts/assignments/", neither, format="json").status_code, 400)
        ok = {"shift": shift.id, "employee": self.emp.id, "start_date": "2026-09-01"}
        self.assertEqual(self.admin.post("/api/shifts/assignments/", ok, format="json").status_code, 201)
        self.assertEqual(self.emp_client.post("/api/shifts/assignments/", ok, format="json").status_code, 403)

    def test_cannot_assign_before_an_existing_start_date(self):
        shift = Shift.objects.create(name="A", start_time=time(8), end_time=time(16))
        assign_shift(shift, date(2026, 9, 1), self.admin_user, employee=self.emp)
        body = {"shift": shift.id, "employee": self.emp.id, "start_date": "2026-08-01"}
        self.assertEqual(self.admin.post("/api/shifts/assignments/", body, format="json").status_code, 400)

    def test_shift_with_history_cannot_be_deleted(self):
        shift = Shift.objects.create(name="A", start_time=time(8), end_time=time(16))
        assign_shift(shift, date(2026, 9, 1), self.admin_user, employee=self.emp)
        self.assertEqual(self.admin.delete(f"/api/shifts/{shift.id}/").status_code, 400)

    def test_employee_sees_only_own_and_department_assignments(self):
        shift = Shift.objects.create(name="A", start_time=time(8), end_time=time(16))
        assign_shift(shift, date(2026, 9, 1), self.admin_user, employee=self.emp)
        other = make_employee()
        assign_shift(shift, date(2026, 9, 1), self.admin_user, employee=other)
        rows = self.emp_client.get("/api/shifts/assignments/").json()["results"]
        self.assertEqual([r["employee"] for r in rows], [self.emp.id])


class ShiftAttendanceTests(TestCase):
    """Late / early / overtime come from the shift. Time is frozen so the numbers are exact."""

    def setUp(self):
        self.admin_user = make_user("ADMIN")
        self.emp = make_employee()
        self.api = client_for(self.emp.user)
        self.day = date(2026, 9, 14)  # a Monday

    def punch(self, path, when):
        with patch("django.utils.timezone.now", return_value=when):
            return self.api.post(f"/api/attendance/{path}/")

    def test_on_time_check_in_is_not_late(self):
        r = self.punch("check-in", at(self.day, 9, 10))  # general shift 09:00, grace 15
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json()["late_minutes"], 0)

    def test_late_check_in_records_minutes_and_notifies(self):
        r = self.punch("check-in", at(self.day, 9, 40))
        self.assertEqual(r.json()["late_minutes"], 40)
        self.assertTrue(self.emp.user.notifications.filter(kind="ATTENDANCE", title="Late check-in").exists())

    def test_early_exit_and_overtime(self):
        self.punch("check-in", at(self.day, 9, 0))
        r = self.punch("check-out", at(self.day, 17, 0))  # shift ends 18:00
        self.assertEqual(r.json()["early_exit_minutes"], 60)
        self.assertEqual(Decimal(r.json()["overtime_hours"]), 0)

        other = make_employee()
        api2 = client_for(other.user)
        with patch("django.utils.timezone.now", return_value=at(self.day, 9, 0)):
            api2.post("/api/attendance/check-in/")
        with patch("django.utils.timezone.now", return_value=at(self.day, 19, 30)):
            r = api2.post("/api/attendance/check-out/")
        self.assertEqual(Decimal(r.json()["overtime_hours"]), Decimal("1.50"))  # 10.5 h worked - 9 h shift window
        self.assertEqual(r.json()["early_exit_minutes"], 0)

    def test_half_day_follows_shift_hours(self):
        self.punch("check-in", at(self.day, 9, 0))
        r = self.punch("check-out", at(self.day, 12, 0))  # 3 hours < half of 8
        self.assertEqual(r.json()["status"], "HALF_DAY")

    def test_flexible_shift_is_never_late(self):
        flex = Shift.objects.create(name="Flex", kind="FLEXIBLE", start_time=time(10), end_time=time(19))
        assign_shift(flex, date(2026, 1, 1), self.admin_user, employee=self.emp)
        r = self.punch("check-in", at(self.day, 13, 0))
        self.assertEqual(r.json()["late_minutes"], 0)

    def test_night_shift_checks_out_next_morning(self):
        night = Shift.objects.create(name="Night", kind="NIGHT", start_time=time(21), end_time=time(6), grace_minutes=15)
        assign_shift(night, date(2026, 1, 1), self.admin_user, employee=self.emp)
        r = self.punch("check-in", at(self.day, 21, 30))
        self.assertEqual(r.json()["late_minutes"], 30)
        r = self.punch("check-out", at(date(2026, 9, 15), 7, 0))  # next morning, 9.5 h worked
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Decimal(r.json()["working_hours"]), Decimal("9.50"))
        self.assertEqual(Decimal(r.json()["overtime_hours"]), Decimal("0.50"))  # 9.5 h worked - 9 h window
        self.assertEqual(r.json()["early_exit_minutes"], 0)

    def test_forgotten_day_shift_checkout_cannot_be_closed_next_day(self):
        self.punch("check-in", at(self.day, 9, 0))
        r = self.punch("check-out", at(date(2026, 9, 15), 9, 0))
        self.assertEqual(r.status_code, 400)

    def test_double_check_in_and_check_out_messages_unchanged(self):
        self.punch("check-in", at(self.day, 9, 0))
        self.assertEqual(self.punch("check-in", at(self.day, 9, 5)).status_code, 400)
        self.punch("check-out", at(self.day, 18, 0))
        r = self.punch("check-out", at(self.day, 18, 5))
        self.assertIn("already checked out", r.json()["error"])

    def test_admin_override_recalculates_shift_numbers(self):
        admin = client_for(self.admin_user)
        body = {"employee": self.emp.id, "date": "2026-09-14", "note": "Forgot to punch",
                "check_in": at(self.day, 9, 30).isoformat(), "check_out": at(self.day, 19, 0).isoformat()}
        r = admin.post("/api/attendance/override/", body, format="json")
        self.assertEqual(r.status_code, 201)
        d = r.json()
        self.assertEqual((d["late_minutes"], d["early_exit_minutes"]), (30, 0))
        self.assertEqual(Decimal(d["overtime_hours"]), Decimal("0.50"))  # 9:30 -> 19:00 = 9.5 h, window is 9 h
        self.assertTrue(d["is_overridden"])

    def test_override_can_pick_another_shift(self):
        night = Shift.objects.create(name="Night", kind="NIGHT", start_time=time(21), end_time=time(6))
        admin = client_for(self.admin_user)
        body = {"employee": self.emp.id, "date": "2026-09-14", "status": "PRESENT", "note": "Moved to night", "shift": night.id}
        r = admin.post("/api/attendance/override/", body, format="json")
        self.assertEqual(r.json()["shift_name"], "Night")


class ShiftReportTests(TestCase):
    def test_report_rows_and_permissions(self):
        emp = make_employee()
        shift = default_shift()
        Attendance.objects.create(employee=emp, date=date(2026, 9, 14), check_in=at(date(2026, 9, 14), 9, 40), check_out=at(date(2026, 9, 14), 18, 0),
                                  working_hours=Decimal("8.33"), status="PRESENT", shift=shift, late_minutes=40)
        hr = client_for(make_user("HR"))
        r = hr.get(f"/api/reports/shift-attendance/?date_from=2026-09-01&date_to=2026-09-30&shift={shift.id}")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(len(data["rows"]), 1)
        self.assertEqual(data["rows"][0][1], "General Shift")
        self.assertEqual(data["rows"][0][8], "40")
        self.assertEqual(hr.get("/api/reports/shift-attendance/?format=csv").status_code, 200)
        self.assertEqual(client_for(emp.user).get("/api/reports/shift-attendance/").status_code, 403)
