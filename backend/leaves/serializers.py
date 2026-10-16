from datetime import date
from rest_framework import serializers
from .models import LeaveBalance, LeaveRequest, LeaveType
from .services import working_days_between


class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = "__all__"


class LeaveBalanceSerializer(serializers.ModelSerializer):
    leave_type_name = serializers.CharField(source="leave_type.name", read_only=True)
    remaining = serializers.DecimalField(max_digits=5, decimal_places=1, read_only=True)

    class Meta:
        model = LeaveBalance
        fields = ["id", "employee", "leave_type", "leave_type_name", "year", "allocated", "used", "remaining"]


class LeaveRequestSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.full_name", read_only=True)
    employee_code = serializers.CharField(source="employee.employee_code", read_only=True)
    leave_type_name = serializers.CharField(source="leave_type.name", read_only=True)
    reviewed_by_name = serializers.CharField(source="reviewed_by.username", read_only=True, default="")

    class Meta:
        model = LeaveRequest
        fields = ["id", "employee", "employee_name", "employee_code", "leave_type", "leave_type_name", "start_date",
                  "end_date", "days", "lop_days", "reason", "status", "applied_at", "reviewed_by_name", "reviewed_at", "remarks"]
        read_only_fields = ["id", "employee", "days", "lop_days", "status", "applied_at", "reviewed_at", "remarks"]

    def validate(self, a):
        s, e = a["start_date"], a["end_date"]
        emp = self.context["request"].user.employee
        if e < s:
            raise serializers.ValidationError("End date cannot be before start date.")
        if s < date.today():
            raise serializers.ValidationError("Cannot apply for leave in the past.")
        if s < emp.joining_date:
            raise serializers.ValidationError("Leave cannot start before your joining date.")
        if s.year != e.year:
            raise serializers.ValidationError("Split leave across calendar years into separate requests.")
        if not working_days_between(s, e, emp.region):
            raise serializers.ValidationError("Selected range has no working days (weekends and holidays are excluded).")
        if LeaveRequest.objects.filter(employee=emp, status__in=["PENDING", "APPROVED"], start_date__lte=e, end_date__gte=s).exists():
            raise serializers.ValidationError("You already have a leave request overlapping these dates.")
        return a


class ReviewSerializer(serializers.Serializer):
    remarks = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")
