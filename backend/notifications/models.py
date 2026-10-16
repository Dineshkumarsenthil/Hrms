from django.conf import settings
from django.db import models


class EmailTemplate(models.Model):
    code = models.CharField(max_length=50, unique=True)
    subject = models.CharField(max_length=200)
    body = models.TextField(help_text="Django template syntax, e.g. Hello {{ name }}")

    def __str__(self):
        return self.code


class EmailLog(models.Model):
    class Status(models.TextChoices):
        SENT = "SENT", "Sent"
        FAILED = "FAILED", "Failed"

    template_code = models.CharField(max_length=50, db_index=True)
    to_email = models.EmailField()
    subject = models.CharField(max_length=200)
    body = models.TextField()
    status = models.CharField(max_length=10, choices=Status.choices)
    error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]


# ---------- in-app notifications ----------
class Broadcast(models.Model):
    """An announcement sent by an admin. department = null means the whole organization."""
    title = models.CharField(max_length=120)
    message = models.TextField(max_length=1000)
    department = models.ForeignKey("employees.Department", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    sent_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="+")
    recipient_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class Notification(models.Model):
    class Kind(models.TextChoices):
        LEAVE = "LEAVE", "Leave updates"
        PAYROLL = "PAYROLL", "Payroll & salary slips"
        ATTENDANCE = "ATTENDANCE", "Attendance alerts"
        SHIFT = "SHIFT", "Shift changes"
        ANNOUNCEMENT = "ANNOUNCEMENT", "Announcements"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    kind = models.CharField(max_length=15, choices=Kind.choices, db_index=True)
    title = models.CharField(max_length=120)
    message = models.CharField(max_length=1000)
    link = models.CharField(max_length=100, blank=True, help_text="Frontend page to open, e.g. /leaves")
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    broadcast = models.ForeignKey(Broadcast, null=True, blank=True, on_delete=models.SET_NULL, related_name="notifications")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [models.Index(fields=["user", "is_read", "-created_at"])]


class NotificationPreference(models.Model):
    """A row exists only when a user changed a setting. No row = enabled."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notification_preferences")
    kind = models.CharField(max_length=15, choices=Notification.Kind.choices)
    enabled = models.BooleanField(default=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "kind"], name="one_preference_per_kind")]
