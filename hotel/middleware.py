import hashlib
import ipaddress
import json
import re

from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.core.cache import cache
from django.utils.timezone import now

from .models import Visit


BOT_PATTERN = re.compile(
    (
        r"bot|crawler|spider|slurp|bingpreview|"
        r"facebookexternalhit|whatsapp|telegrambot|"
        r"discordbot|linkedinbot|twitterbot|"
        r"googlebot|bingbot|yandex|baiduspider|"
        r"duckduckbot|semrush|ahrefs|mj12bot|"
        r"dotbot|petalbot|bytespider|uptimerobot|"
        r"headlesschrome|phantomjs|selenium|"
        r"python-requests|python-urllib|curl|wget"
    ),
    re.IGNORECASE,
)


IGNORED_PATH_PREFIXES = (
    "/admin/",
    "/static/",
    "/media/",
    "/accounts/",
    "/user_profile/",
    "/dashboard/",
    "/habitaciones_dashboard/",
    "/contratos/",
    "/visitas/",
    "/formalizaciones/",
    "/formalizacion/",
)


IGNORED_PATHS = {
    "/favicon.ico",
    "/robots.txt",
    "/sitemap.xml",
}


IGNORED_EXTENSIONS = (
    ".css",
    ".js",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".ico",
    ".webp",
    ".woff",
    ".woff2",
    ".ttf",
    ".map",
    ".pdf",
    ".xml",
    ".txt",
)


def get_client_ip(request):
    forwarded_for = request.META.get(
        "HTTP_X_FORWARDED_FOR",
        "",
    )

    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    return request.META.get(
        "REMOTE_ADDR",
        "",
    ).strip()


def is_public_ip(ip):
    try:
        address = ipaddress.ip_address(ip)

        return not (
            address.is_private
            or address.is_loopback
            or address.is_reserved
            or address.is_multicast
            or address.is_unspecified
        )

    except ValueError:
        return False


def is_bot(user_agent):
    if not user_agent:
        return True

    return bool(
        BOT_PATTERN.search(user_agent)
    )


def should_ignore_path(path):
    normalized_path = path.lower()

    if normalized_path in IGNORED_PATHS:
        return True

    if normalized_path.startswith(
        IGNORED_PATH_PREFIXES
    ):
        return True

    return normalized_path.endswith(
        IGNORED_EXTENSIONS
    )


def get_location_data(ip):
    """
    Obtiene una ubicación aproximada y la conserva
    durante 24 horas para evitar consultas repetidas.
    """
    empty_location = {
        "city": None,
        "region": None,
        "country": None,
        "country_code": None,
    }

    if not is_public_ip(ip):
        return empty_location

    cache_key = (
        "visitor-location:"
        + hashlib.sha256(
            ip.encode("utf-8")
        ).hexdigest()
    )

    cached_location = cache.get(
        cache_key
    )

    if cached_location is not None:
        return cached_location

    request = Request(
        f"https://ipapi.co/{ip}/json/",
        headers={
            "User-Agent": (
                "ByColeccion-VisitorAnalytics/1.0"
            ),
            "Accept": "application/json",
        },
    )

    try:
        with urlopen(
            request,
            timeout=2.5,
        ) as response:
            data = json.loads(
                response.read().decode("utf-8")
            )

        if data.get("error"):
            location = empty_location

        else:
            location = {
                "city": (
                    data.get("city") or None
                ),
                "region": (
                    data.get("region") or None
                ),
                "country": (
                    data.get("country_name")
                    or None
                ),
                "country_code": (
                    data.get("country_code")
                    or data.get("country")
                    or None
                ),
            }

    except (
        HTTPError,
        URLError,
        TimeoutError,
        json.JSONDecodeError,
        OSError,
    ):
        location = empty_location

    cache.set(
        cache_key,
        location,
        timeout=60 * 60 * 24,
    )

    return location


class VisitorLoggingMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.method != "GET":
            return response

        if response.status_code >= 400:
            return response

        if (
            hasattr(request, "user")
            and request.user.is_authenticated
        ):
            return response

        path = request.path

        if should_ignore_path(path):
            return response

        user_agent = request.META.get(
            "HTTP_USER_AGENT",
            "",
        )

        if is_bot(user_agent):
            return response

        ip = get_client_ip(request)

        if not ip:
            return response

        visit_key_source = (
            f"{ip}|{path}|{user_agent}"
        )

        visit_key = (
            "visitor-seen:"
            + hashlib.sha256(
                visit_key_source.encode("utf-8")
            ).hexdigest()
        )

        # Una misma persona y página solamente se registra
        # una vez cada treinta minutos.
        if cache.get(visit_key):
            return response

        location = get_location_data(ip)

        try:
            Visit.objects.create(
                ip=ip,
                path=path,
                user_agent=user_agent,
                city=location["city"],
                region=location["region"],
                country=location["country"],
                country_code=(
                    location["country_code"]
                ),
                timestamp=now(),
            )

            cache.set(
                visit_key,
                True,
                timeout=60 * 30,
            )

        except Exception:
            # Las estadísticas jamás deben impedir
            # que la web responda al visitante.
            pass

        return response