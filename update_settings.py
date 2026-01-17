import re

with open('/root/educalims-dev/educalims_project/settings.py', 'r') as f:
    content = f.read()

# Remplacer la configuration de la base de données
old_db = """DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}"""

new_db = """# Configuration de la base de données PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'educalims_dev',
        'USER': 'educalims',
        'PASSWORD': 'educalims_password',
        'HOST': 'db',
        'PORT': '5432',
    }
}"""

content = content.replace(old_db, new_db)

# Ajouter l'IP du VPS aux CSRF_TRUSTED_ORIGINS
old_csrf = """CSRF_TRUSTED_ORIGINS = [
    'https://*.ngrok-free.dev',
    'https://*.ngrok.io',
    'http://*.ngrok-free.dev',
    'http://*.ngrok.io',
    'https://*.pinggy.link',
    'https://*.pinggy.io',
    'https://*.a.free.pinggy.link',
]"""

new_csrf = """CSRF_TRUSTED_ORIGINS = [
    'https://*.ngrok-free.dev',
    'https://*.ngrok.io',
    'http://*.ngrok-free.dev',
    'http://*.ngrok.io',
    'https://*.pinggy.link',
    'https://*.pinggy.io',
    'https://*.a.free.pinggy.link',
    'http://72.62.181.239:8081',
]"""

content = content.replace(old_csrf, new_csrf)

with open('/root/educalims-dev/educalims_project/settings.py', 'w') as f:
    f.write(content)

print('Settings mis à jour avec succès!')
