from .models import Visit
from django.utils.timezone import now

import requests
from .models import Visit
from django.utils.timezone import now

def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip

def get_location_data(ip):
    try:
        response = requests.get(f"https://ipinfo.io/{ip}/json", timeout=3)
        data = response.json()
        return data.get("city", ""), data.get("country", "")
    except:
        return "", ""

class VisitorLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = get_client_ip(request)
        user_agent = request.META.get("HTTP_USER_AGENT", "")
        path = request.path

        if not path.startswith('/admin') and not path.startswith('/static'):
            city, country = get_location_data(ip)
            Visit.objects.create(
                ip=ip,
                path=path,
                user_agent=user_agent,
                city=city,
                country=country,
                timestamp=now()
            )

        return self.get_response(request)
