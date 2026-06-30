from django.db import models


class DashboardStats(models.Model):
    data = models.JSONField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"DashboardStats {self.id}"
