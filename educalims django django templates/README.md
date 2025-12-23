# EDUCALIMS - Application Éducative

## Description
Application web éducative permettant de naviguer dans une hiérarchie de contenus pédagogiques : **Cycles → Disciplines → Niveaux → Unités → Fichiers**.

Intègre un **système d'abonnement payant par niveau** avec intégration **Telegram Mini App**.

## Stack Technique
- **Backend** : Django 6.0
- **Frontend** : Django Templates (pas de React/Vue)
- **UI** : Bootstrap 5.3.2
- **Base de données** : SQLite
- **Telegram** : Mini App SDK avec ngrok

---

## 🚀 Démarrage rapide

```bash
# Activer l'environnement virtuel (Windows)
cd "C:\Users\HP 360\Desktop\educalims django django templates"
venv\Scripts\activate

# Lancer le serveur
python manage.py runserver
```

Puis ouvrez :
- **Site public** : http://127.0.0.1:8000/
- **Admin** : http://127.0.0.1:8000/admin/ (admin / admin123)

---

## ⚠️ CRUCIAL : Gestion de l'encodage UTF-8

### Le problème
Lors de la création de données avec accents français (é, è, à, ê, ë, etc.) dans Django sur Windows, vous risquez d'obtenir un **double encodage UTF-8** :
- Attendu : `Lycée`
- Affiché : `LycÃ©e`

### La solution : Utiliser les codes Unicode échappés

Lors de la création de données avec des accents dans un script Python, utilisez les **codes Unicode échappés** :

```python
# -*- coding: utf-8 -*-
from educalims_app.models import Cycle

# Méthode CORRECTE - utiliser les codes Unicode (\xXX)
cycle = Cycle.objects.create(
    nom="Lyc\xe9e",  # "é" = \xe9
    description="Enseignement secondaire",
    ordre=3
)
```

### Codes Unicode courants pour le français

| Caractère | Code Python | Description |
|-----------|-------------|-------------|
| é | `\xe9` | e accent aigu |
| è | `\xe8` | e accent grave |
| à | `\xe0` | a accent grave |
| ù | `\xf9` | u accent grave |
| ê | `\xea` | e accent circonflexe |
| î | `\xee` | i accent circonflexe |
| ô | `\xf4` | o accent circonflexe |
| ë | `\xeb` | e tréma |
| ç | `\xe7` | c cédille |
| É | `\xc9` | E accent aigu (majuscule) |
| È | `\xc8` | E accent grave (majuscule) |
| À | `\xc0` | A accent grave (majuscule) |
| Ç | `\xc7` | C cédille (majuscule) |

### Exemple complet pour créer des données

```python
# -*- coding: utf-8 -*-
from educalims_app.models import Cycle, Discipline, Niveau, Unite

# Créer un cycle
cycle = Cycle.objects.create(
    nom="Lyc\xe9e",
    description="Enseignement secondaire du lyc\xe9e",
    ordre=3
)

# Créer une discipline
discipline = Discipline.objects.create(
    nom="Sciences de la Vie et de la Terre",
    cycle=cycle,
    icone="bi-flower1",
    couleur="#28a745",
    ordre=1
)

# Créer des niveaux (hiérarchie parent/enfant)
terminale = Niveau.objects.create(
    nom="Terminale",
    discipline=discipline,
    description="Classe de Terminale",
    ordre=3
)

term_c = Niveau.objects.create(
    nom="Terminale C",
    discipline=discipline,
    parent=terminale,
    description="Série C",
    ordre=1
)

term_d = Niveau.objects.create(
    nom="Terminale D",
    discipline=discipline,
    parent=terminale,
    description="Série D",
    ordre=2
)
```

---

## 📂 Structure du projet

```
educalims django django templates/
├── educalims/                    # Configuration Django
│   ├── settings.py               # ALLOWED_HOSTS, INSTALLED_APPS, MIDDLEWARE
│   ├── urls.py                   # Routage principal
│   └── wsgi.py
├── educalims_app/                # Application principale
│   ├── models.py                 # TOUS les modèles (Cycle, Discipline, etc.)
│   ├── views.py                  # Vues principales (navigation contenu)
│   ├── views_abonnement.py      # Système d'abonnement
│   ├── urls.py                   # URLs de l'app
│   ├── admin.py                  # Interface admin
│   ├── middleware.py             # TelegramUserMiddleware
│   └── migrations/                # Base de données
├── templates/                     # Templates Django
│   ├── base.html                 # Layout avec Bootstrap 5 + Telegram SDK
│   ├── home.html                 # Page d'accueil
│   └── educalims_app/
│       ├── cycle_detail.html
│       ├── discipline_detail.html
│       ├── niveau_detail.html
│       ├── unite_detail.html
│       └── abonnement/           # Templates système d'abonnement
│           ├── choix_cycle.html
│           ├── choix_discipline.html
│           ├── choix_niveau.html
│           ├── choix_formule.html
│           ├── paiement.html
│           ├── succes.html
│           ├── echec.html
│           ├── attente.html
│           ├── mes_abonnements.html
│           └── seances.html
├── media/                          # Fichiers uploadés
├── static/                         # Fichiers statiques
├── venv/                           # Environnement virtuel
├── db.sqlite3                      # Base de données
├── manage.py
└── README.md
```

---

## 📊 Hiérarchie pédagogique

```
Cycle (ex: Lycée)
  └── Discipline (ex: SVT)
       └── Niveau parent (ex: Terminale)
            ├── Niveau enfant (ex: Terminale C)
            │    └── Unite parent (Partie)
            │         └── Unite enfant (Chapitre)
            │              └── Fichier (PDF, cours, exercice)
            └── Niveau enfant (ex: Terminale D)
```

**IMPORTANT** : Les abonnements sont liés aux **NIVEAUX** (ex: Terminale C), pas aux disciplines directement.

---

## 🛠️ Commandes Django utiles

```bash
# Activer l'environnement virtuel (Windows)
venv\Scripts\activate

# Créer les migrations
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver

# Ouvrir le shell Django
python manage.py shell

# Vérifier la configuration
python manage.py check
```

---

## 📝 Modèles de données

### Modèles principaux

| Modèle | Description | Champs principaux |
|--------|-------------|-------------------|
| `Cycle` | Cycle éducatif | nom, description, ordre |
| `Discipline` | Matière enseignée | nom, cycle (FK), icone, couleur, ordre |
| `Niveau` | Niveau scolaire | nom, discipline (FK), parent (self), ordre |
| `Unite` | Unité pédagogique | titre, niveau (FK), parent (self), ordre |
| `Fichier` | Ressource pédagogique | titre, fichier_upload, unite (FK), type_fichier |

### Modèles Telegram

| Modèle | Description |
|--------|-------------|
| `TelegramUser` | Utilisateur Telegram capturé automatiquement |

### Modèles Abonnement

| Modèle | Description |
|--------|-------------|
| `Seance` | Séance d'appel (tutorat) |
| `Abonnement` | Lien utilisateur ↔ niveau ↔ type_abonnement |
| `Transaction` | Paiement et webhook |

---

## 💰 Système d'Abonnement par NIVEAU

### ⚠️ POINT CLE : Les abonnements sont par NIVEAU, pas par discipline

**Comprendre la logique** :
- On ne s'abonne pas à "SVT" globalement
- On s'abonne à "SVT - Terminale C" ou "SVT - Terminale D"
- Chaque niveau est une offre d'abonnement distincte

### Les 3 Formules d'Abonnement

| Formule | Prix | Accès |
|---------|------|-------|
| **Accès Essentiel** | 2 500 FCFA/an | Fiches et corrigés illimités du niveau |
| **Séance Unique** | 1 000 FCFA | Une séance d'appel au choix |
| **séance intégrale** | 10 000 FCFA/an | Toutes les séances d'appel |

### Règles de déblocage

- **Accès Essentiel** : Toujours disponible
- **Séance Unique** : Disponible SEULEMENT si l'utilisateur a déjà l'Accès Essentiel pour ce niveau
- **séance intégrale** : Disponible SEULEMENT si l'utilisateur a déjà l'Accès Essentiel pour ce niveau

### Flux Complet d'Achat

```
1. CYCLE       → Sélection du cycle (ex: Lycée)
2. DISCIPLINE  → Sélection de la matière (ex: SVT)
3. NIVEAU      → Sélection du niveau (ex: Terminale C)
4. FORMULE     → Choix de l'abonnement (Essentiel, Séance Unique, intégrale)
5. PAIEMENT    → Transaction et validation
6. CONFIRMATION→ Accès au contenu
```

### Pages du Système

| URL | Description |
|-----|-------------|
| `/abonnement/` | Choix du cycle |
| `/abonnement/cycle/{id}/disciplines/` | Choix de la discipline |
| `/abonnement/discipline/{id}/niveaux/` | Choix du niveau |
| `/abonnement/niveau/{id}/formule/` | Choix de la formule |
| `/abonnement/niveau/{id}/paiement/{type}/` | Page de paiement |
| `/abonnement/succes/{ref}/` | Confirmation succès |
| `/abonnement/echec/{ref}/` | Page d'échec |
| `/abonnement/mes-abonnements/` | Liste des abonnements |
| `/abonnement/discipline/{id}/seances/` | Séances accessibles |

### Templates Abonnement

| Template | Description |
|----------|-------------|
| `choix_cycle.html` | Grille des cycles disponibles |
| `choix_discipline.html` | Grille des disciplines du cycle |
| `choix_niveau.html` | Liste des niveaux (seuls les feuilles) |
| `choix_formule.html` | 3 cartes avec les formules |
| `choix_seance.html` | Liste des séances (pour Séance Unique) |
| `paiement.html` | Récapitulatif et paiement |
| `succes.html` | Confirmation après paiement réussi |
| `echec.html` | Message d'échec |
| `attente.html` | Page d'attente pendant traitement |
| `mes_abonnements.html` | Liste des abonnements utilisateur |
| `seances.html` | Séances auxquelles l'utilisateur a accès |

---

## 📱 Intégration Telegram Mini App

### Configuration

- **Bot Token** : `8539115405:AAFxfimKuOeVKqYL5mQaclVsQ5Lh2hIcIok`
- **ngrok Authtoken** : `34Fiz0WnQdA9PQ9fXv0lS6MAZK0_6GKZSymAvAbqxTzjfSgS8`

### Lancement rapide (Windows)

```python
# start_telegram.py
from pyngrok import ngrok
import subprocess

NGROK_AUTH_TOKEN = "34Fiz0WnQdA9PQ9fXv0lS6MAZK0_6GKZSymAvAbqxTzjfSgS8"
DJANGO_PORT = 8000

ngrok.set_auth_token(NGROK_AUTH_TOKEN)
tunnel = ngrok.connect(DJANGO_PORT)

print("=" * 60)
print("EDUCALIMS - Telegram Mini App")
print("=" * 60)
print(f"URL ngrok  : {tunnel.public_url}")
print(f"URL locale : http://127.0.0.1:{DJANGO_PORT}")
print("=" * 60)
print("\nCOPIEZ cette URL dans @BotFather:")
print(f"{tunnel.public_url}")
print("\nAppuyez sur Ctrl+C pour arrêter...")
print("=" * 60)

try:
    subprocess.run(["python", "manage.py", "runserver"])
finally:
    ngrok.kill()
```

```bash
venv\Scripts\activate
python start_telegram.py
```

### Configuration Django pour ngrok

Dans `educalims/settings.py` :
```python
ALLOWED_HOSTS = ['*']
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

### Middleware Telegram

`TelegramUserMiddleware` capture automatiquement les informations utilisateur à chaque requête Telegram et les stocke en base de données.

---

## 🔐 Accès Admin

- **URL** : http://127.0.0.1:8000/admin/
- **Utilisateur** : admin
- **Mot de passe** : admin123

---

## 🎨 Personnalisation

### Couleurs des disciplines

Chaque discipline a une couleur personnalisée (champ `couleur` en format hexadécimal) :
- SVT : `#28a745` (vert)
- Maths : `#dc3545` (rouge)
- Anglais : `#007bff` (bleu)

### Icônes Bootstrap

Les disciplines utilisent les icônes Bootstrap 5 (champ `icone`) :
- `bi-flower1` pour SVT
- `bi-calculator` pour Maths
- `bi-translate` pour Langues

---

## 📅 Historique du développement

### ÉTAPE 1 - Socle technique ✅
- Environnement virtuel Python
- Django 6.0
- Structure du projet

### ÉTAPE 2 - Modèles & hiérarchie ✅
- 5 modèles principaux avec relations
- Hiérarchie parent/enfant (Niveaux, Unités)
- Migrations et admin

### ÉTAPE 3 - Frontend ✅
- Templates Django + Bootstrap 5.3.2
- Breadcrumbs sur toutes les pages
- Navigation complète

### ÉTAPE 4 - Données SVT ✅
- Cycle Lycée, Discipline SVT
- Niveaux : Terminale → Terminale C, Terminale D
- 28 unités pédagogiques

### ÉTAPE 5 - Telegram Mini App ✅
- SDK Telegram WebApp
- ngrok tunnel HTTPS
- Thème adaptatif
- Capture automatique des utilisateurs

### ÉTAPE 6 - Système d'abonnement par NIVEAU ✅
- Modèles : Seance, Abonnement, Transaction
- Flux : Cycle → Discipline → Niveau → Formule
- 3 types d'abonnements avec déblocage progressif
- Webhook de paiement
- 11 templates pour l'interface utilisateur
- Toutes les breadcrumbs cliquables

---

## 🐛 Problèmes fréquents et solutions

| Erreur | Solution |
|--------|----------|
| `LycÃ©e` au lieu de `Lycée` | Utiliser les codes Unicode (`\xe9` pour é) |
| `DisallowedHost` | Déjà configuré avec `ALLOWED_HOSTS = ['*']` |
| `Cannot find 'discipline_set'` | Utiliser `prefetch_related('disciplines')` (related_name) |
| `No Niveau matches the given query` | Le niveau n'existe pas. Vérifiez avec `python manage.py shell` |
| `prefetch_related invalid` | Vérifiez le `related_name` dans le modèle ForeignKey |

---

## 🚀 Pour les futurs développeurs

### Clés de réussite pour ce projet

1. **TOUJOURS utiliser les codes Unicode** pour les accents français dans les scripts Python
2. **Respecter la hiérarchie** : Cycle → Discipline → Niveau → Unité → Fichier
3. **Les abonnements sont par NIVEAU** : Chaque niveau (Terminale C, Terminale D) est une offre distincte
4. **Déblocage progressif** : Séance Unique et séance intégrale nécessitent l'Accès Essentiel d'abord
5. **Tous les breadcrumbs cliquables** : Navigation fluide à tout moment
6. **related_name** : Toujours vérifier les noms de relation (`disciplines`, `niveaux`, etc.)

### Structure URLs à respecter

```
/abonnement/                           → choix_cycle
/abonnement/cycle/{id}/disciplines/   → choix_discipline (cycle_id)
/abonnement/discipline/{id}/niveaux/ → choix_niveau (discipline_id)
/abonnement/niveau/{id}/formule/     → choix_formule (niveau_id)
/abonnement/niveau/{id}/paiement/{type}/ → paiement (niveau_id, type_abonnement)
```

### Fichiers clés à modifier

- **Modèles** : `educalims_app/models.py`
- **Vues principales** : `educalims_app/views.py`
- **Vues abonnement** : `educalims_app/views_abonnement.py`
- **URLs** : `educalims_app/urls.py`
- **Templates** : `templates/educalims_app/`

---

*Dernière mise à jour : 2025-12-23*
*Version : 2.0 - Système d'abonnement par niveau avec Telegram Mini App*
