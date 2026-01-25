# 🚀 GUIDE DU DÉVELOPPEUR - Hippique TurbFilter

Guide complet pour les développeurs travaillant sur l'application Hippique sur Hostinger.

---

## 🌐 ACCÈS AU SERVEUR

### Connexion SSH

```bash
# Depuis Windows (Git Bash / PowerShell)
ssh -i "C:\Users\HP 360\.ssh\id_ed25519" root@72.62.181.239

# Depuis Linux / macOS
ssh -i ~/.ssh/id_ed25519 root@72.62.181.239
```

### Accès rapide aux applications

| Application | URL | Port | Chemin |
|-------------|-----|------|--------|
| **Educalims Dev** | http://72.62.181.239:8081/ | 8081 | /root/educalims-dev |
| **Educalims Prod** | http://72.62.181.239/ | 80 | /root/educalims-prod |
| **Hippique Dev** | http://72.62.181.239:8082/ | 8082 | /root/hippique-dev |
| **Hippique Prod** | http://72.62.181.239:8083/ | 8083 | /root/hippique-prod |

### Identifiants Admin Django

**Hippique Dev :**
- URL : http://72.62.181.239:8082/admin/
- Username : `admin`
- Password : `admin`

**Hippique Prod :**
- URL : http://72.62.181.239:8083/admin/
- Username : `admin`
- Password : `admin`

> ⚠️ **IMPORTANT** : Changez ces mots de passe après la première connexion !

---

## 📂 STRUCTURE DES PROJETS

### Hippique Dev

```bash
/root/hippique-dev/
├── docker-compose.dev.yml      # Configuration Docker Dev
├── .env.dev                    # Variables d'environnement Dev
├── nginx-dev.conf              # Configuration Nginx Dev
├── git-push.sh                 # Script pour pusher vers GitHub
└── code/                       # Code source (volume monté)
    ├── Dockerfile              # Image du conteneur
    ├── requirements.txt        # Dépendances Python
    ├── manage.py               # Gestion Django
    ├── hippique_project/       # Projet Django
    │   ├── settings.py         # Configuration Django
    │   ├── urls.py             # URLs racines
    │   └── wsgi.py             # WSGI config
    ├── hippie/                 # Application Django
    │   ├── models.py           # Modèles de données
    │   ├── views.py            # Vues et contrôleurs
    │   ├── urls.py             # URLs de l'app
    │   ├── admin.py            # Admin Django
    │   ├── forms.py            # Formulaires
    │   └── templates/          # Templates HTML
    ├── staticfiles/            # Fichiers statiques collectés
    └── media/                  # Fichiers uploadés
```

### Hippique Prod

```bash
/root/hippique-prod/
├── docker-compose.yml          # Configuration Docker Prod
├── .env.prod                   # Variables d'environnement Prod
└── code/                       # Code dans l'image Docker
```

---

## 🐳 COMMANDES DOCKER

### Hippique Dev

```bash
# Se déplacer dans le répertoire
cd /root/hippique-dev

# Démarrer les conteneurs
docker compose -f docker-compose.dev.yml up -d

# Arrêter les conteneurs
docker compose -f docker-compose.dev.yml down

# Voir l'état des conteneurs
docker compose -f docker-compose.dev.yml ps

# Voir les logs en temps réel
docker compose -f docker-compose.dev.yml logs -f

# Logs d'un conteneur spécifique
docker compose -f docker-compose.dev.yml logs -f web
docker compose -f docker-compose.dev.yml logs -f db

# Redémarrer un conteneur
docker compose -f docker-compose.dev.yml restart web
```

### Hippique Prod

```bash
# Se déplacer dans le répertoire
cd /root/hippique-prod

# Mêmes commandes mais SANS le -f docker-compose.dev.yml
docker compose up -d
docker compose down
docker compose ps
docker compose logs -f web
```

---

## 🗄️ BASE DE DONNÉES

### Connexion PostgreSQL

```bash
# Se connecter à la base Dev
docker compose -f /root/hippique-dev/docker-compose.dev.yml exec db psql -U hippique -d hippique_dev

# Se connecter à la base Prod
docker compose -f /root/hippique-prod/docker-compose.yml exec db psql -U hippique -d hippique_prod

# Exécuter une commande SQL directement
docker compose -f /root/hippique-dev/docker-compose.dev.yml exec -T db psql -U hippique -d hippique_dev -c "SELECT COUNT(*) FROM hippique_course;"
```

### Informations de connexion

| Environnement | Database | User | Password | Host | Port |
|--------------|----------|------|----------|------|------|
| **Dev** | hippique_dev | hippique | hippique_dev_password | db | 5432 |
| **Prod** | hippique_prod | hippique | hippique_prod_password | db | 5432 |

### Sauvegarde et restauration

```bash
# Sauvegarder la base Dev
cd /root/hippique-dev
docker compose -f docker-compose.dev.yml exec -T db pg_dump -U hippique hippique_dev > backups/backup_$(date +%Y%m%d_%H%M%S).sql

# Restaurer une sauvegarde
cat backups/backup_XXX.sql | docker compose -f docker-compose.dev.yml exec -T db psql -U hippique hippique_dev
```

---

## 🐍 DJANGO MANAGEMENT

### Commandes de base

```bash
# Se placer dans le répertoire Dev
cd /root/hippique-dev

# Créer des migrations après modification des modèles
docker compose -f docker-compose.dev.yml exec web python manage.py makemigrations

# Appliquer les migrations
docker compose -f docker-compose.dev.yml exec web python manage.py migrate

# Voir les migrations appliquées
docker compose -f docker-compose.dev.yml exec web python manage.py showmigrations

# Créer un superutilisateur
docker compose -f docker-compose.dev.yml exec web python manage.py createsuperuser

# Shell Django interactif
docker compose -f docker-compose.dev.yml exec web python manage.py shell

# Collecter les fichiers statiques
docker compose -f docker-compose.dev.yml exec web python manage.py collectstatic --noinput
```

### Commandes utiles dans le shell Django

```python
# Dans le shell Django
from django.contrib.auth.models import User

# Lister les utilisateurs
User.objects.all()

# Créer un superutilisateur
User.objects.create_superuser('username', 'email@example.com', 'password')

# Changer le mot de passe admin
user = User.objects.get(username='admin')
user.set_password('new_password')
user.save()

# Voir les modèles
from hippie.models import Course, PronosticGroupe
Course.objects.all()
```

---

## 🔧 DÉPLOIEMENT

### Workflow Dev → Prod

```bash
# 1. Travailler en DEV
cd /root/hippique-dev

# 2. Faire les modifications
# ... éditer les fichiers ...

# 3. Vérifier les changements
git status
git diff

# 4. Ajouter et committer
git add .
git commit -m "feat: description du changement"

# 5. Pusher vers GitHub
./git-push.sh

# 6. Merger dev → main
git checkout main
git merge dev
./git-push.sh

# 7. Déployer en PROD
cd /root/hippique-prod
git pull origin main

# 8. ⚠️ IMPORTANT : Rebuild le conteneur web
docker compose up -d --build web

# 9. Appliquer les migrations
docker compose exec web python manage.py migrate

# 10. Retourner sur dev
cd /root/hippique-dev
git checkout dev
```

### Script git-push.sh

Le script `git-push.sh` utilise le token GitHub stocké dans `/root/.github_token`.

```bash
# Pour changer le token
echo 'VOTRE_NOUVEAU_TOKEN' > /root/.github_token
chmod 400 /root/.github_token
```

---

## 🔍 DEBUGGING

### Vérifier l'état des services

```bash
# Vérifier tous les conteneurs
cd /root/hippique-dev
docker compose -f docker-compose.dev.yml ps

# Vérifier les ports ouverts
netstat -tulpn | grep -E "8082|8083"

# Tester la connexion à la base de données
docker compose -f docker-compose.dev.yml exec web python manage.py check

# Voir les erreurs dans les logs
docker compose -f docker-compose.dev.yml logs web | grep -i error
```

### Problèmes courants

**Conteneur web ne démarre pas :**
```bash
# Vérifier les logs
docker compose -f docker-compose.dev.yml logs web

# Rebuild le conteneur
docker compose -f docker-compose.dev.yml up -d --build web
```

**Erreur de connexion à la base :**
```bash
# Vérifier que db est running
docker compose -f docker-compose.dev.yml ps db

# Redémarrer db
docker compose -f docker-compose.dev.yml restart db
```

**Erreur de migration :**
```bash
# Voir les migrations en attente
docker compose -f docker-compose.dev.yml exec web python manage.py showmigrations

# Faire un fake migration si nécessaire
docker compose -f docker-compose.dev.yml exec web python manage.py migrate --fake
```

---

## 📊 STATUT DES SERVICES

### Vérifier tout d'un coup

```bash
# Commande de diagnostic complète
echo "=== HIPPIQUE DEV STATUS ===" && \
cd /root/hippique-dev && \
docker compose -f docker-compose.dev.yml ps && \
echo -e "\n=== TEST HTTP ===" && \
curl -I http://localhost:8082/ 2>/dev/null | head -1 && \
echo -e "\n=== DATABASE ===" && \
docker compose -f docker-compose.dev.yml exec -T db psql -U hippique -d hippique_dev -c "SELECT COUNT(*) FROM hippique_course;" 2>/dev/null
```

---

## 📝 MODÈLES DE DONNÉES

### Liste des modèles

```python
from hippie.models import (
    Course,                  # Courses hippiques
    PronosticGroupe,        # Groupes de pronostics
    FiltreConfiguration,    # Configurations de filtres
    ResultatAnalyse,        # Résultats d'analyses
    Backtest,              # Tests d'arrivée
    UtilisateurPreferences, # Préférences utilisateur
    CourseReelle,          # Arrivées officielles
    CacheAnalyse,          # Cache de performance
    PerformanceStats,      # Statistiques
)
```

---

## 🔐 IDENTIFIANTS ET TOKENS

### GitHub

**Token stocké dans :** `/root/.github_token`
**Permissions nécessaires :** repo (full control)

### Base de données PostgreSQL

| Dev | Prod |
|-----|------|
| DB: hippique_dev | DB: hippique_prod |
| User: hippique | User: hippique |
| Password: hippique_dev_password | Password: hippique_prod_password |

### Django Superuser

| Environnement | Username | Password |
|--------------|----------|----------|
| Dev | admin | admin |
| Prod | admin | admin |

---

## 📚 RÉFÉRENCES

- **Documentation complète** : Voir `CLAUDE_HIPPIQUE.md`
- **Quick start** : Voir `QUICKSTART.md`
- **GitHub** : https://github.com/andypaypow/hippique-django-hostinger.git
- **Source original** : https://github.com/andypaypow/turboquinteplus

---

**Dernière mise à jour** : 22 Janvier 2026
**Version** : 1.0.0
**Serveur** : Hostinger VPS (72.62.181.239)
