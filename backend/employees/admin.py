from django.contrib import admin
from .models import Department, Employee, EmployeeDocument
admin.site.register([Department, Employee, EmployeeDocument])
