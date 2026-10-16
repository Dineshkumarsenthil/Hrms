from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/employees/", include("employees.urls")),
    path("api/attendance/", include("attendance.urls")),
    path("api/leaves/", include("leaves.urls")),
    path("api/payroll/", include("payroll.urls")),
    path("api/notifications/", include("notifications.urls")),
    path("api/reports/", include("reports.urls")),
    path("api/audit/", include("audit.urls")),
    path("api/holidays/", include("holidays.urls")),
    path("api/shifts/", include("shifts.urls")),
]
# NOTE: uploaded documents are NOT served publicly; they are streamed through authenticated endpoints.
