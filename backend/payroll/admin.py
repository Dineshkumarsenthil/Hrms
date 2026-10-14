from django.contrib import admin
from .models import Payroll, SalarySlip
admin.site.register([Payroll, SalarySlip])
