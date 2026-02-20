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
from django.db.models import Sum

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




@csrf_exempt
def login_phone(request):
    """API de connexion par numéro de téléphone"""
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Methode non autorisee"}, status=405)

    telephone = request.POST.get("telephone", "")

    if not telephone:
        return JsonResponse({"success": False, "error": "Numero de telephone requis"}, status=400)

    # Chercher l"utilisateur par son téléphone
    try:
        profile = UserProfile.objects.get(telephone=telephone)
        user = profile.user

        if user.is_active:
            login(request, user)

            # Mettre a jour la derniere connexion
            try:
                profile.derniere_connexion = timezone.now()
                profile.save(update_fields=["derniere_connexion"])
            except Exception:
                pass

            return JsonResponse({"success": True, "redirect": "/"})
        else:
            return JsonResponse({"success": False, "error": "Compte desactive"}, status=401)

    except UserProfile.DoesNotExist:
        return JsonResponse({"success": False, "error": "Numero de telephone non enregistre"}, status=401)


def register_page(request):
    """Page d'inscription"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            try:
                user = form.save()
                # Connecter l'utilisateur automatiquement
                login(request, user)

                # Creer l'empreinte d'appareil (sans bloquer l'inscription)
                try:
                    from gosen.utils import get_or_create_device_fingerprint
                    device_fp, fingerprint = get_or_create_device_fingerprint(request, user)
                except Exception:
                    pass  # Ignorer les erreurs de device fingerprint

                return JsonResponse({'success': True, 'redirect': '/'})
            except Exception as e:
                return JsonResponse({'success': False, 'errors': {'__all__': [str(e)]}}, status=500)
        else:
            errors = {}
            for field, errors_list in form.errors.items():
                errors[field] = [str(e) for e in errors_list]
            return JsonResponse({'success': False, 'errors': errors}, status=400)
    else:
        form = CustomUserCreationForm()

    return render(request, 'gosen/auth/register.html', {'form': form})





@login_required
def payment_success(request):
    """Page de succes de paiement"""
    return render(request, "gosen/auth/payment_success.html")

@login_required
def payment_cancel(request):
    """Page d'annulation de paiement"""
    return render(request, "gosen/auth/payment_cancel.html")


def logout_view(request):
    """Déconnexion"""
    logout(request)
    return redirect('/')




def device_not_authorized(request):
    """Page affichee quand l"utilisateur n"est pas autorise sur cet appareil"""
    return render(request, "gosen/auth/device_not_authorized.html")


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
    """Tableau de bord utilisateur avec stats admin pour le staff"""
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

    # Ajouter les stats admin si l'utilisateur est staff
    if request.user.is_staff:
        from gosen.models import UserSession, ActivityLog, UserProfile, SubscriptionPayment
        
        maintenant = timezone.now()
        aujourd_hui = maintenant.date()
        debut_mois = maintenant.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Stats utilisateurs
        total_users = User.objects.filter(is_active=True).count()
        abonnes = UserProfile.objects.filter(a_un_abonnement=True).select_related('user')
        total_abonnes = sum(1 for p in abonnes if p.est_abonne)
        
        # Sessions actives
        sessions_actives = UserSession.get_sessions_actives()
        connectes_maintenant = sessions_actives.count()
        
        # Revenus du jour et du mois
        revenus_today = SubscriptionPayment.objects.filter(
            statut='complete', date_paiement__gte=aujourd_hui
        ).aggregate(total=Sum('montant'))['total'] or 0
        
        revenus_mois = SubscriptionPayment.objects.filter(
            statut='complete', date_paiement__gte=debut_mois
        ).aggregate(total=Sum('montant'))['total'] or 0
        
        # Activités récentes
        activites_recentes = ActivityLog.objects.select_related(
            'user'
        ).order_by('-date_creation')[:10]
        
        # Sessions data
        sessions_data = []
        for session in sessions_actives[:10]:
            sessions_data.append({
                'username': session.user.username,
                'ip': str(session.ip_address),
                'duree': session.duree_session(),
            })
        
        # Ajouter au contexte
        context.update({
            'is_staff': True,
            'total_users': total_users,
            'total_abonnes': total_abonnes,
            'connectes_maintenant': connectes_maintenant,
            'revenus_today': f"{revenus_today:,.0f}".replace(',', ' '),
            'revenus_mois': f"{revenus_mois:,.0f}".replace(',', ' '),
            'activites_recentes': activites_recentes,
            'sessions_data': sessions_data,
        })
    else:
        context['is_staff'] = False

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
