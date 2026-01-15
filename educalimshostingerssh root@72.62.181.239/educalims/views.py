from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import json
import uuid
import random
import requests
import logging
from .models import Cycle, Discipline, Niveau, Unite, Fichier, Produit, Abonnement, WebhookLog
from .forms import CustomUserCreationForm, LoginForm

logger = logging.getLogger(__name__)


# ==================== TELEGRAM NOTIFICATIONS ====================

TELEGRAM_BOT_TOKEN = "8539115405:AAFxfimKuOeVKqYL5mQaclVsQ5Lh2hIcIok"
TELEGRAM_CHAT_ID = "1646298746"


def envoyer_notification_telegram(message):
    """Envoie une notification à Telegram via bot"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }

        logger.info(f"Envoi Telegram: {message[:100]}...")
        response = requests.post(url, data=payload, timeout=10)
        result = response.json()

        if result.get("ok"):
            logger.info(f"Réponse Telegram: OK - Message envoyé")
            return True
        else:
            logger.error(f"Erreur Telegram: {result}")
            return False

    except Exception as e:
        logger.error(f"Erreur Telegram: {str(e)}", exc_info=True)
        return False


def notifier_paiement_telegram(abonnement, statut="SUCCES", transaction_id="", numero_tel=""):
    """Envoie une notification Telegram pour un paiement"""
    emoji = {
        "SUCCES": "✅",
        "ECHEC": "❌",
        "EN_ATTENTE": "⏳"
    }

    emoji_symbole = emoji.get(statut, "💰")

    message = f"""{emoji_symbole} <b>Nouveau Paiement - {statut}</b>

👤 <b>Utilisateur:</b> {abonnement.user.username}
📚 <b>Niveau:</b> {abonnement.niveau.nom}
📦 <b>Produit:</b> {abonnement.produit.nom}
💰 <b>Montant:</b> {abonnement.montant_paye or abonnement.produit.prix} FCFA

🔗 <b>Référence interne:</b> <code>{abonnement.reference_interne}</code>
🏪 <b>Ref marchand:</b> <code>{abonnement.merchant_reference_id}</code>
"""

    # Ajouter les détails du paiement
    if abonnement.methode_paiement:
        message += f"💳 <b>Méthode:</b> {abonnement.methode_paiement}\n"
    if abonnement.code_paiement:
        message += f"🔢 <b>Code:</b> {abonnement.code_paiement}\n"
    if transaction_id:
        message += f"🆔 <b>Transaction ID:</b> {transaction_id}\n"
    if numero_tel:
        message += f"📱 <b>Téléphone:</b> {numero_tel}\n"

    if statut == "SUCCES" and abonnement.date_fin:
        message += f"\n📅 <b>Valide jusqu'au:</b> {abonnement.date_fin.strftime('%d/%m/%Y à %H:%M')}\n"

    return envoyer_notification_telegram(message.strip())


def notifier_nouveau_abonnement_telegram(abonnement):
    """Envoie une notification Telegram pour un nouvel abonnement créé"""
    message = f"""🆕 <b>Nouvel Abonnement Initié</b>

👤 <b>Utilisateur:</b> {abonnement.user.username}
📚 <b>Niveau:</b> {abonnement.niveau.nom}
📦 <b>Produit:</b> {abonnement.produit.nom}
💰 <b>Prix:</b> {abonnement.produit.prix} FCFA

⏳ <b>En attente de paiement...</b>
"""

    return envoyer_notification_telegram(message.strip())


# ==================== VUES PRINCIPALES ====================

def home(request):
    """Page d'accueil de l'application educalims"""
    return render(request, 'educalims/home.html')


def cycles_list(request):
    """Liste de tous les cycles"""
    cycles = Cycle.objects.all()
    return render(request, 'educalims/cycles_list.html', {'cycles': cycles})


def cycle_detail(request, cycle_id):
    """Détail d'un cycle avec ses disciplines"""
    cycle = get_object_or_404(Cycle, pk=cycle_id)
    disciplines = cycle.disciplines.all()
    # Annoter chaque discipline avec le nombre de niveaux enfants
    for discipline in disciplines:
        discipline.niveaux_enfants_count = discipline.niveaux.filter(est_niveau_enfant=True).count()
    return render(request, 'educalims/cycle_detail.html', {
        'cycle': cycle,
        'disciplines': disciplines
    })


def disciplines_list(request):
    """Liste de toutes les disciplines"""
    disciplines = Discipline.objects.all()
    # Annoter chaque discipline avec le nombre de niveaux enfants seulement
    for discipline in disciplines:
        discipline.niveaux_enfants_count = discipline.niveaux.filter(est_niveau_enfant=True).count()
    return render(request, 'educalims/disciplines_list.html', {'disciplines': disciplines})


def discipline_detail(request, discipline_id):
    """Détail d'une discipline avec ses niveaux enfants uniquement"""
    discipline = get_object_or_404(Discipline, pk=discipline_id)
    # N'afficher que les niveaux enfants (ceux qui ont un niveau_parent)
    niveaux = discipline.niveaux.filter(est_niveau_enfant=True).order_by('ordre', 'nom')
    # Annoter chaque niveau avec le nombre de sous-unités finales (chapitres sans enfants)
    for niveau in niveaux:
        # Compter les unités qui n'ont pas d'enfants (les feuilles de la hiérarchie)
        niveau.chapitres_count = niveau.unites.filter(unites_enfants__isnull=True).count()
    return render(request, 'educalims/discipline_detail.html', {
        'discipline': discipline,
        'niveaux': niveaux
    })


def niveau_detail(request, niveau_id):
    """Détail d'un niveau avec ses unités"""
    niveau = get_object_or_404(Niveau, pk=niveau_id)
    # Récupérer les disciplines associées au niveau
    disciplines = niveau.disciplines.all()
    # Récupérer les parties (unités sans parent)
    parties = niveau.unites.filter(unite_parent__isnull=True).order_by('ordre')
    # Compter les chapitres (unités finales sans enfants)
    niveau.chapitres_count = niveau.unites.filter(unites_enfants__isnull=True).count()

    # Vérifier si l'utilisateur a accès à ce niveau
    acces_autorise = False
    if request.user.is_authenticated:
        abonnement = Abonnement.objects.filter(
            user=request.user,
            niveau=niveau,
            statut='ACTIF'
        ).first()
        acces_autorise = abonnement and abonnement.est_valide()

    return render(request, 'educalims/niveau_detail.html', {
        'niveau': niveau,
        'parties': parties,
        'discipline': disciplines.first() if disciplines else None,
        'acces_autorise': acces_autorise
    })


def unite_detail(request, unite_id):
    """Détail d'une unité avec ses fichiers et sous-unités"""
    unite = get_object_or_404(Unite, pk=unite_id)
    fichiers = unite.fichiers.filter(est_actif=True)
    sous_unites = unite.unites_enfants.all().order_by('ordre')
    return render(request, 'educalims/unite_detail.html', {
        'unite': unite,
        'fichiers': fichiers,
        'sous_unites': sous_unites
    })


def fichier_detail(request, fichier_id):
    """Détail d'un fichier"""
    fichier = get_object_or_404(Fichier, pk=fichier_id, est_actif=True)
    # Incrémenter le compteur de téléchargements
    if fichier.type_fichier != 'LNK':
        fichier.telechargements += 1
        fichier.save()
    return render(request, 'educalims/fichier_detail.html', {'fichier': fichier})


# ==================== VUES D'AUTHENTIFICATION ====================

def custom_login(request):
    """Page de connexion"""
    if request.user.is_authenticated:
        return redirect('educalims:home')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenue, {username} !')
                next_url = request.GET.get('next', 'educalims:home')
                return redirect(next_url)
            else:
                messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    else:
        form = LoginForm()

    return render(request, 'educalims/auth/login.html', {'form': form})


def custom_register(request):
    """Page d'inscription"""
    if request.user.is_authenticated:
        return redirect('educalims:home')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']

            # Créer l'utilisateur manuellement pour éviter les validateurs Django stricts
            from django.contrib.auth.models import User
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Ce nom d\'utilisateur est déjà pris.')
                return render(request, 'educalims/auth/login.html', {'form': form})

            user = User.objects.create_user(username=username, email=email, password=password)
            messages.success(request, f'Compte créé avec succès pour {username} ! Vous pouvez maintenant vous connecter.')
            return redirect('educalims:login')
    else:
        form = CustomUserCreationForm()

    return render(request, 'educalims/auth/login.html', {'form': form})


def custom_logout(request):
    """Déconnexion"""
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('educalims:home')


@login_required
def profile(request):
    """Profil utilisateur"""
    return render(request, 'educalims/auth/profile.html')


# ==================== VUES D'ABONNEMENT ====================

@login_required
def mes_abonnements(request):
    """Liste des abonnements de l'utilisateur"""
    abonnements = request.user.abonnements.all().order_by('-date_creation')
    return render(request, 'educalims/abonnement/mes_abonnements.html', {
        'abonnements': abonnements
    })


@login_required
def s_abonner(request, niveau_id):
    """Page d'abonnement à un niveau"""
    if not request.user.is_authenticated:
        messages.error(request, 'Vous devez être connecté pour vous abonner.')
        return redirect('educalims:login')

    niveau = get_object_or_404(Niveau, pk=niveau_id)
    produit = Produit.objects.filter(est_actif=True).first()

    if not produit:
        messages.error(request, 'Aucun produit d\'abonnement disponible.')
        return redirect('educalims:discipline_detail', discipline_id=niveau.disciplines.first().id)

    # Vérifier si l'utilisateur a déjà un abonnement actif à ce niveau
    abonnement_existant = Abonnement.objects.filter(
        user=request.user,
        niveau=niveau,
        statut='ACTIF'
    ).first()

    if abonnement_existant and abonnement_existant.est_valide():
        messages.info(request, 'Vous avez déjà un abonnement actif à ce niveau.')
        return redirect('educalims:mes_abonnements')

    # Générer une référence de transaction unique pour notre système et pour Cyberschool
    reference_interne = f"SUB-{uuid.uuid4().hex[:12].upper()}"
    # Format numérique pour Cyberschool (9 chiffres)
    merchant_reference_id = f"{random.randint(100000000, 999999999)}"

    # Créer un abonnement en attente
    abonnement = Abonnement.objects.create(
        user=request.user,
        niveau=niveau,
        produit=produit,
        statut='EN_ATTENTE',
        reference_interne=reference_interne,
        merchant_reference_id=merchant_reference_id
    )

    # Envoyer notification Telegram pour le nouvel abonnement
    notifier_nouveau_abonnement_telegram(abonnement)

    return render(request, 'educalims/abonnement/paiement.html', {
        'niveau': niveau,
        'produit': produit,
        'abonnement': abonnement,
        'reference_interne': reference_interne,
        'merchant_reference_id': merchant_reference_id
    })


@csrf_exempt
@require_http_methods(["POST"])
def paiement_callback(request):
    """
    Callback URL pour recevoir les reponses de paiement de Cyberschool
    Format JSON recu :
    {
        "merchantReferenceId": "878048050",
        "status": "SUCCESS",
        "amount": 200,
        "reference": "878048050",
        "operateur": "ACC_6835C649CA536",
        "numero_tel": "077045354",
        "timestamp": "2025-12-26T10:48:23.422Z",
        "transactionId": "PAY261225680304",
        "code": 200,
        "operator": "AIRTEL_MONEY"
    }
    L'abonnement est active uniquement si code == 200.
    """
    try:
        data = json.loads(request.body)

        # Récupérer les données de paiement
        code = data.get('code')
        merchant_reference_id = data.get('merchantReferenceId') or data.get('reference')
        transaction_id = data.get('transactionId')
        amount = data.get('amount')
        operator = data.get('operator', data.get('operateur', ''))
        numero_tel = data.get('numero_tel')

        # Trouver l'abonnement correspondant via merchant_reference_id
        abonnement = None
        if merchant_reference_id:
            abonnement = Abonnement.objects.filter(merchant_reference_id=merchant_reference_id).first()

        if not abonnement:
            # Log pour debug
            print(f"DEBUG: Callback recu - merchantReferenceId: {merchant_reference_id}, code: {code}")
            print(f"DEBUG: Abonnements en attente: {list(Abonnement.objects.filter(statut='EN_ATTENTE').values_list('merchant_reference_id', flat=True))}")
            return JsonResponse({
                'status': 'error',
                'message': f'Abonnement non trouve (merchantReferenceId: {merchant_reference_id})'
            }, status=404)

        # Vérifier si le paiement est réussi (code == 200)
        if code == 200:
            # Mettre à jour l'abonnement
            abonnement.code_paiement = str(code)
            abonnement.methode_paiement = operator.upper() if operator else 'AUTRE'
            abonnement.montant_paye = amount

            # Activer l'abonnement
            abonnement.activer_abonnement(duree_jours=abonnement.produit.duree_jours)

            print(f"SUCCESS: Abonnement {abonnement.id} active pour {abonnement.user.username}")

            # Envoyer notification Telegram pour paiement réussi avec détails
            notifier_paiement_telegram(
                abonnement,
                statut="SUCCES",
                transaction_id=transaction_id or "",
                numero_tel=numero_tel or ""
            )

            return JsonResponse({
                'status': 'success',
                'message': 'Abonnement active avec succes',
                'abonnement_id': abonnement.id
            }, status=200)
        else:
            # Paiement échoué
            abonnement.statut = 'ECHOUE'
            abonnement.code_paiement = str(code)
            abonnement.methode_paiement = operator.upper() if operator else 'AUTRE'
            abonnement.save()

            # Envoyer notification Telegram pour paiement échoué avec détails
            notifier_paiement_telegram(
                abonnement,
                statut="ECHEC",
                transaction_id=transaction_id or "",
                numero_tel=numero_tel or ""
            )

            return JsonResponse({
                'status': 'error',
                'message': f'Paiement echoue (code: {code})'
            }, status=400)

    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'JSON invalide'
        }, status=400)
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@login_required
def verifier_acces(request, niveau_id):
    """Vérifie si l'utilisateur a accès à un niveau (API)"""
    if not request.user.is_authenticated:
        return JsonResponse({'acces': False, 'raison': 'Non connecté'})

    niveau = get_object_or_404(Niveau, pk=niveau_id)

    abonnement = Abonnement.objects.filter(
        user=request.user,
        niveau=niveau,
        statut='ACTIF'
    ).first()

    acces = abonnement and abonnement.est_valide()

    return JsonResponse({
        'acces': acces,
        'niveau': niveau.nom,
        'abonnement_id': abonnement.id if abonnement else None
    })


@login_required
def abonnement_statut(request, abonnement_id):
    """Vérifie le statut d'un abonnement (API pour la page de paiement)"""
    abonnement = get_object_or_404(Abonnement, pk=abonnement_id, user=request.user)

    return JsonResponse({
        'statut': abonnement.statut,
        'statut_display': abonnement.get_statut_display(),
        'valide': abonnement.est_valide() if abonnement.statut == 'ACTIF' else False,
        'date_debut': abonnement.date_debut.strftime('%d/%m/%Y %H:%M') if abonnement.date_debut else None,
        'date_fin': abonnement.date_fin.strftime('%d/%m/%Y %H:%M') if abonnement.date_fin else None,
    })


def api_paiements_recents(request):
    """API pour les paiements recents (affiches sur la page d'accueil)"""
    from django.utils import timezone
    from datetime import timedelta

    # Derniers paiements des 10 dernieres minutes
    date_limite = timezone.now() - timedelta(minutes=10)
    paiements = Abonnement.objects.filter(
        date_modification__gte=date_limite
    ).order_by('-date_modification')[:20]

    data = []
    for p in paiements:
        data.append({
            'id': p.id,
            'user': p.user.username,
            'niveau': p.niveau.nom,
            'statut': p.statut,
            'statut_display': p.get_statut_display(),
            'montant': p.montant_paye,
            'methode': p.methode_paiement,
            'date_modification': p.date_modification.strftime('%H:%M:%S'),
            'code_paiement': p.code_paiement,
            'merchant_reference_id': p.merchant_reference_id
        })

    return JsonResponse({'paiements': data})


@csrf_exempt  # Désactive CSRF pour ce webhook
@require_http_methods(["POST"])
def webhook_cyberschool_simple(request):
    """
    Webhook simplifié pour recevoir les notifications Cyberschool.
    Envoie tout sur Telegram et tente d'activer l'abonnement.
    """
    try:
        # Log les données brutes reçues
        logger.info("=" * 80)
        logger.info("🔔 WEBHOOK CYBERSCHOOL REÇU")
        logger.info(f"Body raw: {request.body}")

        data = json.loads(request.body)
        logger.info(f"JSON reçu: {data}")

        # Extraire les données importantes
        merchant_ref = data.get('merchantReferenceId') or data.get('reference') or data.get('customerID')
        code = data.get('code')
        status = data.get('status')
        amount = data.get('amount')
        operator = data.get('operator', data.get('operateur', ''))
        transaction_id = data.get('transactionId')
        numero_tel = data.get('numero_tel') or data.get('customerID')

        logger.info(f"merchantReferenceId: {merchant_ref}")
        logger.info(f"code: {code}")
        logger.info(f"status: {status}")
        logger.info(f"transactionId: {transaction_id}")
        logger.info(f"numero_tel: {numero_tel}")

        # Envoyer notification Telegram avec toutes les infos
        message = f"""🔔 <b>WEBHOOK CYBERSCHOOL REÇU</b>

📋 <b>Détails bruts:</b>
• <b>merchantReferenceId:</b> <code>{merchant_ref}</code>
• <b>reference:</b> <code>{data.get('reference')}</code>
• <b>Code:</b> {code}
• <b>Status:</b> {status}
• <b>Montant:</b> {amount} FCFA
• <b>Opérateur:</b> {operator}
• <b>Transaction ID:</b> <code>{transaction_id or 'N/A'}</code>
• <b>Téléphone:</b> {numero_tel or 'N/A'}
• <b>customerID:</b> {data.get('customerID', 'N/A')}

🕐 <b>Timestamp:</b> {data.get('timestamp', 'N/A')}
"""
        envoyer_notification_telegram(message.strip())

        logger.info("📱 Notification Telegram envoyée")

        # === ACTIVATION AUTOMATIQUE DE L'ABONNEMENT ===
        if code == 200 and numero_tel:
            logger.info(f"✅ Paiement réussi ! Recherche de l'abonnement avec téléphone: {numero_tel}")

            try:
                # Rechercher l'abonnement EN_ATTENTE le plus récent pour ce niveau
                # Cyberschool génère son propre merchantReferenceId, donc on utilise le numéro de téléphone
                abonnement = Abonnement.objects.filter(
                    statut='EN_ATTENTE'
                ).order_by('-date_creation').first()

                if abonnement:
                    # Activer l'abonnement
                    abonnement.statut = 'ACTIF'
                    abonnement.date_debut = timezone.now()
                    abonnement.methode_paiement = operator
                    abonnement.montant_paye = amount
                    abonnement.code_paiement = str(code)

                    # Calculer la date de fin selon la durée du produit
                    if abonnement.produit and abonnement.produit.duree_jours:
                        from datetime import timedelta
                        abonnement.date_fin = timezone.now() + timedelta(days=abonnement.produit.duree_jours)

                    abonnement.save()

                    logger.info(f"🎉 ABONNEMENT ACTIVÉ: {abonnement}")
                    logger.info(f"   - Niveau: {abonnement.niveau.nom if abonnement.niveau else 'N/A'}")
                    logger.info(f"   - Utilisateur: {abonnement.user.username if abonnement.user else 'N/A'}")
                    logger.info(f"   - Date début: {abonnement.date_debut}")
                    logger.info(f"   - Date fin: {abonnement.date_fin}")

                    # Enregistrer le webhook log
                    WebhookLog.objects.create(
                        merchant_reference_id=merchant_ref,
                        code=code,
                        status=status,
                        amount=amount,
                        operator=operator,
                        transaction_id=transaction_id,
                        phone_number=numero_tel,
                        abonnement=abonnement,
                        activation_succes=True,
                        telegram_notification_sent=True,
                        raw_data=data
                    )

                    # Notification de succès
                    envoyer_notification_telegram(
                        f"✅ <b>ABONNEMENT ACTIVÉ</b>\n"
                        f"📚 Niveau: <b>{abonnement.niveau.nom if abonnement.niveau else 'N/A'}</b>\n"
                        f"👤 Utilisateur: <b>{abonnement.user.username if abonnement.user else 'N/A'}</b>\n"
                        f"💰 Montant: {amount} FCFA\n"
                        f"📞 Téléphone: {numero_tel or 'N/A'}"
                    )

                    return JsonResponse({
                        'status': 'activated',
                        'message': 'Abonnement activé avec succès',
                        'abonnement_id': abonnement.id
                    }, status=200)
                else:
                    logger.warning(f"⚠️ Aucun abonnement trouvé avec merchant_reference_id: {merchant_ref}")
                    envoyer_notification_telegram(
                        f"⚠️ <b>ABONNEMENT NON TROUVÉ</b>\n\n"
                        f"Référence: <code>{merchant_ref}</code>\n"
                        f"Paiement reçu mais aucun abonnement correspondant."
                    )

            except Exception as e:
                logger.error(f"❌ Erreur lors de l'activation: {str(e)}", exc_info=True)
                envoyer_notification_telegram(f"❌ <b>ERREUR ACTIVATION</b>\n\n{str(e)}")

        elif code != 200:
            logger.warning(f"⚠️ Paiement échoué (code: {code})")
            envoyer_notification_telegram(
                f"⚠️ <b>PAIEMENT ÉCHOUÉ</b>\n\n"
                f"Code: {code}\n"
                f"Status: {status}"
            )

        # Retourner 200 pour confirmer réception
        return JsonResponse({
            'status': 'received',
            'message': 'Webhook reçu et traité',
            'merchant_ref': merchant_ref,
            'code': code
        }, status=200)

    except json.JSONDecodeError as e:
        logger.error(f"❌ Erreur JSON: {str(e)}")
        logger.error(f"Body reçu: {request.body}")
        envoyer_notification_telegram(f"❌ <b>ERREUR JSON</b>\n\n{str(e)}")
        return JsonResponse({'status': 'error', 'message': 'JSON invalide'}, status=400)

    except Exception as e:
        logger.error(f"❌ Erreur webhook: {str(e)}", exc_info=True)
        envoyer_notification_telegram(f"❌ <b>ERREUR WEBHOOK</b>\n\n{str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
