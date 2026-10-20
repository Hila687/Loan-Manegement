"""
Serve the built Vue app (index.html) for every page URL, so the site and
the API live on one address. Assets under /assets/ are served by WhiteNoise.
"""

from django.conf import settings
from django.db import connection
from django.http import FileResponse, HttpResponse, JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie


@never_cache
@ensure_csrf_cookie
def spa_index(request, *args, **kwargs):
    index = settings.FRONTEND_DIST / "index.html"

    if not index.exists():
        return HttpResponse(
            "The frontend has not been built. "
            "Run `npm run build` in frontend/client "
            "(the Docker image does this automatically).",
            status=503,
            content_type="text/plain; charset=utf-8",
        )

    return FileResponse(open(index, "rb"), content_type="text/html; charset=utf-8")


@never_cache
def health(request):
    """For the hosting platform's health check: app up + database reachable."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception:
        return JsonResponse({"status": "error", "database": False}, status=503)

    return JsonResponse({"status": "ok", "database": True})
