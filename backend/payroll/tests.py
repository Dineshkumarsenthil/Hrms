import shutil
import tempfile
from datetime import date
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase, override_settings

from attendance.models import Attendance
from attendance.services import working_dates
from config.testing import client_for, make_employee, make_user
from holidays.models import Holiday
from . import services
from .models import MonthlyVariablePay, Payroll, SalaryComponent

TODAY = date(2026, 10, 15)
MEDIA = tempfile.mkdtemp()


def D(v):
    return Decimal(str(v))


@override_settings(MEDIA_ROOT=MEDIA)
class PayrollBase(TestCase):
    """August 2026 has 21 weekdays; a holiday on Fri 14 Aug leaves 20 working days."""

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA, ignore_errors=True)

    def setUp(self):
        patcher = patch("django.utils.timezone.localdate", return_value=TODAY)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.admin_user, self.hr_user = make_user("ADMIN"), make_user("HR")
        self.admin, self.hr = client_for(self.admin_user), client_for(self.hr_user)
        self.emp = make_employee(joining=date(2026, 1, 1))
        self.emp_api = client_for(self.emp.user)
        Holiday.objects.create(name="Founders Day", date=date(2026, 8, 14), kind="COMPANY")
        services.default_components()
        self.comp = {c.code: c for c in SalaryComponent.objects.all()}
        self.conveyance = SalaryComponent.objects.create(name="Conveyance", code="CONVEYANCE", kind="EARNING", display_order=5)

    def structure_body(self, start="2026-01-01", basic="30000", **extra):
        items = [{"component": self.comp["BASIC"].id, "value": basic}, {"component": self.comp["HRA"].id, "value": "10000"},
                 {"component": self.conveyance.id, "value": "2000"}, {"component": self.comp["PF"].id, "value": "12"},
                 {"component": self.comp["TAX"].id, "value": "500"}]
        return {"employee": self.emp.id, "effective_from": start, "reason": "Joining", "new_items": items, **extra}

    def give_structure(self, **kw):
        r = self.admin.post("/api/payroll/structures/", self.structure_body(**kw), format="json")
        self.assertEqual(r.status_code, 201, r.content)
        return r.json()

    def mark_present(self, skip=0):
        days = working_dates(2026, 8, self.emp.joining_date, self.emp.region)
        for day in days[skip:]:
            Attendance.objects.create(employee=self.emp, date=day, working_hours=D(9), status="PRESENT")
        return days


class SalaryComponentTests(PayrollBase):
    def test_default_components_exist(self):
        for code in ("BASIC", "HRA", "ALLOWANCE", "PF", "TAX", "BONUS"):
            self.assertIn(code, self.comp)

    def test_only_admin_changes_components(self):
        body = {"name": "Meal Card", "code": "meal card", "kind": "EARNING", "calc_type": "FIXED"}
        self.assertEqual(self.hr.post("/api/payroll/components/", body, format="json").status_code, 403)
        r = self.admin.post("/api/payroll/components/", body, format="json")
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json()["code"], "MEAL_CARD")  # normalised
        self.assertEqual(self.hr.get("/api/payroll/components/").status_code, 200)
        self.assertEqual(self.emp_api.get("/api/payroll/components/").status_code, 403)

    def test_variable_must_be_a_fixed_earning(self):
        bad = {"name": "Penalty", "code": "PEN", "kind": "DEDUCTION", "is_variable": True}
        self.assertEqual(self.admin.post("/api/payroll/components/", bad, format="json").status_code, 400)
        bad = {"name": "Incentive", "code": "INC", "kind": "EARNING", "is_variable": True, "calc_type": "PERCENT_OF_BASIC"}
        self.assertEqual(self.admin.post("/api/payroll/components/", bad, format="json").status_code, 400)

    def test_system_components_are_protected(self):
        basic = self.comp["BASIC"]
        self.assertEqual(self.admin.delete(f"/api/payroll/components/{basic.id}/").status_code, 400)
        self.assertEqual(self.admin.patch(f"/api/payroll/components/{basic.id}/", {"kind": "DEDUCTION"}, format="json").status_code, 400)
        self.assertEqual(self.admin.patch(f"/api/payroll/components/{basic.id}/", {"is_active": False}, format="json").status_code, 400)
        self.assertEqual(self.admin.patch(f"/api/payroll/components/{basic.id}/", {"name": "Basic Salary"}, format="json").status_code, 200)

    def test_used_component_cannot_be_deleted_unused_can(self):
        self.give_structure()
        self.assertEqual(self.admin.delete(f"/api/payroll/components/{self.conveyance.id}/").status_code, 400)
        spare = SalaryComponent.objects.create(name="Spare", code="SPARE", kind="EARNING")
        self.assertEqual(self.admin.delete(f"/api/payroll/components/{spare.id}/").status_code, 204)


class SalaryStructureTests(PayrollBase):
    def test_only_admin_can_revise(self):
        self.assertEqual(self.hr.post("/api/payroll/structures/", self.structure_body(), format="json").status_code, 403)
        self.assertEqual(self.emp_api.post("/api/payroll/structures/", self.structure_body(), format="json").status_code, 403)
        self.give_structure()

    def test_validation(self):
        post = lambda body: self.admin.post("/api/payroll/structures/", body, format="json").status_code
        body = self.structure_body()
        self.assertEqual(post({**body, "new_items": []}), 400)
        self.assertEqual(post({**body, "new_items": [i for i in body["new_items"] if i["component"] != self.comp["BASIC"].id]}), 400)
        too_much = [{"component": self.comp["BASIC"].id, "value": "30000"}, {"component": self.comp["PF"].id, "value": "150"}]
        self.assertEqual(post({**body, "new_items": too_much}), 400)
        twice = [{"component": self.comp["BASIC"].id, "value": "30000"}, {"component": self.comp["BASIC"].id, "value": "1"}]
        self.assertEqual(post({**body, "new_items": twice}), 400)
        variable = [{"component": self.comp["BASIC"].id, "value": "30000"}, {"component": self.comp["BONUS"].id, "value": "100"}]
        self.assertEqual(post({**body, "new_items": variable}), 400)
        negative = [{"component": self.comp["BASIC"].id, "value": "-5"}]
        self.assertEqual(post({**body, "new_items": negative}), 400)

    def test_same_start_date_twice_is_rejected(self):
        self.give_structure()
        self.assertEqual(self.admin.post("/api/payroll/structures/", self.structure_body(), format="json").status_code, 400)

    def test_revision_keeps_history_and_updates_employee_fields(self):
        self.give_structure(start="2026-01-01")
        self.give_structure(start="2026-06-01", basic="36000")
        history = self.admin.get(f"/api/payroll/structures/?employee={self.emp.id}").json()["results"]
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["effective_from"], "2026-06-01")  # newest first
        self.emp.refresh_from_db()
        self.assertEqual(self.emp.basic_salary, D(36000))
        self.assertEqual(self.emp.allowances, D(2000))  # conveyance
        self.assertEqual(self.emp.tax_deduction, D(500))

    def test_employee_sees_only_own_history(self):
        self.give_structure()
        other = make_employee()
        services.create_structure(other, date(2026, 1, 1), "x", [(self.comp["BASIC"], D(1000))], self.admin_user)
        rows = self.emp_api.get("/api/payroll/structures/").json()["results"]
        self.assertEqual([r["employee"] for r in rows], [self.emp.id])

    def test_current_endpoint_falls_back_to_profile_fields(self):
        r = self.admin.get(f"/api/payroll/structures/current/?employee={self.emp.id}").json()
        self.assertIsNone(r["id"])
        self.assertEqual(next(i["value"] for i in r["items"] if i["code"] == "BASIC"), "30000.00")

    def test_salary_fields_on_profile_are_ignored_once_structure_exists(self):
        self.give_structure()
        r = self.hr.patch(f"/api/employees/{self.emp.id}/", {"basic_salary": "99999", "designation": "Lead"}, format="json")
        self.assertEqual(r.status_code, 200, r.content)
        self.emp.refresh_from_db()
        self.assertEqual(self.emp.designation, "Lead")
        self.assertEqual(self.emp.basic_salary, D(30000))


class PayrollCalculationTests(PayrollBase):
    def test_full_attendance_with_structure(self):
        self.give_structure()
        self.mark_present()
        p = services.compute(self.emp, 2026, 8)
        self.assertEqual(p["working_days"], 20)  # holiday removed
        self.assertEqual(p["lop_days"], 0)
        self.assertEqual(p["gross_salary"], D(42000))  # 30000 + 10000 + 2000
        self.assertEqual(p["pf_deduction"], D(3600))
        self.assertEqual(p["tax_deduction"], D(500))
        self.assertEqual(p["net_salary"], D(37900))
        names = [(l["code"], l["amount"]) for l in p["lines"]]
        self.assertIn(("CONVEYANCE", D(2000)), names)
        self.assertIn(("PF", D(3600)), names)

    def test_holiday_is_not_counted_as_absence(self):
        self.give_structure()
        self.mark_present()  # nobody works on 14 Aug and nothing is lost
        self.assertEqual(services.compute(self.emp, 2026, 8)["lop_days"], 0)

    def test_one_missing_day_is_loss_of_pay(self):
        self.give_structure()
        self.mark_present(skip=1)
        p = services.compute(self.emp, 2026, 8)
        self.assertEqual(p["lop_days"], 1)
        self.assertEqual(p["lop_deduction"], D(2100))  # 42000 / 20 working days
        self.assertEqual(p["net_salary"], D(35800))

    def test_variable_pay_is_added(self):
        self.give_structure()
        self.mark_present()
        MonthlyVariablePay.objects.create(employee=self.emp, year=2026, month=8, component=self.comp["BONUS"], amount=D(3000))
        p = services.compute(self.emp, 2026, 8)
        self.assertEqual(p["variable_pay"], D(3000))
        self.assertEqual(p["net_salary"], D(40900))
        self.assertIn("BONUS", [l["code"] for l in p["lines"]])

    def test_overtime_pay(self):
        self.give_structure()
        days = self.mark_present()
        Attendance.objects.filter(employee=self.emp, date=days[0]).update(overtime_hours=D(2))
        p = services.compute(self.emp, 2026, 8)
        # hourly basic = 30000 / 20 days / 8 hours = 187.50; 2 hours x 1.5
        self.assertEqual(p["overtime_pay"], D("562.50"))
        self.assertEqual(p["net_salary"], D("38462.50"))

    def test_approved_paid_leave_is_not_loss_of_pay(self):
        from leaves.models import LeaveRequest, LeaveType
        self.give_structure()
        days = self.mark_present(skip=1)
        lt = LeaveType.objects.create(name="Casual", annual_quota=12, is_paid=True)
        LeaveRequest.objects.create(employee=self.emp, leave_type=lt, start_date=days[0], end_date=days[0], days=1, lop_days=0, reason="x", status="APPROVED")
        self.assertEqual(services.compute(self.emp, 2026, 8)["lop_days"], 0)

    def test_employee_without_structure_uses_profile_salary(self):
        self.mark_present()
        p = services.compute(self.emp, 2026, 8)
        self.assertEqual(p["gross_salary"], D(40000))
        self.assertEqual(p["pf_deduction"], D(3600))
        self.assertEqual(p["net_salary"], D(36400))

    def test_structure_in_force_is_picked_by_month(self):
        self.give_structure(start="2026-01-01", basic="30000")
        self.give_structure(start="2026-09-01", basic="40000")
        self.assertEqual(services.compute(self.emp, 2026, 8)["basic"], D(30000))  # old pay for August
        self.assertEqual(services.compute(self.emp, 2026, 9)["basic"], D(40000))

    def test_net_is_never_negative(self):
        services.create_structure(self.emp, date(2026, 1, 1), "x", [(self.comp["BASIC"], D(1000)), (self.comp["TAX"], D(5000))], self.admin_user)
        self.mark_present()
        self.assertEqual(services.compute(self.emp, 2026, 8)["net_salary"], D(0))


class PayrollGenerationTests(PayrollBase):
    def generate(self, employee=None):
        return self.hr.post("/api/payroll/generate/", {"year": 2026, "month": 8, "employee": (employee or self.emp).id}, format="json")

    def test_generate_creates_lines_slip_and_notification(self):
        self.give_structure()
        self.mark_present()
        r = self.generate()
        self.assertEqual(r.status_code, 201, r.content)
        p = Payroll.objects.get(employee=self.emp)
        self.assertEqual(p.net_salary, D(37900))
        self.assertEqual(p.lines.filter(kind="EARNING").count(), 3)  # basic, hra, conveyance
        self.assertEqual(p.lines.filter(kind="DEDUCTION").count(), 2)  # pf, tax
        self.assertTrue(hasattr(p, "slip"))
        self.assertTrue(self.emp.user.notifications.filter(kind="PAYROLL").exists())

    def test_employee_sees_breakdown_in_api(self):
        self.give_structure()
        self.mark_present()
        self.generate()
        row = self.emp_api.get("/api/payroll/").json()["results"][0]
        self.assertEqual({l["code"] for l in row["lines"]}, {"BASIC", "HRA", "CONVEYANCE", "PF", "TAX"})
        self.assertEqual(self.emp_api.get(f"/api/payroll/{row['id']}/slip/").status_code, 200)

    def test_other_employee_cannot_download_slip(self):
        self.give_structure()
        self.mark_present()
        self.generate()
        pid = Payroll.objects.get(employee=self.emp).id
        stranger = client_for(make_employee().user)
        self.assertEqual(stranger.get(f"/api/payroll/{pid}/slip/").status_code, 404)

    def test_old_payroll_does_not_change_after_pay_revision(self):
        self.give_structure()
        self.mark_present()
        self.generate()
        # August is generated: a revision inside that month is refused, a later one is accepted
        self.assertEqual(self.admin.post("/api/payroll/structures/", self.structure_body(start="2026-08-20", basic="50000"), format="json").status_code, 400)
        self.assertEqual(self.admin.post("/api/payroll/structures/", self.structure_body(start="2026-09-01", basic="50000"), format="json").status_code, 201)
        p = Payroll.objects.get(employee=self.emp)
        self.assertEqual(p.basic, D(30000))
        self.assertEqual(p.lines.get(code="BASIC").amount, D(30000))

    def test_cannot_generate_current_month(self):
        r = self.hr.post("/api/payroll/generate/", {"year": 2026, "month": 10, "employee": self.emp.id}, format="json")
        self.assertEqual(r.status_code, 400)

    def test_generate_twice_is_skipped(self):
        self.give_structure()
        self.mark_present()
        self.generate()
        self.assertEqual(self.generate().json()["generated"], 0)

    def test_unlock_adjust_keeps_new_net_formula(self):
        self.give_structure()
        self.mark_present()
        MonthlyVariablePay.objects.create(employee=self.emp, year=2026, month=8, component=self.comp["BONUS"], amount=D(3000))
        self.generate()
        pid = Payroll.objects.get(employee=self.emp).id
        self.assertEqual(self.admin.post(f"/api/payroll/{pid}/adjust/", {"amount": "500", "note": "x"}, format="json").status_code, 400)  # locked
        self.admin.post(f"/api/payroll/{pid}/unlock/", {"reason": "bonus fix"}, format="json")
        r = self.admin.post(f"/api/payroll/{pid}/adjust/", {"amount": "500", "note": "spot award"}, format="json")
        self.assertEqual(r.status_code, 200, r.content)
        self.assertEqual(D(r.json()["net_salary"]), D(37900 + 3000 + 500))

    def test_hr_cannot_adjust_or_unlock(self):
        self.give_structure()
        self.mark_present()
        self.generate()
        pid = Payroll.objects.get(employee=self.emp).id
        self.assertEqual(self.hr.post(f"/api/payroll/{pid}/unlock/", {"reason": "x"}, format="json").status_code, 403)

    def test_report_has_new_columns(self):
        self.give_structure()
        self.mark_present()
        self.generate()
        data = self.hr.get("/api/reports/payroll/?date_from=2026-08-01&date_to=2026-08-31").json()
        self.assertIn("Variable", data["columns"])
        self.assertIn("Overtime", data["columns"])


class VariablePayApiTests(PayrollBase):
    def body(self, **extra):
        return {"employee": self.emp.id, "year": 2026, "month": 8, "component": self.comp["BONUS"].id, "amount": "3000", "note": "Sprint", **extra}

    def test_hr_can_add_and_update_but_employee_cannot(self):
        self.assertEqual(self.hr.post("/api/payroll/variable-pay/", self.body(), format="json").status_code, 201)
        self.assertEqual(self.hr.post("/api/payroll/variable-pay/", self.body(amount="4500"), format="json").status_code, 201)  # updates, no duplicate
        self.assertEqual(MonthlyVariablePay.objects.count(), 1)
        self.assertEqual(MonthlyVariablePay.objects.get().amount, D(4500))
        self.assertEqual(self.emp_api.post("/api/payroll/variable-pay/", self.body(), format="json").status_code, 403)
        self.assertEqual(self.emp_api.get("/api/payroll/variable-pay/").status_code, 403)

    def test_only_variable_earning_components_allowed(self):
        self.assertEqual(self.hr.post("/api/payroll/variable-pay/", self.body(component=self.comp["BASIC"].id), format="json").status_code, 400)
        self.assertEqual(self.hr.post("/api/payroll/variable-pay/", self.body(amount="0"), format="json").status_code, 400)
        self.assertEqual(self.hr.post("/api/payroll/variable-pay/", self.body(month=13), format="json").status_code, 400)

    def test_locked_after_payroll_is_generated(self):
        self.give_structure()
        self.mark_present()
        self.hr.post("/api/payroll/generate/", {"year": 2026, "month": 8, "employee": self.emp.id}, format="json")
        self.assertEqual(self.hr.post("/api/payroll/variable-pay/", self.body(), format="json").status_code, 400)
