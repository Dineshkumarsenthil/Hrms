import tempfile
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase, override_settings


@override_settings(MEDIA_ROOT=tempfile.mkdtemp(), EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class FullFlowTest(TestCase):
    """Runs smoke_test.py (auth, RBAC, employees, attendance, leave, payroll, reports, audit) on a throw-away test DB."""

    def test_full_flow(self):
        call_command("seed_data", verbosity=0)
        code = (Path(settings.BASE_DIR) / "smoke_test.py").read_text()
        g = {}
        exec(compile(code, "smoke_test.py", "exec"), g)
        self.assertEqual(g["fails"], [], f"Failing checks: {g['fails']}")
