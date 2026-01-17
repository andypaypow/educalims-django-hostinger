"""
URL configuration for educalims_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from educalims.models import Abonnement


# Vue admin dashboard pour les paiements
def admin_payment_dashboard(request):
    """Dashboard pour voir les paiements recus"""
    if not request.user.is_superuser:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Accès réservé aux administrateurs")

    # Derniers abonnements
    derniers_abonnements = Abonnement.objects.all().order_by('-date_creation')[:20]

    # Abonnements en attente
    abonnements_attente = Abonnement.objects.filter(
        statut='EN_ATTENTE'
    ).order_by('-date_creation')[:10]

    # Abonnements actifs
    abonnements_actifs = Abonnement.objects.filter(
        statut='ACTIF'
    ).order_by('-date_debut')[:10]

    # Abonnements echoues
    abonnements_echoues = Abonnement.objects.filter(
        statut='ECHOUE'
    ).order_by('-date_creation')[:10]

    context = {
        'title': 'Dashboard Paiements',
        'derniers_abonnements': derniers_abonnements,
        'abonnements_attente': abonnements_attente,
        'abonnements_actifs': abonnements_actifs,
        'abonnements_echoues': abonnements_echoues,
        'total_attente': Abonnement.objects.filter(statut='EN_ATTENTE').count(),
        'total_actifs': Abonnement.objects.filter(statut='ACTIF').count(),
        'total_echoues': Abonnement.objects.filter(statut='ECHOUE').count(),
        'site_title': admin.site.site_title,
        'site_header': admin.site.site_header,
    }

    return render(request, 'admin/educalims/payment_dashboard.html', context)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin/payment-dashboard/', admin_payment_dashboard, name='admin_payment_dashboard'),
    path('', include('educalims.urls')),
]

# Servir les fichiers media et static en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
