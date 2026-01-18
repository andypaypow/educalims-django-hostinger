from django.contrib import admin
from .models import Cycle, Discipline, Niveau, Unite, Fichier, Produit, Abonnement, WebhookLog


@admin.register(Cycle)
class CycleAdmin(admin.ModelAdmin):
    """Admin pour Cycle"""
    list_display = ['nom', 'ordre', 'date_creation', 'date_modification']
    search_fields = ['nom', 'description']
    list_editable = ['ordre']
    ordering = ['ordre', 'nom']


@admin.register(Discipline)
class DisciplineAdmin(admin.ModelAdmin):
    """Admin pour Discipline"""
    list_display = ['nom', 'couleur', 'ordre', 'liste_cycles', 'date_creation']
    search_fields = ['nom', 'description']
    list_filter = ['cycles']
    list_editable = ['ordre', 'couleur']
    filter_horizontal = ['cycles']
    ordering = ['ordre', 'nom']

    def liste_cycles(self, obj):
        return ", ".join([c.nom for c in obj.cycles.all()])
    liste_cycles.short_description = 'Cycles'


@admin.register(Niveau)
class NiveauAdmin(admin.ModelAdmin):
    """Admin pour Niveau"""
    list_display = ['__str__', 'cycle', 'specialite', 'est_niveau_enfant', 'niveau_parent', 'ordre', 'date_creation']
    search_fields = ['nom', 'description']
    list_filter = ['cycle', 'specialite', 'est_niveau_enfant']
    list_editable = ['ordre', 'specialite']
    filter_horizontal = ['disciplines']
    ordering = ['cycle', 'ordre', 'nom']

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj and obj.niveau_parent:
            form.base_fields['specialite'].initial = obj.specialite
        return form


@admin.register(Unite)
class UniteAdmin(admin.ModelAdmin):
    """Admin pour Unite"""
    list_display = ['__str__', 'niveau', 'discipline', 'type_unite', 'unite_parent', 'ordre', 'date_creation']
    search_fields = ['nom', 'description']
    list_filter = ['type_unite', 'niveau__cycle', 'discipline']
    list_editable = ['ordre', 'type_unite']
    ordering = ['niveau', 'discipline', 'ordre', 'nom']
    raw_id_fields = ['unite_parent']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('niveau', 'discipline', 'unite_parent')


@admin.register(Fichier)
class FichierAdmin(admin.ModelAdmin):
    """Admin pour Fichier"""
    list_display = ['nom', 'unite', 'type_fichier', 'est_actif', 'telechargements', 'date_creation']
    search_fields = ['nom', 'description']
    list_filter = ['type_fichier', 'est_actif', 'unite__niveau__cycle', 'unite__discipline']
    list_editable = ['est_actif']
    ordering = ['-date_creation', 'nom']
    readonly_fields = ['telechargements', 'date_creation', 'date_modification']

    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'unite', 'type_fichier', 'description')
        }),
        ('Contenu', {
            'fields': (('fichier', 'contenu_texte', 'url_lien'), 'duree', 'taille')
        }),
        ('Statistiques', {
            'fields': ('telechargements', 'est_actif', 'date_creation', 'date_modification')
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('unite__niveau', 'unite__discipline')


# ==================== ADMIN ABONNEMENT ====================

@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    """Admin pour Produit"""
    list_display = ['nom', 'prix', 'date_expiration', 'est_actif', 'date_creation']
    search_fields = ['nom', 'description']
    list_filter = ['est_actif', 'date_expiration']
    list_editable = ['est_actif', 'prix', 'date_expiration']
    ordering = ['-date_creation', 'nom']


@admin.register(Abonnement)
class AbonnementAdmin(admin.ModelAdmin):
    """Admin pour Abonnement"""
    list_display = ['user', 'niveau', 'produit', 'statut', 'merchant_reference_id', 'date_debut', 'date_fin', 'methode_paiement', 'montant_paye']
    search_fields = ['user__username', 'niveau__nom', 'reference_interne', 'merchant_reference_id']
    list_filter = ['statut', 'methode_paiement', 'produit', 'date_creation']
    list_editable = ['statut']
    ordering = ['-date_creation', '-date_debut']
    readonly_fields = ['date_creation', 'date_modification']

    fieldsets = (
        ('Informations générales', {
            'fields': ('user', 'niveau', 'produit', 'statut')
        }),
        ('Transaction', {
            'fields': ('reference_interne', 'merchant_reference_id', 'code_paiement', 'methode_paiement', 'montant_paye')
        }),
        ('Dates', {
            'fields': ('date_debut', 'date_fin', 'date_creation', 'date_modification')
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'niveau', 'niveau__cycle', 'produit')


@admin.register(WebhookLog)
class WebhookLogAdmin(admin.ModelAdmin):
    """Admin pour WebhookLog"""
    list_display = ['created_at', 'merchant_reference_id', 'status', 'amount', 'operator', 'phone_number', 'activation_succes', 'telegram_notification_sent', 'abonnement']
    list_filter = ['status', 'operator', 'activation_succes', 'telegram_notification_sent', 'created_at']
    search_fields = ['merchant_reference_id', 'transaction_id', 'phone_number']
    readonly_fields = ['created_at', 'raw_data']
    ordering = ['-created_at']

    fieldsets = (
        ('Informations générales', {
            'fields': ('merchant_reference_id', 'status', 'code')
        }),
        ('Détails de la transaction', {
            'fields': ('amount', 'operator', 'transaction_id', 'phone_number')
        }),
        ('Statut', {
            'fields': ('activation_succes', 'telegram_notification_sent', 'abonnement')
        }),
        ('Données brutes', {
            'fields': ('raw_data', 'created_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('abonnement__user', 'abonnement__niveau')

# ==================== ADMIN USER PROFILE ====================
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profil'
    fields = ('recommande_par', 'telephone')


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_recommande_par', 'get_telephone')
    inlines = (UserProfileInline,)
    
    def get_recommande_par(self, obj):
        profile = UserProfile.objects.filter(user=obj).first()
        if profile:
            return profile.get_recommande_par_display()
        return '-'
    get_recommande_par.short_description = 'Recommandé par'
    
    def get_telephone(self, obj):
        profile = UserProfile.objects.filter(user=obj).first()
        return profile.telephone if profile else '-'
    get_telephone.short_description = 'Téléphone'

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
