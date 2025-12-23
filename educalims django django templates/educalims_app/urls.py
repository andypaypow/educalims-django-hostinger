# -*- coding: utf-8 -*-
from django.urls import path
from . import views
from . import views_abonnement

app_name = 'educalims_app'

urlpatterns = [
    # Page d'accueil
    path('', views.home, name='home'),

    # Cycles
    path('cycle/<int:pk>/', views.cycle_detail, name='cycle_detail'),

    # Disciplines
    path('discipline/<int:pk>/', views.discipline_detail, name='discipline_detail'),

    # Niveaux
    path('niveau/<int:pk>/', views.niveau_detail, name='niveau_detail'),

    # Unités
    path('unite/<int:pk>/', views.unite_detail, name='unite_detail'),

    # Fichiers
    path('fichier/<int:pk>/', views.fichier_detail, name='fichier_detail'),

    # =========================================================================
    # SYSTÈME D'ABONNEMENT
    # =========================================================================

    # Choix du cycle (étape 1)
    path('abonnement/', views_abonnement.abonnement_choix_discipline, name='abonnement_choix_cycle'),

    # Choix de la discipline par cycle (étape 2)
    path('abonnement/cycle/<int:cycle_id>/disciplines/', views_abonnement.abonnement_disciplines_par_cycle, name='abonnement_choix_discipline'),

    # Choix du niveau par discipline (étape 3)
    path('abonnement/discipline/<int:discipline_id>/niveaux/', views_abonnement.abonnement_choix_niveau, name='abonnement_choix_niveau'),

    # Choix de la formule (étape 4)
    path('abonnement/niveau/<int:niveau_id>/formule/', views_abonnement.abonnement_choix_formule, name='abonnement_choix_formule'),

    # Choix de la séance (étape 4b pour SEANCE_UNIQUE)
    path('abonnement/niveau/<int:niveau_id>/seance/', views_abonnement.abonnement_choix_seance, name='abonnement_choix_seance'),

    # Paiement (étape 5)
    path('abonnement/niveau/<int:niveau_id>/paiement/<str:type_abonnement>/', views_abonnement.abonnement_paiement, name='abonnement_paiement'),

    # Pages de retour après paiement
    path('abonnement/succes/<str:reference>/', views_abonnement.abonnement_succes, name='abonnement_succes'),
    path('abonnement/echec/<str:reference>/', views_abonnement.abonnement_echec, name='abonnement_echec'),
    path('abonnement/attente/<str:reference>/', views_abonnement.abonnement_attente, name='abonnement_attente'),

    # Mes abonnements
    path('abonnement/mes-abonnements/', views_abonnement.abonnement_mes_abonnements, name='mes_abonnements'),

    # Séances d'une discipline
    path('abonnement/discipline/<int:discipline_id>/seances/', views_abonnement.abonnement_seances, name='abonnement_seances'),

    # =========================================================================
    # API CALLBACK (WEBHOOK)
    # =========================================================================

    # Callback avec référence dans l'URL
    path('api/payment/callback/<str:reference>/', views_abonnement.paiement_callback, name='paiement_callback'),

    # Callback générique (référence dans le JSON)
    path('api/payment/callback/', views_abonnement.paiement_callback_genrique, name='paiement_callback_genérique'),
]
