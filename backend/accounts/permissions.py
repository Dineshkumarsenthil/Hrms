from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and u.role == "ADMIN")


class IsAdminOrHR(BasePermission):
    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and u.role in ("ADMIN", "HR"))


class IsEmployee(BasePermission):
    """Any logged-in user that has an employee profile (employees, and HR/admin who are also staff)."""
    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and hasattr(u, "employee"))


ROLE_MATRIX = {
    "ADMIN": ["Everything", "Manage roles & users", "Unlock/adjust payroll", "View audit logs"],
    "HR": ["Manage employees", "Attendance override", "Approve/reject leave", "Generate payroll", "Reports", "View audit logs"],
    "EMPLOYEE": ["View own profile", "Check-in/out", "Apply for leave", "View own attendance & salary slips"],
}
