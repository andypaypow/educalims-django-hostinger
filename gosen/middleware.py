import re
from django.shortcuts import render, redirect
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from urllib.parse import urlencode


class LoginRequiredMiddleware(MiddlewareMixin):
    """
    Middleware qui exige que l'utilisateur soit authentifié pour accéder à l'application.
    Redirige vers la page de connexion avec le paramètre 'next' pour revenir après connexion.
    DOIT être placé APRÈS AuthenticationMiddleware dans la liste MIDDLEWARE.
    """

    # URLs qui ne nécessitent pas d'authentification
    EXEMPT_URLS = [
        r'^/admin/?$',
        r'^/admin/.*',
        r'^/auth/login/?$',
        r'^/auth/login/phone/?$',
        r'^/auth/register/?$',
        r'^/auth/logout/?$',
        r'^/static/.*',
        r'^/media/.*',
        r'^/payment/.*',
    ]

    def __init__(self, get_response):
        self.get_response = get_response
        self.exempt_patterns = [re.compile(pattern) for pattern in self.EXEMPT_URLS]

    def is_exempt(self, path):
        """Vérifie si le chemin est exempté de l'authentification"""
        for pattern in self.exempt_patterns:
            if pattern.match(path):
                return True
        return False

    def __call__(self, request):
        """Traite chaque requête pour vérifier l'authentification"""

        # Si l'utilisateur est déjà authentifié, passer au middleware suivant
        if request.user.is_authenticated:
            return self.get_response(request)

        # Si le chemin est exempté, passer au middleware suivant
        if self.is_exempt(request.path):
            return self.get_response(request)

        # Rediriger vers la page de connexion avec le paramètre 'next'
        login_url = settings.LOGIN_URL
        next_url = request.path
        redirect_url = f"{login_url}?{urlencode({'next': next_url})}"
        return redirect(redirect_url)


class DeviceVerificationMiddleware(MiddlewareMixin):
    """Middleware pour verifier que l'utilisateur utilise le bon appareil"""

    EXEMPT_URLS = [
        r'^/admin/?$',
        r'^/admin/.*',
        r'^/auth/login/?$',
        r'^/auth/login/phone/?$',
        r'^/auth/register/?$',
        r'^/auth/logout/?$',
        r'^/static/.*',
        r'^/media/.*',
        r'^/payment/.*',
        r'^/auth/device-not-authorized/.*',
    ]

    def __init__(self, get_response):
        self.get_response = get_response
        self.exempt_patterns = [re.compile(pattern) for pattern in self.EXEMPT_URLS]

    def is_exempt(self, path):
        for pattern in self.exempt_patterns:
            if pattern.match(path):
                return True
        return False

    def __call__(self, request):
        response = self.get_response(request)

        if not request.user.is_authenticated:
            return response

        if self.is_exempt(request.path):
            return response

        if request.user.is_superuser or request.user.username == 'admin':
            return response

        try:
            from gosen.models import UserProfile, DeviceFingerprint
            from gosen.utils import is_device_authorized, generate_device_fingerprint, get_or_create_device_fingerprint

            profile = request.user.profile

            if not profile.est_abonne:
                return response

            device_fingerprint_exists = DeviceFingerprint.objects.filter(user=request.user).exists()

            if not device_fingerprint_exists:
                device_fp, fingerprint = get_or_create_device_fingerprint(request, request.user)
                return response

            if not is_device_authorized(request, request.user):
                request.session['unauthorized_device'] = True
                request.session['current_fingerprint'] = generate_device_fingerprint(request)

                if request.path != '/auth/device-not-authorized/':
                    return redirect('/auth/device-not-authorized/')

        except Exception as e:
            import logging
            logging.error(f'Erreur middleware: {e}')
            pass

        return response
