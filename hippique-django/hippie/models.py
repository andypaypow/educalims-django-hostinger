"""
Models for TurfFilter application
"""
from django.db import models
from django.contrib.auth.models import User


class Scenario(models.Model):
    """
    Scénario de filtrage sauvegardable
    Permet de stocker une configuration complète de filtres
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100, verbose_name="Nom du scénario")
    description = models.TextField(blank=True, verbose_name="Description")

    # Configuration
    n_partants = models.IntegerField(verbose_name="Nombre de partants")
    k_taille = models.IntegerField(verbose_name="Taille de combinaison")

    # Informations sur la course
    date_course = models.DateField(null=True, blank=True, verbose_name="Date de la course")
    nom_course = models.CharField(max_length=200, blank=True, verbose_name="Nom de la course")

    # Données JSON pour la configuration
    pronostics_text = models.TextField(blank=True, verbose_name="Texte des pronostics")
    groups = models.JSONField(default=list, verbose_name="Groupes de pronostics")
    filters = models.JSONField(default=dict, verbose_name="Filtres appliqués")

    # Arrivée et résultats
    arrivee = models.JSONField(null=True, blank=True, verbose_name="Arrivée de la course")
    nb_combinaisons_restantes = models.IntegerField(null=True, blank=True, verbose_name="Nombre de combinaisons restantes")

    # Métadonnées
    is_favorite = models.BooleanField(default=False, verbose_name="Favori")
    is_public = models.BooleanField(default=False, verbose_name="Public")
    usage_count = models.IntegerField(default=0, verbose_name="Nombre d'utilisations")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")

    class Meta:
        verbose_name = "Scénario"
        verbose_name_plural = "Scénarios"
        ordering = ['-is_favorite', '-updated_at']

    def __str__(self):
        return f"{self.name} (C{self.n_partants}, K{self.k_taille})"

    def increment_usage(self):
        """Incrémente le compteur d'utilisation"""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])


class ScenarioTag(models.Model):
    """Tags pour organiser les scénarios"""
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default="#009E60")
    scenarios = models.ManyToManyField(Scenario, related_name='tags')

    def __str__(self):
        return self.name
