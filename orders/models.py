
from django.db import models

class Order(models.Model):
    order_no = models.CharField(max_length=100, unique=True)
    shop_name = models.CharField(max_length=100)
    region = models.CharField(max_length=10, default='OTHER')
    create_time = models.DateTimeField(null=True)
    created_hours = models.FloatField(default=0)
    logistics_no = models.CharField(max_length=100, blank=True, null=True)
    fulfillment_type = models.CharField(max_length=50, blank=True, null=True)


class OrderRisk(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    is_delay_risk = models.BooleanField(default=False)
