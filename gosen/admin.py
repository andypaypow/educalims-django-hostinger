"""
Administration Django pour l'application Gosen TurfFilter
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.utils import timezone
import json

from .models import WebhookLog, UserProfile, SubscriptionPayment, SubscriptionProduct, DeviceFingerprint, Partner, ContactMessage, UserSession, ActivityLog, BacktestAnalysis, DeviceTracking


# ============================================
# INLINE ADMIN FOR USER PROFILE
# ============================================

class UserProfileInline(admin.StackedInline):
    """Inline admin pour UserProfile dans User admin"""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profil'
    readonly_fields = ['date_creation_compte', 'derniere_connexion', 'nb_filtres_realises', 'date_reset_filtres']
    fields = [
        'telephone',
        'device_id',
        'date_creation_compte',
        'derniere_connexion',
        'nb_filtres_realises',
        'est_actif',
        'a_un_abonnement',
        'type_abonnement',
        'date_debut_abonnement',
        'date_fin_abonnement',
        'filtres_gratuits_utilises',
        'date_reset_filtres',
    ]


class SubscriptionPaymentInline(admin.TabularInline):
    """Inline admin pour SubscriptionPayment dans User admin"""
    model = SubscriptionPayment
    can_delete = True
    verbose_name_plural = 'Paiements'
    readonly_fields = ['date_creation', 'date_paiement', 'reference_transaction']
    fields = [
        'produit',
        'type_abonnement',
        'montant',
        'devise',
        'statut',
        'reference_transaction',
        'telephone',
        'date_creation',
        'date_paiement',
    ]
    extra = 0


# ============================================
# EXTEND USER ADMIN
# ============================================

class CustomUserAdmin(UserAdmin):
    """Admin étendu pour User avec profil et abonnements"""

    inlines = [UserProfileInline, SubscriptionPaymentInline]

    list_display = UserAdmin.list_display + ('get_abonnement', 'get_telephone', 'get_nb_filtres')

    def get_abonnement(self, obj):
        """Affiche le statut d'abonnement"""
        if hasattr(obj, 'profile'):
            if obj.profile.est_abonne:
                return format_html(
                    '<span style="color: #28a745; font-weight: bold;">⭐ {}</span>',
                    obj.profile.get_type_abonnement_display()
                )
            return format_html(
                '<span style="color: #ffc107;">Gratuit</span>'
            )
        return '-'
    get_abonnement.short_description = 'Abonnement'

    def get_telephone(self, obj):
        """Affiche le numéro de téléphone"""
        if hasattr(obj, 'profile') and obj.profile.telephone:
            return obj.profile.telephone
        return '-'
    get_telephone.short_description = 'Téléphone'

    def get_nb_filtres(self, obj):
        """Affiche le nombre de filtres réalisés"""
        if hasattr(obj, 'profile'):
            return obj.profile.nb_filtres_realises
        return '-'
    get_nb_filtres.short_description = 'Filtres'


# Désenregistrer l'ancien UserAdmin et enregistrer le nouveau
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# ============================================
# SUBSCRIPTION PRODUCT ADMIN
# ============================================

@admin.register(SubscriptionProduct)
class SubscriptionProductAdmin(admin.ModelAdmin):
    """Administration des produits d'abonnement"""

    list_display = [
        'id',
        'nom',
        'type_abonnement',
        'prix_display',
        'duree_display',
        'est_actif',
        'ordre_affichage',
    ]

    list_filter = [
        'type_abonnement',
        'est_actif',
        'devise',
    ]

    search_fields = [
        'nom',
        'description',
        'type_abonnement',
    ]

    readonly_fields = ['date_creation', 'date_modification']

    fieldsets = (
        ('Informations générales', {
            'fields': (
                'nom',
                'description',
                'type_abonnement',
            )
        }),
        ('Prix', {
            'fields': (
                'prix',
                'devise',
            )
        }),
        ('Durée', {
            'fields': (
                'duree_jours',
                'duree_heures',
            )
        }),
        ('URLs de paiement', {
            'fields': (
                'url_moov_money',
                'url_airtel_money',
            ),
            'classes': ('collapse',)
        }),
        ('Affichage', {
            'fields': (
                'est_actif',
                'ordre_affichage',
            )
        }),
        ('Métadonnées', {
            'fields': (
                'date_creation',
                'date_modification',
            ),
            'classes': ('collapse',)
        }),
    )

    list_editable = ['est_actif', 'ordre_affichage']
    ordering = ['ordre_affichage', 'prix']
    list_per_page = 25

    def prix_display(self, obj):
        """Affiche le prix formaté"""
        return f'{obj.prix:,} {obj.devise}'.replace(',', ' ')
    prix_display.short_description = 'Prix'

    def duree_display(self, obj):
        """Affiche la durée formatée"""
        return obj.duree_affichage
    duree_display.short_description = 'Durée'


# ============================================
# WEBHOOK LOG ADMIN
# ============================================

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
        'statut',
        'est_en_retard_admin',
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

    def est_en_retard_admin(self, obj):
        """Affiche un indicateur si le webhook est en retard"""
        try:
            en_retard = obj.est_en_retard
        except:
            en_retard = False

        if en_retard:
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">⚠️ OUI</span>'
            )
        return format_html(
            '<span style="color: #28a745;">✓ Non</span>'
        )
    est_en_retard_admin.short_description = 'En retard'

    def payload_display(self, obj):
        """Affiche le payload formaté"""
        if obj.payload:
            payload_json = json.dumps(obj.payload, indent=2, ensure_ascii=False)
            return format_html(
                '<pre style="background: #1e1e1e; color: #d4d4d4; padding: 15px; border-radius: 6px; max-height: 400px; overflow: auto; font-size: 12px;">{}</pre>',
                payload_json
            )
        return '-'
    payload_display.short_description = 'Payload'

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
        try:
            if obj.duree_traitement:
                return f'{obj.duree_traitement:.2f} s'
        except:
            pass
        return '-'
    duree_traitement.short_description = 'Durée de traitement'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


# Actions personnalisées pour WebhookLog
@admin.action(description='Marquer comme traités (Succès)')
def marquer_traite(modeladmin, request, queryset):
    count = 0
    for log in queryset:
        log.marque_traite(succes=True)
        count += 1
    modeladmin.message_user(request, f'{count} webhooks marqués comme traités.')


@admin.action(description='Marquer comme en erreur')
def marquer_erreur(modeladmin, request, queryset):
    count = 0
    for log in queryset:
        log.marque_traite(succes=False, message="Marqué manuellement comme erreur")
        count += 1
    modeladmin.message_user(request, f'{count} webhooks marqués comme en erreur.')


WebhookLogAdmin.actions = [marquer_traite, marquer_erreur]


# ============================================
# SUBSCRIPTION PAYMENT ADMIN
# ============================================

@admin.register(SubscriptionPayment)
class SubscriptionPaymentAdmin(admin.ModelAdmin):
    """Administration des paiements d'abonnement"""

    list_display = [
        'id',
        'utilisateur',
        'produit_display',
        'type_abonnement',
        'montant_display',
        'statut',
        'reference_transaction',
        'date_creation',
        'date_paiement',
    ]

    list_filter = [
        'statut',
        'type_abonnement',
        'produit',
        'date_creation',
    ]

    search_fields = [
        'utilisateur__username',
        'utilisateur__email',
        'reference_transaction',
        'telephone',
    ]

    readonly_fields = [
        'utilisateur',
        'produit',
        'type_abonnement',
        'montant',
        'devise',
        'reference_transaction',
        'code_paiement',
        'telephone',
        'date_creation',
        'date_paiement',
        'webhook_log',
    ]

    date_hierarchy = 'date_creation'
    ordering = ['-date_creation']
    list_per_page = 25

    fieldsets = (
        ('Informations générales', {
            'fields': (
                'utilisateur',
                'produit',
                'type_abonnement',
                'montant',
                'devise',
                'statut',
            )
        }),
        ('Transaction', {
            'fields': (
                'reference_transaction',
                'code_paiement',
                'telephone',
            )
        }),
        ('Dates', {
            'fields': (
                'date_creation',
                'date_paiement',
            )
        }),
        ('Webhook associé', {
            'fields': (
                'webhook_log',
            ),
            'classes': ('collapse',)
        }),
    )

    def produit_display(self, obj):
        """Affiche le produit lié"""
        if obj.produit:
            return obj.produit.nom
        return '-'
    produit_display.short_description = 'Produit'

    def montant_display(self, obj):
        """Affiche le montant formaté"""
        return f'{obj.montant:,} {obj.devise}'.replace(',', ' ')
    montant_display.short_description = 'Montant'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(DeviceFingerprint)
class DeviceFingerprintAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "fingerprint", "user_agent_display", "created_at", "last_seen", "is_active"]
    list_filter = ["is_active", "created_at", "last_seen"]
    search_fields = ["user__username", "fingerprint", "user_agent"]
    readonly_fields = ["user", "fingerprint", "user_agent", "created_at", "last_seen"]
    date_hierarchy = "created_at"
    ordering = ["-created_at"]

    def user_agent_display(self, obj):
        if obj.user_agent:
            return obj.user_agent[:50] + ("..." if len(obj.user_agent) > 50 else "")
        return "-"
    user_agent_display.short_description = "User-Agent"



# ============================================
# PARTNER ADMIN
# ============================================

@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    """Administration des partenaires"""

    list_display = [
        'id',
        'nom',
        'logo_preview',
        'lien',
        'ordre_affichage',
        'est_actif',
        'date_creation',
    ]

    list_filter = [
        'est_actif',
        'date_creation',
    ]

    search_fields = [
        'nom',
        'description',
    ]

    readonly_fields = [
        'date_creation',
        'date_modification',
        'logo_preview',
    ]

    fieldsets = (
        ('Informations générales', {
            'fields': (
                'nom',
                'description',
                'lien',
                'logo',
                'logo_preview',
            )
        }),
        ('Affichage', {
            'fields': (
                'est_actif',
                'ordre_affichage',
            )
        }),
        ('Métadonnées', {
            'fields': (
                'date_creation',
                'date_modification',
            ),
            'classes': ('collapse',)
        }),
    )

    ordering = ['ordre_affichage', 'nom']
    list_per_page = 20

    def logo_preview(self, obj):
        """Affiche un aperçu du logo dans la liste"""
        if obj.logo:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: contain; border-radius: 8px;" />',
                obj.logo.url
            )
        return '-'
    logo_preview.short_description = 'Logo'


# ============================================
# CONTACT MESSAGE ADMIN
# ============================================

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """Administration des messages de contact"""

    list_display = [
        'id',
        'nom',
        'email',
        'type_demande',
        'date_creation',
        'est_traite',
    ]

    list_filter = [
        'type_demande',
        'est_traite',
        'date_creation',
    ]

    search_fields = [
        'nom',
        'email',
        'message',
    ]

    readonly_fields = [
        'nom',
        'email',
        'type_demande',
        'message',
        'date_creation',
    ]

    fieldsets = (
        ('Message', {
            'fields': (
                'nom',
                'email',
                'type_demande',
                'message',
                'date_creation',
            )
        }),
        ('Statut', {
            'fields': (
                'est_traite',
            )
        }),
    )

    ordering = ['-date_creation']
    list_per_page = 25

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'ip_address', 'date_connexion', 'duree_session', 'est_actif']
    list_filter = ['est_actif', 'date_connexion']
    search_fields = ['user__username', 'ip_address', 'session_key']
    readonly_fields = ['user', 'session_key', 'ip_address', 'user_agent', 'date_connexion', 'derniere_activite']
    date_hierarchy = 'date_connexion'
    ordering = ['-derniere_activite']

    def duree_session(self, obj):
        return obj.duree_session()
    duree_session.short_description = 'Duree'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['type_action', 'user', 'description', 'date_creation']
    list_filter = ['type_action', 'date_creation']
    search_fields = ['user__username', 'description', 'ip_address']
    readonly_fields = ['user', 'type_action', 'description', 'donnees', 'ip_address', 'user_agent', 'date_creation']
    date_hierarchy = 'date_creation'
    ordering = ['-date_creation']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(BacktestAnalysis)
class BacktestAnalysisAdmin(admin.ModelAdmin):
    list_display = ['user', 'arrivee_display', 'nombre_trouvees', 'date_creation']
    list_filter = ['date_creation', 'nombre_trouvees']
    search_fields = ['user__username', 'nom']
    readonly_fields = ['user', 'num_partants', 'taille_combinaison', 'pronostics', 'criteres_filtres', 
                       'arrivee', 'combinaisons_filtrees', 'combinaisons_trouvees', 'nombre_trouvees', 
                       'rapport', 'nom', 'date_creation']
    date_hierarchy = 'date_creation'
    ordering = ['-date_creation']

    def arrivee_display(self, obj):
        if obj.arrivee:
            return ', '.join(map(str, obj.arrivee))
        return '-'
    arrivee_display.short_description = 'Arrivee'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(DeviceTracking)
class DeviceTrackingAdmin(admin.ModelAdmin):
    """Administration du tracking des appareils"""
    list_display = ['user_display', 'ip_address', 'premiere_visite', 'duree_session', 'est_actif', 'nombre_visites']
    list_filter = ['est_actif', 'premiere_visite', 'pays']
    search_fields = ['user__username', 'ip_address', 'fingerprint', 'user_agent']
    readonly_fields = ['fingerprint', 'session_key', 'user', 'ip_address', 'user_agent', 'premiere_visite', 
                       'derniere_activite', 'est_actif', 'nombre_visites', 'nombre_pages_vues', 
                       'pages_vues_session', 'pays', 'ville']
    date_hierarchy = 'premiere_visite'
    ordering = ['-derniere_activite']

    def user_display(self, obj):
        if obj.user:
            return obj.user.username
        return '<span style="color: #FF7F00;">Anonyme</span>'
    user_display.short_description = 'User'
    user_display.allow_tags = True

    def duree_session(self, obj):
        return obj.duree_session()
    duree_session.short_description = 'Duree'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
