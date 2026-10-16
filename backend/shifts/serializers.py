from datetime import date
from decimal import Decimal
from rest_framework import serializers

from employees.models import Department, Employee
from .models import Shift, ShiftAssignment


class ShiftSerializer(serializers.ModelSerializer):
    kind_label = serializers.CharField(source="get_kind_display", read_only=True)
    is_overnight = serializers.BooleanField(read_only=True)
    scheduled_hours = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)

    class Meta:
        model = Shift
        fields = ["id", "name", "kind", "kind_label", "start_time", "end_time", "is_overnight", "scheduled_hours", "grace_minutes", "work_hours", "is_active"]

    def validate(self, a):
        start = a.get("start_time", getattr(self.instance, "start_time", None))
        end = a.get("end_time", getattr(self.instance, "end_time", None))
        if start == end:
            raise serializers.ValidationError("Start and end time cannot be the same.")
        hours = a.get("work_hours", getattr(self.instance, "work_hours", Decimal("8")))
        if not (Decimal("1") <= hours <= Decimal("16")):
            raise serializers.ValidationError({"work_hours": "Must be between 1 and 16 hours."})
        if a.get("grace_minutes", 0) > 120:
            raise serializers.ValidationError({"grace_minutes": "Grace period cannot be more than 120 minutes."})
        return a


class ShiftAssignmentSerializer(serializers.ModelSerializer):
    shift_name = serializers.CharField(source="shift.name", read_only=True)
    employee_code = serializers.CharField(source="employee.employee_code", read_only=True, default="")
    employee_name = serializers.CharField(source="employee.full_name", read_only=True, default="")
    department_name = serializers.CharField(source="department.name", read_only=True, default="")
    assigned_by_name = serializers.CharField(source="assigned_by.username", read_only=True, default="")

    class Meta:
        model = ShiftAssignment
        fields = ["id", "shift", "shift_name", "employee", "employee_code", "employee_name", "department", "department_name",
                  "start_date", "end_date", "assigned_by_name", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate(self, a):
        emp, dept = a.get("employee"), a.get("department")
        if bool(emp) == bool(dept):
            raise serializers.ValidationError("Choose either an employee or a department.")
        if emp and not emp.is_active:
            raise serializers.ValidationError({"employee": "Employee is inactive."})
        start, end = a["start_date"], a.get("end_date")
        if end and end < start:
            raise serializers.ValidationError({"end_date": "End date cannot be before the start date."})
        return a
