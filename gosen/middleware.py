from django.utils import timezone
from django.contrib.auth.models import AnonymousUser
import json


class UserActivityMiddleware:
    """Middleware pour tracker tous les appareils (connectes et anonymes)"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Traiter la requete
        response = self.get_response(request)

        # Tracker l'activite apres traitement
        self.track_activity(request, response)

        return response

    def track_activity(self, request, response):
        """Track tous les appareils (connectes et anonymes)"""
        # Ignorer les fichiers statiques et media
        path = request.path.lower()
        if path.startswith(('/static/', '/media/')):
            return

        try:
            from .models import UserSession, ActivityLog, DeviceTracking
            
            # Toujours tracker l'appareil (meme anonyme)
            DeviceTracking.get_or_create_appareil(request)
            
            # Suite: tracker les sessions utilisateurs connectes
            user = getattr(request, 'user', None)
            if not user or isinstance(user, AnonymousUser):
                return

            # Récupérer ou créer la session utilisateur
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key

            # Récupérer l'IP
            ip_address = self.get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')

            # Mettre à jour ou créer la session
            session, created = UserSession.objects.get_or_create(
                session_key=session_key,
                defaults={
                    'user': user,
                    'ip_address': ip_address,
                    'user_agent': user_agent,
                    'est_actif': True,
                }
            )

            if not created:
                # Mettre à jour la dernière activité
                session.derniere_activite = timezone.now()
                session.est_actif = True
                session.save(update_fields=['derniere_activite', 'est_actif'])

            # Logger certaines activités spécifiques
            self.log_specific_activity(request, response, user, ip_address, user_agent)

        except Exception as e:
            # Ne pas bloquer l'application en cas d'erreur de tracking
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Erreur tracking activité: {e}')

    def log_specific_activity(self, request, response, user, ip_address, user_agent):
        """Logger les activités spécifiques (connexion, inscription, etc.)"""
        from .models import ActivityLog

        path = request.path
        action_type = None
        description = ''
        donnees = {}

        # Connexion réussie
        if path == '/auth/login/' and response.status_code == 302:
            action_type = 'connexion'
            description = f'Connexion de {user.username}'
            donnees = {'redirect_to': response.get('Location', '')}

        # Inscription
        elif '/auth/register/' in path:
            action_type = 'inscription'
            description = f'Inscription de {user.username}'

        # Déconnexion
        elif path == '/auth/logout/' and response.status_code == 302:
            action_type = 'deconnexion'
            description = f'Déconnexion de {user.username}'
            # Marquer la session comme inactive
            try:
                from .models import UserSession
                session_key = request.session.session_key
                UserSession.objects.filter(session_key=session_key).update(est_actif=False)
            except:
                pass

        # Message de contact
        elif path == '/api/contact/submit/' and response.status_code == 200:
            action_type = 'message_contact'
            description = f'Message de contact de {user.username}'

        # Logger l'activité
        if action_type:
            ActivityLog.objects.create(
                user=user,
                type_action=action_type,
                description=description,
                donnees=donnees,
                ip_address=ip_address,
                user_agent=user_agent[:500] if user_agent else ''
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
