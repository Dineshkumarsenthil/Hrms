from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class HRMSUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("HRMS", {"fields": ("role", "must_change_password")}),)
    list_display = ("username", "email", "role", "is_active")
