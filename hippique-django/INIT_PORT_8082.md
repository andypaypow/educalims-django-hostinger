# /init - Gosen TurfFilter - Port 8082 (DEV uniquement)

> **Date**: 1er février 2026
> **Objectif**: Travailler uniquement sur le port 8082 (DEV) - Hostinger VPS

---

## Serveur

- **IP**: 72.62.181.239
- **Port**: 8082 (DEV uniquement)
- **SSH**: `ssh -i ~/.ssh/id_ed25519 root@72.62.181.239`
- **Dossier**: `/root/gosen-filter-dev/`

---

## Application

**Nom**: Gosen TurfFilter - Application de filtrage de combinaisons hippiques

**Tech Stack**:
- Django + PostgreSQL + Gunicorn
- Whitenoise (fichiers statiques)
- Docker Compose

**URL**: http://72.62.181.239:8082/

---

## Architecture (Calculs Côté Serveur)

```
Navigateur (client)
    ↓ Envoie paramètres POST
API: /api/filter/
    ↓ Calculs avec formules cachées
Django Serveur (views/filters.py)
    ↓ Renvoie JSON
Navigateur affiche les résultats
```

**Points clés**:
- Tous les calculs sont côté serveur (formules protégées)
- Le client envoie les paramètres, reçoit les résultats
- Formules dans `/code/gosen/views/filters.py` (invisibles client)

---

## Fichiers principaux

| Fichier | Description |
|---------|-------------|
| `gosen/views/filters.py` | API de filtrage côté serveur |
| `gosen/views/base.py` | Vue principale, vérif abonnement |
| `gosen/models.py` | Models Produit, Abonnement, UserProfile |
| `gosen/urls.py` | Routing URLs |
| `gosen/templates/gosen/base.html` | HTML principal |
| `gosen/static/gosen/css/styles.css` | Styles |
| `gosen/static/gosen/js/main.js` | JavaScript (appelle API) |

---

## Système de Paiement (Cyberschool)

### Configuration

- **Bot Telegram**: @Filtrexpert_bot
- **Token**: `8547430409:AAGx2LxGxP6fBd9mn13LSmRbU4y3wlopIq4`
- **Chat ID**: `1646298746`

### Webhook

```
http://72.62.181.239:8082/webhook-cyberschool/
```

### Flux de paiement

1. Clic "S'abonner (100F/jour)"
2. Redirection → Cyberschool
3. Paiement → Code "200"
4. Webhook appelé → Création abonnement
5. Notification @Filtrexpert_bot
6. Expire à 23h59 le jour du paiement

### Tables principales

- `gosen_produit` : Produits d'abonnement
- `gosen_abonnement` : Abonnements utilisateurs
- `gosen_gosenuserprofile` : Profils avec device_id
- `gosen_webhooklog` : Journal webhooks

---

## Commandes Docker (8082)

```bash
# Connexion
ssh -i ~/.ssh/id_ed25519 root@72.62.181.239

# Voir conteneurs
docker ps | grep gosen

# Logs temps réel
docker logs gosen-dev-web -f

# Redémarrer
docker restart gosen-dev-web

# Shell Django
docker exec -it gosen-dev-web python manage.py shell

# Migrations
docker exec gosen-dev-web python manage.py makemigrations
docker exec gosen-dev-web python manage.py migrate

# Fichiers statiques
docker exec gosen-dev-web python manage.py collectstatic --noinput
```

---

## Git Workflow

**Branche actuelle**: `prod`

**Branches**:
- `main` : Stable
- `prod` : Production (8083) - PAS UTILISÉ
- `dev` : Développement (8082)

**Pour travailler sur 8082 uniquement**:
```bash
git checkout dev
# Modifications
git add .
git commit -m "feat: description"
git push origin dev
```

---

## Configuration Django (settings.py)

```python
# Telegram Bot
TELEGRAM_BOT_TOKEN = '8547430409:AAGx2LxGxP6fBd9mn13LSmRbU4y3wlopIq4'
TELEGRAM_CHAT_ID = '1646298746'

# Cyberschool
CYBERSCHOOL_WEBHOOK = 'http://72.62.181.239:8082/webhook-cyberschool/'

# Middleware (Whitenoise en premier)
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    # ...
]
```

---

## Vérification

```bash
# Test HTTP
curl -s http://localhost:8082/ | grep -E '(config-card|pronostics-card)'

# Test API
curl -s -X POST http://localhost:8082/api/filter/ \
  -H "Content-Type: application/json" \
  -d '{"n":16,"k":6,"groups":[],"orFilters":[]}'
```

---

## Dépannage rapide

| Problème | Solution |
|----------|----------|
| Conteneur ne démarre pas | `docker logs gosen-dev-web` |
| Fichiers statiques 404 | `python manage.py collectstatic --noinput` |
| Migration nécessaire | `python manage.py migrate` |
| API ne répond pas | Vérifier `gosen/urls.py` et `views/filters.py` |

---

## Webhooks

### URLs disponibles

| URL | Description |
|-----|-------------|
| `/webhook/receiver/` | Point de terminaison principal pour recevoir les webhooks |
| `/webhook/test/` | Page de test pour envoyer des webhooks |
| `/webhook/logs/` | Liste des logs webhooks (admin uniquement) |

### URL du webhook (à configurer dans Cyberschool)

```
http://72.62.181.239:8082/webhook/receiver/
```

### Modèle WebhookLog

Enregistre tous les webhooks reçus avec :
- Source (Cyberschool, Moov Money, Airtel Money)
- Payload et headers complets
- Référence transaction, code paiement, montant, téléphone
- Date réception, date traitement, statut
- IP et User Agent de l'expéditeur

### Test du webhook

Ouvrez : http://72.62.181.239:8082/webhook/test/

---

## Attention

- Ne PAS toucher au port 8083 (PROD)
- Travail ciblé sur 8082 uniquement
- Formules protégées côté serveur
- Webhook Cyberschool doit pointer vers 8082

---

## Skills disponibles

- `gosen-payment.md` : Système de paiement détaillé
- `docker-commands/` : Commandes Docker complètes
- `django-migrate/` : Gestion des migrations
- `git-workflow/` : Workflow Git
- `fix-whitenoise/` : Configuration Whitenoise
- `server-side-calculations.md` : Architecture calculs serveur
- `reset-gosen-dev.md` : Reset rapide DEV
- `fix-csrf-domain.md` : Fix CSRF domaine
- `connect-subscription-system.md` : Système abonnement
- `deploy-dev-to-prod.md` : Déploiement vers PROD (PAS UTILISÉ)
