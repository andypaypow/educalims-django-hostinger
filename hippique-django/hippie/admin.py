"""
Django Admin pour Filtre Expert +
"""
from django.contrib import admin
from .models import (
    Scenario,
    ScenarioTag,
    SessionUser,
    ProduitAbonnement,
    Abonnement,
    WebhookLog,
)


# ==================== EXISTING ====================

@admin.register(Scenario)
class ScenarioAdmin(admin.ModelAdmin):
    list_display = ['name', 'n_partants', 'k_taille', 'is_favorite', 'usage_count', 'created_at']
    list_filter = ['is_favorite', 'is_public', 'n_partants', 'k_taille']
    search_fields = ['name', 'description', 'nom_course']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    ordering = ['-is_favorite', '-updated_at']


@admin.register(ScenarioTag)
class ScenarioTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color']
    search_fields = ['name']


# ==================== ABONNEMENT ====================

@admin.register(SessionUser)
class SessionUserAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'telegram_user_id', 'phone_number', 'created_at', 'last_active']
    list_filter = ['created_at', 'last_active']
    search_fields = ['session_id', 'telegram_user_id', 'phone_number']
    readonly_fields = ['created_at', 'last_active']
    date_hierarchy = 'created_at'
    ordering = ['-last_active']


@admin.register(ProduitAbonnement)
class ProduitAbonnementAdmin(admin.ModelAdmin):
    list_display = ['nom', 'prix', 'duree_jours', 'est_actif', 'produit_id']
    list_filter = ['est_actif', 'duree_jours']
    search_fields = ['nom', 'produit_id']
    list_editable = ['est_actif']
    ordering = ['-est_actif', 'nom']


@admin.register(Abonnement)
class AbonnementAdmin(admin.ModelAdmin):
    list_display = ['session_user', 'produit', 'statut', 'montant_paye', 'date_debut', 'date_fin', 'created_at']
    list_filter = ['statut', 'produit', 'methode_paiement', 'created_at']
    search_fields = ['session_user__session_id', 'merchant_reference_id', 'session_user__phone_number']
    readonly_fields = ['created_at', 'merchant_reference_id']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']


@admin.register(WebhookLog)
class WebhookLogAdmin(admin.ModelAdmin):
    list_display = ['merchant_reference_id', 'code', 'status', 'activation_succes', 'phone_number', 'created_at']
    list_filter = ['status', 'activation_succes', 'code', 'created_at']
    search_fields = ['merchant_reference_id', 'phone_number']
    readonly_fields = ['raw_data', 'created_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
