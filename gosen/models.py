from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class WebhookLog(models.Model):
    """Modèle pour enregistrer tous les webhooks reçus"""
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

    source = models.CharField(max_length=50, choices=SOURCE_CHOICES, default='cyberschool')
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='SUCCES')
    payload = models.JSONField(default=dict)
    headers = models.JSONField(default=dict)
    reference_transaction = models.CharField(max_length=255, blank=True, null=True)
    code_paiement = models.CharField(max_length=50, blank=True, null=True)
    montant = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fees = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    telephone = models.CharField(max_length=50, blank=True, null=True)
    date_reception = models.DateTimeField(auto_now_add=True)
    date_traitement = models.DateTimeField(blank=True, null=True)
    message_erreur = models.TextField(blank=True, null=True)
    tentatives = models.IntegerField(default=0)
    utilisateur = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='weblogs_recus')
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-date_reception']
        verbose_name = 'Log Webhook'
        verbose_name_plural = 'Logs Webhooks'

    def __str__(self):
        return f'Webhook {self.source} - {self.reference_transaction or "N/A"}'


class UserProfile(models.Model):
    """Profil utilisateur étendu avec gestion des abonnements"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    telephone = models.CharField(max_length=50, blank=True, null=True)
    device_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    date_creation_compte = models.DateTimeField(auto_now_add=True)
    derniere_connexion = models.DateTimeField(blank=True, null=True)
    nb_filtres_realises = models.IntegerField(default=0)
    est_actif = models.BooleanField(default=True)

    a_un_abonnement = models.BooleanField(default=False)
    type_abonnement = models.CharField(max_length=20, choices=[
        ('mensuel', 'Mensuel'),
        ('annuel', 'Annuel'),
        ('a_vie', 'À vie'),
        ('gratuit', 'Gratuit'),
    ], default='gratuit')
    date_debut_abonnement = models.DateTimeField(blank=True, null=True)
    date_fin_abonnement = models.DateTimeField(blank=True, null=True)

    filtres_gratuits_utilises = models.IntegerField(default=0)
    date_reset_filtres = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = 'Profil Utilisateur'
        verbose_name_plural = 'Profils Utilisateurs'

    def __str__(self):
        return f'Profil de {self.user.username}'

    @property
    def est_abonne(self):
        if not self.a_un_abonnement:
            return False
        if self.type_abonnement == 'a_vie':
            return True
        if self.date_fin_abonnement:
            maintenant = timezone.now()
            if self.date_fin_abonnement.tzinfo is None:
                fin = self.date_fin_abonnement.replace(tzinfo=timezone.utc)
            else:
                fin = self.date_fin_abonnement
            return maintenant < fin
        return False

    @property
    def jours_restants_abonnement(self):
        if not self.est_abonne or not self.date_fin_abonnement:
            return 0
        # Gerer les datetime naive et aware
        if self.date_fin_abonnement.tzinfo is None:
            fin = self.date_fin_abonnement.replace(tzinfo=timezone.utc)
        else:
            fin = self.date_fin_abonnement
        delta = fin - timezone.now()
        return max(0, delta.days)

    @property
    def filtres_gratuits_restants(self):
        # Pour les abonnes, filtres illimites
        if self.est_abonne:
            return 999
        # Pour les non-abonnes, 5 filtres TOTAUX (pas de reset quotidien)
        return max(0, 5 - self.filtres_gratuits_utilises)

    def incrementer_filtres(self):
        # Ne pas incrementer pour les abonnes
        if self.est_abonne:
            return
        # Incrementer le compteur de filtres gratuits utilises
        if self.filtres_gratuits_utilises < 5:
            self.filtres_gratuits_utilises += 1
        self.nb_filtres_realises += 1
        self.save(update_fields=['filtres_gratuits_utilises', 'nb_filtres_realises'])

    def activer_abonnement(self, type_abonnement, duree_jours=None):
        maintenant = timezone.now()
        
        # IMPORTANT: Activer l'abonnement
        self.type_abonnement = type_abonnement
        self.a_un_abonnement = True

        # Determiner la date de fin
        nouvelle_fin = None
        
        if type_abonnement == 'mensuel':
            nouvelle_fin = maintenant + timezone.timedelta(days=30)
        elif type_abonnement == 'annuel':
            nouvelle_fin = maintenant + timezone.timedelta(days=365)
        elif type_abonnement == 'a_vie':
            nouvelle_fin = None

        if duree_jours:
            nouvelle_fin = maintenant + timezone.timedelta(days=duree_jours)

        # Prolongation si deja abonne et que l'ancienne abonnement est encore valide
        if self.date_fin_abonnement and nouvelle_fin:
            # Convertir en aware pour comparaison
            ancienne_fin = self.date_fin_abonnement
            if ancienne_fin.tzinfo is None:
                ancienne_fin = ancienne_fin.replace(tzinfo=timezone.utc)
            
            # Si l'ancien abonnement est encore valide, prolonger a partir de la fin
            if ancienne_fin > maintenant:
                if type_abonnement == 'mensuel':
                    nouvelle_fin = ancienne_fin + timezone.timedelta(days=30)
                elif type_abonnement == 'annuel':
                    nouvelle_fin = ancienne_fin + timezone.timedelta(days=365)

        self.date_fin_abonnement = nouvelle_fin

        if not self.date_debut_abonnement:
            self.date_debut_abonnement = maintenant
        
        self.save()

    def desactiver_abonnement(self):
        self.a_un_abonnement = False
        self.type_abonnement = 'gratuit'
        self.save()


class SubscriptionProduct(models.Model):
    """Produits d'abonnement disponibles"""
    TYPE_ABONNEMENT_CHOICES = [
        ('mensuel', 'Mensuel'),
        ('annuel', 'Annuel'),
        ('a_vie', 'À vie'),
        ('essai', 'Essai gratuit'),
        ('custom', 'Personnalisé'),
    ]

    nom = models.CharField(max_length=100, help_text="Nom du produit (ex: Mensuel, Essai 7 jours)")
    description = models.TextField(blank=True, help_text="Description du produit")
    type_abonnement = models.CharField(max_length=20, choices=TYPE_ABONNEMENT_CHOICES)

    # Prix
    prix = models.DecimalField(max_digits=10, decimal_places=2, help_text="Prix en devise")
    devise = models.CharField(max_length=10, default='XAF', help_text="Devise (XAF, EUR, USD...)")

    # Durée
    duree_jours = models.IntegerField(blank=True, null=True, help_text="Durée en jours (null pour à vie)")
    duree_heures = models.IntegerField(blank=True, null=True, help_text="Durée en heures (pour essais)")

    # URLs de paiement
    url_moov_money = models.URLField(blank=True, help_text="URL de paiement Moov Money avec paramètres")
    url_airtel_money = models.URLField(blank=True, help_text="URL de paiement Airtel Money avec paramètres")

    # Affichage
    est_actif = models.BooleanField(default=True, help_text="Produit visible sur le site")
    ordre_affichage = models.IntegerField(default=0, help_text="Ordre d'affichage (plus petit = en premier)")

    # Méta
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Produit d\'abonnement'
        verbose_name_plural = 'Produits d\'abonnements'
        ordering = ['ordre_affichage', 'prix']
        indexes = [
            models.Index(fields=['type_abonnement']),
            models.Index(fields=['est_actif']),
            models.Index(fields=['ordre_affichage']),
        ]

    def __str__(self):
        return f'{self.nom} - {self.prix} {self.devise}'

    @property
    def duree_affichage(self):
        """Retourne la durée formatée pour l'affichage"""
        if self.duree_heures:
            return f'{self.duree_heures} heures'
        if self.duree_jours:
            if self.duree_jours >= 365:
                annees = self.duree_jours // 365
                return f'{annees} an{"s" if annees > 1 else ""}'
            elif self.duree_jours >= 30:
                mois = self.duree_jours // 30
                return f'{mois} mois'
            else:
                return f'{self.duree_jours} jours'
        return 'Illimité'

    @property
    def est_populaire(self):
        """Marque certains produits comme populaires (à personnaliser)"""
        return self.type_abonnement == 'annuel'


class SubscriptionPayment(models.Model):
    """Historique des paiements d'abonnement"""
    TYPE_ABONNEMENT_CHOICES = [
        ('mensuel', 'Mensuel'),
        ('annuel', 'Annuel'),
        ('a_vie', 'À vie'),
    ]
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('complete', 'Complété'),
        ('echoue', 'Échoué'),
        ('rembourse', 'Remboursé'),
    ]

    # Lier à un produit
    produit = models.ForeignKey(SubscriptionProduct, on_delete=models.SET_NULL, blank=True, null=True, related_name='payments')
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    type_abonnement = models.CharField(max_length=20, choices=TYPE_ABONNEMENT_CHOICES)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    devise = models.CharField(max_length=10, default='XAF')
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    reference_transaction = models.CharField(max_length=255, unique=True)
    code_paiement = models.CharField(max_length=50, blank=True, null=True)
    telephone = models.CharField(max_length=50, blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_paiement = models.DateTimeField(blank=True, null=True)
    webhook_log = models.ForeignKey(WebhookLog, on_delete=models.SET_NULL, blank=True, null=True, related_name='payments')

    class Meta:
        verbose_name = 'Paiement abonnement'
        verbose_name_plural = 'Paiements abonnements'
        ordering = ['-date_creation']

    def __str__(self):
        return f'Paiement {self.reference_transaction} - {self.utilisateur.username}'

    def marquer_complet(self):
        self.statut = 'complete'
        self.date_paiement = timezone.now()
        self.save()
        profile = self.utilisateur.profile
        if self.produit and self.produit.duree_jours:
            profile.activer_abonnement(self.type_abonnement, duree_jours=self.produit.duree_jours)
        elif self.type_abonnement == 'mensuel':
            profile.activer_abonnement('mensuel')
        elif self.type_abonnement == 'annuel':
            profile.activer_abonnement('annuel')
        elif self.type_abonnement == 'a_vie':
            profile.activer_abonnement('a_vie')

    @property
    def est_en_retard(self):
        """Vérifie si le webhook n'a pas été traité dans les 5 minutes"""
        if not self.date_traitement:
            return (timezone.now() - self.date_reception).total_seconds() > 300
        return False
