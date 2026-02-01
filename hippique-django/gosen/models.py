from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json


class WebhookLog(models.Model):
    """
    Modèle pour enregistrer tous les webhooks reçus
    Permet de tracer et débugger les notifications
    """
    SOURCE_CHOICES = [
        ('cyberschool', 'Cyberschool'),
        ('moov_money', 'Moov Money'),
        ('airtel_money', 'Airtel Money'),
        ('autre', 'Autre'),
    ]

    STATUT_CHOICES = [
        ('SUCCES', 'Succès'),
        ('ERREUR', 'Erreur'),
        ('EN_ATTENTE', 'En attente'),
    ]

    # Informations de base
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES, default='cyberschool')
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='SUCCES')

    # Données du webhook
    payload = models.JSONField(default=dict, help_text="Données brutes reçues")
    headers = models.JSONField(default=dict, help_text="En-têtes HTTP reçus")

    # Informations de paiement extraites
    reference_transaction = models.CharField(max_length=255, blank=True, null=True, help_text="Référence de la transaction")
    code_paiement = models.CharField(max_length=50, blank=True, null=True, help_text="Code de paiement")
    montant = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Montant payé")
    fees = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Frais de transaction")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Montant total (incluant les frais)")
    telephone = models.CharField(max_length=50, blank=True, null=True, help_text="Numéro de téléphone")

    # Traitement
    date_reception = models.DateTimeField(auto_now_add=True, help_text="Date de réception du webhook")
    date_traitement = models.DateTimeField(blank=True, null=True, help_text="Date de traitement")
    message_erreur = models.TextField(blank=True, null=True, help_text="Message d'erreur si échec")
    tentatives = models.IntegerField(default=0, help_text="Nombre de tentatives de traitement")

    # Utilisateur associé (si trouvé)
    utilisateur = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='weblogs_recus')

    # Métadonnées
    ip_address = models.GenericIPAddressField(blank=True, null=True, help_text="IP de l'expéditeur")
    user_agent = models.TextField(blank=True, null=True, help_text="User Agent de l'expéditeur")

    class Meta:
        ordering = ['-date_reception']
        verbose_name = "Log Webhook"
        verbose_name_plural = "Logs Webhooks"
        indexes = [
            models.Index(fields=['reference_transaction']),
            models.Index(fields=['statut']),
            models.Index(fields=['source']),
            models.Index(fields=['-date_reception']),
        ]

    def __str__(self):
        return f"Webhook {self.source} - {self.reference_transaction or 'N/A'} - {self.date_reception.strftime('%d/%m/%Y %H:%M')}"

    def marque_traite(self, succes=True, message=""):
        """Marque le webhook comme traité"""
        self.date_traitement = timezone.now()
        self.statut = 'SUCCES' if succes else 'ERREUR'
        if message:
            self.message_erreur = message
        self.save()

    def incrementer_tentative(self):
        """Incrémente le compteur de tentatives"""
        self.tentatives += 1
        self.save()

    @property
    def duree_traitement(self):
        """Retourne la durée de traitement en secondes"""
        if self.date_traitement and self.date_reception:
            return (self.date_traitement - self.date_reception).total_seconds()
        return None

    @property
    def est_en_retard(self):
        """Vérifie si le webhook n'a pas été traité dans les 5 minutes"""
        if not self.date_traitement:
            return (timezone.now() - self.date_reception).total_seconds() > 300
        return False
