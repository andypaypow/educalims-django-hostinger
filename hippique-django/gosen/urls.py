"""
URLs pour l'application Gosen TurfFilter
"""
from django.urls import path
from .views import webhooks, base, filters


app_name = 'gosen'


urlpatterns = [
    # ============================================
    # HOME - Application principale
    # ============================================

    # Page d'accueil (application Gosen TurfFilter)
    path('', base.index, name='home'),

    # API pour compter les combinaisons
    path('api/combinations/count/', base.api_combinations_count, name='api_combinations_count'),

    # API pour parser les pronostics
    path('api/parse-pronostics/', base.parse_pronostics, name='parse_pronostics'),

    # API pour filtrer les combinaisons
    path('api/filter/', filters.api_filter_combinations, name='api_filter'),

    # ============================================
    # WEBHOOKS
    # ============================================

    # Point de terminaison principal pour recevoir les webhooks
    path('webhook/receiver/', webhooks.webhook_receiver, name='webhook_receiver'),

    # Page de test pour envoyer des webhooks
    path('webhook/test/', webhooks.webhook_test, name='webhook_test'),

    # Liste des logs webhooks (admin uniquement)
    path('webhook/logs/', webhooks.webhook_logs_list, name='webhook_logs'),

    # Détail d'un log webhook (admin uniquement)
    path('webhook/logs/<int:log_id>/', webhooks.webhook_log_detail, name='webhook_log_detail'),

    # Supprimer un log webhook (admin uniquement)
    path('webhook/logs/<int:log_id>/delete/', webhooks.webhook_log_delete, name='webhook_log_delete'),
]
