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
from notifications.inapp import notify
from .models import MonthlyVariablePay, Payroll, PayrollLine, SalaryComponent, SalaryStructure, SalaryStructureItem
from .serializers import (AdjustSerializer, GenerateSerializer, MonthlyVariablePaySerializer, PayrollSerializer, ReasonSerializer,
                          SalaryComponentSerializer, SalaryStructureSerializer)


class PayrollViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Employees: own history only. HR/Admin: all."""
    serializer_class = PayrollSerializer
    filterset_fields = {"year": ["exact"], "month": ["exact"], "employee": ["exact"], "status": ["exact"], "employee__department": ["exact"]}

    def get_queryset(self):
        qs = Payroll.objects.select_related("employee__user", "employee__department", "slip").prefetch_related("lines")
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


class SalaryComponentViewSet(viewsets.ModelViewSet):
    """Admin configures the components. HR can read them (needed for variable pay)."""
    queryset = SalaryComponent.objects.all()
    serializer_class = SalaryComponentSerializer
    pagination_class = None
    filterset_fields = ["kind", "is_active", "is_variable"]

    def get_permissions(self):
        return [IsAdminOrHR()] if self.request.method in ("GET", "HEAD", "OPTIONS") else [IsAdmin()]

    def perform_create(self, s):
        o = s.save(); log_action(self.request, "SALARY_COMPONENT_CREATE", "SalaryComponent", o.id, {"code": o.code, "kind": o.kind})

    def perform_update(self, s):
        o = s.save(); log_action(self.request, "SALARY_COMPONENT_UPDATE", "SalaryComponent", o.id, {"code": o.code})

    def perform_destroy(self, o):
        used = SalaryStructureItem.objects.filter(component=o).exists() or PayrollLine.objects.filter(code=o.code).exists() or MonthlyVariablePay.objects.filter(component=o).exists()
        if o.is_system:
            raise ValidationError("System components cannot be deleted.")
        if used:
            raise ValidationError("This component is already used in salary history. Deactivate it instead.")
        log_action(self.request, "SALARY_COMPONENT_DELETE", "SalaryComponent", o.id, {"code": o.code}); o.delete()


class SalaryStructureViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    """Salary versions. Employees see their own history; HR/Admin see everyone; only Admin can revise pay."""
    serializer_class = SalaryStructureSerializer
    filterset_fields = ["employee"]

    def get_permissions(self):
        return [IsAdmin()] if self.action == "create" else super().get_permissions()

    def get_queryset(self):
        qs = SalaryStructure.objects.select_related("employee__user", "created_by").prefetch_related("items__component")
        u = self.request.user
        return qs if u.is_hr_or_admin else qs.filter(employee__user=u)

    def perform_create(self, s):
        d = s.validated_data
        items = [(i["component"], i["value"]) for i in d["_items"]]
        st = services.create_structure(d["employee"], d["effective_from"], d.get("reason", ""), items, self.request.user)
        s.instance = st
        log_action(self.request, "SALARY_REVISE", "SalaryStructure", st.id, {"employee": st.employee.employee_code, "from": str(st.effective_from), "reason": st.reason})
        notify(st.employee.user, "PAYROLL", "Salary structure revised", f"Your compensation was revised, effective {st.effective_from}.", "/payroll")

    @action(detail=False, methods=["get"])
    def current(self, request):
        """The structure in force today (or the flat fields as a read-only fallback) for ?employee=<id>."""
        u = request.user
        emp = u.employee if (not u.is_hr_or_admin and hasattr(u, "employee")) else get_object_or_404(Employee, pk=request.query_params.get("employee"))
        st = services.structure_in_force(emp, timezone.localdate())
        if st:
            return Response(SalaryStructureSerializer(st).data)
        items = [{"component": c.id, "name": c.name, "code": c.code, "kind": c.kind, "calc_type": c.calc_type, "value": f"{v:.2f}"} for c, v in services.legacy_items(emp)]
        return Response({"id": None, "employee": emp.id, "employee_code": emp.employee_code, "employee_name": emp.full_name, "effective_from": emp.joining_date,
                         "reason": "Salary fields of the employee profile (no structure created yet)", "items": items})


class MonthlyVariablePayViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """Bonus / incentive entered per employee per month, before payroll is generated."""
    queryset = MonthlyVariablePay.objects.select_related("employee__user", "component")
    serializer_class = MonthlyVariablePaySerializer
    permission_classes = [IsAdminOrHR]
    filterset_fields = ["year", "month", "employee"]

    def perform_create(self, s):
        d = s.validated_data
        obj, _ = MonthlyVariablePay.objects.update_or_create(
            employee=d["employee"], year=d["year"], month=d["month"], component=d["component"],
            defaults={"amount": d["amount"], "note": d.get("note", ""), "entered_by": self.request.user})
        s.instance = obj
        log_action(self.request, "VARIABLE_PAY_SET", "MonthlyVariablePay", obj.id, {"employee": obj.employee.employee_code, "period": f"{obj.year}-{obj.month:02d}", "amount": str(obj.amount)})

    def perform_destroy(self, o):
        if Payroll.objects.filter(employee=o.employee, year=o.year, month=o.month).exists():
            raise ValidationError("Payroll for that month is already generated and locked.")
        log_action(self.request, "VARIABLE_PAY_DELETE", "MonthlyVariablePay", o.id); o.delete()
