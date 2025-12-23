# -*- coding: utf-8 -*-
"""
Middleware pour capturer et stocker les utilisateurs Telegram Mini App.
"""
from django.utils import timezone
from .models import TelegramUser


class TelegramUserMiddleware:
    """
    Middleware qui capture automatiquement les données utilisateur
    provenant de Telegram Mini App et les stocke en base de données.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Récupérer les données Telegram depuis les headers ou le body
        telegram_user = self._get_telegram_user(request)

        if telegram_user:
            # Stocker l'utilisateur Telegram dans la request pour usage ultérieur
            request.telegram_user = telegram_user
            # Ajouter au contexte de template
            request.telegram_user_data = telegram_user

        response = self.get_response(request)
        return response

    def _get_telegram_user(self, request):
        """
        Extrait les données utilisateur Telegram de la requête
        et les enregistre/mets à jour en base de données.
        """
        # Essayer de récupérer depuis différentes sources

        # 1. Depuis le header WebApp-Data (envoyé par Telegram)
        webapp_data = request.headers.get('WebApp-Data')

        # 2. Depuis le header X-Telegram-User-Data
        if not webapp_data:
            webapp_data = request.headers.get('X-Telegram-User-Data')

        # 3. Depuis un paramètre POST (pour les formulaires)
        if not webapp_data and request.method == 'POST':
            webapp_data = request.POST.get('telegram_user_data')

        # 4. Depuis un paramètre GET (pour les tests)
        if not webapp_data:
            webapp_data = request.GET.get('telegram_user_data')

        if not webapp_data:
            # Pas de données Telegram, retourner None
            return None

        # Parser les données JSON
        try:
            import json
            user_data = json.loads(webapp_data)

            # Créer ou mettre à jour l'utilisateur Telegram
            telegram_user, created = TelegramUser.get_or_create_from_webapp(user_data)

            if telegram_user:
                if not created:
                    # Incrémenter le compteur de connexions
                    telegram_user.increment_connection()

                # Log pour debugging
                print(f"[Telegram] Utilisateur {'créé' if created else 'mis à jour'}: {telegram_user}")

            return telegram_user

        except (json.JSONDecodeError, ValueError) as e:
            print(f"[Telegram] Erreur de parsing des données: {e}")
            return None
        except Exception as e:
            print(f"[Telegram] Erreur lors de la création de l'utilisateur: {e}")
            return None
