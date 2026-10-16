from rest_framework import serializers
from shifts.models import Shift
from .models import Attendance
from .services import hours_and_status


class AttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.full_name", read_only=True)
    employee_code = serializers.CharField(source="employee.employee_code", read_only=True)
    department = serializers.CharField(source="employee.department.name", read_only=True, default="")
    shift_name = serializers.CharField(source="shift.name", read_only=True, default="")

    class Meta:
        model = Attendance
        fields = ["id", "employee", "employee_name", "employee_code", "department", "date", "check_in", "check_out",
                  "working_hours", "status", "is_overridden", "override_note", "shift", "shift_name", "late_minutes",
                  "early_exit_minutes", "overtime_hours"]
        read_only_fields = fields


class OverrideSerializer(serializers.Serializer):
    employee = serializers.IntegerField()
    date = serializers.DateField()
    check_in = serializers.DateTimeField(required=False, allow_null=True)
    check_out = serializers.DateTimeField(required=False, allow_null=True)
    status = serializers.ChoiceField(choices=Attendance.Status.choices, required=False)
    shift = serializers.PrimaryKeyRelatedField(queryset=Shift.objects.filter(is_active=True), required=False, allow_null=True)
    note = serializers.CharField(max_length=255)  # a reason is mandatory for corrections

    def validate(self, a):
        ci, co = a.get("check_in"), a.get("check_out")
        if co and not ci:
            raise serializers.ValidationError("check_out requires check_in.")
        if ci and co and co <= ci:
            raise serializers.ValidationError("check_out must be after check_in.")
        if not a.get("status") and not (ci and co):
            raise serializers.ValidationError("Provide status, or both check_in and check_out.")
        return a
