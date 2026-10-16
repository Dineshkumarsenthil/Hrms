import calendar
import secrets
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import transaction
from django.utils import timezone

from attendance.services import attendance_counts, working_dates
from audit.utils import log_action
from leaves.services import leave_days_in_month
from notifications.inapp import notify
from notifications.service import send_templated
from .models import MonthlyVariablePay, Payroll, PayrollLine, SalaryComponent, SalaryStructure, SalaryStructureItem, SalarySlip
from .pdf import build_slip_pdf

Q = Decimal("0.01")
EARNING, DEDUCTION = SalaryComponent.Kind.EARNING, SalaryComponent.Kind.DEDUCTION

# components every company needs: (code, name, kind, calc type, variable?, system?, order)
DEFAULT_COMPONENTS = [
    ("BASIC", "Basic Pay", EARNING, "FIXED", False, True, 1),
    ("HRA", "House Rent Allowance", EARNING, "FIXED", False, True, 2),
    ("ALLOWANCE", "Other Allowances", EARNING, "FIXED", False, True, 3),
    ("BONUS", "Performance Bonus", EARNING, "FIXED", True, False, 4),
    ("PF", "Provident Fund", DEDUCTION, "PERCENT_OF_BASIC", False, True, 10),
    ("TAX", "Tax / TDS", DEDUCTION, "FIXED", False, True, 11),
]


def q(v):
    return Decimal(v).quantize(Q, rounding=ROUND_HALF_UP)


def default_components():
    """Returns {code: SalaryComponent}, creating the standard ones when missing."""
    out = {}
    for code, name, kind, calc, variable, system, order in DEFAULT_COMPONENTS:
        out[code], _ = SalaryComponent.objects.get_or_create(
            code=code, defaults={"name": name, "kind": kind, "calc_type": calc, "is_variable": variable, "is_system": system, "display_order": order})
    return out


def legacy_items(employee):
    """The old flat salary fields of an employee, written as structure items."""
    comps = default_components()
    return [(comps["BASIC"], employee.basic_salary), (comps["HRA"], employee.hra), (comps["ALLOWANCE"], employee.allowances),
            (comps["PF"], employee.pf_percent), (comps["TAX"], employee.tax_deduction)]


def structure_in_force(employee, on_date):
    return (SalaryStructure.objects.filter(employee=employee, effective_from__lte=on_date)
            .prefetch_related("items__component").order_by("-effective_from", "-id").first())


def items_for(employee, on_date):
    """(component, value) pairs to pay on a date. Employees with no structure fall back to their flat salary fields."""
    structure = structure_in_force(employee, on_date)
    if structure:
        return [(i.component, i.value) for i in structure.items.all()]
    return legacy_items(employee)


def component_amount(component, value, basic):
    return q(basic * value / 100) if component.calc_type == SalaryComponent.Calc.PERCENT_OF_BASIC else q(value)


def build_lines(employee, year, month):
    """Earning and deduction amounts from the salary structure of that month."""
    month_end = date(year, month, calendar.monthrange(year, month)[1])
    items = sorted(items_for(employee, month_end), key=lambda it: (it[0].display_order, it[0].name))
    basic = next((Decimal(v) for c, v in items if c.code == "BASIC"), Decimal("0"))
    lines = []
    for comp, value in items:
        lines.append({"name": comp.name, "code": comp.code, "kind": comp.kind, "amount": component_amount(comp, value, basic), "order": comp.display_order})
    return basic, lines


def compute(employee, year, month):
    """All numbers of a payroll month. Returns the Payroll fields plus a `lines` list for the slip breakdown."""
    wdays = working_dates(year, month, employee.joining_date, employee.region)
    working = len(wdays)
    c = attendance_counts(employee, year, month)
    paid_leave, _lop_leave = leave_days_in_month(employee, year, month)
    present = c["present_equivalent"]
    lop_days = max(Decimal("0"), Decimal(working) - present - paid_leave)  # every unaccounted working day is LOP

    basic, lines = build_lines(employee, year, month)
    earnings = [l for l in lines if l["kind"] == EARNING]
    deductions = [l for l in lines if l["kind"] == DEDUCTION]
    gross = sum((l["amount"] for l in earnings), Decimal("0"))
    hra = sum((l["amount"] for l in earnings if l["code"] == "HRA"), Decimal("0"))

    # bonus and other variable pay entered for this month
    variable = MonthlyVariablePay.objects.filter(employee=employee, year=year, month=month).select_related("component")
    variable_total = sum((v.amount for v in variable), Decimal("0"))
    for v in variable:
        lines.append({"name": v.component.name, "code": v.component.code, "kind": EARNING, "amount": q(v.amount), "order": 80})

    # overtime: basic -> hourly rate -> x multiplier
    hourly = (basic / working / settings.STANDARD_DAY_HOURS) if working else Decimal("0")
    overtime_hours = c["overtime_hours"]
    overtime_pay = q(overtime_hours * hourly * settings.OVERTIME_MULTIPLIER)
    if overtime_pay > 0:
        lines.append({"name": f"Overtime ({overtime_hours} hrs)", "code": "OVERTIME", "kind": EARNING, "amount": overtime_pay, "order": 90})

    per_day = (gross / working) if working else Decimal("0")
    lop_ded = q(per_day * lop_days)
    pf = sum((l["amount"] for l in deductions if l["code"] == "PF"), Decimal("0"))
    tax = sum((l["amount"] for l in deductions if l["code"] == "TAX"), Decimal("0"))
    other = sum((l["amount"] for l in deductions), Decimal("0")) - pf - tax
    net = max(Decimal("0.00"), q(gross + variable_total + overtime_pay - lop_ded - pf - tax - other))  # never negative

    fields = dict(working_days=working, present_days=present, paid_leave_days=paid_leave, lop_days=lop_days,
                  basic=q(basic), hra=q(hra), allowances=q(gross - basic - hra), gross_salary=q(gross),
                  variable_pay=q(variable_total), overtime_hours=overtime_hours, overtime_pay=overtime_pay,
                  lop_deduction=lop_ded, pf_deduction=q(pf), tax_deduction=q(tax), other_deductions=q(other), net_salary=net)
    return {**fields, "lines": lines}


def recompute_net(p):
    p.net_salary = max(Decimal("0.00"), q(p.gross_salary + p.variable_pay + p.overtime_pay - p.lop_deduction - p.pf_deduction
                                          - p.tax_deduction - p.other_deductions + p.adjustment))


def save_slip(p):
    """Create the slip PDF, or regenerate it (e.g. after a manual adjustment)."""
    pdf = build_slip_pdf(p)
    name = f"{p.employee.employee_code}_{p.year}-{p.month:02d}.pdf"
    slip = SalarySlip.objects.filter(payroll=p).first()
    if slip:
        slip.file.delete(save=False)
        slip.file.save(name, ContentFile(pdf), save=True)
        return slip
    return SalarySlip.objects.create(payroll=p, file=ContentFile(pdf, name=name))


def period_label(p):
    return f"{calendar.month_name[p.month]} {p.year}"


@transaction.atomic
def generate_for_employee(employee, year, month, user, request=None):
    data = compute(employee, year, month)
    lines = data.pop("lines")
    p = Payroll.objects.create(employee=employee, year=year, month=month, generated_by=user, locked=True, **data)
    PayrollLine.objects.bulk_create([PayrollLine(payroll=p, **line) for line in lines])
    save_slip(p)
    log_action(request, "PAYROLL_GENERATE", "Payroll", p.id, {"employee": employee.employee_code, "period": f"{year}-{month:02d}", "net": str(p.net_salary)}, user=user)
    return p


def notify_payroll(p):
    ctx = {"name": p.employee.full_name, "period": period_label(p), "net": f"{p.net_salary:,.2f}"}
    send_templated("PAYROLL_PROCESSED", p.employee.user.email, ctx)
    send_templated("SALARY_SLIP_READY", p.employee.user.email, ctx)
    notify(p.employee.user, "PAYROLL", f"Payroll processed for {ctx['period']}", f"Your net salary is {ctx['net']}. The salary slip is ready to download.", "/payroll")


def simulate_credit(p, user, request=None):
    p.status = Payroll.Status.CREDITED
    p.credited_at = timezone.now()
    p.transaction_ref = f"SIM-{p.year}{p.month:02d}-{p.employee.employee_code}-{secrets.token_hex(3).upper()}"
    p.locked = True
    p.save()
    log_action(request, "PAYROLL_CREDIT_SIMULATED", "Payroll", p.id, {"ref": p.transaction_ref}, user=user)
    notify(p.employee.user, "PAYROLL", "Salary credited", f"Your salary for {period_label(p)} has been credited (ref {p.transaction_ref}).", "/payroll")


@transaction.atomic
def create_structure(employee, effective_from, reason, items, user):
    """Revise compensation: adds a new version (old ones stay). items = [(component, value)]."""
    structure = SalaryStructure.objects.create(employee=employee, effective_from=effective_from, reason=reason, created_by=user)
    SalaryStructureItem.objects.bulk_create([SalaryStructureItem(structure=structure, component=comp, value=value) for comp, value in items])
    if effective_from <= timezone.localdate():
        sync_employee_fields(employee, items)
    return structure


def sync_employee_fields(employee, items):
    """Keep the flat fields on Employee (used by the Employees page) in step with the newest structure."""
    basic = next((Decimal(v) for c, v in items if c.code == "BASIC"), Decimal("0"))
    employee.basic_salary = basic
    employee.hra = sum((Decimal(v) for c, v in items if c.code == "HRA"), Decimal("0"))
    employee.allowances = sum((component_amount(c, Decimal(v), basic) for c, v in items if c.kind == EARNING and c.code not in ("BASIC", "HRA")), Decimal("0"))
    for comp, value in items:
        if comp.code == "PF" and comp.calc_type == SalaryComponent.Calc.PERCENT_OF_BASIC:
            employee.pf_percent = value
        if comp.code == "TAX":
            employee.tax_deduction = value
    employee.save(update_fields=["basic_salary", "hra", "allowances", "pf_percent", "tax_deduction"])
