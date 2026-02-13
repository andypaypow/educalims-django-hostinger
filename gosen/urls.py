"""
URLs pour l'application Gosen TurfFilter
"""
from django.urls import path
from .views import webhooks, base, filters, auth, subscriptions, contact
from .views.contact import contact_page


app_name = 'gosen'


urlpatterns = [
    # ============================================
    # HOME - Application principale
    # ============================================

    # Page d'accueil (application Gosen TurfFilter)
    path('', base.index, name='home'),
    # Page de contact
    path('contact/', contact_page, name='contact'),

    # API pour les partenaires
    path('api/partners/', contact.get_partners, name='api_partners'),

    # API pour compter les combinaisons
    path('api/combinations/count/', base.api_combinations_count, name='api_combinations_count'),

    # API pour parser les pronostics
    path('api/parse-pronostics/', base.parse_pronostics, name='parse_pronostics'),

    # API pour filtrer les combinaisons
    path('api/filter/', filters.api_filter_combinations, name='api_filter'),

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
]

# ============================================
# SERVEUR DE FICHIERS MEDIA (DEV ONLY)
# ============================================
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
