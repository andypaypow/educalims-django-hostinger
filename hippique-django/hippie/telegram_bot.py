"""
Telegram Bot pour Filtre Expert +
Gère les notifications de paiement et les commandes utilisateurs
"""
import requests
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)

# Configuration
TELEGRAM_BOT_TOKEN = "8547430409:AAGx2LxGxP6fBd9mn13LSmRbU4y3wlopIq4"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# Chat ID pour les notifications administrateur
ADMIN_CHAT_ID = "1646298746"  # À remplacer par votre chat ID


# ==================== FONCTIONS UTILITAIRES ====================

def envoyer_message(chat_id, message):
    """
    Envoie un message sur Telegram.

    Args:
        chat_id: ID du chat Telegram (int ou str)
        message: Contenu du message

    Returns:
        bool: True si succès, False sinon
    """
    try:
        url = f"{TELEGRAM_API_URL}/sendMessage"
        response = requests.post(url, json={
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }, timeout=10)

        result = response.json()
        if result.get("ok"):
            logger.info(f"✅ Message Telegram envoyé à {chat_id}")
            return True
        else:
            logger.error(f"❌ Erreur Telegram: {result}")
            return False

    except Exception as e:
        logger.error(f"❌ Erreur envoi Telegram: {str(e)}", exc_info=True)
        return False


def envoyer_notification_admin(message):
    """
    Envoie une notification à l'administrateur.

    Args:
        message: Contenu du message
    """
    return envoyer_message(ADMIN_CHAT_ID, message)


# ==================== NOTIFICATIONS DE PAIEMENT ====================

def envoyer_notification_webhook_recu(data):
    """
    Notifie l'admin qu'un webhook Cyberschool a été reçu.

    Args:
        data: Données brutes du webhook
    """
    merchant_ref = data.get('merchantReferenceId', 'N/A')
    code = data.get('code', 'N/A')
    status = data.get('status', 'N/A')
    amount = data.get('amount', 'N/A')
    operator = data.get('operator', 'N/A')
    phone = data.get('numero_tel') or data.get('customerID', 'N/A')

    message = f"""🔔 <b>WEBHOOK CYBERSCHOOL REÇU</b>

📋 <b>Détails bruts:</b>
• <b>merchantReferenceId:</b> <code>{merchant_ref}</code>
• <b>Code:</b> {code}
• <b>Status:</b> {status}
• <b>Montant:</b> {amount} FCFA
• <b>Opérateur:</b> {operator}
• <b>Téléphone:</b> {phone}

🕐 <b>Timestamp:</b> {data.get('timestamp', 'N/A')}
"""

    logger.info(f"🔔 Webhook reçu: code={code}, merchant_ref={merchant_ref}, phone={phone}")
    return envoyer_notification_admin(message.strip())


def envoyer_notification_paiement_reussi(abonnement):
    """
    Notifie l'admin et l'utilisateur qu'un paiement a réussi.

    Args:
        abonnement: Instance du modèle Abonnement
    """
    temps_restant = abonnement.date_fin - timezone.now()

    # Notification à l'utilisateur (si lié à Telegram)
    if abonnement.session_user.telegram_user_id:
        message = f"""✅ <b>Paiement confirmé !</b>

🔓 Votre abonnement est maintenant <b>ACTIF</b>

📅 Valide jusqu'au : {abonnement.date_fin.strftime('%d/%m/%Y à 23h59')}
⏳ Temps restant : {temps_restant.days + 1} jours

👇 Retournez sur la page pour voir vos combinaisons :
http://72.62.181.239:8000/hippie/turf-filter/

💡 Vos résultats sont maintenant visibles !
"""
        envoyer_message(abonnement.session_user.telegram_user_id, message.strip())

    # Notification à l'admin
    message_admin = f"""✅ <b>PAIEMENT RÉUSSI - Abonnement Activé</b>

👤 <b>Session:</b> <code>{abonnement.session_user.session_id}</code>
📦 <b>Produit:</b> {abonnement.produit.nom}
💰 <b>Montant:</b> {abonnement.montant_paye} FCFA
💳 <b>Méthode:</b> {abonnement.methode_paiement}

🔗 <b>Référence marchand:</b> <code>{abonnement.merchant_reference_id}</code>

📅 <b>Valide jusqu'au:</b> {abonnement.date_fin.strftime('%d/%m/%Y à 23h59')}
⏳ <b>Temps restant:</b> {temps_restant.days + 1} jours
"""

    logger.info(f"✅ Paiement réussi: session={abonnement.session_user.session_id}, montant={abonnement.montant_paye}")
    return envoyer_notification_admin(message_admin.strip())


def envoyer_notification_paiement_echec(webhook_log):
    """
    Notifie l'admin qu'un paiement a échoué.

    Args:
        webhook_log: Instance du modèle WebhookLog
    """
    message = f"""❌ <b>PAIEMENT ÉCHOUÉ</b>

🔗 <b>Référence:</b> <code>{webhook_log.merchant_reference_id}</code>
🔢 <b>Code:</b> {webhook_log.code}
📋 <b>Status:</b> {webhook_log.status}
💰 <b>Montant:</b> {webhook_log.amount} FCFA
📱 <b>Téléphone:</b> {webhook_log.phone_number}
"""

    logger.warning(f"❌ Paiement échoué: ref={webhook_log.merchant_reference_id}, code={webhook_log.code}")
    return envoyer_notification_admin(message.strip())


# ==================== COMMANDES DU BOT ====================

def cmd_start(update):
    """
    Commande /start - Initialise l'utilisateur Telegram.
    Gère aussi le contexte HIPPIE vs EDUCALIMS
    """
    from .models import SessionUser, Abonnement, ProduitAbonnement
    import uuid

    user_id = update['message']['from']['id']
    username = update['message']['from'].get('username', 'N/A')
    message_text = update['message'].get('text', '')

    # Déterminer le contexte (hippie ou educalims) basé sur le message
    is_hippie_context = 'hippie' in message_text.lower() or 'filtre' in message_text.lower() or 'turf' in message_text.lower() or 'quinté' in message_text.lower()

    # Lier le Telegram user à une session
    session_id = f"tg_{user_id}_{uuid.uuid4().hex[:8]}"
    session_user, created = SessionUser.objects.get_or_create(
        telegram_user_id=user_id,
        defaults={'session_id': session_id}
    )

    if created:
        logger.info(f"🆕 Nouvel utilisateur Telegram: {user_id} ({username})")
    else:
        logger.info(f"👤 Utilisateur Telegram existant: {user_id} ({username})")

    # Vérifier l'abonnement
    abonnement = Abonnement.objects.filter(
        session_user=session_user,
        statut='ACTIF',
        date_fin__gte=timezone.now()
    ).first()

    if abonnement and abonnement.est_valide():
        temps_restant = abonnement.date_fin - timezone.now()
        message = f"""🏇 <b>Bienvenue sur Filtre Expert +</b>

✅ Votre abonnement est <b>ACTIF</b>

⏳ Expire dans : <b>{temps_restant.days + 1} jours</b>
📅 Date fin : {abonnement.date_fin.strftime('%d/%m/%Y à 23h59')}

👇 <a href="http://72.62.181.239:8000/hippie/turf-filter/">Cliquez ici pour accéder aux combinaisons</a>

⚠️ <i>Important:</i> Sauvegardez ce lien pour y revenir plus tard.
"""
    else:
        produit = ProduitAbonnement.objects.filter(est_actif=True).first()
        if not produit:
            message = "⚠️ Aucun produit d'abonnement disponible actuellement."
        else:
            merchant_ref = create_pending_abonnement(session_user, produit)
            lien_paiement = f"{produit.url_paiement}?merchantReferenceId={merchant_ref}"
            message = f"""🏇 <b>Bienvenue sur Filtre Expert +</b>

Pour voir les résultats de vos combinaisons, vous devez avoir un abonnement actif.

💰 <b>Abonnement Journalier - {produit.prix} FCFA</b>
Valide jusqu'à 23h59 aujourd'hui

👇 <a href="{lien_paiement}">Cliquez ici pour payer</a>

⚠️ Après paiement, revenez sur la page pour voir vos résultats.
"""

    envoyer_message(user_id, message.strip())


def cmd_compteur(update):
    """
    Commande /compteur - Affiche le compteur d'expiration.
    """
    from .models import SessionUser, Abonnement

    user_id = update['message']['from']['id']
    session_user = SessionUser.objects.filter(telegram_user_id=user_id).first()

    if not session_user:
        envoyer_message(user_id, "❌ Utilisateur non trouvé. Utilisez /start")
        return

    abonnement = Abonnement.objects.filter(
        session_user=session_user,
        statut='ACTIF',
        date_fin__gte=timezone.now()
    ).first()

    if abonnement and abonnement.est_valide():
        temps_restant = abonnement.date_fin - timezone.now()
        heures = temps_restant.seconds // 3600
        minutes = (temps_restant.seconds % 3600) // 60

        message = f"""⏰ <b>Compteur d'Expiration</b>

📅 Expire le : {abonnement.date_fin.strftime('%d/%m/%Y à 23h59')}
⏳ Il vous reste : <b>{temps_restant.days} jours, {heures}h {minutes}min</b>

💡 Vos résultats sont visibles sur :
http://72.62.181.239:8000/hippie/turf-filter/
"""
    else:
        message = "❌ Aucun abonnement actif. Utilisez /start pour vous abonner."

    envoyer_message(user_id, message.strip())


def cmd_help(update):
    """
    Commande /help - Affiche l'aide.
    """
    user_id = update['message']['from']['id']
    message = """🏇 <b>Filtre Expert + - Aide</b>

<b>Commandes disponibles:</b>

/start - Initialiser votre compte et vérifier votre abonnement
/compteur - Voir le temps restant avant expiration
/help - Afficher cette aide

<b>Comment ça marche ?</b>

1. Allez sur http://72.62.181.239:8000/hippie/turf-filter/
2. Configurez vos filtres
3. Payez pour voir les résultats (100 FCFA/jour)
4. Les résultats apparaissent automatiquement après paiement !

💡 <b> Astuce:</b> Sauvegardez le lien de la page pour y revenir facilement.
"""

    envoyer_message(user_id, message.strip())


# ==================== FONCTIONS UTILITAIRES ====================

def create_pending_abonnement(session_user, produit):
    """
    Crée un abonnement en attente et retourne la référence marchand.

    Args:
        session_user: Instance de SessionUser
        produit: Instance de ProduitAbonnement

    Returns:
        str: Référence marchand (merchant_reference_id)
    """
    from .models import Abonnement
    import uuid

    merchant_ref = str(uuid.uuid4())
    Abonnement.objects.create(
        session_user=session_user,
        produit=produit,
        merchant_reference_id=merchant_ref,
        statut='EN_ATTENTE'
    )

    logger.info(f"📝 Abonnement créé en attente: session={session_user.session_id}, ref={merchant_ref}")
    return merchant_ref


# ==================== WEBHOOK TELEGRAM ====================

def traiter_update_telegram(update):
    """
    Traite une mise à jour (update) du bot Telegram.

    Args:
        update: Dictionnaire contenant la mise à jour Telegram
    """
    message = update.get('message', {})

    if not message:
        return

    text = message.get('text', '')

    if text == '/start':
        cmd_start(update)
    elif text == '/compteur':
        cmd_compteur(update)
    elif text == '/help':
        cmd_help(update)
    else:
        # Message non reconnu
        user_id = message.get('from', {}).get('id')
        if user_id:
            envoyer_message(user_id, "❌ Commande non reconnue. Utilisez /help pour voir les commandes disponibles.")
