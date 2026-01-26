"""
Django Admin pour Hippique TurfFilter
"""
from django.contrib import admin
from .models import Scenario, Combinaison


@admin.register(Scenario)
class ScenarioAdmin(admin.ModelAdmin):
    """Administration des scénarios"""
    list_display = ['nom', 'date_course', 'combinaisons_conservees', 'taux_filtrage', 'is_favorite', 'updated_at']
    list_filter = ['is_favorite', 'is_public', 'date_course', 'n_partants', 'k_taille']
    search_fields = ['nom', 'description', 'nom_course']
    readonly_fields = ['date_creation', 'updated_at']
    date_hierarchy = 'date_course'
    ordering = ['-is_favorite', '-updated_at']

    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'description', 'date_course', 'nom_course', 'arrivee')
        }),
        ('Paramètres de la course', {
            'fields': ('n_partants', 'k_taille')
        }),
        ('Filtres', {
            'fields': ('filtres_ou', 'filtres_et', 'filtres_pairs_impairs',
                      'filtres_petits_suites', 'filtre_limitation',
                      'filtre_poids', 'filtre_alternance')
        }),
        ('Résultats', {
            'fields': ('combinaisons_total', 'combinaisons_conservees',
                      'taux_filtrage', 'resultat')
        }),
        ('Métadonnées', {
            'fields': ('is_favorite', 'is_public', 'usage_count',
                      'date_creation', 'updated_at')
        }),
    )


@admin.register(Combinaison)
class CombinaisonAdmin(admin.ModelAdmin):
    """Administration des combinaisons"""
    list_display = ['scenario', 'combinaison', 'est_gagnante', 'nb_bons', 'rang']
    list_filter = ['est_gagnante', 'scenario__date_course']
    search_fields = ['combinaison', 'scenario__nom']
    readonly_fields = ['date_creation']
    ordering = ['scenario', 'rang']
