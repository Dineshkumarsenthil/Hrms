from decimal import Decimal
from rest_framework import serializers

from employees.models import Employee
from .models import MonthlyVariablePay, Payroll, PayrollLine, SalaryComponent, SalaryStructure


class PayrollLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollLine
        fields = ["id", "name", "code", "kind", "amount"]


class PayrollSerializer(serializers.ModelSerializer):
    lines = PayrollLineSerializer(many=True, read_only=True)
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


class SalaryComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaryComponent
        fields = ["id", "name", "code", "kind", "calc_type", "is_variable", "is_system", "is_active", "display_order"]
        read_only_fields = ["is_system"]

    def validate_code(self, v):
        return v.strip().upper().replace(" ", "_")

    def validate(self, a):
        kind = a.get("kind", getattr(self.instance, "kind", None))
        variable = a.get("is_variable", getattr(self.instance, "is_variable", False))
        calc = a.get("calc_type", getattr(self.instance, "calc_type", "FIXED"))
        if variable and kind == SalaryComponent.Kind.DEDUCTION:
            raise serializers.ValidationError("Only earnings can be variable (bonus, incentive).")
        if variable and calc != SalaryComponent.Calc.FIXED:
            raise serializers.ValidationError("A variable component must be a fixed amount each month.")
        if self.instance and self.instance.is_system:
            # payroll rules depend on the code, kind and calculation of system components
            for field in ("code", "kind", "calc_type", "is_variable"):
                if field in a and a[field] != getattr(self.instance, field):
                    raise serializers.ValidationError(f"'{self.instance.name}' is a system component; {field} cannot be changed.")
            if a.get("is_active") is False:
                raise serializers.ValidationError("System components cannot be deactivated.")
        return a


class StructureItemInput(serializers.Serializer):
    component = serializers.PrimaryKeyRelatedField(queryset=SalaryComponent.objects.all())
    value = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal("0"))


class SalaryStructureSerializer(serializers.ModelSerializer):
    employee_code = serializers.CharField(source="employee.employee_code", read_only=True)
    employee_name = serializers.CharField(source="employee.full_name", read_only=True)
    created_by_name = serializers.CharField(source="created_by.username", read_only=True, default="")
    items = serializers.SerializerMethodField()
    new_items = StructureItemInput(many=True, write_only=True, source="_items")

    class Meta:
        model = SalaryStructure
        fields = ["id", "employee", "employee_code", "employee_name", "effective_from", "reason", "created_by_name", "created_at", "items", "new_items"]
        read_only_fields = ["id", "created_at"]

    def get_items(self, obj):
        out = []
        for i in obj.items.all():
            c = i.component
            out.append({"component": c.id, "name": c.name, "code": c.code, "kind": c.kind, "calc_type": c.calc_type, "value": f"{i.value:.2f}"})
        return out

    def validate(self, a):
        emp, start, items = a["employee"], a["effective_from"], a["_items"]
        if not emp.is_active:
            raise serializers.ValidationError({"employee": "Employee is inactive."})
        if not items:
            raise serializers.ValidationError({"new_items": "Add at least one component."})
        seen = set()
        for it in items:
            comp = it["component"]
            if comp.id in seen:
                raise serializers.ValidationError({"new_items": f"{comp.name} is added twice."})
            seen.add(comp.id)
            if not comp.is_active:
                raise serializers.ValidationError({"new_items": f"{comp.name} is inactive."})
            if comp.is_variable:
                raise serializers.ValidationError({"new_items": f"{comp.name} is a variable component; enter it month by month under Variable pay."})
            if comp.calc_type == SalaryComponent.Calc.PERCENT_OF_BASIC and it["value"] > 100:
                raise serializers.ValidationError({"new_items": f"{comp.name}: percent cannot be more than 100."})
        if not any(it["component"].code == "BASIC" and it["value"] > 0 for it in items):
            raise serializers.ValidationError({"new_items": "Basic pay is required and must be above zero."})
        if SalaryStructure.objects.filter(employee=emp, effective_from=start).exists():
            raise serializers.ValidationError({"effective_from": "A structure already starts on this date."})
        if Payroll.objects.filter(employee=emp).filter(year__gt=start.year).exists() or Payroll.objects.filter(employee=emp, year=start.year, month__gte=start.month).exists():
            raise serializers.ValidationError({"effective_from": "Payroll is already generated for that month or later. Pick a later date."})
        return a


class MonthlyVariablePaySerializer(serializers.ModelSerializer):
    employee_code = serializers.CharField(source="employee.employee_code", read_only=True)
    employee_name = serializers.CharField(source="employee.full_name", read_only=True)
    component_name = serializers.CharField(source="component.name", read_only=True)

    class Meta:
        model = MonthlyVariablePay
        fields = ["id", "employee", "employee_code", "employee_name", "year", "month", "component", "component_name", "amount", "note"]
        read_only_fields = ["id"]
        validators = []  # saving the same employee/month/component again updates the amount instead of failing

    def validate_amount(self, v):
        if v <= 0:
            raise serializers.ValidationError("Amount must be above zero.")
        return v

    def validate_month(self, v):
        if not 1 <= v <= 12:
            raise serializers.ValidationError("Month must be 1-12.")
        return v

    def validate_component(self, c):
        if not (c.is_variable and c.is_active and c.kind == SalaryComponent.Kind.EARNING):
            raise serializers.ValidationError("Choose an active variable earning component.")
        return c

    def validate(self, a):
        if Payroll.objects.filter(employee=a["employee"], year=a["year"], month=a["month"]).exists():
            raise serializers.ValidationError("Payroll for that month is already generated and locked.")
        return a
