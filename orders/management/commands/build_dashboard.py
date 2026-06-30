# orders/management/commands/build_dashboard.py

from django.core.management.base import BaseCommand
from orders.models import Order, DashboardStats

class Command(BaseCommand):
    def handle(self, *args, **kwargs):

        qs = Order.objects.all()

        stats = {
            "total": qs.count(),
            "eu": qs.filter(region="EU").count(),
            "us": qs.filter(region="US").count(),
            "ca": qs.filter(region="CA").count(),
            "other": qs.exclude(region__in=["EU","US","CA"]).count(),

            "pending_process_risk": qs.filter(created_hours__gte=12).count(),
            "pending_ship_risk": qs.filter(created_hours__gte=24).count(),
            "pickup_appointment_risk": qs.filter(created_hours__gte=36).count(),
            "pickup_risk": qs.filter(created_hours__gte=48).count(),
        }

        DashboardStats.objects.all().delete()
        DashboardStats.objects.create(**stats, data=stats)

        self.stdout.write("dashboard cached OK")
