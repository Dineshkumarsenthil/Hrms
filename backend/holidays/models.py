from django.db import models


class Holiday(models.Model):
    class Kind(models.TextChoices):
        COMPANY = "COMPANY", "Company-wide"
        REGIONAL = "REGIONAL", "Regional"
        OPTIONAL = "OPTIONAL", "Optional"

    name = models.CharField(max_length=100)
    date = models.DateField(db_index=True)
    kind = models.CharField(max_length=10, choices=Kind.choices, default=Kind.COMPANY, db_index=True)
    region = models.CharField(max_length=50, blank=True, help_text="Only for regional holidays, e.g. Tamil Nadu")
    description = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date", "name"]
        constraints = [models.UniqueConstraint(fields=["date", "name"], name="uniq_holiday_per_day")]

    def __str__(self):
        return f"{self.date} {self.name}"
