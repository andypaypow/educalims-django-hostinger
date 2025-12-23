# -*- coding: utf-8 -*-
"""
EDUCALIMS - Telegram Mini App Launcher
Lance Django et ngrok en une seule commande
"""
from pyngrok import ngrok
import subprocess

# Configuration
NGROK_AUTH_TOKEN = "34Fiz0WnQdA9PQ9fXv0lS6MAZK0_6GKZSymAvAbqxTzjfSgS8"
DJANGO_PORT = 8000

# Configurer ngrok
ngrok.set_auth_token(NGROK_AUTH_TOKEN)
tunnel = ngrok.connect(DJANGO_PORT)

print("=" * 60)
print("EDUCALIMS - Telegram Mini App")
print("=" * 60)
print(f"URL ngrok  : {tunnel.public_url}")
print(f"URL locale : http://127.0.0.1:{DJANGO_PORT}")
print("=" * 60)
print("\nCOPIEZ cette URL dans @BotFather > Mini App:")
print(f"{tunnel.public_url}")
print("\nAppuyez sur Ctrl+C pour arrêter...")
print("=" * 60)

# Lancer le serveur Django (ce blocera)
try:
    subprocess.run(["python", "manage.py", "runserver"])
finally:
    print("\nFermeture du tunnel ngrok...")
    ngrok.kill()
