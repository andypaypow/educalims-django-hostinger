import hashlib
import uuid
from django.conf import settings


def generate_device_fingerprint(request):
    """Genere une empreinte unique pour l'appareil actuel"""
    # Utiliser plusieurs facteurs pour creer une empreinte unique
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
    accept_encoding = request.META.get('HTTP_ACCEPT_ENCODING', '')
    
    # Creer l'empreinte
    fingerprint_data = f'{user_agent}:{accept_language}:{accept_encoding}'
    fingerprint = hashlib.sha256(fingerprint_data.encode()).hexdigest()[:32]
    
    return fingerprint


def get_or_create_device_fingerprint(request, user):
    """Recupere ou cree l'empreinte d'appareil pour l'utilisateur"""
    from gosen.models import DeviceFingerprint
    
    fingerprint = generate_device_fingerprint(request)
    
    # Essayer de recuperer l'empreinte existante
    device_fingerprint, created = DeviceFingerprint.objects.get_or_create(
        user=user,
        defaults={
            'fingerprint': fingerprint,
            'user_agent': request.META.get('HTTP_USER_AGENT', '')[:255]
        }
    )
    
    return device_fingerprint, fingerprint


def is_device_authorized(request, user):
    """Verifie si l'appareil actuel est autorise pour cet utilisateur"""
    # L'admin a toujours acces
    if user.is_superuser or user.username == 'admin':
        return True
    
    # Verifier l'empreinte de l'appareil
    from gosen.models import DeviceFingerprint
    
    try:
        device_fingerprint = DeviceFingerprint.objects.get(user=user)
        current_fingerprint = generate_device_fingerprint(request)
        return device_fingerprint.fingerprint == current_fingerprint and device_fingerprint.is_active
    except DeviceFingerprint.DoesNotExist:
        return False
