from datetime import time
from decimal import Decimal
from django.db import migrations


def add_general_shift(apps, schema_editor):
    Shift = apps.get_model("shifts", "Shift")
    Shift.objects.get_or_create(name="General Shift", defaults={"kind": "GENERAL", "start_time": time(9, 0), "end_time": time(18, 0), "grace_minutes": 15, "work_hours": Decimal("8")})


class Migration(migrations.Migration):
    dependencies = [("shifts", "0001_initial")]
    operations = [migrations.RunPython(add_general_shift, migrations.RunPython.noop)]
