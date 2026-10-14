import calendar
import secrets
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from django.core.files.base import ContentFile
from django.db import transaction
from django.utils import timezone

from attendance.services import attendance_counts, working_dates
from audit.utils import log_action
from leaves.services import leave_days_in_month
from notifications.service import send_templated
from .models import Payroll, SalarySlip
from .pdf import build_slip_pdf

Q = Decimal("0.01")


def q(v):
    return Decimal(v).quantize(Q, rounding=ROUND_HALF_UP)


def compute(employee, year, month):
    wdays = working_dates(year, month, employee.joining_date)
    working = len(wdays)
    c = attendance_counts(employee, year, month)
    paid_leave, _lop_leave = leave_days_in_month(employee, year, month)
    present = c["present_equivalent"]
    lop_days = max(Decimal("0"), Decimal(working) - present - paid_leave)  # every unaccounted working day is LOP
    gross = employee.basic_salary + employee.hra + employee.allowances
    per_day = (gross / working) if working else Decimal("0")
    lop_ded = q(per_day * lop_days)
    pf = q(employee.basic_salary * employee.pf_percent / 100)
    net = max(Decimal('0.00'), q(gross - lop_ded - pf - employee.tax_deduction))  # never negative
    return dict(working_days=working, present_days=present, paid_leave_days=paid_leave, lop_days=lop_days,
                basic=employee.basic_salary, hra=employee.hra, allowances=employee.allowances, gross_salary=q(gross),
                lop_deduction=lop_ded, pf_deduction=pf, tax_deduction=employee.tax_deduction, net_salary=net)


def recompute_net(p):
    p.net_salary = max(Decimal('0.00'), q(p.gross_salary - p.lop_deduction - p.pf_deduction - p.tax_deduction + p.adjustment))


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
    p = Payroll.objects.create(employee=employee, year=year, month=month, generated_by=user, locked=True, **compute(employee, year, month))
    save_slip(p)
    log_action(request, "PAYROLL_GENERATE", "Payroll", p.id, {"employee": employee.employee_code, "period": f"{year}-{month:02d}", "net": str(p.net_salary)}, user=user)
    return p


def notify_payroll(p):
    ctx = {"name": p.employee.full_name, "period": period_label(p), "net": f"{p.net_salary:,.2f}"}
    send_templated("PAYROLL_PROCESSED", p.employee.user.email, ctx)
    send_templated("SALARY_SLIP_READY", p.employee.user.email, ctx)


def simulate_credit(p, user, request=None):
    p.status = Payroll.Status.CREDITED
    p.credited_at = timezone.now()
    p.transaction_ref = f"SIM-{p.year}{p.month:02d}-{p.employee.employee_code}-{secrets.token_hex(3).upper()}"
    p.locked = True
    p.save()
    log_action(request, "PAYROLL_CREDIT_SIMULATED", "Payroll", p.id, {"ref": p.transaction_ref}, user=user)
