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


# ==================== MODELES D'ABONNEMENT ====================

class UserProfile(models.Model):
    """
    Profil utilisateur avec device_id pour la sécurité
    Inspiré du système educalims qui fonctionne
    """
    RECOMMANDATION_CHOICES = [
        ('gosenmarket', 'Gosenmarket'),
        ('A01', 'A01'),
        ('A02', 'A02'),
        ('A03', 'A03'),
        ('A04', 'A04'),
        ('A05', 'A05'),
        ('aucun', 'Aucun'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='hippie_profile')
    recommande_par = models.CharField(
        max_length=20,
        choices=RECOMMANDATION_CHOICES,
        default='aucun',
        verbose_name='Recommandé par'
    )
    telephone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Téléphone')
    # Appareil autorisé pour cet utilisateur (sécurité JWT)
    device_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        unique=True,
        help_text="Identifiant unique de l'appareil autorisé"
    )

    def __str__(self):
        return f"Profile de {self.user.username}"

    class Meta:
        verbose_name = 'Profil utilisateur'
        verbose_name_plural = 'Profils utilisateurs'


class SessionUser(models.Model):
    """
    Utilisateur identifié par session (localStorage)
    Gardé pour compatibilité, sera progressivement remplacé par UserProfile
    """
    session_id = models.CharField(max_length=100, unique=True)
    telegram_user_id = models.BigIntegerField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Utilisateur de session"
        verbose_name_plural = "Utilisateurs de session"
        ordering = ['-last_active']

    def __str__(self):
        return f"{self.session_id} ({self.telegram_user_id or 'No Telegram'})"


class ProduitAbonnement(models.Model):
    """Produit d'abonnement avec configuration"""
    nom = models.CharField(max_length=200)
    produit_id = models.CharField(max_length=100, unique=True, help_text="ID Cyberschool")
    prix = models.PositiveIntegerField(help_text="Prix en FCFA")
    url_paiement = models.URLField(help_text="URL de base Cyberschool")
    duree_jours = models.PositiveIntegerField(default=1, help_text="Durée en jours")
    description = models.TextField(blank=True)
    est_actif = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        verbose_name = "Produit d'abonnement"
        verbose_name_plural = "Produits d'abonnement"
        ordering = ['-est_actif', 'nom']

    def __str__(self):
        return f"{self.nom} - {self.prix} FCFA"


class Abonnement(models.Model):
    """Abonnement utilisateur"""
    STATUT_CHOICES = [
        ('EN_ATTENTE', 'En attente'),
        ('ACTIF', 'Actif'),
        ('EXPIRE', 'Expiré'),
    ]

    session_user = models.ForeignKey(SessionUser, on_delete=models.CASCADE, related_name='abonnements')
    produit = models.ForeignKey(ProduitAbonnement, on_delete=models.PROTECT, related_name='abonnements')
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='EN_ATTENTE')
    merchant_reference_id = models.CharField(max_length=200, unique=True)
    montant_paye = models.PositiveIntegerField(null=True, blank=True)
    methode_paiement = models.CharField(max_length=20, blank=True)
    date_debut = models.DateTimeField(null=True, blank=True)
    date_fin = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Abonnement"
        verbose_name_plural = "Abonnements"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.session_user.session_id} - {self.produit.nom} ({self.get_statut_display()})"

    def est_valide(self):
        """Vérifie si l'abonnement est actif et non expiré"""
        from django.utils import timezone
        if self.statut != 'ACTIF':
            return False
        if self.date_fin and self.date_fin < timezone.now():
            return False
        return True

    def activer(self, montant, methode):
        """Active l'abonnement jusqu'à 23h59 le jour du paiement"""
        from django.utils import timezone
        from datetime import datetime, time, timedelta

        self.statut = 'ACTIF'
        self.date_debut = timezone.now()
        self.montant_paye = montant
        self.methode_paiement = methode
        # Expiration à 23h59 le jour du paiement + (durée-1) jours
        fin_date = timezone.now().date() + timedelta(days=self.produit.duree_jours - 1)
        self.date_fin = datetime.combine(fin_date, time.max)
        self.save()


class WebhookLog(models.Model):
    """Journal des webhooks Cyberschool"""
    merchant_reference_id = models.CharField(max_length=255)
    code = models.IntegerField()
    status = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    operator = models.CharField(max_length=50, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    abonnement = models.ForeignKey(Abonnement, on_delete=models.SET_NULL, null=True, blank=True, related_name='webhook_logs')
    activation_succes = models.BooleanField(default=False)
    raw_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Journal Webhook"
        verbose_name_plural = "Journaux Webhooks"
        ordering = ['-created_at']

    def __str__(self):
        return f"Webhook {self.merchant_reference_id} - {self.status}"
