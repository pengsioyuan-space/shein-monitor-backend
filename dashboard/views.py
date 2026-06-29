
from django.shortcuts import render
from orders.models import Order

def dashboard(request):
    qs = Order.objects.all()
