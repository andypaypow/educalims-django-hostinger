# Hippique TurbFilter - Application Django

## 📋 Description

Application Django de filtrage de combinaisons hippiques avec filtres experts personnalisables.

### Fonctionnalités principales

- **Filtrage expert** : Filtres OU (inclusif) et ET (exclusif) avec groupes de pronostics
- **Paires/Impairs** : Contrôle de la répartition des numéros
- **Petits/Suites** : Filtres sur les petits numéros et suites consécutives
- **Limitation** : Limite du nombre de chevaux par sélection
- **Poids** : Filtrage par poids des chevaux (synthèse des pronostics)
- **Alternance** : Gestion des alternances successifs/non-successifs
- **Sauvegarde** : Scénarios sauvegardables avec arrivée

## 🌐 Accès

### Environnements sur Hostinger VPS

| Environnement | URL Application | URL Admin | Port | Chemin |
|----------------|-----------------|-----------|------|--------|
| **Hippique Dev** | http://72.62.181.239:8082/ | http://72.62.181.239:8082/admin/ | 8082 | `/root/hippique-dev` |
| **Hippique Prod** | http://72.62.181.239:8083/ | http://72.62.181.239:8083/admin/ | 8083 | `/root/hippique-prod` |

### Identifiants Admin

- **Username** : `admin`
- **Password** : `admin`

## 🔑 Connexion SSH au serveur

### Depuis Windows (Git Bash / PowerShell)

```bash
ssh -i "C:\Users\HP 360\.ssh\id_ed25519" root@72.62.181.239
```

### Depuis Linux / macOS

```bash
ssh -i ~/.ssh/id_ed25519 root@72.62.181.239
```

## 📁 Structure sur le serveur

| Environnement | Chemin | Code | Docker Compose |
|----------------|--------|------|----------------|
| **Hippique Dev** | `/root/hippique-dev/` | `/root/hippique-dev/code/main/` | `docker-compose.dev.yml` |
| **Hippique Prod** | `/root/hippique-prod/` | `/root/hippique-prod/code/main/` | `docker-compose.prod.yml` |

## 🐳 Commandes Docker utiles

### Hippique Dev

```bash
cd /root/hippique-dev

# Voir les logs
docker compose -f docker-compose.dev.yml logs -f web

# Redémarrer le conteneur
docker compose -f docker-compose.dev.yml restart web

# Arrêter tous les conteneurs
docker compose -f docker-compose.dev.yml down

# Démarrer tous les conteneurs
docker compose -f docker-compose.dev.yml up -d
```

### Hippique Prod

```bash
cd /root/hippique-prod

# Voir les logs
docker compose -f docker-compose.prod.yml logs -f web

# Redémarrer le conteneur
docker compose -f docker-compose.prod.yml restart web

# Arrêter tous les conteneurs
docker compose -f docker-compose.prod.yml down

# Démarrer tous les conteneurs
docker compose -f docker-compose.prod.yml up -d
```

## 🔄 Déploiement

### Déployer sur Hippique Dev

```bash
# Copier le fichier modifié
scp -i "C:\Users\HP 360\.ssh\id_ed25519" "chemin\local\fichier.py" root@72.62.181.239:/root/hippique-dev/code/main/fichier.py

# Redémarrer le conteneur
ssh -i "C:\Users\HP 360\.ssh\id_ed25519" root@72.62.181.239 "cd /root/hippique-dev && docker compose -f docker-compose.dev.yml restart web"
```

### Déployer sur Hippique Prod

```bash
# Copier le fichier modifié
scp -i "C:\Users\HP 360\.ssh\id_ed25519" "chemin\local\fichier.py" root@72.62.181.239:/root/hippique-prod/code/main/fichier.py

# Redémarrer le conteneur
ssh -i "C:\Users\HP 360\.ssh\id_ed25519" root@72.62.181.239 "cd /root/hippique-prod && docker compose -f docker-compose.prod.yml restart web"
```

## 📊 Base de données

- **Type** : PostgreSQL
- **Conteneur** : `hippique-dev-db-1`
- **Migration** : `docker compose -f docker-compose.dev.yml exec web python manage.py migrate`

## 🛠️ Technologies

- **Backend** : Django 4.2+
- **Frontend** : HTML/CSS/JavaScript (vanilla)
- **Base de données** : PostgreSQL 15
- **Serveur web** : Nginx + Gunicorn
- **Conteneurisation** : Docker + Docker Compose

## 📝 Dernière mise à jour

- **Date** : 26 Janvier 2026
- **Version** : Filtres fonctionnels (commit 662ee73)
- **État** : Système de paiement désactivé, filtres entièrement fonctionnels
