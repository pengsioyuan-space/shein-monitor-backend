# orders/models.py

class DashboardStats(models.Model):
    updated_at = models.DateTimeField(auto_now=True)

    total = models.IntegerField(default=0)
    eu = models.IntegerField(default=0)
    us = models.IntegerField(default=0)
    ca = models.IntegerField(default=0)
    other = models.IntegerField(default=0)

    pending_process_risk = models.IntegerField(default=0)
    pending_ship_risk = models.IntegerField(default=0)
    pickup_appointment_risk = models.IntegerField(default=0)
    pickup_risk = models.IntegerField(default=0)

    data = models.JSONField(default=dict)
