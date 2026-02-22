"""
Vue pour la page d'accueil de Filtre Expert
"""
from django.shortcuts import render
from django.utils import timezone
from gosen.models import WebhookLog


def home(request):
    """Page d'accueil de l'application"""
    # Statistiques webhooks récents
    stats = {
        'total_webhooks': WebhookLog.objects.count(),
        'webhooks_today': WebhookLog.objects.filter(
            date_reception__date=timezone.now().date()
        ).count(),
        'webhooks_success': WebhookLog.objects.filter(statut='SUCCES').count(),
        'webhooks_error': WebhookLog.objects.filter(statut='ERREUR').count(),
    }

    # Derniers webhooks
    recent_webhooks = WebhookLog.objects.order_by('-date_reception')[:5]

    context = {
        'stats': stats,
        'recent_webhooks': recent_webhooks,
        'webhook_url': request.build_absolute_uri('/webhook/receiver/'),
    }

    return render(request, 'gosen/home.html', context)
