"""
Vues d'authentification et de gestion des utilisateurs
Utilise le modèle User natif de Django (django.contrib.auth.models.User)
"""
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction, IntegrityError

from gosen.forms import CustomUserCreationForm, UserProfileForm, SubscriptionForm
from gosen.models import UserProfile, SubscriptionPayment


def login_page(request):
    """Page de connexion pour les utilisateurs"""
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

        # S'assurer que le profil existe
        try:
            profile = user.profile
        except UserProfile.DoesNotExist:
            # Créer le profil s'il n'existe pas
            profile = UserProfile.objects.create(user=user)

        # Mettre à jour la dernière connexion
        try:
            profile.derniere_connexion = timezone.now()
            profile.save(update_fields=['derniere_connexion'])
        except Exception:
            pass  # Ignorer les erreurs de mise à jour

        return JsonResponse({'success': True, 'redirect': '/'})

    return JsonResponse({'success': False, 'error': 'Identifiants incorrects'}, status=401)


def register_page(request):
    """Page d'inscription"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                # Connecter l'utilisateur automatiquement
                login(request, user)
                return JsonResponse({'success': True, 'redirect': '/'})
            except IntegrityError:
                return JsonResponse({'success': False, 'errors': {'__all__': ['Ce nom d\'utilisateur existe déjà.']}}, status=400)
            except Exception as e:
                return JsonResponse({'success': False, 'errors': {'__all__': [str(e)]}}, status=400)
        else:
            errors = {}
            for field, errors_list in form.errors.items():
                errors[field] = [str(e) for e in errors_list]
            return JsonResponse({'success': False, 'errors': errors}, status=400)
    else:
        form = CustomUserCreationForm()

    return render(request, 'gosen/auth/register.html', {'form': form})


def logout_view(request):
    """Déconnexion"""
    logout(request)
    return redirect('/')


def check_auth(request):
    """Vérifie si l'utilisateur est authentifié"""
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
            return JsonResponse({
                'is_authenticated': True,
                'username': request.user.username,
                'email': request.user.email,
                'est_abonne': profile.est_abonne,
                'type_abonnement': profile.type_abonnement,
                'filtres_gratuits_restants': profile.filtres_gratuits_restants,
                'jours_restants': profile.jours_restants_abonnement,
            })
        except UserProfile.DoesNotExist:
            # Créer le profil s'il n'existe pas
            profile = UserProfile.objects.create(user=request.user)
            return JsonResponse({
                'is_authenticated': True,
                'username': request.user.username,
                'email': request.user.email,
                'est_abonne': False,
                'type_abonnement': 'gratuit',
                'filtres_gratuits_restants': 5,
                'jours_restants': 0,
            })
    return JsonResponse({
        'is_authenticated': False,
        'est_abonne': False,
        'filtres_gratuits_restants': 5,
    })


@login_required
def profile_page(request):
    """Page de profil utilisateur"""
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)

    payments = request.user.payments.all().order_by('-date_creation')[:10]

    context = {
        'profile': profile,
        'payments': payments,
    }
    return render(request, 'gosen/auth/profile.html', context)


@login_required
def profile_edit(request):
    """Modifier le profil utilisateur"""
    if request.method == 'POST':
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=request.user)

        form = UserProfileForm(request.POST, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Profil mis à jour'})
        else:
            return JsonResponse({'success': False, 'errors': dict(form.errors)}, status=400)
    else:
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=request.user)

        form = UserProfileForm(instance=profile, user=request.user)

    return render(request, 'gosen/auth/profile_edit.html', {'form': form})


@login_required
def subscription_page(request):
    """Page d'abonnement"""
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)

    payments = request.user.payments.all().order_by('-date_creation')[:10]

    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            type_abonnement = form.cleaned_data['type_abonnement']
            telephone = form.cleaned_data['telephone']

            # Créer un paiement en attente
            payment = SubscriptionPayment.objects.create(
                utilisateur=request.user,
                type_abonnement=type_abonnement,
                montant=get_montant_abonnement(type_abonnement),
                telephone=telephone,
                reference_transaction=f'PENDING-{timezone.now().timestamp()}',
                statut='en_attente'
            )

            # Rediriger vers la page de paiement
            return JsonResponse({
                'success': True,
                'payment_id': payment.id,
                'redirect': f'/payment/initiate/{payment.id}/'
            })
        else:
            return JsonResponse({'success': False, 'errors': dict(form.errors)}, status=400)
    else:
        form = SubscriptionForm()

    context = {
        'form': form,
        'profile': profile,
        'payments': payments,
        'prix_mensuel': 5000,
        'prix_annuel': 50000,
        'prix_vie': 150000,
    }
    return render(request, 'gosen/auth/subscription.html', context)


@login_required
def dashboard_page(request):
    """Tableau de bord utilisateur"""
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)

    recent_payments = request.user.payments.all().order_by('-date_creation')[:5]

    context = {
        'profile': profile,
        'recent_payments': recent_payments,
        'total_filtres': profile.nb_filtres_realises,
        'est_abonne': profile.est_abonne,
    }
    return render(request, 'gosen/auth/dashboard.html', context)


def get_montant_abonnement(type_abonnement):
    """Retourne le montant d'un abonnement"""
    montants = {
        'mensuel': 5000,
        'annuel': 50000,
        'a_vie': 150000,
    }
    return montants.get(type_abonnement, 5000)


# API pour vérifier les filtres restants
def check_filters_remaining(request):
    """API pour vérifier le nombre de filtres restants"""
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=request.user)

        return JsonResponse({
            'filtres_restants': profile.filtres_gratuits_restants if not profile.est_abonne else 999,
            'est_abonne': profile.est_abonne,
        })
    return JsonResponse({
        'filtres_restants': 5,
        'est_abonne': False,
    })


@login_required
def increment_filter_count(request):
    """Incrémente le compteur de filtres après utilisation"""
    if request.method == 'POST':
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=request.user)

        if not profile.est_abonne:
            if profile.filtres_gratuits_restants > 0:
                profile.incrementer_filtres()
                return JsonResponse({'success': True, 'filtres_restants': profile.filtres_gratuits_restants})
            else:
                return JsonResponse({'success': False, 'error': 'Limite atteinte', 'redirect': '/auth/subscription/'})
        return JsonResponse({'success': True, 'filtres_restants': 999})
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=405)
