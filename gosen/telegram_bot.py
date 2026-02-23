"""
Module pour l'envoi de messages Telegram
"""
import logging
import os
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
import json

logger = logging.getLogger(__name__)


REPONSES_ADMIN_TELEGRAM = {
    "don": """🎁 <b>Nouvelle demande de DON</b>

Un turfiste souhaite faire un don pour soutenir Filtre Expert.

À contacter rapidement pour les modalités de paiement.""",

    "partenariat": """🤝 <b>Nouvelle demande de PARTENARIAT</b>

Une opportunité de collaboration stratégique dans l'univers des courses hippiques.

À étudier sous 24h.""",

    "acces_gratuit": """🌟 <b>Nouvelle demande d'ACCÈS GRATUIT</b>

Un turfiste souhaite découvrir nos outils gratuitement.

Demande à étudier attentivement.""",

    "support": """🔧 <b>Nouvelle demande de SUPPORT</b>

Un utilisateur a besoin d'assistance technique.

À traiter en priorité.""",

    "autre": """✉️ <b>Nouveau message de contact</b>

Un utilisateur a posé une question générale.

À répondre dès que possible.""",
}


REPONSES_SUGGEREES = {
    "don": """Bonjour très cher(e) {nom},

Merci pour votre proposition de don ! 🎁

C'est un geste précieux qui nous aide à améliorer Filtre Expert.

Pour les modalités de transfert, voici nos coordonnées :
- Mobile Money: [...]
- PayPal: [...]

Merci encore pour votre soutien !

---
Gosenmarket, partenaire de filtreexpert.org
Succès et paix en salutations hippiques""",

    "partenariat": """Bonjour très cher(e) {nom},

Merci pour votre intérêt pour un partenariat ! 🤝

Votre proposition nous intéresse.

Pouvez-vous nous en dire plus sur :
- Votre secteur d'activité
- La nature du partenariat envisagé
- Les bénéfices mutuels attendus

Nous vous répondrons sous 24h.

---
Gosenmarket, partenaire de filtreexpert.org
Succès et paix en salutations hippiques""",

    "acces_gratuit": """Bonjour très cher(e) {nom},

Merci pour votre demande d'accès gratuit ! 🌟

Nous comprenons que chaque turfiste mérite de découvrir nos outils.

Votre demande est en cours d'étude.

Nous avons quelques questions pour vous :
- Depuis quand suivez-vous les courses hippiques ?
- Quelle est votre approche actuelle ?

À très bientôt !

---
Gosenmarket, partenaire de filtreexpert.org
Succès et paix en salutations hippiques""",

    "support": """Bonjour très cher(e) {nom},

Merci pour votre message de support ! 🔧

Nous avons bien reçu votre demande et notre équipe technique la traite.

Nous reviendrons vers vous rapidement avec une solution.

Si urgent : WhatsApp au [...]

---
Gosenmarket, partenaire de filtreexpert.org
Succès et paix en salutations hippiques""",

    "autre": """Bonjour très cher(e) {nom},

Merci pour votre message ! ✉️

Nous avons bien reçu votre demande.

Nous vous répondrons dans les plus brefs délais.

N'hésitez pas à nous contacter pour toute autre question.

---
Gosenmarket, partenaire de filtreexpert.org
Succès et paix en salutations hippiques""",
}


def envoyer_message_telegram(message):
    try:
        bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        chat_id = os.environ.get('TELEGRAM_CHAT_ID')
        
        if not bot_token or not chat_id:
            logger.warning('TELEGRAM_BOT_TOKEN ou TELEGRAM_CHAT_ID non configure')
            return False
        
        url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
        data = json.dumps({
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }).encode('utf-8')
        
        req = Request(url, data=data, headers={'Content-Type': 'application/json'})
        
        with urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            if result.get('ok'):
                logger.info(f'Message Telegram envoye avec succes: {result}')
                return True
            else:
                logger.error(f'Erreur Telegram API: {result}')
                return False
        
    except (URLError, HTTPError) as e:
        logger.error(f'Erreur lors de l envoi Telegram (HTTP): {e}')
        return False
    except Exception as e:
        logger.error(f'Erreur inattendue lors de l envoi Telegram: {e}')
        return False


def formater_message_contact(nom, whatsapp, type_demande, message_texte):
    emoji_type = {
        'don': '🎁',
        'partenariat': '🤝',
        'acces_gratuit': '🌟',
        'support': '🔧',
        'autre': '✉️',
    }.get(type_demande, '📩')
    
    reponse_admin = REPONSES_ADMIN_TELEGRAM.get(type_demande, REPONSES_ADMIN_TELEGRAM['autre'])
    reponse_suggeree = REPONSES_SUGGEREES.get(type_demande, REPONSES_SUGGEREES['autre']).format(nom=nom)
    
    message = f"""{reponse_admin}

--------------------

<b>{emoji_type} Details du message</b>

👤 <b>Nom:</b> {nom}
📱 <b>WhatsApp:</b> {whatsapp}
📋 <b>Type:</b> {type_demande.upper()}

💬 <b>Message:</b>
<code>{message_texte}</code>

--------------------

📝 <b>REPONSE SUGGÉRÉE</b> <i>(à personnaliser et envoyer)</i>:

<code>{reponse_suggeree}</code>

<i>{get_date_actuelle()}</i>

---
🔗 <b>Lien rapide:</b> https://filtreexpert.org/admin/gosen/contactmessage/
"""
    return message


def get_reponse_utilisateur(type_demande):
    reponses = {
        "don": """🎁 Votre demande de don a été enregistrée !

Elle est actuellement en attente de traitement par notre équipe.

Nous vous recontacterons très bientôt pour les modalités de paiement.

---
Gosenmarket, partenaire de filtreexpert.org
Succès et paix en salutations hippiques""",
        "partenariat": """🤝 Votre demande de partenariat a été enregistrée !

Elle est actuellement en attente de traitement par notre équipe.

Nous vous répondrons sous 24h.

---
Gosenmarket, partenaire de filtreexpert.org
Succès et paix en salutations hippiques""",
        "acces_gratuit": """🌟 Votre demande d'accès gratuit a été enregistrée !

Elle est actuellement en attente de traitement par notre équipe.

Nous vous recontacterons rapidement.

---
Gosenmarket, partenaire de filtreexpert.org
Succès et paix en salutations hippiques""",
        "support": """🔧 Votre demande de support a été enregistrée !

Elle est actuellement en attente de traitement par notre équipe technique.

Nous vous répondrons dans les plus brefs délais.

---
Gosenmarket, partenaire de filtreexpert.org
Succès et paix en salutations hippiques""",
        "autre": """✉️ Votre message a été enregistré !

Il est actuellement en attente de traitement par notre équipe.

Nous vous répondrons avec plaisir.

---
Gosenmarket, partenaire de filtreexpert.org
Succès et paix en salutations hippiques""",
    }
    return reponses.get(type_demande, reponses['autre'])


def get_date_actuelle():
    from datetime import datetime
    return datetime.now().strftime('%d/%m/%Y %H:%M')
