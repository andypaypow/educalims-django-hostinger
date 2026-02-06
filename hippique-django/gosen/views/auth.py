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
            response_data = {
                'is_authenticated': True,
                'username': request.user.username,
                'email': request.user.email,
                'telephone': profile.telephone,
                'est_abonne': profile.est_abonne,
                'type_abonnement': profile.type_abonnement,
                'filtres_gratuits_restants': profile.filtres_gratuits_restants,
                'jours_restants': profile.jours_restants_abonnement,
                # Debug info
                'debug': {
                    'a_un_abonnement': profile.a_un_abonnement,
                    'date_fin_abonnement': profile.date_fin_abonnement.isoformat() if profile.date_fin_abonnement else None,
                    'timezone_now': timezone.now().isoformat(),
                }
            }
            return JsonResponse(response_data)
        except UserProfile.DoesNotExist:
            # Créer le profil s'il n'existe pas
            profile = UserProfile.objects.create(user=request.user)
            return JsonResponse({
                'is_authenticated': True,
                'username': request.user.username,
                'email': request.user.email,
                'telephone': profile.telephone,
                'est_abonne': False,
                'type_abonnement': 'gratuit',
                'filtres_gratuits_restants': 5,
                'jours_restants': 0,
            })
    return JsonResponse({
        'is_authenticated': False,
        'est_abonne': False,
        'filtres_gratuits_restants': 5,
        'telephone': None,
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


def api_debug_user(request):
    """API de diagnostic pour vérifier l'état de l'utilisateur et son abonnement"""
    from gosen.models import UserProfile, SubscriptionProduct, SubscriptionPayment, WebhookLog

    debug_info = {
        'current_user': {
            'is_authenticated': request.user.is_authenticated,
            'username': request.user.username if request.user.is_authenticated else None,
        }
    }

    if request.user.is_authenticated:
        try:
            profile = request.user.profile
            debug_info['profile'] = {
                'telephone': profile.telephone,
                'a_un_abonnement': profile.a_un_abonnement,
                'type_abonnement': profile.type_abonnement,
                'est_abonne': profile.est_abonne,
                'date_debut_abonnement': profile.date_debut_abonnement.isoformat() if profile.date_debut_abonnement else None,
                'date_fin_abonnement': profile.date_fin_abonnement.isoformat() if profile.date_fin_abonnement else None,
                'jours_restants': profile.jours_restants_abonnement,
            }

            # Récupérer les paiements
            payments = request.user.payments.all().order_by('-date_creation')[:5]
            debug_info['payments'] = [{
                'id': p.id,
                'montant': str(p.montant),
                'statut': p.statut,
                'type_abonnement': p.type_abonnement,
                'produit_nom': p.produit.nom if p.produit else None,
                'date_creation': p.date_creation.isoformat() if p.date_creation else None,
            } for p in payments]

            # Récupérer les webhooks récents
            webhooks = WebhookLog.objects.filter(telephone=profile.telephone).order_by('-date_reception')[:5]
            debug_info['webhooks'] = [{
                'id': w.id,
                'source': w.source,
                'code_paiement': w.code_paiement,
                'montant': str(w.montant) if w.montant else None,
                'statut': w.statut,
                'date_reception': w.date_reception.isoformat() if w.date_reception else None,
            } for w in webhooks]

            # Produits disponibles
            produits = SubscriptionProduct.objects.filter(est_actif=True)
            debug_info['produits_disponibles'] = [{
                'nom': p.nom,
                'prix': str(p.prix),
                'type_abonnement': p.type_abonnement,
                'duree_jours': p.duree_jours,
            } for p in produits]

        except UserProfile.DoesNotExist:
            debug_info['error'] = 'Profil utilisateur non trouvé'

    return JsonResponse(debug_info)


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


@csrf_exempt
def login_by_phone(request):
    """Connexion par numéro de téléphone (sans mot de passe)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=405)

    phone = request.POST.get('phone', '').strip()
    if not phone:
        return JsonResponse({'success': False, 'error': 'Numéro de téléphone requis'}, status=400)

    # Normaliser le numéro
    phone_normalized = phone.replace('+', '').replace(' ', '')

    # Chercher le profil par téléphone
    profile = UserProfile.objects.filter(telephone__icontains=phone_normalized).first()

    if profile and profile.est_abonne:
        # Connecter l'utilisateur
        login(request, profile.user)
        profile.derniere_connexion = timezone.now()
        profile.save(update_fields=['derniere_connexion'])

        return JsonResponse({
            'success': True,
            'redirect': '/',
            'username': profile.user.username,
            'est_abonne': True
        })

    return JsonResponse({
        'success': False,
        'error': 'Aucun abonnement trouvé pour ce numéro'
    }, status=401)


def auto_login(request, token):
    """
    Connexion automatique via token généré après paiement
    URL: /auth/auto-login/<token>/
    """
    from gosen.models import AuthToken
    import hashlib

    # Chercher le token
    auth_token = AuthToken.objects.filter(token=token).first()

    if not auth_token:
        return render(request, 'gosen/auth/login.html', {
            'error': 'Token invalide. Veuillez vous connecter avec votre numéro de téléphone.'
        })

    if not auth_token.est_valide:
        return render(request, 'gosen/auth/login.html', {
            'error': 'Token expiré ou déjà utilisé. Veuillez vous connecter avec votre numéro de téléphone.'
        })

    # Générer le device_id (fingerprint du navigateur) AVANT de traiter le profil
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
    accept_encoding = request.META.get('HTTP_ACCEPT_ENCODING', '')
    fingerprint = f"{user_agent}|{accept_language}|{accept_encoding}"
    device_id = hashlib.sha256(fingerprint.encode()).hexdigest()[:32]

    # Connecter l'utilisateur
    login(request, auth_token.user)

    # Récupérer ou créer le profil avec device_id
    try:
        profile = auth_token.user.profile
        profile.derniere_connexion = timezone.now()
        profile.device_id = device_id
        profile.save(update_fields=['derniere_connexion', 'device_id'])
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(
            user=auth_token.user,
            device_id=device_id,
            derniere_connexion=timezone.now()
        )

    # Marquer le token comme utilisé
    auth_token.marquer_utilise()

    # Rediriger vers l'accueil avec cookie
    response = redirect('/')
    # Définir le cookie pour les prochaines visites (valide 1 an)
    max_age = 365 * 24 * 60 * 60
    if profile.telephone:
        response.set_cookie(
            'user_phone',
            profile.telephone,
            max_age=max_age,
            httponly=True,
            secure=False,  # Mettre True en production avec HTTPS
            samesite='Lax'
        )
    return response


def payment_success(request):
    """
    Page de succès après paiement
    URL: /payment/success/
    Peut recevoir un token en paramètre GET pour connexion automatique
    """
    token = request.GET.get('token')

    if token:
        # Rediriger vers l'auto-login avec le token
        from django.urls import reverse
        return redirect(reverse('auto_login', kwargs={'token': token}))

    # Afficher la page de succès sans token
    return render(request, 'gosen/auth/payment_success.html', {
        'message': 'Paiement reçu avec succès ! Vous pouvez maintenant vous connecter avec votre numéro de téléphone.'
    })


def payment_cancel(request):
    """
    Page d'annulation après paiement
    URL: /payment/cancel/
    """
    return render(request, 'gosen/auth/payment_cancel.html', {
        'message': 'Paiement annulé. Vous pouvez réessayer ultérieurement.'
    })
