# Fix Whitenoise - Gosen Filter

## Problème

Les fichiers statiques (CSS, JS, images) ne sont pas servis correctement.

---

## Solution : Configurer Whitenoise

Whitenoise sert les fichiers statiques directement depuis Django, sans nécessiter Nginx ou un serveur séparé.

---

## Étape 1 : Installer Whitenoise

```bash
# Se connecter au serveur
ssh -i ~/.ssh/id_ed25519 root@72.62.181.239

# Éditer requirements.txt
cd /root/gosen-filter-dev
nano requirements.txt
```

Ajouter :
```
whitenoise==6.6.0
```

---

## Étape 2 : Configurer dans settings.py

```python
# gosen_project/settings.py

# MIDDLEWARE : Ajouter Whitenoise en premier
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',  # <-- Ajouter ceci
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # ... autres middleware
]

# STATIC FILES
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Whitenoise configuration
WHITENOISE_USE_FINDERS = True
WHITENOISE_IGNORE_REGEXES = [
    r'^\.git',
    r'^\.svn',
    r'^\.hg',
    r'^\.bzr',
    r'^\.DS_Store',
    r'^node_modules',
]
```

---

## Étape 3 : Collecter les fichiers statiques

```bash
# Entrer dans le conteneur
docker exec -it gosen-dev-web bash

# Collecter les fichiers statiques
python manage.py collectstatic --noinput

# Sortir du conteneur
exit

# Redémarrer le conteneur
docker restart gosen-dev-web
```

---

## Étape 4 : Vérifier

```bash
# Vérifier que les fichiers statiques sont servis
curl -I http://localhost:8082/static/gosen/css/style.css

# Doit retourner HTTP 200
```

---

## Dépannage

### Les fichiers statiques ne sont toujours pas servis

```bash
# Vérifier que STATIC_ROOT existe
ls -la /root/gosen-filter-dev/staticfiles/

# Recollecter
docker exec gosen-dev-web python manage.py collectstatic --noinput --clear

# Vérifier les permissions
chmod -R 755 /root/gosen-filter-dev/staticfiles/
```

### Erreur 404 sur les fichiers statiques

```bash
# Vérifier la configuration
docker exec gosen-dev-web python manage.py shell
>>> from django.conf import settings
>>> print(settings.STATIC_ROOT)
>>> print(settings.STATIC_URL)

# Vérifier que Whitenoise est dans MIDDLEWARE
>>> print(settings.MIDDLEWARE)
```

### Les changements ne sont pas pris en compte

```bash
# Forcer la recollection
docker exec gosen-dev-web python manage.py collectstatic --clear --noinput

# Redémarrer
docker restart gosen-dev-web

# Attendre 10 secondes
sleep 10

# Vérifier
curl -I http://localhost:8082/static/gosen/css/style.css
```

---

## Docker Compose Configuration

```yaml
# docker-compose.dev.yml
services:
  web:
    build: .
    command: gunicorn gosen_project.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - .:/code
      - static_volume:/code/staticfiles
    # ...
```

---

## Bonnes pratiques

1. **Toujours faire `collectstatic`** après avoir ajouté des fichiers statiques
2. **Redémarrer le conteneur** après `collectstatic`
3. **Vérifier les permissions** des fichiers statiques
4. **Utiliser `--clear`** pour forcer la recollection

---

## Alternatives

Si Whitenoise ne fonctionne pas, utiliser Nginx :

```nginx
# nginx.conf
location /static/ {
    alias /code/staticfiles/;
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

---

**Projet** : Gosen TurfFilter
**Documentation** : 30 Janvier 2026
