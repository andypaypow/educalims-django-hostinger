"""
Configuration de l'application Gosen Filter
"""
from django.apps import AppConfig


class GosenConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gosen'
    verbose_name = 'Gosen Filter'
    
    def ready(self):
        """Appeler ready pour connecter les signaux"""
        import gosen.signals  # noqa: F401
