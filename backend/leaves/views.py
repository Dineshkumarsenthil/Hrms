from decimal import Decimal
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from accounts.permissions import IsAdminOrHR, IsEmployee
from audit.utils import log_action
from employees.models import Employee
from notifications.inapp import notify, notify_staff
from notifications.service import send_templated
from .models import LeaveBalance, LeaveRequest, LeaveType
from .serializers import LeaveBalanceSerializer, LeaveRequestSerializer, LeaveTypeSerializer, ReviewSerializer
from .services import ensure_balances, working_days_between

User = get_user_model()


def _mail_ctx(r):
    return {"name": r.employee.full_name, "leave_type": r.leave_type.name, "start": r.start_date, "end": r.end_date,
            "days": r.days, "lop_days": r.lop_days, "remarks": r.remarks or "-"}


def _available(emp, lt, year, exclude_request=None):
    bal = ensure_balances(emp, year).get(leave_type=lt)
    pending = LeaveRequest.objects.filter(employee=emp, leave_type=lt, status="PENDING", start_date__year=year)
    if exclude_request:
        pending = pending.exclude(pk=exclude_request.pk)
    held = sum((p.days - p.lop_days for p in pending), Decimal("0"))
    return max(Decimal("0"), bal.allocated - bal.used - held)


class LeaveTypeViewSet(viewsets.ModelViewSet):
    queryset = LeaveType.objects.all().order_by("name")
    serializer_class = LeaveTypeSerializer
    pagination_class = None

    def get_permissions(self):
        return [IsAdminOrHR()] if self.request.method not in ("GET", "HEAD", "OPTIONS") else super().get_permissions()

    def perform_create(self, s):
        o = s.save(); log_action(self.request, "LEAVE_TYPE_CREATE", "LeaveType", o.id, {"name": o.name})

    def perform_update(self, s):
        o = s.save(); log_action(self.request, "LEAVE_TYPE_UPDATE", "LeaveType", o.id, {"name": o.name})


class LeaveBalanceViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = LeaveBalanceSerializer
    pagination_class = None

    def list(self, request, *args, **kwargs):
        year = int(request.query_params.get("year", timezone.localdate().year))
        if request.user.is_hr_or_admin and request.query_params.get("employee"):
            emp = Employee.objects.get(pk=request.query_params["employee"])
        elif hasattr(request.user, "employee"):
            emp = request.user.employee
        else:
            return Response([])
        return Response(self.get_serializer(ensure_balances(emp, year), many=True).data)


class LeaveRequestViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = LeaveRequestSerializer
    filterset_fields = {"status": ["exact"], "leave_type": ["exact"], "employee": ["exact"],
                        "employee__department": ["exact"], "start_date": ["gte", "lte"]}

    def get_queryset(self):
        qs = LeaveRequest.objects.select_related("employee__user", "leave_type", "reviewed_by")
        u = self.request.user
        return qs if u.is_hr_or_admin else qs.filter(employee__user=u)

    def get_permissions(self):
        return [IsEmployee()] if self.action in ("create", "cancel") else super().get_permissions()

    @transaction.atomic
    def perform_create(self, s):
        emp = self.request.user.employee
        d = s.validated_data
        days = Decimal(len(working_days_between(d["start_date"], d["end_date"], emp.region)))
        lt = d["leave_type"]
        lop = days if not lt.is_paid else max(Decimal("0"), days - _available(emp, lt, d["start_date"].year))
        r = s.save(employee=emp, days=days, lop_days=lop)
        log_action(self.request, "LEAVE_APPLY", "LeaveRequest", r.id, {"days": str(days), "lop_days": str(lop)})
        send_templated("LEAVE_APPLIED", emp.user.email, _mail_ctx(r))
        for hr in User.objects.filter(role__in=["HR", "ADMIN"], is_active=True).exclude(pk=emp.user_id):
            send_templated("LEAVE_APPLIED_HR", hr.email, _mail_ctx(r))
        notify_staff("LEAVE", "New leave request", f"{emp.full_name} applied for {lt.name} from {r.start_date} to {r.end_date}.", "/leaves", exclude_user=emp.user)

    def _review(self, request, pk, approve):
        s = ReviewSerializer(data=request.data); s.is_valid(raise_exception=True)
        with transaction.atomic():
            r = LeaveRequest.objects.select_for_update().select_related("employee__user", "leave_type").get(pk=pk)
            if r.status != "PENDING":
                raise ValidationError(f"Request is already {r.status.lower()}.")
            if r.employee.user_id == request.user.id:
                raise ValidationError("You cannot review your own leave request.")
            if approve:
                year = r.start_date.year
                bal = ensure_balances(r.employee, year).select_for_update().get(leave_type=r.leave_type)
                available = max(Decimal("0"), bal.allocated - bal.used)
                r.lop_days = r.days if not r.leave_type.is_paid else max(Decimal("0"), r.days - available)  # recalculated at approval
                bal.used += r.days - r.lop_days  # automatic balance adjustment
                bal.save()
            r.status = "APPROVED" if approve else "REJECTED"
            r.reviewed_by, r.reviewed_at, r.remarks = request.user, timezone.now(), s.validated_data["remarks"]
            r.save()
        log_action(request, "LEAVE_APPROVE" if approve else "LEAVE_REJECT", "LeaveRequest", r.id, {"employee": r.employee.employee_code, "lop_days": str(r.lop_days)})
        send_templated("LEAVE_APPROVED" if approve else "LEAVE_REJECTED", r.employee.user.email, _mail_ctx(r))
        word = "approved" if approve else "rejected"
        notify(r.employee.user, "LEAVE", f"Leave request {word}", f"Your {r.leave_type.name} request ({r.start_date} to {r.end_date}) was {word}." + (f" Remarks: {r.remarks}" if r.remarks else ""), "/leaves")
        return Response(LeaveRequestSerializer(r).data)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminOrHR])
    def approve(self, request, pk=None):
        return self._review(request, pk, True)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminOrHR])
    def reject(self, request, pk=None):
        return self._review(request, pk, False)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        with transaction.atomic():
            r = LeaveRequest.objects.select_for_update().get(pk=pk, employee__user=request.user)
            if r.status == "APPROVED" and r.start_date > timezone.localdate():
                bal = LeaveBalance.objects.get(employee=r.employee, leave_type=r.leave_type, year=r.start_date.year)
                bal.used -= r.days - r.lop_days  # give the balance back
                bal.save()
            elif r.status != "PENDING":
                raise ValidationError("Only pending or future approved requests can be cancelled.")
            r.status = "CANCELLED"; r.save()
        log_action(request, "LEAVE_CANCEL", "LeaveRequest", r.id)
        return Response(LeaveRequestSerializer(r).data)
