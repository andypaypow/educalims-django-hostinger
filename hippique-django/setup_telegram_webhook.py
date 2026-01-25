"""
Script pour configurer le webhook Telegram pour Filtre Expert +
"""
import requests
import os
import sys

# Configuration
TELEGRAM_BOT_TOKEN = "8547430409:AAGx2LxGxP6fBd9mn13LSmRbU4y3wlopIq4"

# IMPORTANT: Telegram exige HTTPS pour les webhooks
# Remplacez cette URL par votre URL HTTPS publique
# Options:
# 1. Utiliser ngrok pour les tests: ngrok http 8000
# 2. Configurer SSL sur votre serveur
# 3. Utiliser un service comme Cloudflare Tunnel

WEBHOOK_URL = "https://votre-domaine.com/hippie/telegram-webhook/"  # À REMPLACER

def set_webhook():
    """Configure le webhook Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook"

    # Pour ngrok (exemple): https://abc123.ngrok.io/hippie/telegram-webhook/
    # Pour votre serveur avec SSL: https://72.62.181.239/hippie/telegram-webhook/

    print(f"🔧 Configuration du webhook Telegram...")
    print(f"📍 URL du webhook: {WEBHOOK_URL}")
    print(f"⚠️  IMPORTANT: L'URL doit être en HTTPS !")

    response = requests.post(url, json={
        'url': WEBHOOK_URL,
        'drop_pending_updates': True
    }, timeout=10)

    result = response.json()

    if result.get('ok'):
        print("✅ Webhook configuré avec succès !")
        print(f"📍 Webhook URL: {WEBHOOK_URL}")
    else:
        print(f"❌ Erreur de configuration: {result}")
        return False

    return True


def get_webhook_info():
    """Récupère les informations du webhook"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getWebhookInfo"

    response = requests.get(url, timeout=10)
    result = response.json()

    if result.get('ok'):
        info = result.get('result', {})
        print("\n📋 Informations du webhook:")
        print(f"   URL: {info.get('url', 'Non configuré')}")
        print(f"   Has custom certificate: {info.get('has_custom_certificate', False)}")
        print(f"   Pending update count: {info.get('pending_update_count', 0)}")
        print(f"   Last error: {info.get('last_error_message', 'Aucune')}")

        if not info.get('url'):
            print("\n⚠️  Le webhook n'est PAS configuré !")
            print("   Utilisez: python setup_telegram_webhook.py")
    else:
        print(f"❌ Erreur: {result}")


def delete_webhook():
    """Supprime le webhook (pour revenir au polling)"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/deleteWebhook"

    response = requests.post(url, timeout=10)
    result = response.json()

    if result.get('ok'):
        print("✅ Webhook supprimé. Le bot utilisera le polling.")
    else:
        print(f"❌ Erreur: {result}")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Gérer le webhook Telegram')
    parser.add_argument('action', choices=['set', 'info', 'delete'],
                       help='Action: set (configurer), info (voir infos), delete (supprimer)')
    parser.add_argument('--url', help='URL du webhook (HTTPS requis)', default=WEBHOOK_URL)

    args = parser.parse_args()

    if args.action == 'set':
        WEBHOOK_URL = args.url
        set_webhook()
    elif args.action == 'info':
        get_webhook_info()
    elif args.action == 'delete':
        delete_webhook()
