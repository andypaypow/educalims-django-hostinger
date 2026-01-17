# Guide de Réinitialisation - Environnement de Développement Educalims

> Documentation pour les futurs développeurs
> Ce guide explique comment réinitialiser l'environnement de développement depuis zéro.

---

## Prérequis

- Accès SSH au VPS Hostinger
- Docker et Docker Compose installés
- URL du dépôt GitHub : https://github.com/andypaypow/educalims-django-hostinger.git

---

## Réinitialisation complète ( étapes par étapes )

### 1. Arrêter et supprimer les conteneurs

```bash
cd /root/educalims-dev
docker compose -f docker-compose.dev.yml down -v
```

### 2. Sauvegarder (optionnel)

```bash
mv /root/educalims-dev /root/educalims-dev.backup.$(date +%Y%m%d_%H%M%S)
```

### 3. Cloner le dépôt

```bash
cd /root
git clone https://github.com/andypaypow/educalims-django-hostinger.git educalims-dev
```

### 4. Réorganiser la structure

```bash
cd /root/educalims-dev
cp -r 'educalimshostingerssh root@72.62.181.239/'/* .
rm -rf 'educalimshostingerssh root@72.62.181.239' Educalim 'educalims django django templates' 'educalims fulstack'
```

### 5. Créer requirements.txt

```bash
cp requirements-docker.txt requirements.txt
```

### 6. Mettre à jour settings.py pour PostgreSQL

```bash
python3 << 'PYEOF'
with open('educalims_project/settings.py', 'r') as f:
    content = f.read()

old_db = "DATABASES = {\n    'default': {\n        'ENGINE': 'django.db.backends.sqlite3',\n        'NAME': BASE_DIR / 'db.sqlite3',\n    }\n}"
new_db = "DATABASES = {\n    'default': {\n        'ENGINE': 'django.db.backends.postgresql',\n        'NAME': 'educalims_dev',\n        'USER': 'educalims',\n        'PASSWORD': 'educalims_password',\n        'HOST': 'db',\n        'PORT': '5432',\n    }\n}"
content = content.replace(old_db, new_db)

content = content.replace("'https://*.a.free.pinggy.link',", "'https://*.a.free.pinggy.link',\n    'http://72.62.181.239:8081',")

with open('educalims_project/settings.py', 'w') as f:
    f.write(content)
PYEOF
```

### 7. Construire et démarrer

```bash
docker compose -f docker-compose.dev.yml build
docker compose -f docker-compose.dev.yml up -d
```

### 8. Migrations

```bash
docker compose -f docker-compose.dev.yml exec -T web python manage.py migrate
```

### 9. Créer l'admin

```bash
docker compose -f docker-compose.dev.yml exec -T web python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@educalims.com', 'admin123')"
```

### 10. Importer les instances

```bash
docker compose -f docker-compose.dev.yml exec -T web python insert_instances_from_md.py
```

---

## Erreurs fréquentes et solutions

### Erreur: Forbidden (403) CSRF

**Cause:** CSRF_TRUSTED_ORIGINS ne contient pas l'IP du serveur

**Solution:**
```bash
# Ajouter dans settings.py
CSRF_TRUSTED_ORIGINS = [
    'http://72.62.181.239:8081',
]
# Puis redémarrer
docker compose -f docker-compose.dev.yml restart web
```

### Erreur: requirements.txt non trouvé

**Solution:**
```bash
cp requirements-docker.txt requirements.txt
```

---

## Connexion

| Service | URL |
|---------|-----|
| Site | http://72.62.181.239:8081/ |
| Admin | http://72.62.181.239:8081/admin/ |

**Identifiants:** admin / admin123

---

## Commandes utiles

```bash
# Logs
docker compose -f docker-compose.dev.yml logs -f web

# Redémarrer web
docker compose -f docker-compose.dev.yml restart web

# Shell Django
docker compose -f docker-compose.dev.yml exec web python manage.py shell

# État
docker compose -f docker-compose.dev.yml ps
```

---
**Dernière mise à jour :** 2026-01-17
