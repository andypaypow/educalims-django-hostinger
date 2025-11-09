# Educalim - Plateforme Éducative

Plateforme web Django pour la gestion de contenus éducatifs (fiches, sujets, cahiers types) destinée aux collégiens et lycéens.

## 🎯 Fonctionnalités

- **Gestion des disciplines** : SVT, Physique-Chimie, Mathématiques, Philosophie, Histoire-Géographie
- **Organisation par cycles** : Collège et Lycée
- **Classification par niveaux** : 6ème, 5ème, 4ème, 3ème, Seconde, Première, Terminale
- **Leçons et chapitres** : Organisation des contenus pédagogiques
- **Types de contenus** : Fiches, Sujets d'exercices, Cahiers types
- **Recherche** : Recherche全文 dans tous les contenus
- **Interface responsive** : Compatible mobile et desktop

## 🚀 Installation

### Prérequis
- Python 3.8+
- Git

### Installation pas à pas

1. **Cloner le projet**
```bash
git clone <repository-url>
cd Educalim
```

2. **Créer et activer l'environnement virtuel**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# ou
source venv/bin/activate  # Linux/Mac
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configurer les variables d'environnement**
   - Copier le fichier `.env` et ajuster la configuration si nécessaire
   - La SECRET_KEY est déjà générée pour le développement

5. **Appliquer les migrations**
```bash
python manage.py migrate
```

6. **Créer des données de test (optionnel)**
```bash
python create_test_data.py
```

7. **Créer un superutilisateur**
```bash
python manage.py createsuperuser
```

8. **Démarrer le serveur**
```bash
python manage.py runserver
```

L'application sera accessible sur `http://127.0.0.1:8000/`

## 📁 Structure du Projet

```
Educalim/
├── manage.py                    # Script de gestion Django
├── requirements.txt             # Dépendances Python
├── .env                         # Variables d'environnement
├── .gitignore                   # Fichiers ignorés par Git
├── create_test_data.py          # Script de données de test
├── site_educatif/               # Configuration du projet Django
│   ├── __init__.py
│   ├── settings.py              # Paramètres de configuration
│   ├── urls.py                  # URLs principales
│   ├── wsgi.py                  # Configuration WSGI
│   └── asgi.py                  # Configuration ASGI
├── educalims/                   # Application principale
│   ├── __init__.py
│   ├── models.py                # Modèles de données
│   ├── views.py                 # Vues Django
│   ├── urls.py                  # URLs de l'application
│   ├── admin.py                 # Administration Django
│   ├── apps.py                  # Configuration de l'application
│   └── migrations/              # Migrations de base de données
├── templates/                   # Templates HTML
│   ├── base.html               # Template de base
│   └── educalims/              # Templates de l'application
│       ├── home.html           # Page d'accueil
│       ├── disciplines_list.html
│       ├── discipline_detail.html
│       ├── niveau_detail.html
│       ├── unite_detail.html
│       └── search.html
├── static/                      # Fichiers statiques
│   ├── css/
│   │   └── style.css           # Styles personnalisés
│   ├── js/
│   │   └── script.js           # JavaScript personnalisé
│   └── images/
└── media/                       # Fichiers uploadés
    └── uploads/
```

## 🗄️ Modèles de Données

### Discipline
Matières scolaires disponibles (ex: SVT, Mathématiques)

### Cycle
Niveaux d'enseignement (Collège, Lycée)

### Niveau
Classes spécifiques (6ème, 5ème, etc.)

### UniteEnseignement
Leçons et chapitres organisés par niveau

### Contenu
Documents téléchargeables (Fiches, Sujets, Cahiers types)

## 🔧 Configuration

### Variables d'environnement (.env)
```
SECRET_KEY=votre-clé-secrète
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
STATIC_URL=/static/
MEDIA_URL=/media/
```

### Base de données
- **Développement** : SQLite3 (fichier `db.sqlite3`)
- **Production** : Configurer PostgreSQL ou MySQL selon les besoins

## 📱 Accès à l'application

- **Page d'accueil** : `http://127.0.0.1:8000/`
- **Liste des disciplines** : `http://127.0.0.1:8000/disciplines/`
- **Recherche** : `http://127.0.0.1:8000/search/`
- **Administration** : `http://127.0.0.1:8000/admin/`

## 🎨 Interface Utilisateur

- **Design responsive** avec Bootstrap 5
- **Navigation intuitive** avec menu déroulant des disciplines
- **Recherche en temps réel** avec suggestions
- **Affichage des statistiques** sur le tableau de bord
- **Téléchargement direct** des documents pédagogiques

## 🔍 Fonctionnalités de recherche

La recherche permet de trouver :
- **Unités d'enseignement** : leçons et chapitres
- **Contenus** : fiches, sujets, cahiers types
- **Disciplines** : matières scolaires
- **Recherche全文** dans les titres et descriptions

## 📊 Administration

L'interface Django Admin permet de :
- Gérer les disciplines, cycles et niveaux
- Ajouter/modifier les leçons et chapitres
- Uploader des fiches, sujets et cahiers types
- Configurer les relations entre les contenus

## 🚀 Déploiement

Pour la production :
1. **Désactiver le mode debug** : `DEBUG=False`
2. **Configurer ALLOWED_HOSTS** avec votre domaine
3. **Utiliser une base de données robuste** (PostgreSQL recommandé)
4. **Configurer les fichiers statiques** avec un service CDN
5. **Mettre en place HTTPS** avec SSL/TLS
6. **Utiliser un serveur d'application** (Gunicorn + Nginx)

## 📝 Développement

### Ajouter une nouvelle discipline
1. Via l'admin Django : `admin/`
2. Ou créer un script de migration

### Ajouter des contenus
1.Uploader les fichiers dans l'interface admin
2. Associer aux unités d'enseignement appropriées

### Personnalisation
- **CSS** : Modifier `static/css/style.css`
- **JavaScript** : Modifier `static/js/script.js`
- **Templates** : Modifier les fichiers dans `templates/`

## 🤝 Contribution

1. Forker le projet
2. Créer une branche de fonctionnalité
3. Commiter les modifications
4. Pousser vers la branche
5. Créer une Pull Request

## 📄 Licence

Ce projet est sous licence MIT.

## 📞 Support

Pour toute question ou problème :
- Créer une issue sur le dépôt GitHub
- Contacter l'équipe de développement

---

**Educalim** - Platforme éducative moderne pour l'apprentissage numérique.