# 🏇 Hippique TurbFilter - Django Application

Application de filtrage de combinaisons hippiques avec Django, Docker et PostgreSQL.

---

## 🚀 CONNEXION RAPIDE

### Accès SSH au serveur

```bash
# Connexion au serveur Hostinger
ssh -i "C:\Users\HP 360\.ssh\id_ed25519" root@72.62.181.239
```

### Accès aux applications

| Application | URL | Port | Chemin |
|-------------|-----|------|--------|
| **Hippique Dev** | http://72.62.181.239:8082/ | 8082 | `/root/hippique-dev` |
| **Admin Dev** | http://72.62.181.239:8082/admin/ | 8082 | `/root/hippique-dev` |
| **Hippique Prod** | http://72.62.181.239:8083/ | 8083 | `/root/hippique-prod` |
| **Admin Prod** | http://72.62.181.239:8083/admin/ | 8083 | `/root/hippique-prod` |

### Identifiants

**Django Admin :**
- Username : `admin`
- Password : `admin`

**PostgreSQL Dev :**
- Database : `hippique_dev`
- User : `hippique`
- Password : `hippique_dev_password`
- Host : `db` (ou `localhost` depuis l'hôte)

### Commandes essentielles

```bash
# Démarrer/Arrêter Dev
cd /root/hippique-dev
docker compose -f docker-compose.dev.yml up -d    # Démarrer
docker compose -f docker-compose.dev.yml down     # Arrêter

# Voir les logs
docker compose -f docker-compose.dev.yml logs -f web

# Connexion à la base de données
docker compose -f docker-compose.dev.yml exec db psql -U hippique -d hippique_dev

# Shell Django
docker compose -f docker-compose.dev.yml exec web python manage.py shell
```

### Documentation complète

- **Guide du développeur** : [DEV_GUIDE.md](./DEV_GUIDE.md) ⭐ **À lire en premier !**
- **Documentation technique** : [CLAUDE_HIPPIQUE.md](./CLAUDE_HIPPIQUE.md)
- **Quick start** : [QUICKSTART.md](./QUICKSTART.md)

---

## 📋 Prérequis

- Docker et Docker Compose installés
- Serveur Hostinger VPS avec accès SSH
- Token GitHub pour le déploiement

## 🚀 Installation Rapide

### 1. Copier le script sur Hostinger

```bash
scp -i ~/.ssh/id_ed25519 setup-hippique.sh root@72.62.181.239:/root/
```

### 2. Exécuter le script

```bash
ssh -i ~/.ssh/id_ed25519 root@72.62.181.239
sudo chmod +x /root/setup-hippique.sh
sudo /root/setup-hippique.sh
```

### 3. Accéder à l'application

- **Dev** : http://72.62.181.239:8082/
- **Admin Dev** : http://72.62.181.239:8082/admin/

## 🔑 Identifiants Admin par défaut

- **Username** : `admin`
- **Password** : `admin`

> ⚠️ **Important** : Changez le mot de passe après la première connexion !

## 📁 Structure

```
/root/
├── hippique-dev/          ← Environnement de développement (Port 8082)
│   ├── docker-compose.dev.yml
│   ├── .env.dev
│   ├── git-push.sh
│   └── code/ (volume monté)
│
└── hippique-prod/         ← Environnement de production (Port 8083)
    ├── docker-compose.yml
    ├── .env.prod
    └── code (image Docker)
```

## 🔧 Commandes Utiles

### Dev

```bash
cd /root/hippique-dev
docker compose -f docker-compose.dev.yml up -d
docker compose -f docker-compose.dev.yml logs -f web
docker compose -f docker-compose.dev.yml down
```

### Prod

```bash
cd /root/hippique-prod
docker compose up -d
docker compose logs -f web
docker compose down
```

### Git

```bash
cd /root/hippique-dev
git add .
git commit -m "feat: description"
./git-push.sh
```

## 📚 Documentation

Voir `CLAUDE_HIPPIQUE.md` pour la documentation complète.

## 🌐 Formules Mathématiques

L'application implémente 14 formules de filtrage :

1. **C(n,k)** - Combinaisons (coefficient binomial)
2. **Synthèse par Citation** - Compte les apparitions
3. **Synthèse par Position** - Score pondéré par position
4. **Synthèse Expert** - Combinaison pondérée des 3 synthèses
5. **Filtre Poids** - Calcul du poids total des combinaisons
6. **Filtre Alternance** - Compte les changements Sélectionné/Non-Sélectionné
7. **Filtre Expert 1** - Filtrage standard (OU logique)
8. **Filtre Expert 2** - Filtrage avancé (ET logique)
9. **Filtre Pairs/Impairs** - Basé sur la parité
10. **Filtre Petits/Grands** - Basé sur les numéros
11. **Filtre Suites** - Détection de suites consécutives
12. **Filtre Groupe Min/Max** - Nombre de chevaux par groupe
13. **Backtest** - Test des arrivées officielles
14. **Taux de Filtrage** - Pourcentage de combinaisons éliminées

## 📦 Déploiement

### Dev → Prod

```bash
# 1. Merger dev vers main
cd /root/hippique-dev
git checkout main
git merge dev
./git-push.sh

# 2. Déployer en prod
cd /root/hippique-prod
git pull origin main
docker compose up -d --build web
docker compose exec web python manage.py migrate

# 3. Retourner sur dev
cd /root/hippique-dev
git checkout dev
```

## 🔗 Liens

- **Repository** : https://github.com/andypaypow/hippique-django-hostinger.git
- **Documentation** : [CLAUDE_HIPPIQUE.md](./CLAUDE_HIPPIQUE.md)
- **Source** : https://github.com/andypaypow/turboquinteplus
