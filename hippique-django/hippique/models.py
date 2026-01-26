"""
Models for Hippique TurfFilter application
"""
from django.db import models
from django.utils import timezone


class Scenario(models.Model):
    """Scénario de filtres avec arrivée"""

    # Informations de base
    nom = models.CharField(max_length=200, verbose_name="Nom du scénario")
    description = models.TextField(blank=True, verbose_name="Description")
    date_course = models.DateField(verbose_name="Date de la course")
    nom_course = models.CharField(max_length=200, blank=True, verbose_name="Nom de la course")
    arrivee = models.CharField(max_length=50, blank=True, verbose_name="Arrivée (ex: 1-4-7-8-12-15)")

    # Paramètres des filtres (JSON)
    filtres_ou = models.JSONField(default=dict, blank=True, verbose_name="Filtres OU")
    filtres_et = models.JSONField(default=dict, blank=True, verbose_name="Filtres ET")
    filtres_pairs_impairs = models.JSONField(default=dict, blank=True, verbose_name="Filtres Pairs/Impairs")
    filtres_petits_suites = models.JSONField(default=dict, blank=True, verbose_name="Filtres Petits/Suites")
    filtre_limitation = models.JSONField(default=dict, blank=True, verbose_name="Filtre Limitation")
    filtre_poids = models.JSONField(default=dict, blank=True, verbose_name="Filtre Poids")
    filtre_alternance = models.JSONField(default=dict, blank=True, verbose_name="Filtre Alternance")

    # Résultats du filtrage
    n_partants = models.IntegerField(default=16, verbose_name="Nombre de partants")
    k_taille = models.IntegerField(default=6, verbose_name="Taille de la combinaison")
    combinaisons_total = models.IntegerField(default=8008, verbose_name="Nombre total de combinaisons")
    combinaisons_conservees = models.IntegerField(default=8008, verbose_name="Combinaisons conservées")
    taux_filtrage = models.FloatField(default=0.0, verbose_name="Taux de filtrage (%)")

    # Résultat de l'arrivée
    resultat = models.JSONField(null=True, blank=True, verbose_name="Résultat (bons sur total)")

    # Favori et utilisation
    is_favorite = models.BooleanField(default=False, verbose_name="Favori")
    is_public = models.BooleanField(default=False, verbose_name="Public")
    usage_count = models.IntegerField(default=0, verbose_name="Nombre d'utilisations")

    # Dates
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière mise à jour")

    class Meta:
        ordering = ['-is_favorite', '-updated_at']
        verbose_name = "Scénario"
        verbose_name_plural = "Scénarios"

    def __str__(self):
        return f"{self.nom} ({self.date_course})"

    def calculer_resultat(self):
        """Calcule le résultat par rapport à l'arrivée"""
        if not self.arrivee or not self.resultat:
            return None

        arrivee_nums = [int(x.strip()) for x in self.arrivee.split('-') if x.strip().isdigit()]

        if not arrivee_nums:
            return None

        # Trouver le nombre de combinaisons gagnantes
        combinaisons = self.resultat.get('combinaisons', [])
        gagnantes = 0

        for comb in combinaisons:
            comb_nums = [int(x) for x in comb.split(' - ')]
            bons = len(set(comb_nums) & set(arrivee_nums))
            if bons >= 3:  # Au moins 3 bons sur 6
                gagnantes += 1

        total = len(combinaisons)
        if total > 0:
            return {
                'gagnantes': gagnantes,
                'total': total,
                'pourcentage': round((gagnantes / total) * 100, 2)
            }
        return None


class Combinaison(models.Model):
    """Combinaison sauvegardée pour un scénario"""

    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE, related_name='combinaisons')
    combinaison = models.CharField(max_length=50, verbose_name="Combinaison")

    # Métadonnées
    est_gagnante = models.BooleanField(null=True, blank=True, verbose_name="Est gagnante")
    nb_bons = models.IntegerField(null=True, blank=True, verbose_name="Nombre de bons")
    rang = models.IntegerField(null=True, blank=True, verbose_name="Rang dans l'arrivée")

    # Statistiques
    frequence_chevaux = models.JSONField(default=dict, blank=True, verbose_name="Fréquence des chevaux")

    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")

    class Meta:
        ordering = ['scenario', 'rang']
        verbose_name = "Combinaison"
        verbose_name_plural = "Combinaisons"
        unique_together = ['scenario', 'combinaison']

    def __str__(self):
        return f"{self.combinaison} ({self.scenario.nom})"

    def calculer_bons(self, arrivee):
        """Calcule le nombre de chevaux dans l'arrivée"""
        if not arrivee:
            return None

        arrivee_nums = [int(x.strip()) for x in arrivee.split('-') if x.strip().isdigit()]
        comb_nums = [int(x) for x in self.combinaison.split(' - ')]

        bons = len(set(comb_nums) & set(arrivee_nums))
        self.nb_bons = bons
        self.est_gagnante = bons >= 3
        self.save()
        return bons
