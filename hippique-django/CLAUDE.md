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
| Dev | http://72.62.181.239:8082/ | http://72.62.181.239:8082/admin/ |
| Prod | http://72.62.181.239:8083/ | http://72.62.181.239:8083/admin/ |
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

**Dernière mise à jour** : 28 Janvier 2026
**Projet** : Hippique - Plateforme de pronostics hippiques + FiltreExpert Supabase
**Repository** : https://github.com/andypaypow/hippique-django.git
**VPS** : Hostinger (72.62.181.239)
**Supabase** : https://qfkyzljqykymahlpmdnu.supabase.co
