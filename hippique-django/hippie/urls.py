"""
URL Configuration for Hippique App
"""
from django.urls import path
from . import views

app_name = 'hippie'

urlpatterns = [
    # Page views
    path('', views.home, name='home'),
    path('turf-filter/', views.turf_filter, name='turf_filter'),

    # Authentification
    path('login/', views.custom_login, name='login'),
    path('register/', views.custom_register, name='register'),
    path('logout/', views.custom_logout, name='logout'),
    path('profile/', views.profile, name='profile'),

    # API endpoints
    path('api/combinations-count/', views.api_combinations_count, name='api_combinations_count'),
    path('api/parse-pronostics/', views.api_parse_pronostics, name='api_parse_pronostics'),
    path('api/synthesis/', views.api_synthesis, name='api_synthesis'),
    path('api/filter/', views.api_filter_combinations, name='api_filter_combinations'),
    path('api/backtest/', views.api_backtest, name='api_backtest'),
    path('api/weight-bounds/', views.api_weight_bounds, name='api_weight_bounds'),
    path('api/alternance-max/', views.api_alternance_max, name='api_alternance_max'),

    # Scénarios
    path('api/scenarios/', views.api_scenarios_list, name='api_scenarios_list'),
    path('api/scenario/save/', views.api_scenario_save, name='api_scenario_save'),
    path('api/scenario/load/', views.api_scenario_load, name='api_scenario_load'),
    path('api/scenario/delete/', views.api_scenario_delete, name='api_scenario_delete'),

    # Abonnement & Webhooks
    path('api/verifier-abonnement/', views.api_verifier_abonnement, name='api_verifier_abonnement'),
    path('api/creer-paiement/', views.api_creer_paiement, name='api_creer_paiement'),
    path('webhook/cyberschool/', views.webhook_cyberschool, name='webhook_cyberschool'),
    path('telegram-webhook/', views.telegram_webhook, name='telegram_webhook'),
]
