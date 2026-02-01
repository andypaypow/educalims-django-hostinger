# Deploy Gosen DEV (8082) → GitHub → PROD (8083)

## 🎯 Objectif

Déployer les changements du port 8082 (DEV) vers le port 8083 (PROD) en passant par GitHub.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Workflow de déploiement                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1️⃣ PORT 8082 (DEV)                                      │
│     /root/gosen-filter-dev/                                │
│     Modifications testées                                 │
│           │                                                  │
│           │ git add, commit, push                          │
│           ▼                                                  │
│  2️⃣ GITHUB - Branche 'dev'                                │
│     https://github.com/andypaypow/educalims-django-hostinger│
│           │                                                  │
│           │ git checkout prod && git merge dev              │
│           ▼                                                  │
│  3️⃣ GITHUB - Branche 'prod'                               │
│           │                                                  │
│           │ git pull (sur le serveur)                      │
│           ▼                                                  │
│  4️⃣ PORT 8083 (PROD)                                      │
│     /root/gosen-prod/                                       │
│     docker compose build + up -d                          │
│     Application déployée                                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Processus complet

### Étape 1 : Vérifier les changements sur DEV

```bash
# Se connecter au serveur
ssh -i ~/.ssh/id_ed25519 root@72.62.181.239

# Vérifier que tout fonctionne sur 8082
curl -s http://localhost:8082/ | grep -E '(config-card|pronostics-card)'
curl -s -X POST http://localhost:8082/api/filter/ \
  -H "Content-Type: application/json" \
  -d '{"n":16,"k":6,"groups":[],"orFilters":[]}'
```

---

### Étape 2 : Committer sur DEV

Depuis votre **machine locale** :

```bash
cd C:\Users\HP 360\Desktop\hippique-django

# Créer les dossiers nécessaires s'ils n'existent pas
mkdir -p gosen\templates\gosen\auth
mkdir -p gosen\static\gosen\css
mkdir -p gosen\static\gosen\js

# Télécharger les fichiers modifiés depuis DEV
scp -i ~/.ssh/id_ed25519 root@72.62.181.239:/root/gosen-filter-dev/gosen/views/filters.py gosen/views/
scp -i ~/.ssh/id_ed25519 root@72.62.181.239:/root/gosen-filter-dev/gosen/views/auth.py gosen/views/
scp -i ~/.ssh/id_ed25519 root@72.62.181.239:/root/gosen-filter-dev/gosen/models.py gosen/
scp -i ~/.ssh/id_ed25519 root@72.62.181.239:/root/gosen-filter-dev/gosen/urls.py gosen/
scp -i ~/.ssh/id_ed25519 root@72.62.181.239:/root/gosen-filter-dev/gosen/templates/gosen/base.html gosen/templates/gosen/
scp -i ~/.ssh/id_ed25519 root@72.62.181.239:/root/gosen-filter-dev/gosen/templates/gosen/auth/login.html gosen/templates/gosen/auth/
scp -i ~/.ssh/id_ed25519 root@72.62.181.239:/root/gosen-filter-dev/gosen/static/gosen/css/styles.css gosen/static/gosen/css/
scp -i ~/.ssh/id_ed25519 root@72.62.181.239:/root/gosen-filter-dev/gosen/static/gosen/js/main.js gosen/static/gosen/js/

# Se placer sur la branche dev
git checkout dev

# Ajouter les modifications
git add gosen/
git add .claude/skills/

# Committer
git commit -m "description des changements

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: GLM 4.6 <noreply@z.ai>"

# Pousser vers dev
git push origin dev
```

---

### Étape 3 : Merger dev dans prod

```bash
# Sur votre machine locale
cd C:\Users\HP 360\Desktop\hippique-django

# Mettre à jour prod
git checkout prod
git pull origin prod

# Merger dev dans prod
git merge dev

# Pousser vers prod
git push origin prod
```

---

### Étape 4 : Déployer sur PROD (8083)

⚠️ **POINT CRITIQUE** : Le conteneur PROD utilise `build: .` dans docker-compose, ce qui signifie que les fichiers sont **copiés dans l'image Docker au build**. Les fichiers modifiés ne sont pas pris en compte tant qu'on ne reconstruit pas l'image !

```bash
# Se connecter au serveur
ssh -i ~/.ssh/id_ed25519 root@72.62.181.239

# Option 1 : Si gosen-prod est un dépôt git
cd /root/gosen-prod
git pull origin prod
# ⚠️ IMPORTANT : Reconstruire l'image Docker pour copier les nouveaux fichiers
docker compose -f docker-compose.prod.yml build web
docker compose -f docker-compose.prod.yml up -d --force-recreate

# Option 2 : Si gosen-prod n'est PAS un dépôt git (méthode rsync)
cd /root/gosen-prod
docker compose -f docker-compose.prod.yml down
rsync -av --delete \
  --exclude '*.pyc' \
  --exclude '__pycache__' \
  --exclude '.git' \
  --exclude 'postgres_data' \
  --exclude 'staticfiles' \
  --exclude 'db.sqlite3' \
  /root/gosen-filter-dev/ /root/gosen-prod/
# ⚠️ IMPORTANT : Reconstruire l'image Docker pour copier les nouveaux fichiers
docker compose -f docker-compose.prod.yml build web
docker compose -f docker-compose.prod.yml up -d --force-recreate
```

**Pourquoi `build web` est OBLIGATOIRE ?**

Le `docker-compose.prod.yml` contient :
```yaml
web:
  build: .    # ← Construit l'image depuis le Dockerfile
  ...
```

Le `Dockerfile` copie les fichiers dans l'image :
```dockerfile
COPY . /code    # ← Copie tous les fichiers au build
```

**Sans `build web`**, le conteneur utilise l'ancienne image avec les anciens fichiers !

---

### Étape 5 : Vérifier le déploiement

```bash
# Attendre que les conteneurs démarrent
sleep 15

# Vérifier les conteneurs
docker ps | grep gosen

# Tester l'application
curl -s -o /dev/null -w "HTTP: %{http_code}\n" http://localhost:8083/
curl -s http://localhost:8083/ | grep -E '(config-card|pronostics-card)'

# Tester l'API
curl -s -X POST http://localhost:8083/api/filter/ \
  -H "Content-Type: application/json" \
  -d '{"n":16,"k":6,"groups":[],"orFilters":[]}' | head -c 100

# Vérifier les logs si nécessaire
docker logs gosen-prod-web --tail 20
```

---

## 🔑 Configuration SSH GitHub (Si le serveur n'a pas accès)

### Afficher la clé SSH publique du serveur

```bash
# Se connecter au serveur
ssh -i ~/.ssh/id_ed25519 root@72.62.181.239

# Afficher la clé SSH publique
cat ~/.ssh/id_ed25519.pub
```

### Ajouter la clé à GitHub

1. Copiez la clé affichée (commence par `ssh-ed25519` ou `ssh-rsa`)
2. Allez sur https://github.com/settings/keys
3. Cliquez sur **"New SSH key"**
4. Titre : `Hostinger Server` ou `VPS Hostinger`
5. Collez la clé dans le champ "Key"
6. Cliquez sur **"Add SSH key"**

### Tester la connexion

```bash
# Depuis le serveur
ssh -T git@github.com

# Réponse attendue :
# Hi <username>! You've successfully authenticated...
```

### Si la clé SSH ne fonctionne pas

Utilisez un **GitHub Personal Access Token** :

1. Allez sur https://github.com/settings/tokens
2. Cliquez sur **"Generate new token"** → **"Generate new token (classic)"**
3. Cochez `repo` (accès complet aux dépôts)
4. Cliquez sur **"Generate token"**
5. Copiez le token (ne s'affiche qu'une seule fois)

```bash
# Utiliser le token pour le push
cd /root/gosen-filter-dev
git remote set-url origin https://<TOKEN>@github.com/andypaypow/educalims-django-hostinger.git
git push origin dev
```

---

## 🔧 Script de déploiement rapide

Depuis votre **machine locale**, après avoir téléchargé les fichiers depuis DEV :

```bash
cd C:\Users\HP 360\Desktop\hippique-django

# Commit et push sur dev
git checkout dev
git add gosen/
git commit -m "message"
git push origin dev

# Merge et push sur prod
git checkout prod
git pull origin prod
git merge dev
git push origin prod

# Déploiement sur PROD (via SSH)
ssh -i ~/.ssh/id_ed25519 root@72.62.181.239 << 'ENDSSH'
cd /root/gosen-prod
docker compose -f docker-compose.prod.yml down
rsync -av --delete \
  --exclude '*.pyc' \
  --exclude '__pycache__' \
  --exclude '.git' \
  --exclude 'postgres_data' \
  --exclude 'staticfiles' \
  /root/gosen-filter-dev/ /root/gosen-prod/
# ⚠️ CRITIQUE : Reconstruire l'image Docker après modification de fichiers
docker compose -f docker-compose.prod.yml build web
docker compose -f docker-compose.prod.yml up -d --force-recreate
echo "Déploiement terminé !"
ENDSSH
```

---

## 📝 Types de commits

Utilisez des préfixes clairs pour vos messages de commit :

- `feat:` Nouvelle fonctionnalité
  ```bash
  git commit -m "feat: ajouter le filtrage par alternance"
  ```

- `fix:` Correction de bug
  ```bash
  git commit -m "fix: corriger l'affichage des résultats"
  ```

- `refactor:` Refactorisation
  ```bash
  git commit -m "refactor: séparer HTML, CSS et JS"
  ```

- `deploy:` Déploiement
  ```bash
  git commit -m "deploy: calculs côté serveur"
  ```

---

## ⚡ Commandes rapides

### Vérifier l'état des branches

```bash
# Local
git status
git branch -a
git log --oneline -5

# Distant
git fetch origin
git log origin/dev --oneline -5
git log origin/prod --oneline -5
```

### Annuler un commit (avant push)

```bash
# Soft reset (garde les changements)
git reset --soft HEAD~1

# Hard reset (supprime les changements)
git reset --hard HEAD~1
```

### Résoudre les conflits de merge

```bash
# Si conflit lors du merge
git merge dev

# Éditer les fichiers avec conflits
# Chercher <<<<<<<, =======, >>>>>>

# Après résolution
git add fichier.py
git merge --continue

# Ou annuler
git merge --abort
```

---

## 🚨 Résolution de problèmes

### Les conteneurs ne démarrent pas

```bash
# Vérifier les logs
docker logs gosen-prod-web

# Reconstruire complètement
cd /root/gosen-prod
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.prod.yml up -d --force-recreate
```

### L'API renvoie 404 ou l'ancienne version est toujours utilisée

⚠️ **Problème courant** : L'API renvoie 404 ou les modifications ne sont pas prises en compte.

**Cause** : L'image Docker n'a pas été reconstruite. Le conteneur utilise l'ancienne image.

**Solution** : Reconstruire l'image Docker
```bash
cd /root/gosen-prod

# ⚠️ CRITIQUE : Toujours reconstruire l'image après modification de fichiers Python
docker compose -f docker-compose.prod.yml build web

# Recréer les conteneurs
docker compose -f docker-compose.prod.yml up -d --force-recreate
```

**Pourquoi ?**
- `build: .` dans docker-compose copie les fichiers dans l'image au build
- `docker restart` ne met pas à jour les fichiers dans l'image
- `docker up` sans `--build` utilise l'image existante

### ⚡ Commande de reconstruction complète

```bash
# One-liner pour reconstruire tout
cd /root/gosen-prod && \
  docker compose -f docker-compose.prod.yml down && \
  docker compose -f docker-compose.prod.yml build --no-cache web && \
  docker compose -f docker-compose.prod.yml up -d --force-recreate
```

### Erreur de migration

```bash
# Vérifier les migrations
docker exec gosen-prod-web python manage.py showmigrations

# Appliquer les migrations
docker exec gosen-prod-web python manage.py migrate
```

### Les fichiers statiques ne sont pas à jour

```bash
# Collecter les fichiers statiques
docker exec gosen-prod-web python manage.py collectstatic --noinput

# Redémarrer
docker restart gosen-prod-web
```

### Erreur CSRF 403 avec nginx reverse proxy

⚠️ **Problème** : `Interdit (403) - La vérification CSRF a échoué` lors de la connexion à l'admin via un domaine (ex: `https://filtreexpert.org`).

**Cause** : Django n'a pas le domaine dans `CSRF_TRUSTED_ORIGINS` et ne fait pas confiance au proxy SSL.

**Solution complète** :

#### 1. Modifier `docker-compose.prod.yml`

Ajouter TOUS les domaines utilisés (HTTP et HTTPS) dans `CSRF_TRUSTED_ORIGINS` :

```yaml
web:
  environment:
    - CSRF_TRUSTED_ORIGINS=http://72.62.181.239:8083,http://localhost:8083,http://dev.filtreexpert.org,https://dev.filtreexpert.org,http://filtreexpert.org,https://filtreexpert.org
```

#### 2. Modifier `gosen_project/settings.py`

Ajouter la configuration de confiance du proxy SSL :

```python
# Proxy SSL settings - TRUST HTTPS from nginx proxy
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True

# Disable secure cookies when behind proxy (nginx handles SSL)
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

# CSRF settings - Allow both HTTP and HTTPS origins
CSRF_TRUSTED_ORIGINS = os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',') if os.environ.get('CSRF_TRUSTED_ORIGINS') else [
    'http://72.62.181.239:8082',
    'http://localhost:8082',
    'http://72.62.181.239:8083',
    'http://localhost:8083',
    'http://dev.filtreexpert.org',
    'https://dev.filtreexpert.org',
    'http://filtreexpert.org',
    'https://filtreexpert.org',
]
```

#### 3. Reconstruire l'image Docker

⚠️ **CRITIQUE** : Les fichiers sont copiés dans l'image Docker au build. Il faut reconstruire :

```bash
cd /root/gosen-prod
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml build web
docker compose -f docker-compose.prod.yml up -d
```

#### 4. Vérifier la configuration

```bash
# Vérifier les paramètres Django dans le conteneur
docker exec gosen-prod-web python manage.py shell -c "from django.conf import settings; print('CSRF_TRUSTED_ORIGINS:', settings.CSRF_TRUSTED_ORIGINS)"
```

**Pourquoi ce problème ?**

- Le conteneur Django reçoit des requêtes du nginx via HTTP interne
- Mais l'utilisateur accède via HTTPS (ex: `https://filtreexpert.org`)
- Django voit une incohérence et rejette le cookie CSRF
- `SECURE_PROXY_SSL_HEADER` dit à Django de faire confiance au header `X-Forwarded-Proto` du nginx

---

## 🔄 Workflow visuel complet

```
┌─────────────────────────────────────────────────────────────┐
│                       Machine Locale                         │
│  C:\Users\HP 360\Desktop\hippique-django                    │
│                                                              │
│  1. Télécharger fichiers depuis DEV (8082)                 │
│  2. git checkout dev && git add && git commit               │
│  3. git push origin dev                                    │
│  4. git checkout prod && git merge dev                     │
│  5. git push origin prod                                   │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                         GitHub                              │
│  andypaypow/educalims-django-hostinger                     │
│                                                              │
│  dev (e4ffbc1) ──────────────────────────────┐             │
│       │                                     │               │
│       │ merge                              │               │
│       ▼                                     ▼               │
│  prod (95fdbe0) ◀──────────────────────────┘               │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   Serveur Hostinger                          │
│                  72.62.181.239                               │
│                                                              │
│  ┌─────────────────────┐      ┌─────────────────────┐     │
│  │   DEV (8082)        │      │   PROD (8083)       │     │
│  │                     │      │                     │     │
│  │ /root/gosen-        │      │ /root/gosen-prod/   │     │
│  │   filter-dev/       │◀─────│                     │     │
│  │                     │ rsync │                     │     │
│  │   Tests OK          │      │   git pull / rsync  │     │
│  └─────────────────────┘      │   docker build      │     │
│                               │   docker up          │     │
│                               │                     │     │
│                               │   Production OK      │     │
│                               └─────────────────────┘     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ Checklist de déploiement

Avant de déployer en production :

- [ ] Fonctionnalités testées sur DEV (8082)
- [ ] API `/api/filter/` fonctionne
- [ ] Pages principales s'affichent correctement
- [ ] Pas d'erreurs dans les logs `docker logs gosen-dev-web`
- [ ] Fichiers téléchargés depuis DEV vers local
- [ ] Commit créé avec message clair
- [ ] Push vers dev réussi
- [ ] Merge dev → prod réussi
- [ ] Push vers prod réussi
- [ ] Conteneurs PROD reconstruits
- [ ] Application PROD testée
- [ ] API PROD testée

---

## 📚 Skills connexes

- `reset-gosen-dev.md` : Reset DEV à partir de PROD
- `deploy-gosen-prod/` : Déploiement PROD détaillé
- `git-workflow/` : Workflow Git complet
- `server-side-calculations.md` : Calculs côté serveur

---

**Dernière mise à jour** : 31 Janvier 2026
**Projet** : Gosen TurfFilter
**Environnements** : DEV (8082) → GitHub → PROD (8083)
