"""
URLs du projet Gosen TurfFilter
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Administration Django
    path('admin/', admin.site.urls),

    # URLs de l'application Gosen
    path('', include('gosen.urls')),
]
