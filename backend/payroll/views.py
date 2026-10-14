from django.db import IntegrityError
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAdmin, IsAdminOrHR
from audit.utils import log_action
from employees.models import Employee
from . import services
from .models import Payroll
from .serializers import AdjustSerializer, GenerateSerializer, PayrollSerializer, ReasonSerializer


class PayrollViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Employees: own history only. HR/Admin: all."""
    serializer_class = PayrollSerializer
    filterset_fields = {"year": ["exact"], "month": ["exact"], "employee": ["exact"], "status": ["exact"], "employee__department": ["exact"]}

    def get_queryset(self):
        qs = Payroll.objects.select_related("employee__user", "employee__department", "slip")
        u = self.request.user
        return qs if u.is_hr_or_admin else qs.filter(employee__user=u)

    @action(detail=False, methods=["post"], permission_classes=[IsAdminOrHR])
    def generate(self, request):
        s = GenerateSerializer(data=request.data); s.is_valid(raise_exception=True)
        y, m = s.validated_data["year"], s.validated_data["month"]
        today = timezone.localdate()
        if (y, m) >= (today.year, today.month):
            raise ValidationError("Payroll can only be generated for a completed month.")
        emps = Employee.objects.filter(is_active=True).select_related("user", "department")
        if s.validated_data.get("employee"):
            emps = emps.filter(pk=s.validated_data["employee"])
        created, skipped = [], []
        import calendar, datetime
        month_end = datetime.date(y, m, calendar.monthrange(y, m)[1])
        for e in emps:
            if e.joining_date > month_end:
                skipped.append({"employee": e.employee_code, "reason": "Joined after this month"}); continue
            if Payroll.objects.filter(employee=e, year=y, month=m).exists():
                skipped.append({"employee": e.employee_code, "reason": "Payroll already generated (locked)"}); continue
            try:
                p = services.generate_for_employee(e, y, m, request.user, request)
            except IntegrityError:
                skipped.append({"employee": e.employee_code, "reason": "Payroll already generated (locked)"}); continue
            services.notify_payroll(p)
            created.append(p.id)
        return Response({"generated": len(created), "skipped": skipped, "payroll_ids": created}, status=201 if created else 200)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminOrHR])
    def credit(self, request, pk=None):
        p = self.get_object()
        if p.status == Payroll.Status.CREDITED:
            raise ValidationError("Already credited.")
        if not p.locked:
            raise ValidationError("Lock the payroll before crediting.")
        services.simulate_credit(p, request.user, request)
        return Response(PayrollSerializer(p).data)

    @action(detail=False, methods=["post"], url_path="credit-all", permission_classes=[IsAdminOrHR])
    def credit_all(self, request):
        s = GenerateSerializer(data=request.data); s.is_valid(raise_exception=True)
        qs = Payroll.objects.filter(year=s.validated_data["year"], month=s.validated_data["month"], status="GENERATED", locked=True)
        n = 0
        for p in qs:
            services.simulate_credit(p, request.user, request); n += 1
        return Response({"credited": n})

    @action(detail=True, methods=["post"], permission_classes=[IsAdmin])
    def unlock(self, request, pk=None):
        s = ReasonSerializer(data=request.data); s.is_valid(raise_exception=True)
        p = self.get_object()
        if p.status == Payroll.Status.CREDITED:
            raise ValidationError("Credited payroll cannot be unlocked.")
        p.locked = False; p.save(update_fields=["locked"])
        log_action(request, "PAYROLL_UNLOCK", "Payroll", p.id, {"reason": s.validated_data["reason"]})
        return Response(PayrollSerializer(p).data)

    @action(detail=True, methods=["post"], permission_classes=[IsAdmin])
    def lock(self, request, pk=None):
        p = self.get_object(); p.locked = True; p.save(update_fields=["locked"])
        log_action(request, "PAYROLL_LOCK", "Payroll", p.id)
        return Response(PayrollSerializer(p).data)

    @action(detail=True, methods=["post"], permission_classes=[IsAdmin])
    def adjust(self, request, pk=None):
        s = AdjustSerializer(data=request.data); s.is_valid(raise_exception=True)
        p = self.get_object()
        if p.locked:
            raise ValidationError("Payroll is locked. Unlock it first (Admin) to make a manual adjustment.")
        p.adjustment, p.adjustment_note = s.validated_data["amount"], s.validated_data["note"]
        services.recompute_net(p); p.save()
        services.save_slip(p)  # slip reflects the adjustment
        log_action(request, "PAYROLL_ADJUST", "Payroll", p.id, {"amount": str(p.adjustment), "note": p.adjustment_note, "net": str(p.net_salary)})
        return Response(PayrollSerializer(p).data)

    @action(detail=True, methods=["get"])
    def slip(self, request, pk=None):
        p = self.get_object()  # queryset already scoped: employees can only reach their own
        if not hasattr(p, "slip"):
            return Response({"error": "No slip for this payroll."}, status=404)
        log_action(request, "SLIP_DOWNLOAD", "Payroll", p.id)
        return FileResponse(p.slip.file.open("rb"), as_attachment=True, filename=f"salary_slip_{p.employee.employee_code}_{p.year}-{p.month:02d}.pdf", content_type="application/pdf")
