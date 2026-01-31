from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import secrets
from ..models import AdminUser


def login_page(request):
    """Page de connexion pour les administrateurs"""
    return render(request, 'gosen/auth/login.html')


@csrf_exempt
def login_api(request):
    """API de connexion"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=405)
    
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    
    # Pour l'instant, on utilise un mot de passe fixe pour la demo
    # En production, utilisez un vrai systeme d'authentification
    if password == 'gosen2026admin':
        try:
            admin = AdminUser.objects.get(username=username, is_active=True)
            # Mettre a jour la date de derniere connexion
            admin.last_login = timezone.now()
            admin.save()
            
            response = JsonResponse({'success': True, 'redirect': '/'})
            response.set_cookie('admin_token', admin.token, max_age=7*24*3600)  # 7 jours
            return response
        except AdminUser.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Identifiants incorrects'}, status=401)
    
    return JsonResponse({'success': False, 'error': 'Mot de passe incorrect'}, status=401)


def logout(request):
    """Déconnexion"""
    response = redirect('/')
    response.delete_cookie('admin_token')
    return response


def check_auth(request):
    """Vérifie si l'utilisateur est authentifié comme admin"""
    token = request.COOKIES.get('admin_token')
    if not token:
        return JsonResponse({'is_admin': False})
    
    admin = AdminUser.verify_token(token)
    return JsonResponse({'is_admin': admin is not None, 'username': admin.username if admin else None})
