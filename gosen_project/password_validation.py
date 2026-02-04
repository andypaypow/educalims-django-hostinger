"""
Validateurs de mot de passe permissifs pour Gosen TurfFilter
Autorise tous les types de mots de passe, y compris les simples comme "1234"
"""
from django.core.exceptions import ValidationError


class MinimalPasswordValidator:
    """
    Validateur de mot de passe minimal
    N'applique aucune restriction sur le mot de passe
    """
    def validate(self, password, user=None):
        # Aucune validation - on accepte tous les mots de passe
        pass

    def get_help_text(self):
        return "Votre mot de passe peut être ce que vous voulez."
