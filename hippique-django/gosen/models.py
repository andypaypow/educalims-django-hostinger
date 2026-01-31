from django.db import models


class GosenUserProfile(models.Model):
    """Profil utilisateur pour le suivi des appareils"""
    device_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Profil utilisateur Gosen'
        verbose_name_plural = 'Profils utilisateurs Gosen'
    
    def __str__(self):
        return self.device_id


class FilterPreset(models.Model):
    """Préréglages de filtres enregistrés"""
    name = models.CharField(max_length=200)
    user_profile = models.ForeignKey(GosenUserProfile, on_delete=models.CASCADE, related_name='presets')
    config = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Préréglage de filtre'
        verbose_name_plural = 'Préréglages de filtres'
    
    def __str__(self):
        return f'{self.name} ({self.user_profile.device_id})'


class AdminUser(models.Model):
    """Utilisateurs administrateurs avec accès aux formules"""
    username = models.CharField(max_length=100, unique=True)
    token = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Administrateur'
        verbose_name_plural = 'Administrateurs'
    
    def __str__(self):
        return self.username
    
    @classmethod
    def verify_token(cls, token):
        """Vérifie si un token est valide et retourne l'utilisateur"""
        try:
            admin = cls.objects.get(token=token, is_active=True)
            return admin
        except cls.DoesNotExist:
            return None
