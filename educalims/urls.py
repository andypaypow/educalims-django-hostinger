from django.urls import path
from . import views

app_name = 'educalims'

urlpatterns = [
    # Accueil
    path('', views.home, name='home'),

    # Authentification
    path('login/', views.custom_login, name='login'),
    path('register/', views.custom_register, name='register'),
    path('logout/', views.custom_logout, name='logout'),
    path('profile/', views.profile, name='profile'),

    # Cycles
    path('cycles/', views.cycles_list, name='cycles_list'),
    path('cycles/<int:cycle_id>/', views.cycle_detail, name='cycle_detail'),

    # Disciplines
    path('disciplines/', views.disciplines_list, name='disciplines_list'),
    path('disciplines/<int:discipline_id>/', views.discipline_detail, name='discipline_detail'),

    # Niveaux
    path('niveaux/<int:niveau_id>/', views.niveau_detail, name='niveau_detail'),

    # Unités
    path('unites/<int:unite_id>/', views.unite_detail, name='unite_detail'),

    # Fichiers
    path('fichiers/<int:fichier_id>/', views.fichier_detail, name='fichier_detail'),

    # Abonnements
    path('abonnements/', views.mes_abonnements, name='mes_abonnements'),
    path('s-abonner/<int:niveau_id>/', views.s_abonner, name='s_abonner'),
    path('api/paiement/callback/', views.paiement_callback, name='paiement_callback'),
    path('webhook/cyberschool/', views.webhook_cyberschool_simple, name='webhook_cyberschool_simple'),
    path('api/verifier-acces/<int:niveau_id>/', views.verifier_acces, name='verifier_acces'),
    path('api/abonnement/<int:abonnement_id>/statut/', views.abonnement_statut, name='abonnement_statut'),
    path('api/paiements-recents/', views.api_paiements_recents, name='api_paiements_recents'),
]
