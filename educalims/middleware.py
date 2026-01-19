import hashlib
import jwt
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from functools import wraps
from .models import UserProfile


class DeviceIdMiddleware:
    """Middleware pour gerer l'identifiant unique de l'appareil."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        device_id = self._get_or_create_device_id(request)
        request.device_id = device_id
        response = self.get_response(request)
        return response

    def _get_or_create_device_id(self, request):
        """Recupere le device_id depuis le cookie ou en genere un nouveau."""
        cookie_name = 'device_token'
        device_token = request.COOKIES.get(cookie_name)
        
        if device_token:
            try:
                payload = jwt.decode(
                    device_token,
                    settings.SECRET_KEY,
                    algorithms=['HS256']
                )
                return payload.get('device_id')
            except (jwt.DecodeError, jwt.ExpiredSignatureError):
                pass
        
        device_id = self._generate_device_fingerprint(request)
        return device_id

    def _generate_device_fingerprint(self, request):
        """Genere un fingerprint unique base sur User-Agent."""
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
        accept_encoding = request.META.get('HTTP_ACCEPT_ENCODING', '')
        
        fingerprint = f"{user_agent}|{accept_language}|{accept_encoding}"
        device_id = hashlib.sha256(fingerprint.encode()).hexdigest()
        
        return device_id

    @staticmethod
    def create_device_token(device_id, expiry_days=365):
        """Cree un token JWT contenant le device_id."""
        payload = {
            'device_id': device_id,
            'exp': datetime.utcnow() + timedelta(days=expiry_days),
            'iat': datetime.utcnow(),
        }
        
        token = jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm='HS256'
        )
        
        return token

    @staticmethod
    def verify_device_token(token):
        """Verifie et retourne le device_id depuis un token JWT."""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=['HS256']
            )
            return payload.get('device_id')
        except (jwt.DecodeError, jwt.ExpiredSignatureError):
            return None


def device_required(view_func):
    """Decorateur pour verifier le device_id et retourner une page HTML si non autorise."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        
        request_device_id = getattr(request, 'device_id', None)
        
        try:
            profile = request.user.profile
            registered_device_id = profile.device_id
            
            if registered_device_id and request_device_id != registered_device_id:
                # Device different - afficher une page d'erreur friendly
                from django.shortcuts import render
                return render(request, 'educalims/device_not_authorized.html', {
                    'title': 'Appareil non autorise',
                    'message': 'Cet abonnement est lie a un autre appareil.',
                    'registered_device': registered_device_id[:8] + '...',
                    'current_device': request_device_id[:8] + '...'
                }, status=403)
            
        except UserProfile.DoesNotExist:
            pass
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view
