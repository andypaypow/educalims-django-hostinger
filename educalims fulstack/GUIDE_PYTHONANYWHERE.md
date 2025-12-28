# 📘 Guide PythonAnywhere pour Django - EDUCALIMS

**Guide pratique pour les débutants - Déployez votre projet Django sur PythonAnywhere**

---

## 📋 Table des matières

1. [Qu'est-ce que PythonAnywhere ?](#quest-ce-que-pythonanywhere)
2. [Pourquoi PythonAnywhere ?](#pourquoi-pythonanywhere)
3. [Prérequis](#prérequis)
4. [Compte et tarification](#compte-et-tarification)
5. [Préparation du projet local](#préparation-du-projet-local)
6. [Création du compte PythonAnywhere](#création-du-compte-pythonanywhere)
7. [Configuration de base](#configuration-de-base)
8. [Upload du projet](#upload-du-projet)
9. [Configuration de l'application web](#configuration-de-lapplication-web)
10. [Configuration de la base de données](#configuration-de-la-base-de-données)
11. [Fichiers statiques](#fichiers-statiques)
12. [Dépannage](#dépannage)
13. [Bonnes pratiques](#bonnes-pratiques)
14. [Ressources](#ressources)

---

## Qu'est-ce que PythonAnywhere ?

**PythonAnywhere** est une plateforme d'hébergement web (PaaS) spécialisée dans les applications Python. Elle gère tout le serveur pour vous, vous permettant de vous concentrer sur votre code.

### 🔑 Caractéristiques principales

- ✅ **Hébergement Python spécialisé** - Optimisé pour Django, Flask, etc.
- ✅ **Interface web facile** - Pas besoin de lignes de commande complexes
- ✅ **Plan gratuit généreux** - Idéal pour tester et développer
- ✅ **Base de données MySQL incluse** - Jusqu'à 5 Mo sur le plan gratuit
- ✅ **SSH access** - Accès console même sur le plan gratuit

---

## Pourquoi PythonAnywhere ?

| Avantage | Description |
|----------|-------------|
| 🚀 **Facile** | Interface web intuitive, pas de configuration serveur complexe |
| 💰 **Gratuit** | Plan gratuit avec assez pour un projet perso |
| 📚 **Documentation** | Excellente documentation et tutoriels |
| 🛠️ **Support Django** | Support natif et bien documenté pour Django |
| 🔒 **Sécurité** | HTTPS gratuit, certificats SSL automatiques |
| 📈 **Évolutif** | Facile de passer à un plan payant si besoin |

---

## Prérequis

Avant de commencer, assurez-vous d'avoir :

### 1. Comptes nécessaires
- ✅ Un compte GitHub (votre projet y est déjà !)
- ✅ Un compte PythonAnywhere (nous allons le créer)

### 2. Logiciels nécessaires (votre machine locale)
- ✅ Git installé
- ✅ Un éditeur de texte (VS Code, Sublime Text, etc.)

### 3. À propos de votre projet

Vérifiez que votre projet Django a :
- ✅ Un fichier `requirements.txt` à jour
- ✅ Un fichier `manage.py`
- ✅ Un dossier de settings Django
- ✅ migrations appliquées localement

---

## Compte et tarification

### Plans PythonAnywhere

| Plan | Prix | Caractéristiques | Pour qui ? |
|------|------|------------------|------------|
| **Beginner** | Gratuit | - 1 site web<br>- 5 Mo MySQL<br>- 100 heures/mois | Tests, apprentissage |
| **Basic** | ~5$/mois | - Plus de sites<br>- Plus de MySQL<br>- Plus d'heures | Projets personnels |
| **Professional** | ~12$/mois | - Tout illimité<br>- Support prioritaire | Production, business |

> 💡 **Conseil** : Commencez avec le plan gratuit ! Vous pourrez toujours mettre à niveau plus tard.

---

## Préparation du projet local

Avant de déployer, préparons votre projet sur votre machine locale.

### Étape 1 : Vérifier les dépendances

Ouvrez un terminal dans votre dossier projet et vérifiez que `requirements.txt` est à jour :

```bash
cd "C:\Users\HP 360\Desktop\educalims fulstack"
```

Créez ou mettez à jour votre `requirements.txt` :

```txt
# Django
Django>=4.2,<5.0

# WSGI server
gunicorn>=21.0,<22.0

# PostgreSQL (si vous utilisez PostgreSQL)
psycopg2-binary>=2.9.9

# Autres dépendances de votre projet
# Ajoutez toutes les bibliothèques que vous utilisez
```

### Étape 2 : Vérifier les settings Django

Ouvrez `educalims/settings.py` et vérifiez :

```python
# DEBUG doit être False en production
DEBUG = False

# ALLOWED_HOSTS doit inclure votre domaine PythonAnywhere
ALLOWED_HOSTS = ['.pythonanywhere.com', 'localhost']

# Configuration de la base de données
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # Ou postgresql
        'NAME': BASE_DIR / 'db.sqlite3',
        # Pour MySQL sur PythonAnywhere :
        # 'ENGINE': 'django.db.backends.mysql',
        # 'NAME': 'votre_nom_db',
        # 'USER': 'votre_user',
        # 'PASSWORD': 'votre_password',
        # 'HOST': 'votre_user.mysql.pythonanywhere-services.com',
    }
}

# Fichiers statiques
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # Où les fichiers seront collectés
```

### Étape 3 : Tester localement une dernière fois

```bash
# Activer votre environnement virtuel
venv\Scripts\activate

# Tester que tout marche
python manage.py check
python manage.py migrate
python manage.py runserver
```

Si tout fonctionne, passons au déploiement !

---

## Création du compte PythonAnywhere

### Étape 1 : S'inscrire

1. Allez sur [pythonanywhere.com](https://www.pythonanywhere.com)
2. Cliquez sur **"Sign up"** ou **"Create account"**
3. Choisissez le plan **"Beginner" (Gratuit)**
4. Remplissez le formulaire :
   - **Username** : Choisissez un nom unique (ex: `educalims`, `educalimsapp`)
     - Ce sera votre sous-domaine : `votre_username.pythonanywhere.com`
   - **Email** : Votre adresse email
   - **Password** : Un mot de passe sécurisé

> ⚠️ **Important** : Notez votre username et mot de passe !

### Étape 2 : Vérifier l'email

PythonAnywhere vous enverra un email de confirmation. Cliquez sur le lien pour vérifier votre compte.

### Étape 3 : Premier login

1. Connectez-vous sur [pythonanywhere.com](https://www.pythonanywhere.com)
2. Vous verrez le **dashboard** PythonAnywhere

---

## Configuration de base

### Vue d'ensemble du Dashboard

Une fois connecté, vous verrez :

```
┌─────────────────────────────────────────┐
│  PythonAnywhere Dashboard                │
├─────────────────────────────────────────┤
│  📁 Consoles      - Terminal, Bash      │
│  📁 Files         - Gestionnaire fichiers│
│  📁 Web           - Configuration web    │
│  📁 Tasks         - Tâches planifiées    │
│  📁 Databases     - MySQL, PostgreSQL    │
│  📁 Account       - Paramètres compte    │
└─────────────────────────────────────────┘
```

### Étape 1 : Créer un fichier de démarrage virtuel

PythonAnywhere utilise un environnement virtuel pour isoler votre projet.

1. Allez dans l'onglet **"Consoles"**
2. Cliquez sur **"$"** (Bash console)
3. Dans la console qui s'ouvre, tapez :

```bash
# Créer l'environnement virtuel
mkvirtualenv educalims

# Vous verrez votre prompt changer :
# (educalims) $ ~ $

# Vérifier que Python est installé
python --version

# Mettre à jour pip
pip install --upgrade pip
```

> 💡 **Note** : L'environnement virtuel sera activé automatiquement chaque fois que vous ouvrirez une console.

---

## Upload du projet

Il y a plusieurs méthodes pour uploader votre projet. Voici les plus faciles :

### Méthode 1 : Depuis GitHub (RECOMMANDÉ)

C'est la méthode la plus simple car votre projet est déjà sur GitHub !

1. **Allez dans l'onglet "Consoles"**
2. **Cliquez sur "$"** (Bash console)
3. **Dans la console, tapez :**

```bash
# Aller dans votre dossier home
cd ~

# Cloner votre dépôt
git clone https://github.com/andypaypow/educalimsdjango.git

# Aller dans le dossier du projet
cd educalimsdjango

# Vérifier que tout est là
ls
```

### Méthode 2 : Via le gestionnaire de fichiers

1. **Allez dans l'onglet "Files"**
2. **Cliquez sur le bouton "Upload a file"**
3. **Sélectionnez vos fichiers** (compressés en .zip si plusieurs)

> ⚠️ **Déconseillé** pour les gros projets - utilisez Git !

---

## Configuration de l'application web

Maintenant que votre projet est sur PythonAnywhere, configurons-le comme application web.

### Étape 1 : Créer une nouvelle application web

1. **Allez dans l'onglet "Web"**
2. **Cliquez sur "Add a new web app"**
3. **Suivez l'assistant :**

   **Step 1: Choose a name**
   - Laissez par défaut ou choisissez un nom
   - Cliquez **Next**

   **Step 2: Choose a Python version**
   - Sélectionnez **Python 3.10** ou **3.11** (recommandé)
   - Cliquez **Next**

   **Step 3: Choose a web framework**
   - Sélectionnez **Django**
   - Cliquez **Next**

   **Step 4: Django project**
   - **Path to your Django project's settings.py** : `~/educalimsdjango/educalims/settings.py`
   - Cliquez **Next**

4. **Cliquez sur "Next"** jusqu'à la fin
5. **Cliquez sur "Create web app"**

### Étape 2 : Vérifier la configuration

Une fois créée, vous verrez la page de configuration de votre app.

**Sections importantes :**

- **Code** : Configuration du code source
- **Virtualenv** : Configuration de l'environnement virtuel
- **Web app** : Configuration WSGI
- **Static files** : Configuration des fichiers statiques
- **Log files** : Voir les logs

---

## Installation des dépendances

### Étape 1 : Lier l'environnement virtuel

1. **Allez dans l'onglet "Web"**
2. **Dans la section "Virtualenv"**
3. **Cliquez sur le lien "Enter path to a virtualenv"**
4. **Entrez :** `/home/VOTRE_USERNAME/.virtualenvs/educalims`
5. **Cliquez sur "OK"**

### Étape 2 : Installer les packages

1. **Allez dans l'onglet "Consoles"**
2. **Ouvrez une console Bash**
3. **Tapez :**

```bash
# L'environnement virtuel doit être activé
# Vous verrez (educalims) au début du prompt

# Aller dans votre projet
cd ~/educalimsdjango

# Installer les dépendances
pip install -r requirements.txt

# Si requirements.txt n'existe pas encore
pip install Django gunicorn psycopg2-binary

# Vérifier l'installation
pip list
```

---

## Configuration de la base de données

PythonAnywhere offre gratuitement MySQL (jusqu'à 5 Mo sur le plan gratuit).

### Étape 1 : Créer la base de données

1. **Allez dans l'onglet "Databases"**
2. **Cliquez sur "Initialize a new database"**
3. **Choisissez :**
   - **Database name** : `educalimsdb` (ou ce que vous voulez)
   - **Password** : Choisissez un mot de passe sécurisé
4. **Cliquez sur "Initialize database"**

> ⚠️ **IMPORTANT** : Notez le **MySQL hostname** et le **username** affichés !

### Étape 2 : Configurer Django pour MySQL

Ouvrez votre fichier `settings.py` et modifiez la configuration de la base de données :

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'educalimsdb$educalimsdb',  # Format: username$database
        'USER': 'educalimsdb',              # Votre username MySQL
        'PASSWORD': 'VOTRE_PASSWORD_MYSQL',  # Le mot de passe choisi
        'HOST': 'educalimsdb.mysql.pythonanywhere-services.com',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}
```

**Remplacez :**
- `educalimsdb` par votre username PythonAnywhere
- `VOTRE_PASSWORD_MYSQL` par votre mot de passe MySQL

### Étape 3 : Installer le driver MySQL

```bash
# Dans la console PythonAnywhere
pip install mysqlclient
```

### Étape 4 : Appliquer les migrations

```bash
# Dans la console, toujours dans votre dossier projet
cd ~/educalimsdjango

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur (optionnel)
python manage.py createsuperuser
```

---

## Configuration WSGI

Le fichier WSGI dit à PythonAnywhere comment lancer votre application Django.

### Étape 1 : Éditer le fichier WSGI

1. **Allez dans l'onglet "Web"**
2. **Dans la section "Code"**
3. **Cliquez sur le lien "WSGI configuration file"**
4. **Le fichier s'ouvrira dans l'éditeur web**

Le fichier devrait ressembler à ceci :

```python
import os
import sys

# Chemin vers votre projet
path = '/home/VOTRE_USERNAME/educalimsdjango'
if path not in sys.path:
    sys.path.append(path)

# Chemin vers les settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'educalims.settings'

# Importer Django
import django
django.setup()

# Importer l'application WSGI
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

5. **Cliquez sur "Save"**

---

## Fichiers statiques

Les fichiers statiques (CSS, JS, images) doivent être servis séparément.

### Étape 1 : Configurer STATIC_ROOT

Dans `settings.py`, assurez-vous d'avoir :

```python
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

### Étape 2 : Collecter les fichiers statiques

```bash
# Dans la console PythonAnywhere
cd ~/educalimsdjango

# Collecter tous les fichiers statiques
python manage.py collectstatic
```

Répondez **yes** quand demandé.

### Étape 3 : Configurer le mapping sur PythonAnywhere

1. **Allez dans l'onglet "Web"**
2. **Dans la section "Static files"**
3. **Cliquez sur "Enter URL"**
4. **Configurez :**

   - **URL** : `/static/`
   - **Directory** : `/home/VOTRE_USERNAME/educalimsdjango/staticfiles`

5. **Cliquez sur "Save"**

---

## Déploiement final

### Étape 1 : Recharger l'application

1. **Allez dans l'onglet "Web"**
2. **Cliquez sur le gros bouton vert "Reload"** en haut

### Étape 2 : Vérifier que ça marche

1. **Sur la page "Web"**, vous verrez l'URL de votre site
2. **Cliquez sur l'URL** (ex: `http://educalims.pythonanywhere.com`)
3. **Votre site devrait s'afficher !** 🎉

### Étape 3 : Vérifier les logs si problème

Si ça ne marche pas, vérifiez les logs :

1. **Sur la page "Web"**
2. **Allez dans la section "Log files"**
3. **Cliquez sur les différents logs :**
   - `Error log` - Erreurs serveur
   - `Server log` - Logs du serveur
   - `Access log` - Logs d'accès

---

## Dépannage

### Problème : "ModuleNotFoundError"

**Erreur :** `ModuleNotFoundError: No module named 'django'`

**Solution :**
```bash
# Vérifier que l'environnement virtuel est activé
workon educalims

# Réinstaller les dépendances
pip install -r requirements.txt

# Recharger l'application web (bouton Reload)
```

### Problème : "Bad Request (400)"

**Erreur :** Le site affiche "Bad Request"

**Causes possibles :**
1. `ALLOWED_HOSTS` ne contient pas votre domaine
2. `DEBUG = False` mais une erreur de configuration existe

**Solution :**
```python
# Dans settings.py
ALLOWED_HOSTS = ['.pythonanywhere.com', 'votre_username.pythonanywhere.com']
```

### Problème : "DatabaseError"

**Erreur :** Connexion à la base de données échouée

**Solution :**
```bash
# Vérifier que la base de données est initialisée
# Aller dans l'onglet Databases sur PythonAnywhere

# Vérifier les settings
# ENGINE, NAME, USER, PASSWORD, HOST doivent être corrects

# Ré-appliquer les migrations
python manage.py migrate
```

### Problème : "Static files not found"

**Erreur :** Les CSS/images ne s'affichent pas

**Solution :**
```bash
# Re-collecter les fichiers statiques
python manage.py collectstatic --noinput

# Vérifier le mapping dans l'onglet Web > Static files
```

### Problème : "Permission denied"

**Erreur :** `PermissionError: [Errno 13] Permission denied`

**Solution :**
```bash
# Changer les permissions du dossier
chmod -R 755 ~/educalimsdjango
```

---

## Mises à jour du site

Quand vous modifiez votre code localement :

### Méthode 1 : Via Git (recommandé)

```bash
# Sur votre machine locale
cd "C:\Users\HP 360\Desktop\educalims fulstack"
git add .
git commit -m "Description des changements"
git push

# Sur PythonAnywhere (console)
cd ~/educalimsdjango
git pull

# Recharger l'application web (bouton Reload dans l'onglet Web)
```

### Méthode 2 : Via l'éditeur web

1. **Allez dans l'onglet "Files"**
2. **Naviguez vers le fichier à modifier**
3. **Cliquez sur le nom du fichier**
4. **Éditez dans le navigateur**
5. **Cliquez "Save"**
6. **Reload l'application web**

---

## Sécurité

### 1. Variables d'environnement

Pour les secrets (mots de passe, clés API), utilisez des variables d'environnement :

```bash
# Dans la console PythonAnywhere
nano ~/.bashrc

# Ajouter à la fin :
export DJANGO_SECRET_KEY='votre_clé_secret_ici'
export AUTRE_SECRET='votre_autre_secret'

# Sauvegarder (Ctrl+O, Enter, Ctrl+X)

# Recharger la configuration
source ~/.bashrc
```

Puis dans `settings.py` :

```python
import os

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
```

### 2. HTTPS

PythonAnywhere propose HTTPS gratuitement avec Let's Encrypt :

1. **Allez dans l'onglet "Web"**
2. **Dans la section "Security"**
3. **Cliquez sur "Reload to activate HTTPS"**

### 3. Cacher le dossier .git

```bash
# Créer un fichier .htaccess dans votre dossier
nano ~/educalimsdjango/.htaccess

# Ajouter :
RedirectMatch 404 /\.git
```

---

## Bonnes pratiques

### 📝 Organisation

1. **Gardez votre code à jour**
   - Faites des commits réguliers
   - Pushez souvent vers GitHub

2. **Sauvegardez votre base de données**
   ```bash
   # Sur PythonAnywhere
   mysqldump -u educalimsdb -p educalimsdb$educalimsdb > backup.sql
   ```

3. **Surveillez les logs**
   - Vérifiez régulièrement les logs d'erreur
   - Corrigez les problèmes rapidement

### 🚀 Performance

1. **Utilisez le cache**
   ```python
   # Dans settings.py
   CACHES = {
       'default': {
           'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
       }
   }
   ```

2. **Optimisez les requêtes**
   - Utilisez `select_related()` et `prefetch_related()`
   - Évitez les N+1 requêtes

3. **Compressez les fichiers statiques**
   ```bash
   pip install django-compressor
   ```

### 💰 Coûts

1. **Surveillez votre quota**
   - Le plan gratuit a des limites
   - Vérifiez votre consommation dans l'onglet "Account"

2. **Nettoyez les fichiers inutiles**
   - Supprimez les anciennes migrations
   - Nettoyez les fichiers temporaires

---

## Ressources

### Documentation officielle

- **PythonAnywhere Docs** : [help.pythonanywhere.com](https://help.pythonanywhere.com/)
- **Django on PythonAnywhere** : [help.pythonanywhere.com/pages/Django](https://help.pythonanywhere.com/pages/Django)
- **Flask on PythonAnywhere** : [help.pythonanywhere.com/pages/Flask](https://help.pythonanywhere.com/pages/Flask)

### Tutoriels utiles

- **Official Django Tutorial** : [docs.djangoproject.com](https://docs.djangoproject.com/en/stable/intro/tutorial01/)
- **PythonAnywhere Forum** : [pythonanywhere.com/forums](https://www.pythonanywhere.com/forums/)

### Communauté

- **PythonAnywhere Support** : Envoyez un email via le dashboard
- **Stack Overflow** : Tag `python-anywhere`

---

## 📚 Résumé rapide - Commandes essentielles

```bash
# ====== SUR PYTHONANYWHERE ======

# Créer environnement virtuel
mkvirtualenv educalims

# Cloner le projet
git clone https://github.com/andypaypow/educalimsdjango.git
cd educalimsdjango

# Installer dépendances
pip install -r requirements.txt
pip install mysqlclient

# Base de données
python manage.py migrate

# Fichiers statiques
python manage.py collectstatic

# Mettre à jour le code
git pull

# Recharger l'application web
# (Via l'interface web : bouton Reload)

# ====== SUR MACHINE LOCALE ======

# Pousser les changements
git add .
git commit -m "message"
git push
```

---

## ✅ Checklist de déploiement

- [ ] Compte PythonAnywhere créé
- [ ] Environnement virtuel créé (`mkvirtualenv`)
- [ ] Projet cloné (`git clone`)
- [ ] Dépendances installées (`pip install`)
- [ ] Application web créée
- [ ] Fichier WSGI configuré
- [ ] Base de données initialisée
- [ ] Migrations appliquées
- [ ] Fichiers statiques collectés
- [ ] Mapping static files configuré
- [ ] Application rechargée (Reload)
- [ ] Site accessible via l'URL
- [ ] HTTPS activé (optionnel mais recommandé)
- [ ] Variables d'environnement configurées (si nécessaire)

---

## 🎯 Prochaines étapes

Après avoir déployé votre site :

1. **Testez toutes les fonctionnalités**
   - Création de compte
   - Connexion
   - CRUD de vos modèles
   - Upload de fichiers

2. **Configurez les emails** (optionnel)
   - Pour les notifications
   - Pour la réinitialisation de mot de passe

3. **Surveillez les logs**
   - Vérifiez régulièrement les erreurs
   - Optimisez les performances

4. **Sauvegardez vos données**
   - Exportez la base de données régulièrement
   - Gardez une copie de votre code sur GitHub

---

**Bon déploiement sur PythonAnywhere ! 🚀**

Votre site EDUCALIMS sera bientôt accessible à tous sur Internet !

Pour toute question, consultez la [documentation PythonAnywhere](https://help.pythonanywhere.com/) ou posez votre question sur leurs forums.
