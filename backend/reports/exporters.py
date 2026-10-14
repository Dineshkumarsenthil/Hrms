import csv
from io import BytesIO
from django.http import HttpResponse, JsonResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def respond(fmt, title, columns, rows, filename):
    fmt = (fmt or "json").lower()
    if fmt == "csv":
        resp = HttpResponse(content_type="text/csv")
        resp["Content-Disposition"] = f'attachment; filename="{filename}.csv"'
        w = csv.writer(resp)
        w.writerow(columns)
        for r in rows:
            # guard against CSV/formula injection when opened in Excel
            w.writerow([("'" + str(c)) if isinstance(c, str) and c[:1] in "=+-@" else c for c in r])
        return resp
    if fmt == "pdf":
        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=landscape(A4), leftMargin=10 * mm, rightMargin=10 * mm, topMargin=12 * mm, bottomMargin=12 * mm)
        st = getSampleStyleSheet()
        data = [columns] + [[str(c) for c in r] for r in rows]
        t = Table(data, repeatRows=1)
        t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a8a")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                               ("FONTSIZE", (0, 0), (-1, -1), 7.5), ("GRID", (0, 0), (-1, -1), 0.3, colors.lightgrey),
                               ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.whitesmoke])]))
        doc.build([Paragraph(title, st["Title"]), Spacer(1, 4 * mm), t])
        resp = HttpResponse(buf.getvalue(), content_type="application/pdf")
        resp["Content-Disposition"] = f'attachment; filename="{filename}.pdf"'
        return resp
    return JsonResponse({"title": title, "columns": columns, "rows": [[str(c) if c is not None else "" for c in r] for r in rows]})
