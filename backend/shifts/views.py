from django.db.models import Q
from django.utils import timezone
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAdminOrHR, IsEmployee
from audit.utils import log_action
from notifications.inapp import notify
from . import services
from .models import Shift, ShiftAssignment
from .serializers import ShiftAssignmentSerializer, ShiftSerializer


class ShiftViewSet(viewsets.ModelViewSet):
    """Everyone can see the shift list; only Admin/HR can change it."""
    queryset = Shift.objects.all()
    serializer_class = ShiftSerializer
    pagination_class = None

    def get_permissions(self):
        if self.request.method in ("GET", "HEAD", "OPTIONS"):
            return super().get_permissions()
        return [IsAdminOrHR()]

    def perform_create(self, s):
        o = s.save(); log_action(self.request, "SHIFT_CREATE", "Shift", o.id, {"name": o.name})

    def perform_update(self, s):
        o = s.save(); log_action(self.request, "SHIFT_UPDATE", "Shift", o.id, {"name": o.name})

    def perform_destroy(self, o):
        if o.assignments.exists():
            raise ValidationError("This shift has assignment history. Mark it inactive instead of deleting it.")
        log_action(self.request, "SHIFT_DELETE", "Shift", o.id, {"name": o.name}); o.delete()


class ShiftAssignmentViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    """Assignment history. History is never deleted, a running assignment is ended instead."""
    serializer_class = ShiftAssignmentSerializer
    filterset_fields = ["shift", "employee", "department"]

    def get_permissions(self):
        return [IsAdminOrHR()] if self.action in ("create", "end") else super().get_permissions()

    def get_queryset(self):
        qs = ShiftAssignment.objects.select_related("shift", "employee__user", "department", "assigned_by")
        u = self.request.user
        if u.is_hr_or_admin:
            return qs
        if not hasattr(u, "employee"):
            return qs.none()
        mine = Q(employee__user=u)
        if u.employee.department_id:  # department_id=None would match every employee-level row
            mine |= Q(department_id=u.employee.department_id)
        return qs.filter(mine)

    def perform_create(self, s):
        d = s.validated_data
        a = services.assign_shift(d["shift"], d["start_date"], self.request.user, d.get("employee"), d.get("department"), d.get("end_date"))
        s.instance = a
        log_action(self.request, "SHIFT_ASSIGN", "ShiftAssignment", a.id, {"shift": a.shift.name, "employee": a.employee.employee_code if a.employee else None,
                                                                              "department": a.department.name if a.department else None, "from": str(a.start_date)})
        if a.employee:
            notify(a.employee.user, "SHIFT", "Shift changed", f"You are assigned to {a.shift.name} from {a.start_date}.", "/shifts")

    @action(detail=True, methods=["post"])
    def end(self, request, pk=None):
        a = self.get_object()
        if a.end_date and a.end_date < timezone.localdate():
            raise ValidationError("This assignment has already ended.")
        a.end_date = timezone.localdate()
        a.save(update_fields=["end_date"])
        log_action(request, "SHIFT_ASSIGN_END", "ShiftAssignment", a.id)
        return Response(ShiftAssignmentSerializer(a).data)


class MyShiftView(APIView):
    """Today's shift of the logged-in employee, plus where it comes from."""
    permission_classes = [IsEmployee]

    def get(self, request):
        emp, today = request.user.employee, timezone.localdate()
        found = services.assignment_for(emp, today)
        shift = found.shift if found else services.default_shift()
        source = "default"
        if found:
            source = "employee" if found.employee_id else "department"
        return Response({"shift": ShiftSerializer(shift).data, "source": source})
