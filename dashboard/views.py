from django.http import JsonResponse

def dashboard(request):
    data = {
        "ok": True
    }
    return JsonResponse(data)
