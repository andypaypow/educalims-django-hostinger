"""
Administration Django pour l'application Gosen TurfFilter
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
import json

from .models import WebhookLog


@admin.register(WebhookLog)
class WebhookLogAdmin(admin.ModelAdmin):
    """Administration des logs de webhooks"""

    list_display = [
        'id',
        'date_reception',
        'source',
        'reference_transaction',
        'telephone',
        'montant',
        'fees',
        'total_amount',
        'statut',
        'est_en_retard',
    ]

    list_filter = [
        'statut',
        'source',
        'date_reception',
    ]

    search_fields = [
        'reference_transaction',
        'telephone',
        'code_paiement',
    ]

    readonly_fields = [
        'source',
        'statut',
        'payload_display',
        'headers_display',
        'reference_transaction',
        'code_paiement',
        'montant',
        'fees',
        'total_amount',
        'telephone',
        'date_reception',
        'date_traitement',
        'duree_traitement',
        'message_erreur',
        'tentatives',
        'utilisateur',
        'ip_address',
        'user_agent',
    ]

    date_hierarchy = 'date_reception'

    ordering = ['-date_reception']

    list_per_page = 25

    fieldsets = (
        ('Informations générales', {
            'fields': (
                'source',
                'statut',
                'date_reception',
                'date_traitement',
                'duree_traitement',
                'tentatives',
            )
        }),
        ('Paiement', {
            'fields': (
                'reference_transaction',
                'code_paiement',
                'montant',
                'fees',
                'total_amount',
                'telephone',
            )
        }),
        ('Données reçues', {
            'fields': (
                'payload_display',
                'headers_display',
            ),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': (
                'ip_address',
                'user_agent',
                'utilisateur',
                'message_erreur',
            ),
            'classes': ('collapse',)
        }),
    )

    def est_en_retard(self, obj):
        """Affiche un indicateur si le webhook est en retard"""
        if obj.est_en_retard:
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">⚠️ OUI</span>'
            )
        return format_html(
            '<span style="color: #28a745;">✓ Non</span>'
        )
    est_en_retard.short_description = 'En retard'
    est_en_retard.boolean = False

    def payload_display(self, obj):
        """Affiche le payload formaté"""
        if obj.payload:
            payload_json = json.dumps(obj.payload, indent=2, ensure_ascii=False)
            return format_html(
                '<pre style="background: #1e1e1e; color: #d4d4d4; padding: 15px; border-radius: 6px; max-height: 400px; overflow: auto; font-size: 12px;">{}</pre>',
                payload_json
            )
        return '-'
    payload_display.short_description = 'Payload (données reçues)'

    def headers_display(self, obj):
        """Affiche les headers formatés"""
        if obj.headers:
            headers_json = json.dumps(obj.headers, indent=2, ensure_ascii=False)
            return format_html(
                '<pre style="background: #1e1e1e; color: #d4d4d4; padding: 15px; border-radius: 6px; max-height: 400px; overflow: auto; font-size: 12px;">{}</pre>',
                headers_json
            )
        return '-'
    headers_display.short_description = 'Headers HTTP'

    def duree_traitement(self, obj):
        """Affiche la durée de traitement"""
        if obj.duree_traitement:
            return f'{obj.duree_traitement:.2f} s'
        return '-'
    duree_traitement.short_description = 'Durée de traitement'

    def has_add_permission(self, request):
        """Interdit l'ajout manuel de webhooks"""
        return False

    def has_change_permission(self, request, obj=None):
        """Interdit la modification des webhooks"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Autorise la suppression des webhooks"""
        return True


# Actions personnalisées
@admin.action(description='Marquer comme traités (Succès)')
def marquer_traite(modeladmin, request, queryset):
    """Marque les webhooks sélectionnés comme traités"""
    count = 0
    for log in queryset:
        log.marque_traite(succes=True)
        count += 1
    modeladmin.message_user(request, f'{count} webhooks marqués comme traités.')


@admin.action(description='Marquer comme en erreur')
def marquer_erreur(modeladmin, request, queryset):
    """Marque les webhooks sélectionnés comme en erreur"""
    count = 0
    for log in queryset:
        log.marque_traite(succes=False, message="Marqué manuellement comme erreur")
        count += 1
    modeladmin.message_user(request, f'{count} webhooks marqués comme en erreur.')


# Ajouter les actions à l'admin
WebhookLogAdmin.actions = [marquer_traite, marquer_erreur]
