# CLAUDE.md

Ce fichier fournit des instructions à Claude Code (claude.ai/code) lorsqu'il travaille avec le code de ce dépôt.

---

# 🚀 Hippique - Guide Complet

---

## 📋 Sommaire

1. **Espace Dev et Prod sur Hostinger** - Infrastructure
2. **Base de Données et Instances** - Données et structure
3. **Authentification et Sécurité** - Connexion et appareils
4. **Paiement et Telegram** - Système de paiement
5. **Git et Déploiement** - Commit, Push, Reset
6. **Guide de Reset Git** - Revenir à un commit spécifique
7. **Supabase - Backend as a Service** - Base de données, Auth, Edge Functions
8. **FiltreExpert Supabase** - Frontend statique
9. **FiltreExpert - Paiement** - Système d'abonnement
10. **Gosen Filter** - Projet TurfFilter (Port 8082)

---

## ÉTAPE 1 : ESPACE DEV ET PROD SUR HOSTINGER

### 🌐 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Hostinger VPS                          │
│  IP : 72.62.181.239                                       │
│  SSH : ssh -i ~/.ssh/id_ed25519 root@72.62.181.239      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────┐      ┌──────────────────┐        │
│  │   DEV             │      │   PROD            │        │
│  │ Port : 8082       │      │ Port : 8083       │        │
│  │ Path :hippique-dev│      │ Path:hippique-prod│        │
│  │ Branch:dev        │      │ Branch: prod      │        │
│  └──────────────────┘      └──────────────────┘        │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 🔑 Connexion SSH

**Depuis votre machine locale :**

```bash
ssh -i ~/.ssh/id_ed25519 root@72.62.181.239
```

**Se connecter directement à un environnement :**

```bash
# Dev
ssh -i ~/.ssh/id_ed25519 root@72.62.181.239 "cd /root/hippique-dev && bash"

# Prod
ssh -i ~/.ssh/id_ed25519 root@72.62.181.239 "cd /root/hippique-prod && bash"
```

### 🐳 Conteneurs Docker (par environnement)

| Conteneur | Rôle | Port |
|-----------|------|------|
| **nginx** | Reverse Proxy + Static | 8082 (dev) / 8083 (prod) |
| **web** | Django + Gunicorn | 8000 (interne) |
| **db** | PostgreSQL | 5432 (interne) |

### 📊 Vérifier l'état des conteneurs

```bash
# Tous les conteneurs hippique
ssh -i ~/.ssh/id_ed25519 root@72.62.181.239 "docker ps --filter 'name=hippique' --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"

# Dev uniquement
ssh -i ~/.ssh/id_ed25519 root@72.62.181.239 "cd /root/hippique-dev && docker compose -f docker-compose.dev.yml ps"

# Prod uniquement
ssh -i ~/.ssh/id_ed25519 root@72.62.181.239 "cd /root/hippique-prod && docker compose -f docker-compose.prod.yml ps"
```

---

## ÉTAPE 2 : BASE DE DONNÉES ET INSTANCES

### 🗄️ Structure PostgreSQL

**Dev :** hippique_db | **Prod :** hippique_db | **User :** hippique_user

### 📊 Tables Principales

```sql
hippique_course         -- Courses et événements
hippique_participant    -- Participants/Chevaux
hippique_prediction     -- Prédictions et analyses
hippique_abonnement     -- Abonnements utilisateurs
hippique_webhooklog     -- Journal webhooks
hippique_userprofile    -- Profils utilisateurs (device_id)
```

### 🔌 Connexion à la Base de Données

```bash
# Dev
ssh -i ~/.ssh/id_ed25519 root@72.62.181.239 "cd /root/hippique-dev && docker compose -f docker-compose.dev.yml exec db psql -U hippique_user -d hippique_db"

# Prod
ssh -i ~/.ssh/id_ed25519 root@72.62.181.239 "cd /root/hippique-prod && docker compose -f docker-compose.prod.yml exec db psql -U hippique_user -d hippique_db"
```

### 🔄 Migrations

```bash
# Créer migrations (Dev)
ssh -i ~/.ssh/id_ed25519 root@72.62.181.239 "cd /root/hippique-dev && docker compose -f docker-compose.dev.yml exec web python manage.py makemigrations"

# Appliquer migrations (Dev)
ssh -i ~/.ssh/id_ed25519 root@72.62.181.239 "cd /root/hippique-dev && docker compose -f docker-compose.dev.yml exec web python manage.py migrate"

# Appliquer migrations (Prod)
ssh -i ~/.ssh/id_ed25519 root@72.62.181.239 "cd /root/hippique-prod && docker compose -f docker-compose.prod.yml exec web python manage.py migrate"
```

### ✅ Vérifier l'État de la Base

```bash
ssh -i ~/.ssh/id_ed25519 root@72.62.181.239 "cd /root/hippique-dev && docker compose -f docker-compose.dev.yml exec -T db psql -U hippique_user -d hippique_db -c '\dt'"
```

---

## ÉTAPE 3 : AUTHENTIFICATION ET SÉCURITÉ

### 🔐 Authentification Django

- Sessions
- Cookies
- Middleware CSRF
- Device ID tracking

### 🔑 Configuration

**Fichier :** `.env.dev` sur Hostinger

```bash
SECRET_KEY=django-insecure-hippique-dev-change-in-production
DATABASE_URL=postgresql://hippique_user:hippique_password@db:5432/hippique_db
ALLOWED_HOSTS=localhost,127.0.0.1,72.62.181.239
TELEGRAM_BOT_TOKEN=8539115405:AAFxfimKuOeVKqYL5mQaclVsQ5Lh2hIcIok
TELEGRAM_CHAT_ID=1646298746
```

### 📱 Un Appareil = Un Abonné

**Fonctionnement :**
1. Paiement réussi → device_id enregistré
2. Accès ultérieur → Vérification du device_id
3. Appareil différent → Erreur 403

**Composants :**
- `UserProfile.device_id` - Stocke l'identifiant de l'appareil
- `DeviceIdMiddleware` - Génère et reconnaît l'appareil
- `@device_required` - Décorateur de vérification

### 👤 Superutilisateur

**Identifiants par défaut :**
- Username : `admin`
- Password : `admin`

**Créer sur Hostinger :**

```bash
# Dev
ssh -i ~/.ssh/id_ed25519 root@72.62.181.239 "cd /root/hippique-dev && docker compose -f docker-compose.dev.yml exec web python manage.py createsuperuser"

# Prod
ssh -i ~/.ssh/id_ed25519 root@72.62.181.239 "cd /root/hippique-prod && docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser"
```

---

## ÉTAPE 4 : PAIEMENT ET TELEGRAM

### 💳 Système de Paiement

**Flux :** Utilisateur → Prestataire de paiement → Webhook → Activation → Notification Telegram

### 📱 Notifications Telegram

**Configuration :**
```python
TELEGRAM_BOT_TOKEN = "8539115405:AAFxfimKuOeVKqYL5mQaclVsQ5Lh2hIcIok"
TELEGRAM_CHAT_ID = "1646298746"
```

**URL API Telegram :**
```
https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage
```

---

## ÉTAPE 5 : GIT ET DÉPLOIEMENT

### 🌐 Repository GitHub

**URL :** https://github.com/andypaypow/hippique-django.git

**Branches :**
- `main` - Branche principale (Production)
- `dev` - Branche de développement
- `prod` - Branche de production (deployée sur Hostinger)

### 🔑 GitHub Token

Le token GitHub est stocké sur Hostinger dans `/root/.github_token`

### 📝 Workflow Git

**Depuis votre machine locale :**

```bash
# 1. Vérifier
git status

# 2. Ajouter (PAS de .env, PAS de secrets)
git add .

# 3. Commiter
git commit -m "feat: description"

# 4. Pusher vers GitHub
git push origin <branche>
```

**Depuis Hostinger (Push vers GitHub) :**

```bash
# Se connecter
ssh -i ~/.ssh/id_ed25519 root@72.62.181.239

# Aller dans le projet
cd /root/hippique-prod

# Ajouter et commiter
git add .
git commit -m "feat: description"

# Pusher (en utilisant le token)
TOKEN=$(cat /root/.github_token)
git remote set-url origin "https://${TOKEN}@github.com/andypaypow/hippique-django.git"
git push origin prod
git remote set-url origin "https://github.com/andypaypow/hippique-django.git"
```

### 📋 Format des Commits

```
feat: nouvelle fonctionnalité
fix: correction de bug
refactor: refactoring
docs: documentation
chore: maintenance
```

### 🚀 Déploiement vers Prod

```bash
# 1. Travailler en DEV (local ou sur Hostinger)
cd /root/hippique-dev

# 2. Commiter et pusher vers GitHub
git add .
git commit -m "feat: description"
TOKEN=$(cat /root/.github_token)
git remote set-url origin "https://${TOKEN}@github.com/andypaypow/hippique-django.git"
git push origin dev
git remote set-url origin "https://github.com/andypaypow/hippique-django.git"

# 3. Aller en PROD sur Hostinger
cd /root/hippique-prod

# 4. Pull depuis GitHub
git pull origin prod

# 5. REBUILD le conteneur web (OBLIGATOIRE)
docker compose -f docker-compose.prod.yml up -d --build web

# 6. Appliquer les migrations
docker compose -f docker-compose.prod.yml exec web python manage.py migrate
```

### 📊 Dev vs Prod

| Action | Dev | Prod |
|--------|-----|------|
| Modifier code | Direct, volume monté | Via git uniquement |
| Déploiement | `restart web` | `--build web` OBLIGATOIRE |
| Migrations | `migrate` | `--build web` + `migrate` |
| Port | 8082 | 8083 |

---

## ÉTAPE 6 : GUIDE DE RESET GIT

### ⚡ Reset Rapide vers un Commit Spécifique

```bash
# Remplacer <COMMIT_HASH> par le hash (ex: a1b2c3d)

# === LOCAL ===
git fetch origin
git reset --hard <COMMIT_HASH>
git clean -fd

# === HOSTINGER PROD ===
ssh -i ~/.ssh/id_ed25519 root@72.62.181.239 "cd /root/hippique-prod && git fetch origin && git reset --hard <COMMIT_HASH> && git clean -fd"

# Push forcé vers GitHub (ATTENTION: utiliser avec prudence!)
TOKEN=$(cat /root/.github_token)
git remote set-url origin "https://${TOKEN}@github.com/andypaypow/hippique-django.git"
git push origin prod --force
git remote set-url origin "https://github.com/andypaypow/hippique-django.git"
```

### 🔄 Revenir au Dernier Commit de Main

```bash
# Récupérer le hash du dernier commit main
MAIN_COMMIT=$(git rev-parse origin/main)

# Reset local
git reset --hard $MAIN_COMMIT && git clean -fd

# Reset Hostinger prod
ssh -i ~/.ssh/id_ed25519 root@72.62.181.239 "cd /root/hippique-prod && git reset --hard $MAIN_COMMIT && git clean -fd"
```

### ✅ Vérifier l'Alignement

```bash
echo "=== Local ===" && git log -1 --oneline
echo "=== Hostinger Dev ===" && ssh -i ~/.ssh/id_ed25519 root@72.62.181.239 "cd /root/hippique-dev && git log -1 --oneline"
echo "=== Hostinger Prod ===" && ssh -i ~/.ssh/id_ed25519 root@72.62.181.239 "cd /root/hippique-prod && git log -1 --oneline"
echo "=== GitHub (branche prod) ===" && git log -1 --oneline origin/prod
```

---

## ÉTAPE 7 : SUPABASE - BACKEND AS A SERVICE

### 🔗 Informations de Connexion

**Projet :** filtreexpert
**Dashboard :** https://supabase.com/dashboard/project/qfkyzljqykymahlpmdnu

| Élément | Valeur |
|---------|--------|
| **Project URL** | `https://qfkyzljqykymahlpmdnu.supabase.co` |
| **Project ID** | `qfkyzljqykymahlpmdnu` |
| **Database Password** | `RK8AY46O3WhOlwrA` |

### 🔑 Clés API

```
Anon Key (public):
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFma3l6bGpxeWt5bWFobHBtZG51Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk2Mjc1NzIsImV4cCI6MjA4NTIwMzU3Mn0.g_Rmxo8lY8KAnrQqyzcz0PLh03T1M7_RuBUQT6ObtXg

Service Role Key (admin):
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFma3l6bGpxeWt5bWFobHBtZG51Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2OTYyNzU3MiwiZXhwIjoyMDg1MjAzNTcyfQ.qwZ9S95QLHoROmwcQTqhP8std9eW2NJ4-_Lv8hzeUbo

JWT Secret:
ojdJ5aNShf27eP0g+XNMdKAWlGZRdW1BjJtSPajmpOp/od2aX2XRzdD02d6b7p5kak/pMUottx+QVaVNemmxJw==
```

### 🗄️ Connexion à la Base de Données

**Via psql :**
```bash
psql -h db.qfkyzljqykymahlpmdnu.supabase.co -U postgres -d postgres
# Password: RK8AY46O3WhOlwrA
```

**Connection String :**
```
postgresql://postgres:RK8AY46O3WhOlwrA@db.qfkyzljqykymahlpmdnu.supabase.co:5432/postgres
```

**Via Supabase CLI :**
```bash
# Lier le projet
supabase link --project-ref qfkyzljqykymahlpmdnu

# Ouvrir le dashboard
supabase db remote commit
```

### ⚡ Edge Functions

**Déployer une Edge Function :**
```bash
# Créer une fonction
supabase functions new webhook-payment

# Déployer
supabase functions deploy webhook-payment

# Déployer avec des variables d'environnement
supabase functions deploy webhook-payment --env WEBHOOK_SECRET=xxx
```

**URL des Edge Functions :**
```
https://qfkyzljqykymahlpmdnu.supabase.co/functions/v1/<function-name>
```

### 🔌 API REST

**Exemple d'utilisation :**
```bash
# Lister les tables
curl "https://qfkyzljqykymahlpmdnu.supabase.co/rest/v1/" \
  -H "apikey: <ANON_KEY>" \
  -H "Authorization: Bearer <SERVICE_KEY>"

# Interroger une table
curl "https://qfkyzljqykymahlpmdnu.supabase.co/rest/v1/<table_name>" \
  -H "apikey: <ANON_KEY>" \
  -H "Authorization: Bearer <SERVICE_KEY>"
```

### 🪝 Webhook de Paiement

**Structure recommandée pour le webhook :**
```typescript
// functions/webhook-payment/index.ts
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"

serve(async (req) => {
  // 1. Vérifier la signature
  const signature = req.headers.get('x-webhook-signature')
  // ... vérification HMAC

  // 2. Parser le payload
  const payload = await req.json()

  // 3. Traiter selon le type d'événement
  if (payload.event === 'payment.succeeded') {
    // Mettre à jour la base de données
    // Envoyer notification Telegram
  }

  return new Response(JSON.stringify({ received: true }), {
    headers: { 'Content-Type': 'application/json' },
    status: 200
  })
})
```

**Variables d'environnement pour le webhook :**
```bash
WEBHOOK_SECRET=whsec_xxxxx
PAYMENT_API_KEY=pk_xxxxx
PAYMENT_API_SECRET=sk_xxxxx
TELEGRAM_BOT_TOKEN=8539115405:AAFxfimKuOeVKqYL5mQaclVsQ5Lh2hIcIok
TELEGRAM_CHAT_ID=1646298746
```

### 📊 Tables Principales (Suggestions)

**Tables pour les paiements :**
```sql
CREATE TABLE payments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  provider_payment_id VARCHAR UNIQUE,
  amount DECIMAL(10, 2),
  currency VARCHAR(3),
  status VARCHAR(50),
  customer_email VARCHAR,
  customer_phone VARCHAR,
  device_id VARCHAR,
  metadata JSONB,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE webhook_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  event_type VARCHAR,
  source_ip VARCHAR,
  payload JSONB,
  response_status INTEGER,
  response_body TEXT,
  error_message TEXT,
  processed_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### 🛡️ RLS (Row Level Security)

**Activer RLS sur une table :**
```sql
ALTER TABLE payments ENABLE ROW LEVEL SECURITY;
```

**Créer une policy :**
```sql
CREATE POLICY "Users can view their own payments"
ON payments
FOR SELECT
USING (auth.uid()::text = user_id::text);
```

### 🔐 Authentification Supabase

**Configuration JWT :**
```python
# Dans settings.py ou .env
SUPABASE_URL = "https://qfkyzljqykymahlpmdnu.supabase.co"
SUPABASE_ANON_KEY = "eyJ...g_Rmxo8lY8KAnrQqyzcz0PLh03T1M7_RuBUQT6ObtXg"
SUPABASE_JWT_SECRET = "ojdJ5aNShf27eP0g+XNMdKAWlGZRdW1BjJtSPajmpOp/..."
JWT_EXPIRY = 604800  # 7 jours
```

**Vérifier un JWT en Python :**
```python
import jwt
import requests

def verify_supabase_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            "ojdJ5aNShf27eP0g+XNMdKAWlGZRdW1BjJtSPajmpOp/od2aX2XRzdD02d6b7p5kak/pMUottx+QVaVNemmxJw==",
            algorithms=["HS256"],
            audience="authenticated"
        )
        return payload
    except jwt.InvalidTokenError:
        return None
```

### 📱 Intégration Django + Supabase

**Dans settings.py :**
```python
# Supabase configuration
SUPABASE_CONFIG = {
    'url': 'https://qfkyzljqykymahlpmdnu.supabase.co',
    'anon_key': env('SUPABASE_ANON_KEY'),
    'service_key': env('SUPABASE_SERVICE_KEY'),
    'jwt_secret': env('SUPABASE_JWT_SECRET'),
}
```

**Utiliser le client Supabase :**
```python
from supabase import create_client

supabase = create_client(
    'https://qfkyzljqykymahlpmdnu.supabase.co',
    'eyJ...g_Rmxo8lY8KAnrQqyzcz0PLh03T1M7_RuBUQT6ObtXg'
)

# Interroger une table
response = supabase.table('payments').select('*').execute()
```

### 🚨 Sécurité - Ne JAMAIS Committer

```
❌ Database Password (RK8AY46O3WhOlwrA)
❌ Service Role Key
❌ JWT Secret
❌ Webhook Secret
❌ Clés API de paiement
```

**Fichier .gitignore à mettre à jour :**
```
.env.supabase
supabase/.env
*.supabase-secret
```

---

## 🌐 ACCÈS RAPIDES

| Environnement | URL | Admin |
|---------------|-----|-------|
| **Gosen Filter** | http://72.62.181.239:8082/ | http://72.62.181.239:8082/admin/ |
| **Hippique Prod** | http://72.62.181.239:8083/ | http://72.62.181.239:8083/admin/ |
| **FiltreExpert** | http://72.62.181.239:8090/ | - |
| **Supabase** | https://supabase.com/dashboard/project/qfkyzljqykymahlpmdnu | https://qfkyzljqykymahlpmdnu.supabase.co |

### 🔗 Liens Utiles

- **Repository GitHub** : https://github.com/andypaypow/hippique-django.git
- **Hostinger VPS** : ssh -i ~/.ssh/id_ed25519 root@72.62.181.239
- **Supabase Dashboard** : https://supabase.com/dashboard/project/qfkyzljqykymahlpmdnu
- **Supabase Project** : https://qfkyzljqykymahlpmdnu.supabase.co

---

## 🛠️ COMMANDES UTILES

### Supabase CLI

```bash
# Installer Supabase CLI
npm install -g supabase

# Se connecter
supabase login

# Lier au projet
supabase link --project-ref qfkyzljqykymahlpmdnu

# Déployer une Edge Function
supabase functions deploy <function-name>

# Déployer avec variables d'environnement
supabase functions deploy <function-name> --env VAR=value

# Lister les Edge Functions
supabase functions list

# Voir les logs d'une fonction
supabase functions logs <function-name>

# Base de données
supabase db dump -f dump.sql
supabase db remote commit

# Ouvrir le dashboard dans le navigateur
supabase db inspect
```

### Docker

```bash
# Démarrer tous les conteneurs
docker compose -f docker-compose.dev.yml up -d

# Arrêter tous les conteneurs
docker compose -f docker-compose.dev.yml down

# Voir les logs
docker compose -f docker-compose.dev.yml logs -f

# Redémarrer un conteneur spécifique
docker compose -f docker-compose.dev.yml restart web
```

### Django

```bash
# Ouvrir un shell Django
docker compose -f docker-compose.dev.yml exec web python manage.py shell

# Créer un superutilisateur
docker compose -f docker-compose.dev.yml exec web python manage.py createsuperuser

# Collecter les fichiers statiques
docker compose -f docker-compose.dev.yml exec web python manage.py collectstatic --noinput
```

### Git

```bash
# Voir l'historique des commits
git log --oneline --graph --all

# Voir les branches
git branch -a

# Changer de branche
git checkout <nom_branche>
```

---

## ⚠️ PIÈGES À ÉVITER

1. **NE JAMAIS supprimer les volumes Docker sans sauvegarde** → `docker compose down -v` ❌
2. **JAMAIS modifier directement en prod** → Toujours passer par git
3. **TOUJOURS migrer** après changement de modèles
4. **JAMAIS committer de secrets** → .env, tokens, clés API
5. **En prod : TOUJOURS --build web** après pull
6. **TOUJOURS vérifier** les conteneurs après déploiement

### 🚨 Fichiers à NE JAMAIS COMMIT

```
.env / .env.dev / .env.prod
*.pyc
__pycache__
.github_token
db.sqlite3
*.bak
*.log
.pytest_cache
.coverage
.vscode/
.idea/
```

---

## 📝 STRUCTURE DU PROJET

```
hippique-django/
├── hippique/              # Application principale
│   ├── models/           # Modèles de données
│   ├── views/            # Vues et contrôleurs
│   ├── templates/        # Templates HTML
│   └── static/           # Fichiers statiques
├── hippique_project/     # Configuration Django
│   ├── settings.py       # Paramètres
│   ├── urls.py           # Routes
│   └── wsgi.py           # WSGI
├── docker-compose.dev.yml # Configuration Docker Dev
├── docker-compose.prod.yml # Configuration Docker Prod
├── Dockerfile            # Image Docker
├── nginx.conf            # Configuration Nginx Prod
├── nginx-dev.conf        # Configuration Nginx Dev
├── requirements.txt      # Dépendances Python
└── manage.py             # Script Django
```

---

---

## ÉTAPE 8 : FILTREEXPERT SUPABASE - FRONTEND STATIQUE

### 🎯 Projet FiltreExpert

**Projet :** filtreexpert-supabase
**Backend :** Supabase Edge Functions (Deno/TypeScript)
**Frontend :** HTML/CSS/JS statique

### 🌐 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Hostinger VPS                          │
│  IP : 72.62.181.239                                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────┐      ┌──────────────────┐        │
│  │ FiltreExpert Dev │      │   Supabase        │        │
│  │ Port : 8090       │ ───▶ │ Edge Functions   │        │
│  │ Static HTML/CSS/JS│      │ Backend logic    │        │
│  └──────────────────┘      └──────────────────┘        │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 📂 Structure du Projet

```
filtreexpert-supabase/
├── frontend/               # Frontend statique
│   ├── index.html         # Page principale
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css  # Styles
│   │   └── js/
│   │       └── app-bundle.js  # Logique frontend
│   └── img/               # Images
├── docker-compose.dev.yml # Docker Dev (port 8090)
├── nginx-filtreexpert.conf # Configuration nginx
└── start.bat              # Start local (Python HTTP)
```

### 🚀 Déploiement sur Hostinger

**Conteneur Docker :**
```bash
# Sur Hostinger
ssh -i ~/.ssh/id_ed25519 root@72.62.181.239

# Démarrer le conteneur
cd /root/filtreexpert-dev
docker compose -f docker-compose.dev.yml up -d

# Arrêter le conteneur
docker compose -f docker-compose.dev.yml down

# Vérifier les logs
docker logs filtreexpert-dev-nginx -f
```

### ⚡ Edge Functions Supabase

**Localisation des Edge Functions :**
```
hippique-django/supabase/functions/
├── turboquinte-filter/
│   └── index.ts           # Logique de filtrage
└── turboquinte-backtest/
    └── index.ts           # Logique de backtest
```

**Déployer les Edge Functions :**
```bash
# Se placer dans le dossier avec supabase
cd /path/to/hippique-django

# Déployer le filtre
supabase functions deploy turboquinte-filter

# Déployer le backtest
supabase functions deploy turboquinte-backtest

# Vérifier le déploiement
supabase functions list
```

**URL des Edge Functions :**
```
https://qfkyzljqykymahlpmdnu.supabase.co/functions/v1/turboquinte-filter
https://qfkyzljqykymahlpmdnu.supabase.co/functions/v1/turboquinte-backtest
```

### 📊 Types de Filturs Implémentés

**1. Filtres de Groupes (Min/Max)**
   - Vérifie le nombre de chevaux de chaque groupe dans une combinaison
   - Fonction : `filterByGroupMinMax()`

**2. Expert 1 (OR logic)**
   - Au moins X chevaux dans Y groupes
   - Fonction : `filterStandardOR()`

**3. Expert 2 (AND logic)**
   - X chevaux communs à Y groupes
   - Fonction : `filterAdvancedAND()`

**4. Filtres de Poids**
   - Sources : default, manual, citation, position, results, expert
   - Fonction : `filterByWeight()`

**5. Filtres Statistiques**
   - Pair/Impair : `filterByEvenOdd()`
   - Petit/Grand : `filterBySmallLarge()`
   - Consécutifs : `filterByConsecutive()`

**6. Filtres d'Alternance**
   - Sources : default, manual, citation, position, results, expert
   - Fonction : `filterByAlternance()`

### 📈 Synthèses Calculées

**1. Synthèse par Citation**
   - Classement par nombre d'apparitions dans les groupes

**2. Synthèse par Position**
   - Classement pondéré par la position dans chaque groupe

**3. Synthèse des Résultats**
   - Classement par fréquence dans les combinaisons filtrées

**4. Synthèse Expert**
   - Classement global pondéré (citation + position + résultats)

### 🔧 Développement Local

**Avec Python HTTP Server :**
```bash
# Windows
cd C:\Users\HP 360\Desktop\filtreexpertsupabase
start.bat

# Manuel
cd frontend
python -m http.server 8090 --bind 127.0.0.1
```

**Accès local :**
- URL : http://localhost:8090/
- Frontend : HTML/CSS/JS statique
- Backend : Supabase Edge Functions

### 🌐 URLs de Déploiement

| Environnement | URL |
|---------------|-----|
| **Local** | http://localhost:8090/ |
| **Hostinger Dev** | http://72.62.181.239:8090/ |
| **Supabase Filter** | https://qfkyzljqykymahlpmdnu.supabase.co/functions/v1/turboquinte-filter |
| **Supabase Backtest** | https://qfkyzljqykymahlpmdnu.supabase.co/functions/v1/turboquinte-backtest |

### 📝 Configuration Frontend

**Fichier :** `frontend/static/js/app-bundle.js`

```javascript
const SUPABASE_CONFIG = {
    url: 'https://qfkyzljqykymahlpmdnu.supabase.co',
    anonKey: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
};
```

### 🔑 Appels API Supabase

**Exemple d'appel au filtre :**
```javascript
const response = await fetch(`${SUPABASE_CONFIG.url}/functions/v1/turboquinte-filter`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${SUPABASE_CONFIG.anonKey}`,
        'apikey': SUPABASE_CONFIG.anonKey
    },
    body: JSON.stringify(requestData)
});
```

### 🚨 Sécurité

- **Anon Key** : Utilisable côté client (publique)
- **Service Role Key** : Jamais côté client (admin only)
- **RLS** : Configurer sur les tables si nécessaire
- **CORS** : Configuré dans les Edge Functions

### 🚀 Déploiement Production

**Conteneur Prod sur port 8091 :**
```bash
# Sur Hostinger
cd /root/filtreexpert-prod
docker compose -f docker-compose.prod.yml up -d
```

**Configuration docker-compose.prod.yml :**
```yaml
version: '3.8'
services:
  nginx:
    image: nginx:alpine
    container_name: filtreexpert-prod-nginx
    ports:
      - "8091:80"
    volumes:
      - ./frontend:/usr/share/nginx/html:ro
      - ./nginx-filtreexpert.conf:/etc/nginx/conf.d/default.conf:ro
    restart: unless-stopped
    networks:
      - filtreexpert-network
```

**Différences Dev vs Prod :**
| Environnement | Port | Chemin Hostinger | Branche Git |
|--------------|------|------------------|-------------|
| Dev | 8090 | /root/filtreexpert-dev | dev |
| Prod | 8091 | /root/filtreexpert-prod | prod |

---

## ÉTAPE 9 : FILTREEXPERT - SYSTÈME DE PAIEMENT SUPABASE

### 💳 Architecture du Système de Paiement

```
┌─────────────────────────────────────────────────────────────┐
│                    Flux de Paiement FiltreExpert            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Utilisateur → Bouton "S'abonner (100F/jour)"           │
│  2. Redirection vers Cyberschool (lien de paiement)        │
│  3. Paiement réussi (code "200")                            │
│  4. Cyberschool → Webhook Supabase                          │
│  5. Webhook → Crée abonnement dans Supabase DB              │
│  6. Webhook → Notification Telegram @Filtrexpert_bot        │
│  7. Frontend → Vérifie abonnement → Affiche résultats       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 🔗 URLs Importantes

| Élément | URL |
|---------|-----|
| **Lien de paiement Cyberschool** | `https://sumb.cyberschool.ga/?productId=KzIfBGUYU6glnH3JlsbZ&operationAccountCode=ACC_6835C458B85FF&maison=moov&amount=100` |
| **Webhook Cyberschool → Supabase** | `https://qfkyzljqykymahlpmdnu.supabase.co/functions/v1/webhook-cyberschool` |
| **Bot Telegram FiltreExpert** | `@Filtrexpert_bot` |

### 🔑 Identifiants Telegram FiltreExpert

```
Bot Token: 8547430409:AAGx2LxGxP6fBd9mn13LSmRbU4y3wlopIq4
Chat ID: 1646298746
Bot Username: @Filtrexpert_bot
```

**Note :** Ces identifiants sont différents de ceux du projet Educalims (hippique-django).

### 🗄️ Table subscriptions (Supabase)

**Structure de la table :**
```sql
CREATE TABLE subscriptions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  device_id TEXT UNIQUE NOT NULL,
  jwt_token TEXT UNIQUE NOT NULL,
  payment_status TEXT DEFAULT 'pending',
  transaction_id TEXT,
  phone_number TEXT,
  amount NUMERIC DEFAULT 100,
  payment_date TIMESTAMP WITH TIME ZONE,
  expiry_date TIMESTAMP WITH TIME ZONE,
  fingerprint_data JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index
CREATE INDEX idx_subscriptions_device_id ON subscriptions(device_id);
CREATE INDEX idx_subscriptions_jwt_token ON subscriptions(jwt_token);
CREATE INDEX idx_subscriptions_expiry ON subscriptions(expiry_date);
```

**Logique d'abonnement :**
- Un device_id = un abonnement
- L'abonnement expire à 23h59 le jour du paiement
- Renouvellement quotidien requis (100F/jour)
- Device fingerprinting pour lier l'appareil à l'abonnement

### ⚡ Edge Functions Déployées

**Fonctions actives sur Supabase :**
```
1. webhook-cyberschool    - Reçoit les notifications Cyberschool
2. verify-access          - Vérifie si un device a un abonnement actif
3. turboquinte-filter     - Filtre les combinaisons (avec vérif abonnement)
4. turboquinte-backtest   - Backtest des combinaisons (avec vérif abonnement)
5. create-table           - Fonction temporaire pour créer des tables
```

**Déployer une Edge Function depuis Hostinger :**
```bash
# SSH vers Hostinger
ssh -i ~/.ssh/id_ed25519 root@72.62.181.239

# Créer le dossier temporaire
mkdir -p /tmp/supabase-deploy/supabase/functions/<function-name>

# Copier le fichier
cat > /tmp/supabase-deploy/supabase/functions/<function-name>/index.ts < <local-file>

# Déployer
cd /tmp/supabase-deploy && ~/.local/bin/supabase functions deploy <function-name> --project-ref qfkyzljqykymahlpmdnu
```

**Token d'accès Supabase CLI (sur Hostinger) :**
```bash
# Chemin du token
/root/.supabase/access-token

# Contenu
sbp_2f96bd8c55c691ea2a3af1b65fe86359d42146b9
```

### 🔐 Sécurité et Authentification

**Device Fingerprinting (Frontend) :**
```javascript
// Généré à partir de :
// - User agent
// - Screen resolution
// - Timezone
// - Platform
// - Language
// - Color depth
// - Device memory
// - Hardware concurrency

const deviceId = generateDeviceId(); // Stocké dans localStorage
```

**Vérification d'abonnement (Backend) :**
```typescript
// Dans turboquinte-filter et turboquinte-backtest
const accessCheck = await verifySubscription(deviceId, jwtToken);

if (!accessCheck.hasAccess) {
  return new Response(JSON.stringify({
    error: 'Abonnement requis',
    message: 'Aucun abonnement actif. Veuillez effectuer un paiement.',
    payment_link: PAYMENT_LINK
  }), { status: 403 });
}
```

### 📡 Notification Telegram

**Format de la notification envoyée :**
```
🎉 NOUVEL ABONNEMENT FILTREEXPERT

💰 Montant: 100 F
📱 Tel: +229XXXXXXXX
🔐 Device ID: abc12345...
⏰ Expire: 29/01/2026 23:59:59

Transaction ID: TX-1234567890
```

### 🌐 Configuration Frontend

**Fichiers frontend (filtreexpertsupabase/frontend/) :**
```
index.html              - Page principale avec section abonnement
static/css/style.css    - Styles pour la section abonnement
static/js/app-bundle.js - Logique de vérification d'abonnement
```

**Section abonnement dans index.html :**
```html
<div class="card subscription-card" id="subscription-section">
  <h2>💎 Abonnement Requis</h2>
  <div class="subscription-warning">
    <p>⚠️ L'affichage des combinaisons nécessite un abonnement journalier (100F).</p>
    <p class="device-warning">📱 L'abonnement est lié UNIQUEMENT à cet appareil.</p>
  </div>
  <a href="https://sumb.cyberschool.ga/?..." class="payment-btn">
    💳 S'abonner (100F/jour)
  </a>
</div>
```

**Polling automatique (toutes les 30s) :**
```javascript
// Vérifie automatiquement l'abonnement toutes les 30 secondes
// Arrête le polling quand l'abonnement est détecté comme actif
startSubscriptionPolling();
```

### 🔧 Gestion via API Supabase

**Exécuter du SQL via l'API Management :**
```bash
# Créer une table
curl -X POST "https://api.supabase.com/v1/projects/qfkyzljqykymahlpmdnu/database/query" \
  -H "Authorization: Bearer sbp_2f96bd8c55c691ea2a3af1b65fe86359d42146b9" \
  -H "Content-Type: application/json" \
  -d '{"query": "CREATE TABLE IF NOT EXISTS ..."}'

# Vérifier une table
curl -X POST "https://api.supabase.com/v1/projects/qfkyzljqykymahlpmdnu/database/query" \
  -H "Authorization: Bearer sbp_2f96bd8c55c691ea2a3af1b65fe86359d42146b9" \
  -d '{"query": "SELECT * FROM subscriptions LIMIT 10;"}'
```

**Lister les Edge Functions déployées :**
```bash
curl -s "https://api.supabase.com/v1/projects/qfkyzljqykymahlpmdnu/functions" \
  -H "Authorization: Bearer sbp_2f96bd8c55c691ea2a3af1b65fe86359d42146b9"
```

### ⚠️ Points d'Attention

1. **Device Binding** : L'abonnement est lié à l'appareil. Changer d'appareil = perdra l'accès
2. **Expiration quotidienne** : L'abonnement expire à 23h59 le jour du paiement
3. **Paiement obligatoire** : Sans abonnement actif, les combinaisons ne s'affichent pas (403)
4. **Polling automatique** : Le frontend vérifie automatiquement l'abonnement toutes les 30s
5. **Telegram FiltreExpert** : Bot différent du bot Educalims (@Filtrexpert_bot)

### 🚨 Résolution de Problèmes

**Problème : Les combinaisons s'affichent sans abonnement**
- **Cause** : La table `subscriptions` n'existe pas
- **Solution** : Créer la table via l'API Management ou le Dashboard Supabase

**Problème : Notifications Telegram sur le mauvais bot**
- **Cause** : TELEGRAM_CHAT_ID mal configuré
- **Solution** : Vérifier que webhook-cyberschool utilise `1646298746` et `8547430409:AAGx2LxGxP6fBd9mn13LSmRbU4y3wlopIq4`

**Problème : 403 sur appel API**
- **Cause** : Pas d'abonnement ou device_id invalide
- **Solution** : Vérifier que l'utilisateur a payé et que le device_id correspond

---

## ÉTAPE 10 : GOSEN FILTER - PROJET TURFFILTER

### 🎯 Projet Gosen TurfFilter

**Projet :** gosen-filter-dev
**Port :** 8082
**Chemin Hostinger :** `/root/gosen-filter-dev`
**Conteneur :** `gosen-dev-web`

### 🌐 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Hostinger VPS                          │
│  IP : 72.62.181.239                                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────┐      ┌──────────────────┐        │
│  │ Gosen Filter Dev │      │   PostgreSQL      │        │
│  │ Port : 8082       │ ───▶ │ gosen_dev         │        │
│  │ Django + Gunicorn │      │ Port : 5432       │        │
│  └──────────────────┘      └──────────────────┘        │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 📂 Structure du Projet

```
gosen-filter-dev/
├── gosen/                 # Application principale
│   ├── models.py         # Modèles de données
│   ├── views.py          # Vues API
│   ├── templates/        # Templates HTML
│   └── static/           # Fichiers statiques
├── gosen_project/        # Configuration Django
│   ├── settings.py       # Paramètres
│   ├── urls.py           # Routes
│   └── wsgi.py           # WSGI
├── docker-compose.dev.yml # Configuration Docker
├── Dockerfile            # Image Docker
├── requirements.txt      # Dépendances Python
└── manage.py             # Script Django
```

### ⚡ Conteneurs Docker

```bash
# Vérifier l'état des conteneurs
ssh -i ~/.ssh/id_ed25519 root@72.62.181.239 "docker ps | grep gosen"

# Voir les logs
ssh -i ~/.ssh/id_ed25519 root@72.62.181.239 "docker logs gosen-dev-web -f"

# Redémarrer le conteneur
ssh -i ~/.ssh/id_ed25519 root@72.62.181.239 "docker restart gosen-dev-web"
```

### 🔧 Commandes Django

```bash
# Collecter les fichiers statiques
ssh -i ~/.ssh/id_ed25519 root@72.62.181.239 "docker exec gosen-dev-web python manage.py collectstatic --noinput"

# Créer un superutilisateur
ssh -i ~/.ssh/id_ed25519 root@72.62.181.239 "docker exec gosen-dev-web python manage.py createsuperuser"

# Appliquer les migrations
ssh -i ~/.ssh/id_ed25519 root@72.62.181.239 "docker exec gosen-dev-web python manage.py migrate"

# Ouvrir un shell Django
ssh -i ~/.ssh/id_ed25519 root@72.62.181.239 "docker exec -it gosen-dev-web python manage.py shell"
```

### 🌐 URLs d'Accès

| Élément | URL |
|---------|-----|
| **Application** | http://72.62.181.239:8082/ |
| **Admin Django** | http://72.62.181.239:8082/admin/ |

### 🚨 PROBLÈME : Interface Admin Sans CSS

**Symptôme :**
- L'interface admin s'affiche mais sans le style CSS de Django
- Le contenu HTML est là mais pas les fichiers statiques (CSS, JS, images)

**Cause :**
Le conteneur utilise **Gunicorn directement** sans nginx pour servir les fichiers statiques. En production, Django ne sert pas les fichiers statiques par défaut.

### ✅ SOLUTION : Whitenoise

**Étape 1 : Installer Whitenoise**
```bash
docker exec gosen-dev-web pip install whitenoise
```

**Étape 2 : Configurer Django (settings.py)**

Ajouter Whitenoise dans les middlewares, **juste après** `SecurityMiddleware` :

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ← AJOUTER ICI
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # ... autres middlewares
]
```

Ajouter la configuration de stockage statique :

```python
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

**Étape 3 : Collecter les fichiers statiques**
```bash
docker exec gosen-dev-web python manage.py collectstatic --noinput
```

**Étape 4 : Redémarrer le conteneur**
```bash
docker restart gosen-dev-web
```

### 📋 Ordre Correct des Middlewares

⚠️ **IMPORTANT** : L'ordre des middlewares est critique pour que Whitenoise fonctionne :

```python
MIDDLEWARE = [
    # 1. Sécurité (DOIT être premier)
    'django.middleware.security.SecurityMiddleware',

    # 2. Fichiers statiques (DOIT être juste après SecurityMiddleware)
    'whitenoise.middleware.WhiteNoiseMiddleware',

    # 3. CORS (après Whitenoise pour ne pas bloquer les statiques)
    'corsheaders.middleware.CorsMiddleware',

    # 4. Autres middlewares Django
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # ...
]
```

### 🔍 Vérifier que les statiques sont servis

```bash
# Tester l'accès aux fichiers statiques
curl -I http://72.62.181.239:8082/static/admin/css/base.css

# Doit retourner HTTP 200 avec Content-Type: text/css
```

### 📝 Configuration Complète de settings.py

```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-gosen-dev-change-in-production')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'gosen',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ... reste de la configuration

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
```

### 🚨 Résolution de Problèmes

**Problème : Les fichiers statiques retournent 404**
- **Cause** : Mauvais ordre des middlewares
- **Solution** : Vérifier que Whitenoise est juste après SecurityMiddleware

**Problème : L'admin affiche du HTML sans style**
- **Cause** : Whitenoise n'est pas installé ou pas configuré
- **Solution** : Installer whitenoise et configurer les middlewares

**Problème : Après modification, les changements ne s'appliquent pas**
- **Cause** : Le conteneur doit être redémarré
- **Solution** : `docker restart gosen-dev-web`

---

**Dernière mise à jour** : 29 Janvier 2026
**Projet** : Hippique - Plateforme de pronostics hippiques + FiltreExpert Supabase + Gosen TurfFilter
**Repository** : https://github.com/andypaypow/hippique-django.git
**VPS** : Hostinger (72.62.181.239)
**Supabase** : https://qfkyzljqykymahlpmdnu.supabase.co
