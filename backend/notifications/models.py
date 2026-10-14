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
