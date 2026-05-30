"""mywebsite URL Configuration."""
from django.conf import settings
from django.contrib import admin
from django.urls import path

from main.views import reports
from mywebsite.api import api

urlpatterns = [
    path('my_admin/', admin.site.urls),
    path('main/api/', api.urls),
    path('report', reports, name='report'),
]

if settings.DEBUG:  # pragma: no cover
    from django.conf.urls.static import static  # noqa: WPS433

    urlpatterns = [
        *urlpatterns,
        # Serving media files in development only:
        *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
    ]
