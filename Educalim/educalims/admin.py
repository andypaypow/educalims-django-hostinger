from django.contrib import admin
from django import forms
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from django.db.models import Q
from .models import Discipline, Cycle, Niveau, TypeEnseignement, Palier, Partie, Chapitre, Lecon, Contenu
from .widgets import CheckboxSelectMultipleCustom




@admin.register(Discipline)
class DisciplineAdmin(admin.ModelAdmin):
    list_display = ('nom', 'description')
    search_fields = ('nom',)
    ordering = ('nom',)


@admin.register(Cycle)
class CycleAdmin(admin.ModelAdmin):
    list_display = ('nom', 'description')
    search_fields = ('nom',)
    ordering = ('nom',)


@admin.register(TypeEnseignement)
class TypeEnseignementAdmin(admin.ModelAdmin):
    list_display = ('nom', 'description', 'created_at')
    search_fields = ('nom', 'description')
    ordering = ('nom',)


@admin.register(Niveau)
class NiveauAdmin(admin.ModelAdmin):
    list_display = ('nom', 'discipline', 'cycle', 'parent', 'type_enseignement')
    list_filter = ('discipline', 'cycle', 'parent', 'type_enseignement')
    search_fields = ('nom', 'discipline__nom', 'cycle__nom', 'parent__nom', 'type_enseignement__nom')
    ordering = ('cycle', 'discipline', 'ordre', 'nom')
    raw_id_fields = ('parent',)


@admin.register(Palier)
class PalierAdmin(admin.ModelAdmin):
    list_display = ('titre', 'numero', 'niveau')
    list_filter = ('niveau__discipline', 'niveau__cycle', 'niveau')
    search_fields = ('titre', 'niveau__nom')
    ordering = ('niveau', 'numero')


@admin.register(Partie)
class PartieAdmin(admin.ModelAdmin):
    list_display = ('titre', 'niveau')
    list_filter = ('niveau__discipline', 'niveau__cycle', 'niveau')
    search_fields = ('titre', 'niveau__nom')
    ordering = ('niveau', 'titre')


@admin.register(Chapitre)
class ChapitreAdmin(admin.ModelAdmin):
    list_display = ('titre', 'numero', 'get_parent', 'get_niveau')
    list_filter = ('palier__niveau__discipline', 'partie__niveau__discipline',
                  'palier__niveau', 'partie__niveau')
    search_fields = ('titre', 'palier__titre', 'partie__titre', 'palier__niveau__nom', 'partie__niveau__nom')
    ordering = ('numero', 'titre')
    
    def get_parent(self, obj):
        if obj.palier:
            return f"Palier: {obj.palier.titre}"
        elif obj.partie:
            return f"Partie: {obj.partie.titre}"
        return "Aucun"
    get_parent.short_description = 'Parent'
    
    def get_niveau(self, obj):
        niveau = obj.get_niveau()
        return niveau.nom if niveau else "Aucun"
    get_niveau.short_description = 'Niveau'


@admin.register(Lecon)
class LeconAdmin(admin.ModelAdmin):
    list_display = ('titre', 'numero', 'chapitre', 'get_niveau')
    list_filter = ('chapitre__palier__niveau__discipline',
                  'chapitre__partie__niveau__discipline',
                  'chapitre__palier__niveau',
                  'chapitre__partie__niveau')
    search_fields = ('titre', 'chapitre__titre', 'chapitre__palier__titre', 'chapitre__partie__titre')
    ordering = ('chapitre', 'numero')

    def get_niveau(self, obj):
        niveau = obj.get_niveau()
        return niveau.nom if niveau else "Aucun"
    get_niveau.short_description = 'Niveau'




@admin.register(Contenu)
class ContenuAdmin(admin.ModelAdmin):
    """Admin simple pour le modèle Contenu"""

    list_display = ('titre', 'chapitre', 'date_creation')
    list_filter = ('chapitre', 'chapitre__palier__niveau', 'chapitre__partie__niveau')
    search_fields = ('titre', 'chapitre__titre', 'description')
    ordering = ('chapitre', 'titre')

    fieldsets = (
        ('Informations principales', {
            'fields': ('titre', 'description', 'chapitre', 'fichier')
        }),
    )

    readonly_fields = ('date_creation', 'date_modification')

    # Optimiser les requêtes
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'chapitre', 'chapitre__palier', 'chapitre__partie'
        )


