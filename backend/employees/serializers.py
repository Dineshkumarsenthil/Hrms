import secrets
from datetime import date
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers
from .models import Department, Employee, EmployeeDocument

User = get_user_model()


class DepartmentSerializer(serializers.ModelSerializer):
    employee_count = serializers.IntegerField(source="employees.count", read_only=True)

    class Meta:
        model = Department
        fields = ["id", "name", "employee_count"]


class EmployeeSerializer(serializers.ModelSerializer):
    # user fields (flattened for the frontend)
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email")
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name", required=False, allow_blank=True)
    role = serializers.ChoiceField(source="user.role", choices=User.Role.choices, default="EMPLOYEE")
    department_name = serializers.CharField(source="department.name", read_only=True)
    gross_salary = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Employee
        fields = ["id", "employee_code", "username", "email", "first_name", "last_name", "role", "department",
                  "department_name", "designation", "phone", "joining_date", "region", "basic_salary", "hra", "allowances",
                  "pf_percent", "tax_deduction", "gross_salary", "is_active"]
        read_only_fields = ["is_active"]
        extra_kwargs = {"employee_code": {"required": False}}  # auto-generated when blank

    def validate_email(self, v):
        qs = User.objects.filter(email__iexact=v)
        if self.instance:
            qs = qs.exclude(pk=self.instance.user_id)
        if qs.exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return v.lower()

    def validate_joining_date(self, v):
        if v > date.today():
            raise serializers.ValidationError("Joining date cannot be in the future.")
        return v

    def _check_money(self, attrs):
        for f in ("basic_salary", "hra", "allowances", "tax_deduction"):
            if attrs.get(f) is not None and attrs[f] < 0:
                raise serializers.ValidationError({f: "Must be zero or positive."})
        pf = attrs.get("pf_percent")
        if pf is not None and not (0 <= pf <= 100):
            raise serializers.ValidationError({"pf_percent": "Must be between 0 and 100."})

    def validate(self, attrs):
        self._check_money(attrs)
        return attrs

    @staticmethod
    def _next_code():
        nums = [int(c[3:]) for c in Employee.objects.values_list("employee_code", flat=True) if c.startswith("EMP") and c[3:].isdigit()]
        return f"EMP{(max(nums) + 1) if nums else 1:03d}"

    @transaction.atomic
    def create(self, validated):
        u = validated.pop("user")
        username = self.initial_data.get("username") or u["email"].split("@")[0]
        base, n = username, 1
        while User.objects.filter(username=username).exists():
            n += 1
            username = f"{base}{n}"
        if not validated.get("employee_code"):
            validated["employee_code"] = self._next_code()
        password = secrets.token_urlsafe(9)
        user = User.objects.create_user(username=username, email=u["email"], password=password,
                                        first_name=u.get("first_name", ""), last_name=u.get("last_name", ""),
                                        role=u.get("role", "EMPLOYEE"), must_change_password=True)
        emp = Employee.objects.create(user=user, **validated)
        emp._temp_password = password  # picked up by the view for the onboarding email
        return emp

    @transaction.atomic
    def update(self, instance, validated):
        u = validated.pop("user", {})
        if instance.structures.exists():
            # pay is managed through salary structures (Payroll page); ignore the flat fields here
            for f in ("basic_salary", "hra", "allowances", "pf_percent", "tax_deduction"):
                validated.pop(f, None)
        if "role" in u and not self.context["request"].user.is_admin_role:
            u.pop("role")  # only Admin may change roles
        for k, v in u.items():
            setattr(instance.user, k, v)
        instance.user.save()
        return super().update(instance, validated)


class MyProfileSerializer(EmployeeSerializer):
    """Employees see their profile read-only."""
    class Meta(EmployeeSerializer.Meta):
        read_only_fields = EmployeeSerializer.Meta.fields


class EmployeeDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeDocument
        fields = ["id", "employee", "title", "original_name", "file", "uploaded_at"]
        read_only_fields = ["id", "employee", "original_name", "uploaded_at"]
        extra_kwargs = {"file": {"write_only": True}}
