from django.db import migrations

# code, name, kind, calc type, variable?, system?, order
DEFAULTS = [
    ("BASIC", "Basic Pay", "EARNING", "FIXED", False, True, 1),
    ("HRA", "House Rent Allowance", "EARNING", "FIXED", False, True, 2),
    ("ALLOWANCE", "Other Allowances", "EARNING", "FIXED", False, True, 3),
    ("BONUS", "Performance Bonus", "EARNING", "FIXED", True, False, 4),
    ("PF", "Provident Fund", "DEDUCTION", "PERCENT_OF_BASIC", False, True, 10),
    ("TAX", "Tax / TDS", "DEDUCTION", "FIXED", False, True, 11),
]


def add_defaults(apps, schema_editor):
    Component = apps.get_model("payroll", "SalaryComponent")
    for code, name, kind, calc, variable, system, order in DEFAULTS:
        Component.objects.get_or_create(code=code, defaults={"name": name, "kind": kind, "calc_type": calc, "is_variable": variable, "is_system": system, "display_order": order})


class Migration(migrations.Migration):
    dependencies = [("payroll", "0002_salarycomponent_payroll_other_deductions_and_more")]
    operations = [migrations.RunPython(add_defaults, migrations.RunPython.noop)]
