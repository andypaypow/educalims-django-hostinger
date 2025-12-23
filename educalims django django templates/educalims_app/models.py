# -*- coding: utf-8 -*-
from django.db import models
from django.urls import reverse
import json


class Cycle(models.Model):
    """
    Cycle éducatif (ex: Primaire, Collège, Lycée)
    C'est la racine de la hiérarchie pédagogique.
    """
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    ordre = models.PositiveIntegerField(default=0, help_text="Ordre d'affichage")
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['ordre', 'nom']
        verbose_name = 'Cycle'
        verbose_name_plural = 'Cycles'

    def __str__(self):
        return self.nom

    def get_absolute_url(self):
        return reverse('cycle_detail', kwargs={'pk': self.pk})


class Discipline(models.Model):
    """
    Discipline / Matière enseignée (ex: Mathématiques, Français, Histoire)
    Une discipline appartient à un Cycle.
    """
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    cycle = models.ForeignKey(Cycle, on_delete=models.CASCADE, related_name='disciplines')
    icone = models.CharField(max_length=50, blank=True, help_text="Classe d'icône Bootstrap (ex: bi-calculator)")
    couleur = models.CharField(max_length=7, default='#3498db', help_text="Code couleur HEX")
    ordre = models.PositiveIntegerField(default=0, help_text="Ordre d'affichage")
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['ordre', 'nom']
        verbose_name = 'Discipline'
        verbose_name_plural = 'Disciplines'
        unique_together = ['cycle', 'nom']

    def __str__(self):
        return f"{self.cycle.nom} - {self.nom}"

    def get_absolute_url(self):
        return reverse('discipline_detail', kwargs={'pk': self.pk})


class Niveau(models.Model):
    """
    Niveau scolaire (ex: 6ème, 5ème, CM2, Terminale)
    Un niveau appartient à une Discipline.
    Le champ 'parent' permet une hiérarchie profonde (ex: 6ème → 6ème A).
    """
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    discipline = models.ForeignKey(Discipline, on_delete=models.CASCADE, related_name='niveaux')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='enfants')
    ordre = models.PositiveIntegerField(default=0, help_text="Ordre d'affichage")
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['ordre', 'nom']
        verbose_name = 'Niveau'
        verbose_name_plural = 'Niveaux'

    def __str__(self):
        if self.parent:
            return f"{self.discipline.nom} - {self.nom} (fils de {self.parent.nom})"
        return f"{self.discipline.nom} - {self.nom}"

    def get_absolute_url(self):
        return reverse('niveau_detail', kwargs={'pk': self.pk})


class Unite(models.Model):
    """
    Unité pédagogique (ex: Chapitre, Partie, Leçon)
    Une unité appartient à un Niveau.
    Le champ 'parent' permet une hiérarchie profonde (ex: Chapitre 1 → Partie 1.1).
    """
    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    niveau = models.ForeignKey(Niveau, on_delete=models.CASCADE, related_name='unites')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='enfants')
    ordre = models.PositiveIntegerField(default=0, help_text="Ordre d'affichage")
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['ordre', 'titre']
        verbose_name = 'Unité'
        verbose_name_plural = 'Unités'

    def __str__(self):
        if self.parent:
            return f"{self.niveau.nom} - {self.titre} (fils de {self.parent.titre})"
        return f"{self.niveau.nom} - {self.titre}"

    def get_absolute_url(self):
        return reverse('unite_detail', kwargs={'pk': self.pk})


class TypeFichier(models.TextChoices):
    PDF = 'PDF', 'PDF'
    VIDEO = 'VIDEO', 'Vidéo'
    AUDIO = 'AUDIO', 'Audio'
    IMAGE = 'IMAGE', 'Image'
    DOCUMENT = 'DOCUMENT', 'Document'
    AUTRE = 'AUTRE', 'Autre'


class Fichier(models.Model):
    """
    Ressource pédagogique (PDF, vidéo, audio, image, etc.)
    Un fichier est lié à une Unité.
    """
    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    fichier_upload = models.FileField(upload_to='fichiers_pedagogiques/%Y/%m/%d/')
    unite = models.ForeignKey(Unite, on_delete=models.CASCADE, related_name='fichiers')
    type_fichier = models.CharField(
        max_length=20,
        choices=TypeFichier.choices,
        default=TypeFichier.DOCUMENT
    )
    ordre = models.PositiveIntegerField(default=0, help_text="Ordre d'affichage")
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['ordre', 'titre']
        verbose_name = 'Fichier'
        verbose_name_plural = 'Fichiers'

    def __str__(self):
        return f"{self.unite.titre} - {self.titre}"

    def get_absolute_url(self):
        return reverse('fichier_detail', kwargs={'pk': self.pk})


class TelegramUser(models.Model):
    """
    Utilisateur Telegram connecté via la Mini App.
    Stocke les informations envoyées par Telegram WebApp.
    """
    # ID unique Telegram (obligatoire)
    telegram_id = models.BigIntegerField(unique=True, db_index=True, help_text="ID unique de l'utilisateur Telegram")

    # Informations de base
    first_name = models.CharField(max_length=100, blank=True, help_text="Prénom")
    last_name = models.CharField(max_length=100, blank=True, help_text="Nom")
    username = models.CharField(max_length=100, blank=True, null=True, help_text="Nom d'utilisateur Telegram (@username)")
    language_code = models.CharField(max_length=10, blank=True, help_text="Code langue (ex: fr, en)")

    # Informations supplémentaires
    is_premium = models.BooleanField(default=False, help_text="Compte Telegram Premium")
    is_bot = models.BooleanField(default=False, help_text="Est un bot")

    # Photo de profil
    photo_url = models.URLField(blank=True, help_text="URL de la photo de profil")

    # Données brutes JSON (pour extensibilité)
    raw_data = models.JSONField(blank=True, null=True, help_text="Données brutes Telegram")

    # Suivi des connexions
    first_seen = models.DateTimeField(auto_now_add=True, help_text="Première connexion")
    last_seen = models.DateTimeField(auto_now=True, help_text="Dernière connexion")
    connection_count = models.PositiveIntegerField(default=1, help_text="Nombre de connexions")

    # Statut
    is_active = models.BooleanField(default=True, help_text="Utilisateur actif")

    class Meta:
        ordering = ['-last_seen']
        verbose_name = 'Utilisateur Telegram'
        verbose_name_plural = 'Utilisateurs Telegram'

    def __str__(self):
        name = f"{self.first_name} {self.last_name}".strip() or self.username or f"User_{self.telegram_id}"
        return f"{name} ({self.telegram_id})"

    def increment_connection(self):
        """Incrémente le compteur de connexions et met à jour last_seen"""
        self.connection_count += 1
        self.save(update_fields=['last_seen', 'connection_count'])

    @classmethod
    def get_or_create_from_webapp(cls, webapp_data):
        """
        Crée ou met à jour un utilisateur Telegram à partir des données WebApp.

        Args:
            webapp_data: Dictionnaire contenant les données de Telegram.WebApp.initDataUnsafe.user

        Returns:
            tuple: (TelegramUser instance, created)
        """
        if not webapp_data:
            return None, False

        telegram_id = webapp_data.get('id')
        if not telegram_id:
            return None, False

        # Préparer les données
        defaults = {
            'first_name': webapp_data.get('first_name', ''),
            'last_name': webapp_data.get('last_name', ''),
            'username': webapp_data.get('username'),
            'language_code': webapp_data.get('language_code', ''),
            'is_premium': webapp_data.get('is_premium', False),
            'is_bot': webapp_data.get('is_bot', False),
            'photo_url': webapp_data.get('photo_url', ''),
            'raw_data': webapp_data,
        }

        # Get or create
        user, created = cls.objects.get_or_create(
            telegram_id=telegram_id,
            defaults=defaults
        )

        # Si l'utilisateur existe déjà, mettre à jour ses infos
        if not created:
            for key, value in defaults.items():
                setattr(user, key, value)
            user.save()

        return user, created


# ============================================================================
# SYSTÈME D'ABONNEMENT PAR DISCIPLINE
# ============================================================================

class TypeAbonnement(models.TextChoices):
    """Types d'abonnement disponibles"""
    ESSENTIEL = 'ESSENTIEL', 'Accès Essentiel'
    SEANCE_UNIQUE = 'SEANCE_UNIQUE', 'Séance Unique'
    SEANCE_INTEGRAL = 'SEANCE_INTEGRAL', 'séance intégrale'


class StatutAbonnement(models.TextChoices):
    """Statuts d'un abonnement"""
    EN_ATTENTE = 'EN_ATTENTE', 'En attente de paiement'
    ACTIF = 'ACTIF', 'Actif'
    ANNULE = 'ANNULE', 'Annulé'
    EXPIRE = 'EXPIRE', 'Expiré'


class Seance(models.Model):
    """
    Séance d'appel avec un professeur.
    Une séance est liée à une discipline.
    """
    titre = models.CharField(max_length=200, help_text="Titre de la séance")
    description = models.TextField(blank=True, help_text="Description de la séance")
    discipline = models.ForeignKey(Discipline, on_delete=models.CASCADE, related_name='seances')
    date_heure = models.DateTimeField(help_text="Date et heure de la séance")
    duree_minutes = models.PositiveIntegerField(default=60, help_text="Durée en minutes")
    places_max = models.PositiveIntegerField(default=50, help_text="Nombre de places maximum")
    places_prises = models.PositiveIntegerField(default=0, help_text="Nombre de places réservées")
    lien_meet = models.URLField(blank=True, help_text="Lien Google Meet/Zoom")
    est_active = models.BooleanField(default=True, help_text="Séance active")
    ordre = models.PositiveIntegerField(default=0, help_text="Ordre d'affichage")
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date_heure', 'ordre']
        verbose_name = 'Séance'
        verbose_name_plural = 'Séances'

    def __str__(self):
        return f"{self.discipline.nom} - {self.titre}"

    def places_restantes(self):
        return max(0, self.places_max - self.places_prises)

    def est_complete(self):
        return self.places_prises >= self.places_max


class Abonnement(models.Model):
    """
    Abonnement d'un utilisateur à une discipline pour un niveau spécifique.
    Un utilisateur peut avoir plusieurs abonnements pour différentes disciplines et niveaux.
    """
    # Utilisateur Telegram (ou utilisateur Django si étendu)
    utilisateur = models.ForeignKey(
        TelegramUser,
        on_delete=models.CASCADE,
        related_name='abonnements',
        help_text="Utilisateur Telegram"
    )

    # Discipline concernée
    discipline = models.ForeignKey(
        Discipline,
        on_delete=models.CASCADE,
        related_name='abonnements',
        help_text="Discipline associée"
    )

    # Niveau concerné (ex: Terminale C, 6ème, etc.)
    niveau = models.ForeignKey(
        'Niveau',
        on_delete=models.CASCADE,
        related_name='abonnements',
        null=True,  # Temporairement nullable pour la migration
        help_text="Niveau associé"
    )

    # Type d'abonnement
    type_abonnement = models.CharField(
        max_length=20,
        choices=TypeAbonnement.choices,
        help_text="Type d'abonnement"
    )

    # Statut
    statut = models.CharField(
        max_length=20,
        choices=StatutAbonnement.choices,
        default=StatutAbonnement.EN_ATTENTE,
        help_text="Statut de l'abonnement"
    )

    # Séance spécifique (uniquement pour PROF_UNIQUE)
    seance = models.ForeignKey(
        Seance,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='abonnements_unique',
        help_text="Séance spécifique (pour abonnement UNIQUE)"
    )

    # Dates
    date_debut = models.DateTimeField(help_text="Date de début de l'abonnement")
    date_fin = models.DateTimeField(help_text="Date de fin de l'abonnement")
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    # Paiement
    montant_paye = models.PositiveIntegerField(default=0, help_text="Montant payé en FCFA")
    reference_transaction = models.CharField(max_length=100, blank=True, help_text="Référence de la transaction")

    class Meta:
        ordering = ['-date_creation']
        verbose_name = 'Abonnement'
        verbose_name_plural = 'Abonnements'
        unique_together = ['utilisateur', 'discipline', 'niveau', 'type_abonnement', 'seance']

    def __str__(self):
        return f"{self.utilisateur} - {self.discipline.nom} - {self.niveau.nom} ({self.get_type_abonnement_display()})"

    def est_actif(self):
        """Vérifie si l'abonnement est actif et non expiré"""
        from django.utils import timezone
        return (
            self.statut == StatutAbonnement.ACTIF and
            self.date_debut <= timezone.now() <= self.date_fin
        )

    def peut_acceder_fiches(self):
        """L'utilisateur peut accéder aux fiches/corrigés de ce niveau"""
        return self.type_abonnement in [
            TypeAbonnement.ESSENTIEL,
            TypeAbonnement.SEANCE_UNIQUE,
            TypeAbonnement.SEANCE_INTEGRAL
        ] and self.est_actif()

    def peut_acceder_seance(self, seance):
        """L'utilisateur peut accéder à une séance spécifique"""
        if not self.est_actif():
            return False

        if self.type_abonnement == TypeAbonnement.ESSENTIEL:
            return False  # Essentiel ne donne pas accès aux séances

        if self.type_abonnement == TypeAbonnement.SEANCE_UNIQUE:
            return self.seance == seance  # Uniquement la séance spécifique

        if self.type_abonnement == TypeAbonnement.SEANCE_INTEGRAL:
            return seance.discipline == self.discipline  # Toutes les séances de la discipline

        return False


class Transaction(models.Model):
    """
    Transaction de paiement.
    Une transaction peut être liée à un ou plusieurs abonnements.
    """
    # Identifiants
    reference = models.CharField(max_length=100, unique=True, db_index=True, help_text="Référence unique de la transaction")

    # Utilisateur
    utilisateur = models.ForeignKey(
        TelegramUser,
        on_delete=models.CASCADE,
        related_name='transactions',
        help_text="Utilisateur Telegram"
    )

    # Montant
    montant = models.PositiveIntegerField(help_text="Montant de la transaction en FCFA")

    # Devise (pour compatibilité avec les prestataires de paiement)
    devise = models.CharField(max_length=10, default='XAF', help_text="Code devise (XAF, EUR, etc.)")

    # Statut
    statut = models.CharField(
        max_length=20,
        choices=[
            ('EN_ATTENTE', 'En attente'),
            ('SUCCES', 'Succès'),
            ('ECHEC', 'Échec'),
            ('ANNULE', 'Annulé'),
        ],
        default='EN_ATTENTE',
        help_text="Statut de la transaction"
    )

    # Prestataire de paiement
    fournisseur = models.CharField(max_length=50, blank=True, help_text="Nom du prestataire de paiement")
    fournisseur_transaction_id = models.CharField(max_length=100, blank=True, help_text="ID de transaction chez le prestataire")

    # Abonnements liés (une transaction peut créer plusieurs abonnements)
    abonnements = models.ManyToManyField(
        Abonnement,
        blank=True,
        related_name='transactions',
        help_text="Abonnements créés par cette transaction"
    )

    # Données brutes du prestataire (pour debugging et réconciliation)
    donnees_brutes = models.JSONField(blank=True, null=True, help_text="Données brutes du prestataire")

    # Dates
    date_creation = models.DateTimeField(auto_now_add=True, help_text="Date de création")
    date_validation = models.DateTimeField(null=True, blank=True, help_text="Date de validation du paiement")

    class Meta:
        ordering = ['-date_creation']
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'

    def __str__(self):
        return f"Transaction {self.reference} - {self.montant} FCFA ({self.get_statut_display()})"

    def est_validee(self):
        """Vérifie si la transaction est validée avec succès"""
        return self.statut == 'SUCCES'

    def valider(self):
        """Valide la transaction et active les abonnements associés"""
        from django.utils import timezone

        self.statut = 'SUCCES'
        self.date_validation = timezone.now()
        self.save()

        # Activer tous les abonnements liés
        for abonnement in self.abonnements.all():
            abonnement.statut = StatutAbonnement.ACTIF
            abonnement.save()
