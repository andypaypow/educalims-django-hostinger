# 👋 BIENVENUE SUR LE PROJET HIPPIQUE TURBFILTER

**Commencez ici !** Ce fichier contient les informations essentielles pour démarrer.

---

## 🚀 JE VEUX...

### ...Accéder à l'application immédiatement

- **Application Dev** : http://72.62.181.239:8082/
- **Admin Django** : http://72.62.181.239:8082/admin/
  - Username : `admin`
  - Password : `admin`

### ...Me connecter au serveur

```bash
ssh -i "C:\Users\HP 360\.ssh\id_ed25519" root@72.62.181.239
```

Une fois connecté :
```bash
cd /root/hippique-dev
docker compose -f docker-compose.dev.yml ps     # Voir l'état des conteneurs
docker compose -f docker-compose.dev.yml logs -f web  # Voir les logs
```

### ...Comprendre l'architecture

📖 **Lisez le guide du développeur** : `DEV_GUIDE.md`

### ...Voir la documentation technique

📚 **Lisez la documentation complète** : `CLAUDE_HIPPIQUE.md`

---

## 📂 STRUCTURE DU PROJET

```
/root/hippique-dev/
├── code/                    ← Code source Django
│   ├── hippique_project/   ← Projet Django (settings, urls, wsgi)
│   ├── hippie/             ← Application principale (models, views, templates)
│   ├── manage.py           ← Gestion Django
│   ├── staticfiles/        ← Fichiers statiques
│   └── media/              ← Fichiers uploadés
├── docker-compose.dev.yml  ← Configuration Docker
├── .env.dev                ← Variables d'environnement
├── nginx-dev.conf          ← Configuration Nginx
└── README.md               ← Documentation rapide
```

---

## 🔧 COMMANDES ESSENTIELLES

```bash
# Sur votre machine locale pour vous connecter
ssh -i "C:\Users\HP 360\.ssh\id_ed25519" root@72.62.181.239

# Une fois connecté au serveur
cd /root/hippique-dev

# Démarrer les conteneurs
docker compose -f docker-compose.dev.yml up -d

# Arrêter les conteneurs
docker compose -f docker-compose.dev.yml down

# Voir les logs
docker compose -f docker-compose.dev.yml logs -f web

# Accéder à la base de données
docker compose -f docker-compose.dev.yml exec db psql -U hippique -d hippique_dev

# Shell Django
docker compose -f docker-compose.dev.yml exec web python manage.py shell

# Appliquer les migrations
docker compose -f docker-compose.dev.yml exec web python manage.py migrate

# Créer un superutilisateur
docker compose -f docker-compose.dev.yml exec web python manage.py createsuperuser
```

---

## 🗄️ BASE DE DONNÉES

**PostgreSQL Dev :**
- Database : `hippique_dev`
- User : `hippique`
- Password : `hippique_dev_password`
- Host : `db` (conteneur)
- Port : `5432`

**Connexion directe :**
```bash
docker compose -f docker-compose.dev.yml exec db psql -U hippique -d hippique_dev
```

---

## 📚 DOCUMENTATION

1. **DEV_GUIDE.md** - Guide complet du développeur (SSH, Docker, Django, DB...)
2. **CLAUDE_HIPPIQUE.md** - Documentation technique détaillée
3. **QUICKSTART.md** - Guide de démarrage rapide
4. **README.md** - Vue d'ensemble du projet

---

## 🆘 PROBLÈMES ?

**L'application ne répond pas :**
```bash
cd /root/hippique-dev
docker compose -f docker-compose.dev.yml ps      # Vérifier si les conteneurs sont UP
docker compose -f docker-compose.dev.yml logs   # Voir les erreurs
```

**Erreur de connexion à la base :**
```bash
docker compose -f docker-compose.dev.yml restart db
docker compose -f docker-compose.dev.yml restart web
```

**Besoin d'aide ?**
- Voir la section "DEBUGGING" dans `DEV_GUIDE.md`

---

## 📞 INFORMATIONS SERVEUR

- **IP** : 72.62.181.239
- **Hébergeur** : Hostinger VPS
- **OS** : Linux
- **Docker** : Installé et opérationnel
- **Ports** : 8082 (Dev), 8083 (Prod)

---

**Bon développement !** 🎉
