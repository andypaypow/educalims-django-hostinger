# 🚀 Quick Start - Hippique TurbFilter

Guide de démarrage rapide pour l'application Hippique sur Hostinger.

---

## ⚡ Installation en 3 étapes

### 1️⃣ Préparer le token GitHub

```bash
# Sur votre machine locale
echo 'VOTRE_TOKEN_GITHUB_ICI' > /tmp/github_token
chmod 400 /tmp/github_token
```

### 2️⃣ Transférer et exécuter

```bash
# Transférer les fichiers
scp -i ~/.ssh/id_ed25519 setup-hippique.sh root@72.62.181.239:/root/
scp -i ~/.ssh/id_ed25519 /tmp/github_token root@72.62.181.239:/root/.github_token

# Exécuter le script
ssh -i ~/.ssh/id_ed25519 root@72.62.181.239
sudo chmod +x /root/setup-hippique.sh
sudo /root/setup-hippique.sh
```

### 3️⃣ Vérifier l'accès

```bash
# Ouvrir dans le navigateur
# http://72.62.181.239:8082/
# http://72.62.181.239:8082/admin/
```

---

## 🔑 Identifiants Admin par défaut

- **Username** : `admin`
- **Password** : `admin`

> ⚠️ **Important** : Changez le mot de passe après la première connexion !

---

## 📝 Copier les fichiers du projet

Après l'installation automatique, copier les fichiers depuis TurboQuintePlus :

```bash
# Sur Hostinger
cd /root/hippique-dev/code/hippie

# Copier les fichiers depuis l'analyse
# (Vous devrez transférer ces fichiers depuis votre machine locale)
```

Fichiers à copier dans `/root/hippique-dev/code/hippie/` :
- `formules.py` ← `turboquinteplus/formules_python.py`
- `models.py` ← `turboquinteplus/modeles_django.py`
- `views.py` ← `turboquinteplus/vues_django.py`
- `urls.py` ← `turboquinteplus/urls_django.py`
- `templates/` ← Créer depuis `turboquinteplus/templates_django.py`

---

## 🔄 Premier déploiement en prod

```bash
# Merger et pousser
cd /root/hippique-dev
git checkout main
git merge dev
./git-push.sh

# Déployer en prod
cd /root/hippique-prod
git pull origin main
docker compose up -d --build web
docker compose exec web python manage.py migrate
```

---

## 📊 Vérifier l'état

```bash
# Vérifier les conteneurs
cd /root/hippique-dev
docker compose -f docker-compose.dev.yml ps

# Voir les logs
docker compose -f docker-compose.dev.yml logs -f web

# Compter les enregistrements
docker compose -f docker-compose.dev.yml exec -T db psql -U hippique -d hippique_dev -c "
SELECT 'Courses', COUNT(*) FROM hippique_course
UNION ALL SELECT 'Pronostics', COUNT(*) FROM hippique_pronosticgroupe
UNION ALL SELECT 'Filtres', COUNT(*) FROM hippique_filtreconfiguration;"
```

---

## 🆘 Problèmes courants

### Port 8082 déjà utilisé

```bash
# Vérifier ce qui utilise le port
sudo netstat -tulpn | grep 8082

# Arrêter les conteneurs existants
cd /root/hippique-dev
docker compose -f docker-compose.dev.yml down
```

### Erreur de connexion à la base

```bash
# Vérifier le conteneur db
docker compose -f docker-compose.dev.yml ps db

# Redémarrer db
docker compose -f docker-compose.dev.yml restart db
```

### Erreur de migration

```bash
# Recréer la base de données
docker compose -f docker-compose.dev.yml down
docker volume rm hippique-postgres-data-dev
docker compose -f docker-compose.dev.yml up -d
docker compose -f docker-compose.dev.yml exec web python manage.py migrate
```

---

## 📚 Documentation complète

Voir `CLAUDE_HIPPIQUE.md` pour la documentation détaillée.
