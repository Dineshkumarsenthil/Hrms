import calendar
from io import BytesIO
from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def money(v):
    return f"{v:,.2f}"


def build_slip_pdf(p):
    """Return PDF bytes for a Payroll row."""
    e = p.employee
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=15 * mm, bottomMargin=15 * mm,
                            title=f"Salary Slip {calendar.month_name[p.month]} {p.year}")
    st = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=st["Title"], fontSize=18, spaceAfter=2)
    sub = ParagraphStyle("sub", parent=st["Normal"], alignment=1, textColor=colors.grey)
    grid = [("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey), ("FONTSIZE", (0, 0), (-1, -1), 9), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]
    head_bg = ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a8a"))
    head_fg = ("TEXTCOLOR", (0, 0), (-1, 0), colors.white)

    els = [Paragraph(settings.COMPANY_NAME, h1), Paragraph(f"Salary Slip - {calendar.month_name[p.month]} {p.year}", sub), Spacer(1, 8 * mm)]

    info = [["Employee ID", e.employee_code, "Name", e.full_name],
            ["Department", e.department.name if e.department else "-", "Designation", e.designation],
            ["Date of joining", e.joining_date.strftime("%d %b %Y"), "Email", e.user.email],
            ["Working days", str(p.working_days), "Days paid", str(p.working_days - p.lop_days)],
            ["Present days", str(p.present_days), "Paid leave / LOP", f"{p.paid_leave_days} / {p.lop_days}"]]
    t = Table(info, colWidths=[32 * mm, 50 * mm, 32 * mm, 50 * mm])
    t.setStyle(TableStyle(grid + [("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke), ("BACKGROUND", (2, 0), (2, -1), colors.whitesmoke),
                                  ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"), ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold")]))
    els += [t, Spacer(1, 6 * mm)]

    earn = [("Basic", p.basic), ("House Rent Allowance", p.hra), ("Other Allowances", p.allowances)]
    ded = [("Loss of Pay", p.lop_deduction), ("Provident Fund", p.pf_deduction), ("Tax / TDS", p.tax_deduction)]
    if p.adjustment > 0:
        earn.append((f"Adjustment {('- ' + p.adjustment_note) if p.adjustment_note else ''}".strip(), p.adjustment))
    elif p.adjustment < 0:
        ded.append((f"Adjustment {('- ' + p.adjustment_note) if p.adjustment_note else ''}".strip(), -p.adjustment))
    rows = [["Earnings", "Amount (INR)", "Deductions", "Amount (INR)"]]
    for i in range(max(len(earn), len(ded))):
        a = earn[i] if i < len(earn) else ("", None)
        d = ded[i] if i < len(ded) else ("", None)
        rows.append([a[0], money(a[1]) if a[1] is not None else "", d[0], money(d[1]) if d[1] is not None else ""])
    total_earn = p.gross_salary + (p.adjustment if p.adjustment > 0 else 0)
    total_ded = p.lop_deduction + p.pf_deduction + p.tax_deduction + (-p.adjustment if p.adjustment < 0 else 0)
    rows.append(["Gross earnings", money(total_earn), "Total deductions", money(total_ded)])
    t2 = Table(rows, colWidths=[52 * mm, 38 * mm, 52 * mm, 38 * mm])
    t2.setStyle(TableStyle(grid + [head_bg, head_fg, ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                                   ("BACKGROUND", (0, -1), (-1, -1), colors.whitesmoke), ("ALIGN", (1, 0), (1, -1), "RIGHT"), ("ALIGN", (3, 0), (3, -1), "RIGHT")]))
    els += [t2, Spacer(1, 6 * mm)]

    net = Table([["NET SALARY", f"INR {money(p.net_salary)}"]], colWidths=[90 * mm, 90 * mm])
    net.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#dbeafe")), ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                             ("FONTSIZE", (0, 0), (-1, -1), 12), ("ALIGN", (1, 0), (1, 0), "RIGHT"), ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#1e3a8a")),
                             ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
    els += [net, Spacer(1, 10 * mm),
            Paragraph("This is a system-generated salary slip. LOP = gross / working days x LOP days. PF = basic x PF%.", ParagraphStyle("f", parent=st["Normal"], fontSize=8, textColor=colors.grey))]
    doc.build(els)
    return buf.getvalue()
