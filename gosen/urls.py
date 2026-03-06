"""
URLs pour l'application Filtre Expert
"""
from django.urls import path
from .views import webhooks, base, filters, auth, subscriptions, contact, backtest, admin_dashboard, sauvegardes
from .views.contact import contact_page, submit_contact
from .views.backtest import test_arrivee, save_backtest_analysis, get_backtest_analyses, get_backtest_analysis, delete_backtest_analysis, update_backtest_analysis


app_name = 'gosen'


urlpatterns = [
    # ============================================
    # HOME - Application principale
    # ============================================

    # Page d'accueil (application Filtre Expert)
    path('', base.index, name='home'),
    # Page de contact
    path('contact/', contact_page, name='contact'),
    # API pour soumettre un message de contact
    path('api/contact/submit/', submit_contact, name='api_contact_submit'),

    # API pour les partenaires
    path('api/partners/', contact.get_partners, name='api_partners'),

    # API pour compter les combinaisons
    path('api/combinations/count/', base.api_combinations_count, name='api_combinations_count'),

    # API pour parser les pronostics
    path('api/parse-pronostics/', base.parse_pronostics, name='parse_pronostics'),

    # API pour filtrer les combinaisons
    path('api/filter/', filters.api_filter_combinations, name='api_filter'),
    # Test OCR
    path('test-ocr/', base.test_ocr, name='test_ocr'),

    # API pour les backtests
    path('api/backtest/test/', test_arrivee, name='api_backtest_test'),
    path('api/backtest/save/', save_backtest_analysis, name='api_backtest_save'),
    path('api/backtest/list/', get_backtest_analyses, name='api_backtest_list'),
    path('api/backtest/load/<int:analysis_id>/', get_backtest_analysis, name='api_backtest_load'),
    path('api/backtest/delete/<int:analysis_id>/', delete_backtest_analysis, name='api_backtest_delete'),
    path('api/backtest/update/<int:analysis_id>/', update_backtest_analysis, name='api_backtest_update'),

    # ============================================
    # AUTHENTIFICATION ET UTILISATEURS
    # ============================================

    # Page de connexion
    path('auth/login/', auth.login_page, name='login'),
    path('auth/login/phone/', auth.login_phone, name='login_phone'),
    path('auth/device-not-authorized/', auth.device_not_authorized, name='device_not_authorized'),

    # API de connexion
    path('api/auth/login/', auth.login_api, name='login_api'),

    # Page d'inscription
    path('auth/register/', auth.register_page, name='register'),

    # Déconnexion
    path('auth/logout/', auth.logout_view, name='logout'),

    # Vérifier l'authentification
    path('api/auth/check/', auth.check_auth, name='check_auth'),

    # Vérifier les filtres restants
    path('api/auth/filters/remaining/', auth.check_filters_remaining, name='check_filters_remaining'),

    # Incrémenter le compteur de filtres
    path('api/auth/filters/increment/', auth.increment_filter_count, name='increment_filter_count'),

    # Profil utilisateur
    path('auth/profile/', auth.profile_page, name='profile'),

    # Modifier le profil
    path('auth/profile/edit/', auth.profile_edit, name='profile_edit'),

    # Page d'abonnement
    path('auth/subscription/', auth.subscription_page, name='subscription'),

    # Tableau de bord
    path('auth/dashboard/', auth.dashboard_page, name='dashboard'),

    # ============================================
    # PRODUITS ET PAIEMENTS
    # ============================================

    # API pour récupérer les produits d'abonnement
    path('api/subscriptions/products/', subscriptions.api_products_list, name='api_products_list'),

    # API pour créer un paiement
    path('api/subscriptions/payment/create/', subscriptions.api_create_payment, name='api_create_payment'),
    path('payment/success/', auth.payment_success, name='payment_success'),
    path('payment/cancel/', auth.payment_cancel, name='payment_cancel'),

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
    # ============================================
    # DASHBOARD ADMIN
    # ============================================
    path("staff/dashboard/", admin_dashboard.admin_dashboard, name="staff_dashboard"),
    path("staff/dashboard/api/stats/", admin_dashboard.admin_api_stats, name="staff_api_stats"),
    path("api/admin/stats/filter/", auth.api_stats_filter, name="api_admin_stats_filter"),
    path("api/admin/stats/details/", auth.api_stats_details, name="api_admin_stats_details"),
    # ============================================
    # SAUVEGARDES DE CONFIGURATION
    # ============================================
    path('api/sauvegardes/save/', sauvegardes.sauvegarder_configuration, name='api_sauvegardes_save'),
    path('api/sauvegardes/list/', sauvegardes.lister_sauvegardes, name='api_sauvegardes_list'),
    path('api/sauvegardes/load/<int:sauvegarde_id>/', sauvegardes.charger_sauvegarde, name='api_sauvegardes_load'),
    path('api/sauvegardes/update/<int:sauvegarde_id>/', sauvegardes.modifier_sauvegarde, name='api_sauvegardes_update'),
    path('api/sauvegardes/delete/<int:sauvegarde_id>/', sauvegardes.supprimer_sauvegarde, name='api_sauvegardes_delete'),
]
