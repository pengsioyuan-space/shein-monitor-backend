from django.db import models


class Order(models.Model):
    order_no = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        verbose_name="订单号"
    )

    shop_name = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name="店铺"
    )

    region = models.CharField(
        max_length=20,
        blank=True,
        default="OTHER",
        db_index=True,
        verbose_name="区域"
    )

    created_time = models.CharField(
        max_length=50,
        blank=True,
        default="",
        verbose_name="订单创建时间"
    )

    created_hours = models.FloatField(
        default=0,
        db_index=True,
        verbose_name="已创建小时数"
    )

    package_no = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="妙手包裹号"
    )

    logistics_no = models.CharField(
        max_length=100,
        blank=True,
        default="",
        db_index=True,
        verbose_name="物流单号"
    )

    fulfillment_type = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="履约类型"
    )

    first_collected_time = models.CharField(
        max_length=50,
        blank=True,
        default="",
        verbose_name="首次揽收时间"
    )

    is_collected = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="是否已揽收"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="入库时间"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="更新时间"
    )

    def __str__(self):
        return self.order_no

    class Meta:
        db_table = "orders_order"
        ordering = ["-created_hours"]


class DashboardStats(models.Model):
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

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"DashboardStats {self.id}"

    class Meta:
        db_table = "orders_dashboardstats"
