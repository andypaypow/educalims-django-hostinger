"""
Configuration de l'application Gosen TurfFilter
"""
from django.apps import AppConfig


class GosenConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gosen'
    verbose_name = 'Gosen TurfFilter'
