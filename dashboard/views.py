
from django.shortcuts import render
from orders.models import Order

def dashboard(request):
    qs = Order.objects.all()

    return render(request, 'dashboard.html', {
        'total': qs.count(),
        'eu': qs.filter(region='EU').count(),
        'us': qs.filter(region='US').count(),
        'ca': qs.filter(region='CA').count(),
        't12': qs.filter(created_hours__gte=12).count(),
        't24': qs.filter(created_hours__gte=24).count(),
        't36': qs.filter(created_hours__gte=36).count(),
        't48': qs.filter(created_hours__gte=48).count(),
    })
