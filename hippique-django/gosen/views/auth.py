from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


def login_page(request):
    """Page de connexion pour les administrateurs"""
    return render(request, 'gosen/auth/login.html')


@csrf_exempt
def login_api(request):
    """API de connexion avec authentification Django standard"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=405)
    
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    
    # Authentification Django standard
    user = authenticate(request, username=username, password=password)
    
    if user is not None and user.is_active:
        login(request, user)
        return JsonResponse({'success': True, 'redirect': '/'})
    
    return JsonResponse({'success': False, 'error': 'Identifiants incorrects'}, status=401)


def logout_view(request):
    """Déconnexion"""
    logout(request)
    return redirect('/')


def check_auth(request):
    """Vérifie si l'utilisateur est authentifié"""
    return JsonResponse({
        'is_admin': request.user.is_authenticated,
        'username': request.user.username if request.user.is_authenticated else None
    })
