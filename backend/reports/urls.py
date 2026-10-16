from django.urls import path
from .views import AdminDashboard, AttendanceReport, EmployeeDashboard, LeaveReport, PayrollReport, ShiftAttendanceReport

urlpatterns = [
    path("attendance/", AttendanceReport.as_view()),
    path("shift-attendance/", ShiftAttendanceReport.as_view()),
    path("leaves/", LeaveReport.as_view()),
    path("payroll/", PayrollReport.as_view()),
    path("dashboard/admin/", AdminDashboard.as_view()),
    path("dashboard/employee/", EmployeeDashboard.as_view()),
]
