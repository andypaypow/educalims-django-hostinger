"""Admin dashboard pour voir les paiements en temps reel"""
from django.contrib import admin
from django.shortcuts import render
from django.http import HttpRequest
from .models import Abonnement


@admin.site.register_view
def payment_dashboard(request: HttpRequest):
    """Dashboard pour voir les paiements recus"""
    # Derniers abonnements (tous statuts)
    derniers_abonnements = Abonnement.objects.all()[:20]

    # Abonnements en attente
    abonnements_attente = Abonnement.objects.filter(statut='EN_ATTENTE').order_by('-date_creation')[:10]

    # Abonnements actifs
    abonnements_actifs = Abonnement.objects.filter(statut='ACTIF').order_by('-date_debut')[:10]

    # Abonnements echoues
    abonnements_echoues = Abonnement.objects.filter(statut='ECHOUE').order_by('-date_creation')[:10]

    context = {
        'title': 'Dashboard Paiements',
        'derniers_abonnements': derniers_abonnements,
        'abonnements_attente': abonnements_attente,
        'abonnements_actifs': abonnements_actifs,
        'abonnements_echoues': abonnements_echoues,
        'total_attente': Abonnement.objects.filter(statut='EN_ATTENTE').count(),
        'total_actifs': Abonnement.objects.filter(statut='ACTIF').count(),
        'total_echoues': Abonnement.objects.filter(statut='ECHOUE').count(),
    }

    return render(request, 'admin/educalims/payment_dashboard.html', context)


# Extension du template admin
admin.site.index_title = "Educalims - Gestion des abonnements"
