# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import (
    Cycle, Discipline, Niveau, Unite, Fichier, TelegramUser,
    Seance, Abonnement, Transaction, TypeAbonnement, StatutAbonnement
)


@admin.register(Cycle)
class CycleAdmin(admin.ModelAdmin):
    list_display = ['nom', 'ordre', 'date_creation']
    search_fields = ['nom', 'description']
    list_editable = ['ordre']
    ordering = ['ordre', 'nom']


@admin.register(Discipline)
class DisciplineAdmin(admin.ModelAdmin):
    list_display = ['nom', 'cycle', 'icone', 'couleur', 'ordre', 'date_creation']
    search_fields = ['nom', 'description']
    list_filter = ['cycle']
    list_editable = ['ordre', 'icone', 'couleur']
    ordering = ['cycle', 'ordre', 'nom']


@admin.register(Niveau)
class NiveauAdmin(admin.ModelAdmin):
    list_display = ['nom', 'discipline', 'parent', 'ordre', 'date_creation']
    search_fields = ['nom', 'description']
    list_filter = ['discipline']
    list_editable = ['ordre']
    ordering = ['discipline', 'ordre', 'nom']


@admin.register(Unite)
class UniteAdmin(admin.ModelAdmin):
    list_display = ['titre', 'niveau', 'parent', 'ordre', 'date_creation']
    search_fields = ['titre', 'description']
    list_filter = ['niveau']
    list_editable = ['ordre']
    ordering = ['niveau', 'ordre', 'titre']


@admin.register(Fichier)
class FichierAdmin(admin.ModelAdmin):
    list_display = ['titre', 'unite', 'type_fichier', 'ordre', 'date_creation']
    search_fields = ['titre', 'description']
    list_filter = ['type_fichier', 'unite']
    list_editable = ['ordre']
    ordering = ['unite', 'ordre', 'titre']


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    """Interface d'administration pour les utilisateurs Telegram"""
    list_display = [
        '__str__',
        'telegram_id',
        'username',
        'language_code',
        'is_premium',
        'connection_count',
        'first_seen',
        'last_seen',
        'is_active'
    ]
    list_filter = ['is_premium', 'is_active', 'language_code', 'is_bot']
    search_fields = ['telegram_id', 'first_name', 'last_name', 'username']
    readonly_fields = [
        'telegram_id',
        'first_name',
        'last_name',
        'username',
        'language_code',
        'is_premium',
        'is_bot',
        'photo_url',
        'raw_data',
        'first_seen',
        'last_seen',
        'connection_count'
    ]
    date_hierarchy = 'first_seen'
    ordering = ['-last_seen']

    fieldsets = (
        ('Informations Telegram', {
            'fields': (
                'telegram_id',
                'username',
                'first_name',
                'last_name',
                'language_code'
            )
        }),
        ('Statut', {
            'fields': ('is_premium', 'is_bot', 'is_active')
        }),
        ('Photo', {
            'fields': ('photo_url',)
        }),
        ('Statistiques', {
            'fields': ('first_seen', 'last_seen', 'connection_count')
        }),
        ('Données brutes', {
            'fields': ('raw_data',),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        # Les utilisateurs Telegram sont créés automatiquement par le middleware
        return False

    def has_delete_permission(self, request, obj=None):
        # Permettre la suppression
        return True


# ============================================================================
# ADMIN - SYSTÈME D'ABONNEMENT
# ============================================================================

@admin.register(Seance)
class SeanceAdmin(admin.ModelAdmin):
    """Interface d'administration pour les séances"""
    list_display = ['titre', 'discipline', 'date_heure', 'duree_minutes', 'places_restantes', 'est_active', 'ordre']
    list_filter = ['discipline', 'est_active', 'date_heure']
    search_fields = ['titre', 'description']
    list_editable = ['est_active', 'ordre']
    date_hierarchy = 'date_heure'
    ordering = ['date_heure', 'ordre']

    def places_restantes(self, obj):
        return obj.places_restantes()
    places_restantes.short_description = 'Places restantes'


@admin.register(Abonnement)
class AbonnementAdmin(admin.ModelAdmin):
    """Interface d'administration pour les abonnements"""
    list_display = ['utilisateur', 'discipline', 'type_abonnement', 'statut', 'date_debut', 'date_fin', 'est_actif_display']
    list_filter = ['discipline', 'type_abonnement', 'statut', 'date_debut', 'date_fin']
    search_fields = ['utilisateur__first_name', 'utilisateur__last_name', 'utilisateur__username', 'discipline__nom', 'reference_transaction']
    date_hierarchy = 'date_creation'
    readonly_fields = ['date_creation', 'date_modification', 'reference_transaction']
    ordering = ['-date_creation']

    fieldsets = (
        ('Utilisateur et Discipline', {
            'fields': ('utilisateur', 'discipline')
        }),
        ('Type d\'abonnement', {
            'fields': ('type_abonnement', 'statut', 'seance')
        }),
        ('Dates', {
            'fields': ('date_debut', 'date_fin', 'date_creation', 'date_modification')
        }),
        ('Paiement', {
            'fields': ('montant_paye', 'reference_transaction')
        }),
    )

    def est_actif_display(self, obj):
        return obj.est_actif()
    est_actif_display.boolean = True
    est_actif_display.short_description = 'Est actif'


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """Interface d'administration pour les transactions"""
    list_display = ['reference', 'utilisateur', 'montant', 'statut', 'fournisseur', 'date_creation', 'date_validation']
    list_filter = ['statut', 'fournisseur', 'date_creation']
    search_fields = ['reference', 'utilisateur__first_name', 'utilisateur__last_name', 'fournisseur_transaction_id']
    date_hierarchy = 'date_creation'
    readonly_fields = ['reference', 'date_creation', 'date_validation', 'donnees_brutes']
    ordering = ['-date_creation']

    fieldsets = (
        ('Informations transaction', {
            'fields': ('reference', 'utilisateur', 'montant', 'devise', 'statut')
        }),
        ('Prestataire', {
            'fields': ('fournisseur', 'fournisseur_transaction_id')
        }),
        ('Dates', {
            'fields': ('date_creation', 'date_validation')
        }),
        ('Abonnements liés', {
            'fields': ('abonnements',),
        }),
        ('Données brutes', {
            'fields': ('donnees_brutes',),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        # Les transactions sont créées automatiquement lors du paiement
        return False
