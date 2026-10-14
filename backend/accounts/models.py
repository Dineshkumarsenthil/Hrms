from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        HR = "HR", "HR"
        EMPLOYEE = "EMPLOYEE", "Employee"

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.EMPLOYEE, db_index=True)
    must_change_password = models.BooleanField(default=False)

    REQUIRED_FIELDS = ["email"]

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN

    @property
    def is_hr_or_admin(self):
        return self.role in (self.Role.ADMIN, self.Role.HR)
