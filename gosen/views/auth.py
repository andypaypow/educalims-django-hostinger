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
        from gosen.models import UserSession, ActivityLog, UserProfile, SubscriptionPayment, DeviceTracking
        
        maintenant = timezone.now()
        aujourd_hui = maintenant.date()
        debut_mois = maintenant.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Stats utilisateurs
        total_users = User.objects.filter(is_active=True).count()
        abonnes = UserProfile.objects.filter(a_un_abonnement=True).select_related('user')
        total_abonnes = sum(1 for p in abonnes if p.est_abonne)
        
        # Sessions utilisateurs connectes
        sessions_actives = UserSession.get_sessions_actives()
        connectes_maintenant = sessions_actives.count()
        
        # TOUS les appareils actifs (anonymes + connectes)
        appareils_actifs = DeviceTracking.get_appareils_actifs()
        total_appareils_actifs = appareils_actifs.count()
        
        # Appareils anonymes actifs
        anonymes_actifs = appareils_actifs.filter(user__isnull=True).count()
        
        # STATISTIQUES PAR JOUR (7 derniers jours)
        from django.db.models import Count
        from datetime import timedelta
        
        stats_par_jour = []
        for i in range(7):
            jour = maintenant - timedelta(days=i)
            jour_debut = jour.replace(hour=0, minute=0, second=0, microsecond=0)
            jour_fin = jour.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            # Appareils uniques ce jour-la
            appareils_jour = DeviceTracking.objects.filter(
                premiere_visite__gte=jour_debut,
                premiere_visite__lte=jour_fin
            ).count()
            
            # Visites totales ce jour-la
            visites_jour = DeviceTracking.objects.filter(
                derniere_activite__gte=jour_debut,
                derniere_activite__lte=jour_fin
            ).aggregate(total=Sum('nombre_visites'))['total'] or 0
            
            stats_par_jour.append({
                'date': jour.strftime('%d/%m'),
                'appareils_uniques': appareils_jour,
                'visites': visites_jour,
            })
        
        # Inverser pour avoir du plus recent au plus ancien
        stats_par_jour = list(reversed(stats_par_jour))
        
        # STATISTIQUES PAR SEMAINE (4 dernieres semaines)
        stats_par_semaine = []
        for i in range(4):
            # Debut de la semaine (lundi)
            debut_semaine = maintenant - timedelta(weeks=i, days=maintenant.weekday())
            debut_semaine = debut_semaine.replace(hour=0, minute=0, second=0, microsecond=0)
            # Fin de la semaine (dimanche)
            fin_semaine = debut_semaine + timedelta(days=6, hours=23, minutes=59, seconds=59)
            
            appareils_semaine = DeviceTracking.objects.filter(
                premiere_visite__gte=debut_semaine,
                premiere_visite__lte=fin_semaine
            ).count()
            
            visites_semaine = DeviceTracking.objects.filter(
                derniere_activite__gte=debut_semaine,
                derniere_activite__lte=fin_semaine
            ).aggregate(total=Sum('nombre_visites'))['total'] or 0
            
            stats_par_semaine.append({
                'semaine': f"S{4-i}",
                'date': debut_semaine.strftime('%d/%m'),
                'appareils_uniques': appareils_semaine,
                'visites': visites_semaine,
            })
        
        # STATISTIQUES PAR MOIS (6 derniers mois)
        stats_par_mois = []
        for i in range(6):
            debut_mois_stat = (maintenant.replace(day=1) - timedelta(days=i*30)).replace(day=1)
            if i > 0:
                from calendar import monthrange
                dernier_jour = monthrange(debut_mois_stat.year, debut_mois_stat.month)[1]
                fin_mois_stat = debut_mois_stat.replace(day=dernier_jour, hour=23, minute=59, second=59)
            else:
                fin_mois_stat = maintenant
            
            appareils_mois = DeviceTracking.objects.filter(
                premiere_visite__gte=debut_mois_stat,
                premiere_visite__lte=fin_mois_stat
            ).count()
            
            visites_mois = DeviceTracking.objects.filter(
                derniere_activite__gte=debut_mois_stat,
                derniere_activite__lte=fin_mois_stat
            ).aggregate(total=Sum('nombre_visites'))['total'] or 0
            
            stats_par_mois.append({
                'mois': debut_mois_stat.strftime('%b'),
                'annee': debut_mois_stat.year,
                'appareils_uniques': appareils_mois,
                'visites': visites_mois,
            })
        
        stats_par_mois = list(reversed(stats_par_mois))
        
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
        
        # Sessions data (utilisateurs connectes)
        sessions_data = []
        for session in sessions_actives[:10]:
            sessions_data.append({
                'username': session.user.username,
                'ip': str(session.ip_address),
                'duree': session.duree_session(),
            })
        
        # TOUS les appareils actifs (anonymes + connectes)
        appareils_data = []
        for appareil in appareils_actifs[:20]:
            appareils_data.append({
                'username': appareil.user.username if appareil.user else 'Anonyme',
                'ip': str(appareil.ip_address),
                'duree': appareil.duree_session(),
                'visites': appareil.nombre_visites,
                'user_agent': appareil.user_agent[:80] if appareil.user_agent else 'N/A',
            })
        
        # Ajouter au contexte
        context.update({
            'is_staff': True,
            'total_users': total_users,
            'total_abonnes': total_abonnes,
            'connectes_maintenant': connectes_maintenant,
            'total_appareils_actifs': total_appareils_actifs,
            'anonymes_actifs': anonymes_actifs,
            'revenus_today': f"{revenus_today:,.0f}".replace(',', ' '),
            'revenus_mois': f"{revenus_mois:,.0f}".replace(',', ' '),
            'activites_recentes': activites_recentes,
            'sessions_data': sessions_data,
            'appareils_data': appareils_data,
            'stats_par_jour': stats_par_jour,
            'stats_par_semaine': stats_par_semaine,
            'stats_par_mois': stats_par_mois,
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


@login_required
def api_stats_filter(request):
    """API pour recuperer les stats filtrees par periode"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Non autorise'}, status=403)
    
    import calendar
    from django.http import JsonResponse
    
    periode = request.GET.get('periode', 'jour')  # jour, semaine, mois
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    
    from gosen.models import DeviceTracking
    from django.db.models import Sum, Count
    from django.utils import timezone
    from datetime import timedelta, datetime
    
    # Parser les dates
    if date_debut:
        debut = datetime.strptime(date_debut, '%Y-%m-%d')
        debut = timezone.make_aware(debut)
    else:
        debut = timezone.now()
    
    if date_fin:
        fin = datetime.strptime(date_fin, '%Y-%m-%d')
        fin = timezone.make_aware(fin)
        fin = fin.replace(hour=23, minute=59, second=59)
    else:
        fin = timezone.now()
    
    # Generer les stats selon la periode
    stats = []
    
    if periode == 'jour':
        # Stats par jour
        delta = (fin - debut).days + 1
        for i in range(delta):
            jour = debut + timedelta(days=i)
            jour_debut = jour.replace(hour=0, minute=0, second=0, microsecond=0)
            jour_fin = jour.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            appareils = DeviceTracking.objects.filter(
                premiere_visite__gte=jour_debut,
                premiere_visite__lte=jour_fin
            ).count()
            
            visites = DeviceTracking.objects.filter(
                derniere_activite__gte=jour_debut,
                derniere_activite__lte=jour_fin
            ).aggregate(total=Sum('nombre_visites'))['total'] or 0
            
            stats.append({
                'date': jour.strftime('%d/%m/%Y'),
                'date_raw': jour.strftime('%Y-%m-%d'),
                'appareils_uniques': appareils,
                'visites': visites,
            })
    
    elif periode == 'semaine':
        # Stats par semaine
        delta = (fin - debut).days // 7 + 1
        for i in range(delta):
            debut_semaine = debut + timedelta(weeks=i)
            debut_semaine = debut_semaine - timedelta(days=debut_semaine.weekday())
            debut_semaine = debut_semaine.replace(hour=0, minute=0, second=0, microsecond=0)
            
            fin_semaine = debut_semaine + timedelta(days=6, hours=23, minutes=59, seconds=59)
            
            appareils = DeviceTracking.objects.filter(
                premiere_visite__gte=debut_semaine,
                premiere_visite__lte=fin_semaine
            ).count()
            
            visites = DeviceTracking.objects.filter(
                derniere_activite__gte=debut_semaine,
                derniere_activite__lte=fin_semaine
            ).aggregate(total=Sum('nombre_visites'))['total'] or 0
            
            stats.append({
                'semaine': f'S{i+1}',
                'du': debut_semaine.strftime('%d/%m'),
                'au': fin_semaine.strftime('%d/%m'),
                'debut_raw': debut_semaine.strftime('%Y-%m-%d'),
                'fin_raw': fin_semaine.strftime('%Y-%m-%d'),
                'appareils_uniques': appareils,
                'visites': visites,
            })
    
    elif periode == 'mois':
        # Stats par mois
        current = debut.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        while current <= fin:
            dernier_jour = calendar.monthrange(current.year, current.month)[1]
            fin_mois = current.replace(day=dernier_jour, hour=23, minute=59, second=59)
            
            appareils = DeviceTracking.objects.filter(
                premiere_visite__gte=current,
                premiere_visite__lte=fin_mois
            ).count()
            
            visites = DeviceTracking.objects.filter(
                derniere_activite__gte=current,
                derniere_activite__lte=fin_mois
            ).aggregate(total=Sum('nombre_visites'))['total'] or 0
            
            stats.append({
                'mois': current.strftime('%b'),
                'annee': current.year,
                'appareils_uniques': appareils,
                'visites': visites,
            })
            
            # Passer au mois suivant
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)
    
    return JsonResponse({
        'success': True,
        'stats': stats,
        'periode': periode,
    })


@login_required
def api_stats_details(request):
    """API pour recuperer les details des appareils pour une periode"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Non autorise'}, status=403)
    
    from gosen.models import DeviceTracking
    from django.utils import timezone
    from datetime import datetime, timedelta
    
    periode = request.GET.get('periode')
    details = []
    
    if periode == 'jour':
        date_str = request.GET.get('date')
        if date_str:
            date = datetime.strptime(date_str, '%Y-%m-%d')
            date = timezone.make_aware(date)
            debut = date.replace(hour=0, minute=0, second=0, microsecond=0)
            fin = date.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            devices = DeviceTracking.objects.filter(
                derniere_activite__gte=debut,
                derniere_activite__lte=fin
            ).order_by('-derniere_activite')
            
            for d in devices:
                details.append({
                    'ip_address': str(d.ip_address),
                    'user_agent': d.user_agent[:100] if d.user_agent else 'N/A',
                    'nombre_visites': d.nombre_visites,
                    'nombre_pages_vues': d.nombre_pages_vues,
                })
    
    elif periode == 'semaine':
        debut_str = request.GET.get('debut')
        fin_str = request.GET.get('fin')
        if debut_str and fin_str:
            debut = datetime.strptime(debut_str, '%Y-%m-%d')
            debut = timezone.make_aware(debut)
            fin = datetime.strptime(fin_str, '%Y-%m-%d')
            fin = timezone.make_aware(fin)
            fin = fin.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            devices = DeviceTracking.objects.filter(
                derniere_activite__gte=debut,
                derniere_activite__lte=fin
            ).order_by('-derniere_activite')
            
            for d in devices:
                details.append({
                    'ip_address': str(d.ip_address),
                    'user_agent': d.user_agent[:100] if d.user_agent else 'N/A',
                    'nombre_visites': d.nombre_visites,
                    'nombre_pages_vues': d.nombre_pages_vues,
                })
    
    elif periode == 'mois':
        mois = request.GET.get('mois')
        annee = request.GET.get('annee')
        if mois and annee:
            mois_num = ['janvier', 'fevrier', 'mars', 'avril', 'mai', 'juin', 
                       'juillet', 'aout', 'septembre', 'octobre', 'novembre', 'decembre'].index(mois.lower()) + 1
            debut = datetime(int(annee), mois_num, 1)
            debut = timezone.make_aware(debut)
            
            # Dernier jour du mois
            if mois_num == 12:
                fin = datetime(int(annee) + 1, 1, 1) - timedelta(days=1)
            else:
                fin = datetime(int(annee), mois_num + 1, 1) - timedelta(days=1)
            
            fin = timezone.make_aware(fin)
            fin = fin.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            devices = DeviceTracking.objects.filter(
                derniere_activite__gte=debut,
                derniere_activite__lte=fin
            ).order_by('-derniere_activite')
            
            for d in devices:
                details.append({
                    'ip_address': str(d.ip_address),
                    'user_agent': d.user_agent[:100] if d.user_agent else 'N/A',
                    'nombre_visites': d.nombre_visites,
                    'nombre_pages_vues': d.nombre_pages_vues,
                })
    
    return JsonResponse({
        'success': True,
        'details': details[:100],  # Limiter a 100 resultats
    })
