"""
Vues pour gérer les webhooks et afficher les logs
"""
import json
import logging
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.db.models import Q, Count

from django.contrib.auth.models import User
from gosen.models import WebhookLog, UserProfile, SubscriptionProduct, SubscriptionPayment, AuthToken


logger = logging.getLogger(__name__)


@require_http_methods(["POST", "GET"])
@csrf_exempt
def webhook_receiver(request):
    """
    Point de terminaison générique pour recevoir les webhooks
    Enregistre TOUTES les requêtes pour débugging

    URL: /webhook/receiver/
    """
    # Créer le log
    webhook_log = WebhookLog()

    try:
        # Enregistrer les informations de base
        webhook_log.ip_address = get_client_ip(request)
        webhook_log.user_agent = request.META.get('HTTP_USER_AGENT', '')

        # Capturer les headers
        headers_dict = {}
        for key, value in request.META.items():
            if key.startswith('HTTP_'):
                headers_dict[key[5:]] = value
        webhook_log.headers = headers_dict

        # Si POST, capturer le payload
        if request.method == 'POST':
            try:
                content_type = request.content_type

                if content_type == 'application/json':
                    payload_data = json.loads(request.body)
                elif content_type == 'application/x-www-form-urlencoded':
                    payload_data = dict(request.POST)
                else:
                    # Pour les autres types, essayer de parser comme JSON
                    try:
                        payload_data = json.loads(request.body)
                    except:
                        payload_data = {'raw': request.body.decode('utf-8', errors='ignore')}

                webhook_log.payload = payload_data

                # Extraire des informations courantes
                if isinstance(payload_data, dict):
                    # Cyberschool
                    webhook_log.reference_transaction = payload_data.get('merchantReferenceId') or \
                                                         payload_data.get('reference') or \
                                                         payload_data.get('transaction_id') or \
                                                         payload_data.get('txn_id')

                    webhook_log.code_paiement = payload_data.get('code') or \
                                               payload_data.get('payment_code') or \
                                               payload_data.get('status')

                    # Montant
                    montant = payload_data.get('amount') or \
                             payload_data.get('montant') or \
                             payload_data.get('payment_amount')
                    if montant:
                        try:
                            webhook_log.montant = float(montant)
                        except:
                            pass

                    # Frais (fees)
                    fees = payload_data.get('fees') or \
                           payload_data.get('frais') or \
                           payload_data.get('transaction_fees')
                    if fees:
                        try:
                            webhook_log.fees = float(fees)
                        except:
                            pass

                    # Montant total (totalAmount)
                    total_amount = payload_data.get('totalAmount') or \
                                  payload_data.get('total_amount') or \
                                  payload_data.get('totalamount')
                    if total_amount:
                        try:
                            webhook_log.total_amount = float(total_amount)
                        except:
                            pass

                    # Téléphone (champs Cyberschool: numero_tel, customerID)
                    webhook_log.telephone = payload_data.get('phone') or \
                                           payload_data.get('telephone') or \
                                           payload_data.get('customer_phone') or \
                                           payload_data.get('msisdn') or \
                                           payload_data.get('numero_tel') or \
                                           payload_data.get('customerID')

                    # Source
                    if 'cyberschool' in str(payload_data).lower():
                        webhook_log.source = 'cyberschool'
                    elif 'moov' in str(payload_data).lower():
                        webhook_log.source = 'moov_money'
                    elif 'airtel' in str(payload_data).lower():
                        webhook_log.source = 'airtel_money'

            except Exception as e:
                logger.error(f"Erreur parsing payload: {e}")
                webhook_log.payload = {'error': str(e), 'raw': request.body.decode('utf-8', errors='ignore')}

        # Sauvegarder le log
        webhook_log.save()

        # Variable pour le token d'authentification
        login_token = None
        login_url = None

        # TRAITEMENT AUTOMATIQUE DU PAIEMENT
        # Créer l'utilisateur et activer l'abonnement si paiement réussi
        if webhook_log.telephone and str(webhook_log.code_paiement) in ['200', 200]:
            try:
                # Créer ou récupérer l'utilisateur
                username = 'user_' + webhook_log.telephone.replace('+', '').replace(' ', '')
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': f'{username}@temp.local',
                        'is_active': True
                    }
                )

                # Créer ou récupérer le profil
                profile, profile_created = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={'telephone': webhook_log.telephone}
                )

                # Trouver le produit correspondant au montant
                produit = SubscriptionProduct.objects.filter(
                    est_actif=True,
                    prix=webhook_log.montant
                ).first()

                if produit:
                    # Créer le paiement
                    payment = SubscriptionPayment.objects.create(
                        utilisateur=user,
                        produit=produit,
                        type_abonnement=produit.type_abonnement,
                        montant=webhook_log.montant,
                        statut='complete',
                        reference_transaction=webhook_log.reference_transaction or f'AUTO-{timezone.now().timestamp()}',
                        code_paiement=str(webhook_log.code_paiement),
                        telephone=webhook_log.telephone,
                        date_paiement=timezone.now(),
                        webhook_log=webhook_log
                    )

                    # Activer l'abonnement
                    profile.activer_abonnement(
                        produit.type_abonnement,
                        duree_jours=produit.duree_jours
                    )

                    # Générer un token d'authentification automatique
                    auth_token = AuthToken.creer_pour_utilisateur(user, heures_validite=24)
                    login_token = str(auth_token.token)
                    # URL de connexion automatique (à utiliser avec Cyberschool redirect)
                    login_url = f"http://72.62.181.239:8082/auth/auto-login/{login_token}/"

                    # Mettre à jour le log
                    webhook_log.statut = 'SUCCES'
                    webhook_log.utilisateur = user
                    webhook_log.date_traitement = timezone.now()
                    webhook_log.save()

                    logger.info(f"Abonnement activé pour {username} - Produit: {produit.nom} - Token: {login_token}")

            except Exception as e:
                logger.error(f'Erreur activation abonnement: {e}')
                webhook_log.statut = 'ERREUR'
                webhook_log.message_erreur = str(e)
                webhook_log.save()

        # Logger
        logger.info(f"Webhook reçu - ID: {webhook_log.id}, Source: {webhook_log.source}, Ref: {webhook_log.reference_transaction}")

        # Préparer la réponse
        response_data = {
            'success': True,
            'message': 'Webhook reçu et enregistré',
            'log_id': webhook_log.id,
            'timestamp': timezone.now().isoformat()
        }

        # Inclure le token si généré
        if login_token:
            response_data['login_token'] = login_token
            response_data['login_url'] = login_url

        # Répondre
        return JsonResponse(response_data)

    except Exception as e:
        logger.error(f"Erreur webhook: {e}")
        # Sauvegarder si possible
        try:
            webhook_log.message_erreur = str(e)
            webhook_log.statut = 'ERREUR'
            webhook_log.save()
        except:
            pass

        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def webhook_test(request):
    """
    Page de test pour envoyer des webhooks
    """
    return render(request, 'gosen/webhook/test.html')


@require_http_methods(["GET"])
@staff_member_required
def webhook_logs_list(request):
    """
    Affiche la liste des logs webhooks (admin uniquement)
    """
    # Filtrage
    statut = request.GET.get('statut', '')
    source = request.GET.get('source', '')
    recherche = request.GET.get('q', '')

    logs = WebhookLog.objects.all()

    if statut:
        logs = logs.filter(statut=statut)
    if source:
        logs = logs.filter(source=source)
    if recherche:
        logs = logs.filter(
            Q(reference_transaction__icontains=recherche) |
            Q(telephone__icontains=recherche) |
            Q(code_paiement__icontains=recherche)
        )

    # Statistiques
    stats = {
        'total': WebhookLog.objects.count(),
        'succes': WebhookLog.objects.filter(statut='SUCCES').count(),
        'erreur': WebhookLog.objects.filter(statut='ERREUR').count(),
        'en_attente': WebhookLog.objects.filter(statut='EN_ATTENTE').count(),
        'aujourdhui': WebhookLog.objects.filter(
            date_reception__date=timezone.now().date()
        ).count(),
    }

    # Pagination simple
    page = int(request.GET.get('page', 1))
    per_page = 50
    start = (page - 1) * per_page
    end = start + per_page
    logs_page = logs[start:end]
    has_next = end < logs.count()

    context = {
        'logs': logs_page,
        'stats': stats,
        'statut': statut,
        'source': source,
        'recherche': recherche,
        'page': page,
        'has_next': has_next,
        'sources': WebhookLog.SOURCE_CHOICES,
        'statuts': WebhookLog.STATUT_CHOICES,
    }

    return render(request, 'gosen/webhook/logs.html', context)


@require_http_methods(["GET"])
@staff_member_required
def webhook_log_detail(request, log_id):
    """
    Affiche le détail d'un log webhook
    """
    log = WebhookLog.objects.get(id=log_id)

    context = {
        'log': log,
    }

    return render(request, 'gosen/webhook/detail.html', context)


@require_http_methods(["DELETE", "POST"])
@staff_member_required
def webhook_log_delete(request, log_id):
    """
    Supprime un log webhook
    """
    if request.method == "DELETE" or request.POST.get('_method') == 'DELETE':
        log = WebhookLog.objects.get(id=log_id)
        log.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)


def get_client_ip(request):
    """Récupère l'IP réelle du client"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
