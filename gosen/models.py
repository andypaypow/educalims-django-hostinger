from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


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

    @property
    def nom_produit_abonnement(self):
        """Retourne le nom du produit d'abonnement actuel"""
        if not self.est_abonne:
            return "Gratuit"
        # Chercher le paiement le plus recent pour cet utilisateur
        from gosen.models import SubscriptionPayment
        dernier_paiement = SubscriptionPayment.objects.filter(
            utilisateur=self.user,
            statut='complete'
        ).order_by('-date_paiement').first()
        if dernier_paiement and dernier_paiement.produit:
            return dernier_paiement.produit.nom
        # Fallback sur le type d'abonnement
        type_mapping = {
            'mensuel': 'Abonnement Mensuel',
            'annuel': 'Abonnement Annuel',
            'a_vie': 'Abonnement à Vie',
        }
        return type_mapping.get(self.type_abonnement, 'Gratuit')

    @property
    def date_fin_abonnement_formattee(self):
        """Retourne la date de fin formatée avec heure si < 24h"""
        if not self.est_abonne:
            return "N/A"
        if self.type_abonnement == 'a_vie':
            return "Illimité"
        if not self.date_fin_abonnement:
            return "N/A"
        # Gerer les datetime naive et aware
        if self.date_fin_abonnement.tzinfo is None:
            fin = self.date_fin_abonnement.replace(tzinfo=timezone.utc)
        else:
            fin = self.date_fin_abonnement
        maintenant = timezone.now()
        delta = fin - maintenant
        # Si moins de 24 heures restantes ou durée totale < 24h, afficher l'heure
        if delta.total_seconds() < 86400 or delta.total_seconds() > -86400:
            return fin.strftime('%d/%m/%Y à %H:%M:%S')
        return fin.strftime('%d/%m/%Y')

    def incrementer_filtres(self):
        # Ne pas incrementer pour les abonnes
        if self.est_abonne:
            return
        # Incrementer le compteur de filtres gratuits utilises
        if self.filtres_gratuits_utilises < 5:
            self.filtres_gratuits_utilises += 1
        self.nb_filtres_realises += 1
        self.save(update_fields=['filtres_gratuits_utilises', 'nb_filtres_realises'])

    def activer_abonnement(self, type_abonnement, duree_jours=None, duree_heures=None):
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

        if duree_heures:
            nouvelle_fin = maintenant + timezone.timedelta(hours=duree_heures)
        elif duree_jours:
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


class DeviceFingerprint(models.Model):
    """Empreinte d'appareil pour lier l'abonnement a un appareil specifique"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='device_fingerprint')
    fingerprint = models.CharField(max_length=255, unique=True, db_index=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Empreinte d\'appareil'
        verbose_name_plural = 'Empreintes d\'appareils'
    
    def __str__(self):
        return f'{self.user.username} - {self.fingerprint[:8]}...'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)



class Partner(models.Model):
    """Modèle pour les partenaires (logos et liens)"""
    nom = models.CharField(max_length=200, blank=True, null=True, default='', help_text="Nom du partenaire (optionnel)")
    logo = models.ImageField(upload_to="partners/", blank=True, null=True, help_text="Logo du partenaire")
    lien = models.URLField(blank=True, help_text="Lien vers le site du partenaire")
    description = models.TextField(blank=True, help_text="Description du partenaire")
    ordre_affichage = models.IntegerField(default=0, help_text="Ordre d'affichage (plus petit = en premier)")
    est_actif = models.BooleanField(default=True, help_text="Partenaire visible sur le site")
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Partenaire"
        verbose_name_plural = "Partenaires"
        ordering = ["ordre_affichage", "nom"]

    def __str__(self):
        return self.nom or "Partenaire sans nom"


class ContactMessage(models.Model):
    """Modèle pour les messages de contact des utilisateurs"""
    TYPE_DEMANDE_CHOICES = [
        ("filtre", "Demande de filtre supplémentaire"),
        ("support", "Support technique"),
        ("partenariat", "Proposition de partenariat"),
        ("autre", "Autre"),
    ]

    nom = models.CharField(max_length=200, help_text="Nom de l'utilisateur")
    email = models.EmailField(help_text="Email de contact")
    type_demande = models.CharField(max_length=20, choices=TYPE_DEMANDE_CHOICES, default="autre")
    message = models.TextField(help_text="Message de l'utilisateur")
    date_creation = models.DateTimeField(auto_now_add=True)
    est_traite = models.BooleanField(default=False, help_text="Message traité par l'admin")

    class Meta:
        verbose_name = "Message de contact"
        verbose_name_plural = "Messages de contact"
        ordering = ["-date_creation"]

    def __str__(self):
        return f"Message de {self.nom} - {self.type_demande}"


class BacktestAnalysis(models.Model):
    """Modèle pour sauvegarder les analyses de backtest des utilisateurs"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='backtest_analyses')
    
    # Configuration initiale
    num_partants = models.IntegerField(help_text="Nombre de partants")
    taille_combinaison = models.IntegerField(help_text="Taille des combinaisons")
    
    # Pronostics saisis (JSON)
    pronostics = models.JSONField(help_text="Groupes de pronostics saisis")
    
    # Critères de filtrage (JSON)
    criteres_filtres = models.JSONField(help_text="Critères de filtrage utilisés")
    
    # Arrivée testée
    arrivee = models.JSONField(help_text="Arrivée testée (liste de numéros)")
    
    # Résultats du backtest
    combinaisons_filtrees = models.JSONField(help_text="Combinaisons après filtrage")
    combinaisons_trouvees = models.JSONField(help_text="Combinaisons contenant l'arrivée")
    nombre_trouvees = models.IntegerField(default=0, help_text="Nombre de combinaisons trouvées")
    
    # Rapport complet
    rapport = models.TextField(help_text="Rapport complet du backtest")
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    nom = models.CharField(max_length=200, blank=True, default='', help_text="Nom personnalisé de l'analyse")

    class Meta:
        verbose_name = "Analyse de Backtest"
        verbose_name_plural = "Analyses de Backtest"
        ordering = ["-date_creation"]

    def __str__(self):
        arrivee_str = ', '.join(map(str, self.arrivee)) if self.arrivee else 'N/A'
        return f'Backtest {self.user.username} - Arrivée [{arrivee_str}] - {self.date_creation.strftime("%d/%m/%Y %H:%M")}'


# ============================================
# MODÈLES POUR DASHBOARD ADMIN
# ============================================

class UserSession(models.Model):
    """Track les sessions utilisateurs actives pour le dashboard admin"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=255, unique=True, db_index=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    date_connexion = models.DateTimeField(auto_now_add=True)
    derniere_activite = models.DateTimeField(auto_now=True)
    est_actif = models.BooleanField(default=True)
    device_info = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = 'Session Utilisateur'
        verbose_name_plural = 'Sessions Utilisateurs'
        ordering = ['-derniere_activite']
        indexes = [
            models.Index(fields=['session_key']),
            models.Index(fields=['est_actif']),
            models.Index(fields=['-derniere_activite']),
        ]

    def __str__(self):
        return f'{self.user.username} - {self.ip_address}'

    def duree_session(self):
        """Retourne la durée de session formatée"""
        delta = timezone.now() - self.date_connexion
        heures = int(delta.total_seconds() // 3600)
        minutes = int((delta.total_seconds() % 3600) // 60)
        if heures > 0:
            return f'{heures}h {minutes}min'
        return f'{minutes}min'

    @classmethod
    def nettoyer_sessions_inactives(cls):
        """Marque comme inactives les sessions sans activité depuis 30 minutes"""
        seuil = timezone.now() - timezone.timedelta(minutes=30)
        cls.objects.filter(est_actif=True, derniere_activite__lt=seuil).update(est_actif=False)

    @classmethod
    def get_sessions_actives(cls):
        """Retourne les sessions actives"""
        cls.nettoyer_sessions_inactives()
        return cls.objects.filter(est_actif=True).select_related('user')


class ActivityLog(models.Model):
    """Journal d'activité global pour le dashboard admin"""
    TYPE_ACTION_CHOICES = [
        ('connexion', 'Connexion'),
        ('deconnexion', 'Déconnexion'),
        ('inscription', 'Inscription'),
        ('filtre_realise', 'Filtre réalisé'),
        ('abonnement_souscrit', 'Abonnement souscrit'),
        ('paiement_recu', 'Paiement reçu'),
        ('backtest_sauvegarde', 'Backtest sauvegardé'),
        ('message_contact', 'Message de contact'),
        ('erreur', 'Erreur système'),
        ('autre', 'Autre'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='activities')
    type_action = models.CharField(max_length=50, choices=TYPE_ACTION_CHOICES)
    description = models.TextField(blank=True)
    donnees = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = 'Log d\'activité'
        verbose_name_plural = 'Logs d\'activité'
        ordering = ['-date_creation']
        indexes = [
            models.Index(fields=['-date_creation']),
            models.Index(fields=['type_action']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        user_str = self.user.username if self.user else 'Anonyme'
        return f'{user_str} - {self.get_type_action_display()} - {self.date_creation.strftime("%d/%m/%Y %H:%M")}'

    @classmethod
    def logger(cls, user, type_action, description='', donnees=None, request=None):
        """Méthode helper pour logger une activité"""
        ip = None
        ua = ''
        if request:
            ip = cls.get_client_ip(request)
            ua = request.META.get('HTTP_USER_AGENT', '')[:500]
        
        cls.objects.create(
            user=user,
            type_action=type_action,
            description=description,
            donnees=donnees or {},
            ip_address=ip,
            user_agent=ua
        )

    @staticmethod
    def get_client_ip(request):
        """Récupère l'IP réelle du client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
