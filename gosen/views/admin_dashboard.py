"""
Vues du dashboard admin pour le suivi des utilisateurs et des statistiques
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db.models import Count, Sum, Q, F
from django.utils import timezone
from datetime import timedelta, datetime

from gosen.models import (
    UserSession, ActivityLog, UserProfile, SubscriptionPayment,
    WebhookLog, BacktestAnalysis, ContactMessage
)


@staff_member_required
def admin_dashboard(request):
    """Dashboard admin avec statistiques en temps réel"""

    # Date actuelle
    maintenant = timezone.now()
    aujourd_hui = maintenant.date()
    debut_mois = maintenant.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    debut_annee = maintenant.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

    # STATISTIQUES UTILISATEURS
    total_users = User.objects.filter(is_active=True).count()
    
    # Abonnés vs Gratuits
    abonnes = UserProfile.objects.filter(a_un_abonnement=True).select_related('user')
    total_abonnes = sum(1 for p in abonnes if p.est_abonne)
    total_gratuits = total_users - total_abonnes

    # Nouveaux utilisateurs
    nouveaux_today = User.objects.filter(is_active=True, date_joined__gte=aujourd_hui).count()
    nouveaux_mois = User.objects.filter(is_active=True, date_joined__gte=debut_mois).count()
    nouveaux_annee = User.objects.filter(is_active=True, date_joined__gte=debut_annee).count()

    # SESSIONS ACTIVES
    sessions_actives = UserSession.get_sessions_actives()
    connectes_maintenant = sessions_actives.count()

    # Détail des sessions actives
    sessions_data = []
    for session in sessions_actives[:20]:
        sessions_data.append({
            'username': session.user.username,
            'email': session.user.email or 'N/A',
            'ip': str(session.ip_address),
            'duree': session.duree_session(),
            'connexion': session.date_connexion.strftime('%H:%M'),
            'user_agent': session.user_agent[:100] if session.user_agent else 'N/A',
        })

    # ABONNEMENTS PAR TYPE
    abonnements_par_type = {}
    for p in UserProfile.objects.filter(a_un_abonnement=True):
        if p.est_abonne:
            type_abo = p.get_type_abonnement_display()
            abonnements_par_type[type_abo] = abonnements_par_type.get(type_abo, 0) + 1

    # Abonnements expirant bientôt
    expiration_proche = []
    seuil_expiration = maintenant + timedelta(days=7)
    for p in UserProfile.objects.filter(a_un_abonnement=True):
        if p.est_abonne and p.date_fin_abonnement:
            if p.date_fin_abonnement < seuil_expiration and p.type_abonnement != 'a_vie':
                expiration_proche.append({
                    'username': p.user.username,
                    'type': p.get_type_abonnement_display(),
                    'fin': p.date_fin_abonnement_formattee,
                    'jours': p.jours_restants_abonnement,
                })

    # REVENUS
    paiements_today = SubscriptionPayment.objects.filter(
        statut='complete', date_paiement__gte=aujourd_hui
    ).aggregate(total=Sum('montant'))['total'] or 0

    paiements_mois = SubscriptionPayment.objects.filter(
        statut='complete', date_paiement__gte=debut_mois
    ).aggregate(total=Sum('montant'))['total'] or 0

    paiements_annee = SubscriptionPayment.objects.filter(
        statut='complete', date_paiement__gte=debut_annee
    ).aggregate(total=Sum('montant'))['total'] or 0

    # Derniers paiements
    derniers_paiements = SubscriptionPayment.objects.filter(
        statut='complete'
    ).select_related('utilisateur', 'produit').order_by('-date_paiement')[:10]

    paiements_data = []
    for p in derniers_paiements:
        paiements_data.append({
            'id': p.id,
            'username': p.utilisateur.username,
            'produit': p.produit.nom if p.produit else p.get_type_abonnement_display(),
            'montant': f"{p.montant:,} {p.devise}".replace(',', ' '),
            'date': p.date_paiement.strftime('%d/%m %H:%M'),
        })

    # ACTIVITES RECENTES
    activites_recentes = ActivityLog.objects.select_related('user').order_by('-date_creation')[:20]

    activites_data = []
    for a in activites_recentes:
        activites_data.append({
            'type': a.get_type_action_display(),
            'user': a.user.username if a.user else 'Anonyme',
            'description': a.description,
            'date': a.date_creation.strftime('%d/%m %H:%M'),
            'ip': str(a.ip_address) if a.ip_address else 'N/A',
        })

    # BACKTESTS
    total_backtests = BacktestAnalysis.objects.count()
    backtests_today = BacktestAnalysis.objects.filter(date_creation__gte=aujourd_hui).count()

    # MESSAGES
    messages_non_lus = ContactMessage.objects.filter(est_traite=False).count()
    total_messages = ContactMessage.objects.count()

    # WEBHOOKS
    webhooks_today = WebhookLog.objects.filter(date_reception__gte=aujourd_hui).count()
    webhooks_en_erreur = WebhookLog.objects.filter(
        statut='ERREUR', date_reception__gte=aujourd_hui
    ).count()

    context = {
        'total_users': total_users,
        'total_abonnes': total_abonnes,
        'total_gratuits': total_gratuits,
        'connectes_maintenant': connectes_maintenant,
        'nouveaux_today': nouveaux_today,
        'nouveaux_mois': nouveaux_mois,
        'nouveaux_annee': nouveaux_annee,
        'sessions_data': sessions_data,
        'abonnements_par_type': abonnements_par_type,
        'expiration_proche': sorted(expiration_proche, key=lambda x: x['jours'])[:10],
        'revenus_today': f"{paiements_today:,.0f}".replace(',', ' '),
        'revenus_mois': f"{paiements_mois:,.0f}".replace(',', ' '),
        'revenus_annee': f"{paiements_annee:,.0f}".replace(',', ' '),
        'derniers_paiements': paiements_data,
        'activites_recentes': activites_data,
        'total_backtests': total_backtests,
        'backtests_today': backtests_today,
        'messages_non_lus': messages_non_lus,
        'total_messages': total_messages,
        'webhooks_today': webhooks_today,
        'webhooks_en_erreur': webhooks_en_erreur,
        'date_actuelle': maintenant.strftime('%d/%m/%Y %H:%M'),
    }

    return render(request, 'gosen/admin/admin_dashboard.html', context)


@staff_member_required
def admin_api_stats(request):
    """API pour récupérer les stats en JSON"""
    sessions_actives = UserSession.get_sessions_actives()
    data = {
        'connectes_maintenant': sessions_actives.count(),
        'timestamp': timezone.now().isoformat(),
    }
    return JsonResponse(data)
