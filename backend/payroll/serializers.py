from rest_framework import serializers
from .models import Payroll


class PayrollSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.full_name", read_only=True)
    employee_code = serializers.CharField(source="employee.employee_code", read_only=True)
    department = serializers.CharField(source="employee.department.name", read_only=True, default="")
    has_slip = serializers.SerializerMethodField()

    class Meta:
        model = Payroll
        fields = "__all__"
        read_only_fields = [f.name for f in Payroll._meta.fields]

    def get_has_slip(self, obj):
        return hasattr(obj, "slip")


class GenerateSerializer(serializers.Serializer):
    year = serializers.IntegerField(min_value=2000, max_value=2100)
    month = serializers.IntegerField(min_value=1, max_value=12)
    employee = serializers.IntegerField(required=False)


class AdjustSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    note = serializers.CharField(max_length=255)


class ReasonSerializer(serializers.Serializer):
    reason = serializers.CharField(max_length=255)
