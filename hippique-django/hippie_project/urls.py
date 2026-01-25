from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.http import HttpResponse


def root_redirect(request):
    """Redirige la racine vers turf-filter"""
    return redirect('/hippie/turf-filter/')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', root_redirect),
    path('hippie/', include('hippie.urls')),
]

# Serve static files in development
if settings.DEBUG:
    # Serve from app static directories
    if settings.STATICFILES_DIRS:
        for static_dir in settings.STATICFILES_DIRS:
            urlpatterns += static(settings.STATIC_URL, document_root=static_dir)
    else:
        urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
