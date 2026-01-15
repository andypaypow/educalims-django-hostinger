from django.db import models
from django.contrib.auth.models import User
import uuid



class Cycle(models.Model):
    """Cycle éducatif (Collège, Lycée)"""
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    ordre = models.PositiveIntegerField(default=0, help_text="Ordre d'affichage")
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['ordre', 'nom']
        verbose_name = "Cycle"
        verbose_name_plural = "Cycles"

    def __str__(self):
        return self.nom


class Discipline(models.Model):
    """Discipline (SVT, Mathématiques, etc.)"""
    nom = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)
    cycles = models.ManyToManyField(Cycle, related_name='disciplines', blank=True)
    couleur = models.CharField(max_length=7, default='#667eea', help_text="Code hexadécimal de la couleur")
    icone = models.CharField(max_length=50, blank=True, help_text="Nom de l'icône (FontAwesome, etc.)")
    ordre = models.PositiveIntegerField(default=0, help_text="Ordre d'affichage")
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['ordre', 'nom']
        verbose_name = "Discipline"
        verbose_name_plural = "Disciplines"

    def __str__(self):
        return self.nom


class Niveau(models.Model):
    """Niveau (ex: Terminale -> Terminale C, Terminale D)"""
    SPECIALITE_CHOICES = [
        ('L', 'Littéraire'),
        ('S', 'Scientifique'),
        ('T', 'Technologique'),
        ('P', 'Professionnelle'),
        ('A', 'Autre'),
    ]

    nom = models.CharField(max_length=200)
    cycle = models.ForeignKey(Cycle, on_delete=models.CASCADE, related_name='niveaux')
    disciplines = models.ManyToManyField(Discipline, related_name='niveaux', blank=True)
    niveau_parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='niveaux_enfants',
        null=True,
        blank=True,
        help_text="Niveau parent (ex: Terminale pour Terminale C)"
    )
    specialite = models.CharField(
        max_length=1,
        choices=SPECIALITE_CHOICES,
        default='A',
        help_text="Spécialité du niveau"
    )
    description = models.TextField(blank=True, null=True)
    ordre = models.PositiveIntegerField(default=0, help_text="Ordre d'affichage")
    est_niveau_enfant = models.BooleanField(
        default=False,
        help_text="True si ce niveau a un niveau parent (ex: Terminale C)"
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['ordre', 'nom']
        verbose_name = "Niveau"
        verbose_name_plural = "Niveaux"
        constraints = [
            models.UniqueConstraint(
                fields=['nom', 'niveau_parent'],
                condition=models.Q(niveau_parent__isnull=False),
                name='unique_niveau_enfant_par_parent'
            )
        ]

    def __str__(self):
        if self.niveau_parent:
            return f"{self.niveau_parent.nom} - {self.nom}"
        return self.nom

    def save(self, *args, **kwargs):
        # Définir automatiquement est_niveau_enfant
        self.est_niveau_enfant = self.niveau_parent is not None
        super().save(*args, **kwargs)


class Unite(models.Model):
    """Unité d'enseignement (chapitre, partie, etc.)"""
    TYPE_UNITE_CHOICES = [
        ('C', 'Chapitre'),
        ('P', 'Partie'),
        ('S', 'Section'),
        ('L', 'Leçon'),
        ('T', 'Thème'),
    ]

    nom = models.CharField(max_length=200)
    niveau = models.ForeignKey(Niveau, on_delete=models.CASCADE, related_name='unites')
    discipline = models.ForeignKey(Discipline, on_delete=models.CASCADE, related_name='unites')
    unite_parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='unites_enfants',
        null=True,
        blank=True,
        help_text="Unité parente pour créer une hiérarchie"
    )
    type_unite = models.CharField(
        max_length=1,
        choices=TYPE_UNITE_CHOICES,
        default='C',
        help_text="Type de l'unité"
    )
    description = models.TextField(blank=True, null=True)
    ordre = models.PositiveIntegerField(default=0, help_text="Ordre d'affichage")
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['ordre', 'nom']
        verbose_name = "Unité"
        verbose_name_plural = "Unités"

    def __str__(self):
        prefixe = f"[{self.get_type_unite_display()}] "
        if self.unite_parent:
            return f"{prefixe}{self.unite_parent.nom} > {self.nom}"
        return f"{prefixe}{self.nom}"


class Fichier(models.Model):
    """Fichier pédagogique (Texte, PDF, Vidéo, Liens)"""
    TYPE_FICHIER_CHOICES = [
        ('TXT', 'Texte'),
        ('PDF', 'PDF'),
        ('VID', 'Vidéo'),
        ('LNK', 'Lien'),
        ('IMG', 'Image'),
        ('DOC', 'Document'),
    ]

    nom = models.CharField(max_length=200)
    unite = models.ForeignKey(Unite, on_delete=models.CASCADE, related_name='fichiers')
    type_fichier = models.CharField(
        max_length=3,
        choices=TYPE_FICHIER_CHOICES,
        default='PDF',
        help_text="Type du fichier"
    )
    fichier = models.FileField(
        upload_to='fichiers/%Y/%m/',
        blank=True,
        null=True,
        help_text="Fichier uploadé (pour PDF, images, etc.)"
    )
    contenu_texte = models.TextField(
        blank=True,
        null=True,
        help_text="Contenu texte directement"
    )
    url_lien = models.URLField(
        blank=True,
        null=True,
        help_text="URL externe (pour les liens)"
    )
    duree = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Durée en secondes (pour les vidéos)"
    )
    taille = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Taille du fichier en octets"
    )
    description = models.TextField(blank=True, null=True)
    telechargements = models.PositiveIntegerField(default=0, help_text="Nombre de téléchargements")
    est_actif = models.BooleanField(default=True, help_text="Fichier visible/accessible")
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_creation', 'nom']
        verbose_name = "Fichier"
        verbose_name_plural = "Fichiers"

    def __str__(self):
        return f"{self.get_type_fichier_display()} - {self.nom}"

    def get_fichier_url(self):
        """Retourne l'URL appropriée selon le type de fichier"""
        if self.type_fichier == 'LNK':
            return self.url_lien
        elif self.fichier:
            return self.fichier.url
        return None


# ==================== MODELES D'ABONNEMENT ====================

class Produit(models.Model):
    """Produit d'abonnement avec différents moyens de paiement"""
    TYPE_PAIEMENT_CHOICES = [
        ('AIRTEL', 'Airtel Money'),
        ('MOOV', 'Moov Money'),
    ]

    nom = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)
    prix = models.PositiveIntegerField(help_text="Prix en FCFA")
    airtel_money_url = models.URLField(
        blank=True,
        null=True,
        help_text="URL de paiement Airtel Money"
    )
    moov_money_url = models.URLField(
        blank=True,
        null=True,
        help_text="URL de paiement Moov Money"
    )
    duree_jours = models.PositiveIntegerField(
        default=30,
        help_text="Durée de l'abonnement en jours"
    )
    est_actif = models.BooleanField(default=True, help_text="Produit disponible à la vente")
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_creation', 'nom']
        verbose_name = "Produit"
        verbose_name_plural = "Produits"

    def __str__(self):
        return f"{self.nom} - {self.prix} FCFA"


class Abonnement(models.Model):
    """Abonnement d'un utilisateur à un niveau d'une discipline"""
    STATUT_CHOICES = [
        ('EN_ATTENTE', 'En attente de paiement'),
        ('ACTIF', 'Actif'),
        ('EXPIRE', 'Expiré'),
        ('ANNULE', 'Annulé'),
        ('ECHOUE', 'Échec du paiement'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='abonnements')
    niveau = models.ForeignKey(Niveau, on_delete=models.CASCADE, related_name='abonnements')
    produit = models.ForeignKey(Produit, on_delete=models.PROTECT, related_name='abonnements')
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='EN_ATTENTE',
        help_text="Statut de l'abonnement"
    )
    reference_interne = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        unique=True,
        help_text="Notre reference interne unique de la transaction"
    )
    merchant_reference_id = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Reference marchand envoyee a Cyberschool et renvoyee dans le callback"
    )
    code_paiement = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text="Code de reponse du paiement (ex: 200 pour succes)"
    )
    methode_paiement = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Methode de paiement utilisee (Airtel/Moov)"
    )
    montant_paye = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Montant reellement paye"
    )
    date_debut = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Date de debut de l'abonnement"
    )
    date_fin = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Date de fin de l'abonnement"
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_creation', '-date_debut']
        verbose_name = "Abonnement"
        verbose_name_plural = "Abonnements"
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'niveau', 'statut'],
                condition=models.Q(statut='ACTIF'),
                name='unique_abonnement_actif_par_user_niveau'
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.niveau} ({self.get_statut_display()})"

    def est_valide(self):
        """Vérifie si l'abonnement est actif et non expiré"""
        from django.utils import timezone
        if self.statut != 'ACTIF':
            return False
        if self.date_fin and self.date_fin < timezone.now():
            return False
        return True

    def activer_abonnement(self, duree_jours=30):
        """Active l'abonnement pour la durée spécifiée"""
        from django.utils import timezone
        from datetime import timedelta

        self.statut = 'ACTIF'
        self.date_debut = timezone.now()
        self.date_fin = self.date_debut + timedelta(days=duree_jours)
        self.save()


class WebhookLog(models.Model):
    """Journal des notifications webhook reçues de Cyberschool"""
    STATUT_CHOICES = [
        ('SUCCESS', 'Succès'),
        ('FAILED', 'Échec'),
        ('PENDING', 'En attente'),
    ]

    merchant_reference_id = models.CharField(max_length=255, null=True, blank=True, verbose_name="Référence marchand")
    code = models.IntegerField(null=True, blank=True, verbose_name="Code de réponse")
    status = models.CharField(max_length=20, choices=STATUT_CHOICES, verbose_name="Statut")
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Montant")
    operator = models.CharField(max_length=50, null=True, blank=True, verbose_name="Opérateur")
    transaction_id = models.CharField(max_length=255, null=True, blank=True, verbose_name="ID Transaction")
    phone_number = models.CharField(max_length=20, null=True, blank=True, verbose_name="Numéro de téléphone")
    abonnement = models.ForeignKey(Abonnement, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='webhook_logs', verbose_name="Abonnement")
    activation_succes = models.BooleanField(default=False, verbose_name="Activation réussie")
    telegram_notification_sent = models.BooleanField(default=True, verbose_name="Notif Telegram envoyée")
    raw_data = models.JSONField(default=dict, verbose_name="Données brutes")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de réception")

    class Meta:
        verbose_name = "Journal Webhook"
        verbose_name_plural = "Journaux Webhooks"
        ordering = ['-created_at']

    def __str__(self):
        return f"Webhook {self.merchant_reference_id or 'N/A'} - {self.status} ({self.created_at.strftime('%d/%m/%Y %H:%M')})"
