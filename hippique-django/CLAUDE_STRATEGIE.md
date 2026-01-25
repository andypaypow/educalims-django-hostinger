# 🧠 CLAUDE - Stratégie de Travail - TurfFilter Django

## 📋 Table des Matières

1. [Architecture de Sécurité](#architecture-de-sécurité)
2. [Workflow de Développement](#workflow-de-développement)
3. [Structure du Projet](#structure-du-projet)
4. [Protection de la Propriété Intellectuelle](#protection-de-la-propriété-intellectuelle)
5. [Déploiement Hostinger Dev](#déploiement-hostinger-dev)

---

## 🔒 Architecture de Sécurité

### Principe Fondamental : Server-Side Processing

```
┌─────────────────────────────────────────────────────────────────┐
│                     NAVIGATEUR CLIENT                           │
│  (Ce que l'utilisateur voit et peut inspecter)                 │
├─────────────────────────────────────────────────────────────────┤
│  ✓ HTML rendu (templates Django)                               │
│  ✓ CSS/Statique                                                 │
│  ✓ JavaScript (appels API fetch)                               │
│  ✓ Réponses JSON (résultats filtrés)                           │
│                                                                 │
│  ❌ CODE PYTHON - JAMAIS ACCESSIBLE                            │
│  ❌ formules.py - LOGIQUE MATHÉMATIQUE SECRÈTE                 │
│  ❌ views.py - TRAITEMENT CÔTÉ SERVEUR                         │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ HTTP POST (JSON)
                                │ {n: 16, k: 6, groups: [...], filters: {...}}
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DJANGO SERVEUR (Hostinger)                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ API ENDPOINT (views.py)                                  │  │
│  │  Reçoit → Traite → Répond                                 │  │
│  └───────────────────────┬───────────────────────────────────┘  │
│                          ▼                                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ MOTEUR DE FILTRAGE (formules.py)                         │  │
│  │  • apply_all_filters()                                   │  │
│  │  • combinations_count()                                  │  │
│  │  • expert1_filter(), expert2_filter()                    │  │
│  │  • TOUTE L'INTELLIGENCE DU FILTRAGE                      │  │
│  │                                                          │  │
│  │  🔒 CODE PYTHON EXÉCUTÉ CÔTÉ SERVEUR                    │  │
│  │     JAMAIS TRANSMIS AU CLIENT                            │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Pourquoi c'est inviolable ?

1. **Python est exécuté côté serveur** - Le client ne reçoit que le résultat
2. **Aucun accès au système de fichiers** - Impossible de lire `.py` depuis le navigateur
3. **Django avec DEBUG=False** - En production, les erreurs ne révèlent pas le code source

---

## 🔄 Workflow de Développement

### Phase Actuelle : Développement Local

```
Local (Windows)                  Git (GitHub)                  Hostinger (Dev)
─────────────                   ───────────                   ─────────────────
✓ hippie/formules.py     →     (pas encore)           →     (pas encore)
✓ hippie/views.py        →                           →
✓ hippie/urls.py         →                           →
✓ templates/            →                           →
✓ Django runserver 8082                              (future)
```

### Processus de Travail

```bash
# 1. Modifier le code localement
cd C:\Users\HP 360\Desktop\hippique-django

# 2. Tester localement
python manage.py runserver 8082
# → http://localhost:8082/hippie/turf-filter/

# 3. Valider les fonctionnalités
curl -X POST http://localhost:8082/hippie/api/filter/ \
  -H "Content-Type: application/json" \
  -d '{"n": 16, "k": 6, ...}'

# 4. Commiter (FUTUR)
git add hippie/
git commit -m "Feature: ..."
git push origin main

# 5. Déployer sur Hostinger (FUTUR)
ssh root@72.62.181.239
cd /var/www/hippique-django
git pull
docker-compose restart
```

---

## 📁 Structure du Projet

```
hippique-django/
├── hippie/                        # Application TurfFilter
│   ├── formules.py               # 🔐 MOTEUR MATHÉMATIQUE (809 lignes)
│   │   ├── combinations_count()  #    C(n,k)
│   │   ├── apply_all_filters()   #    Application des filtres
│   │   ├── expert1_filter()      #    Logique OU
│   │   ├── expert2_filter()      #    Logique ET
│   │   └── ...                   #    Toutes les formules
│   │
│   ├── views.py                  # API Endpoints
│   │   ├── api_combinations_count()
│   │   ├── api_parse_pronostics()
│   │   ├── api_synthesis()
│   │   ├── api_filter_combinations()  # ← APPELLE formules.py
│   │   └── api_backtest()
│   │
│   ├── urls.py                  # Routes /hippie/api/*
│   │
│   └── templates/hippie/
│       └── turf_filter.html     # Interface utilisateur
│
├── hippie_project/              # Configuration Django
│   ├── settings.py              # DEBUG=False en production
│   ├── urls.py                  # Inclusion des URLs hippie
│   └── wsgi.py                  # Interface WSGI
│
├── main/                        # Application principale (admin)
│
├── manage.py                    # Commandes Django
├── db.sqlite3                   # Base locale
└── requirements.txt             # Dépendances Python
```

---

## 🛡️ Protection de la Propriété Intellectuelle

### Ce qui est PUBLIC (Client)

```javascript
// Le client voit SEULEMENT ce JavaScript :
async function apiCall(endpoint, data) {
    const response = await fetch(API_BASE + endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    return await response.json();
}

// Et reçoit SEULEMENT ce JSON :
{
    "total": 8008,
    "filtered": 25,
    "combinations": [[1,2,3,4,5,6], ...]
}
```

### Ce qui est PRIVÉ (Serveur)

```python
# JAMAIS ACCESSIBLE depuis le navigateur :
def apply_all_filters(n, k, groups, or_filters, and_filters, ...):
    """Votre propriété intellectuelle protégée"""
    partants = list(range(1, n + 1))
    filtered_combinations = []

    for combi in combination_generator(partants, k):
        # VOTRE LOGIQUE DE FILTRAGE EXCLUSIVE
        if expert1_filter(combi, groups, ...):
            if expert2_filter(combi, groups, ...):
                filtered_combinations.append(sorted(combi))

    return filtered_combinations
```

### Garanties Django

| Risque | Protection Django |
|--------|-------------------|
| Lecture des fichiers `.py` | ❌ Impossible depuis HTTP |
| Accès direct aux formules | ❌ Python exécuté côté serveur |
| Reverse engineering | ⚠️ Seulement les entrées/sorties visibles |
| Dump de la base de données | ❌ Protégé par le pare-feu Hostinger |

---

## 🚀 Déploiement Hostinger Dev (FUTUR)

### Prérequis

- [ ] Compte Hostinger VPS avec accès SSH
- [ ] Docker et Docker Compose installés
- [ ] Domaine configuré : hippique-dev.com
- [ ] PostgreSQL configuré

### Étapes de Déploiement

```bash
# 1. Préparer le code
git add hippie/ hippie_project/ manage.py requirements.txt
git commit -m "Add TurfFilter application"
git push origin main

# 2. Connexion SSH au serveur
ssh root@72.62.181.239

# 3. Cloner/Mettre à jour le dépôt
cd /var/www/
git clone https://github.com/andypaypow/educalims-django-hostinger.git hippique-django
cd hippique-django

# 4. Configuration production
cp .env.prod.template .env
# Éditer .env avec les vraies valeurs

# 5. Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# 6. Migrations
docker-compose exec web python manage.py migrate

# 7. Créer le superuser
docker-compose exec web python manage.py createsuperuser

# 8. Vérifier
curl http://localhost:8082/hippie/turf-filter/
```

### Configuration Production

```python
# hippie_project/settings.py
DEBUG = False  # ← CRITIQUE : Cache les erreurs détaillées
ALLOWED_HOSTS = ['hippique-dev.com', '72.62.181.239']

# Sécurité CSRF
CSRF_TRUSTED_ORIGINS = ['https://hippique-dev.com']

# Base de données PostgreSQL (pas SQLite en prod)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': 'db',
        'PORT': '5432',
    }
}
```

---

## 📊 Résumé Technique

### Stack Technologique

| Couche | Technologie | Rôle |
|--------|-------------|------|
| Frontend | HTML/CSS/JS | Interface utilisateur |
| Backend | Python 3.12+ | Logique métier |
| Framework | Django 4.2+ | Serveur web |
| API | REST (JSON) | Communication client/serveur |
| Base de données | PostgreSQL | Stockage production |
| Déploiement | Docker Compose | Conteneurisation |

### Points d'Accès

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/hippie/turf-filter/` | GET | Interface principale |
| `/hippie/api/combinations-count/` | POST | C(n,k) |
| `/hippie/api/parse-pronostics/` | POST | Parser les groupes |
| `/hippie/api/synthesis/` | POST | Synthèse citation/position |
| `/hippie/api/filter/` | POST | Filtrer les combinaisons |
| `/hippie/api/backtest/` | POST | Tester une arrivée |

---

## 🔑 Points Clés à Retenir

1. **SÉCURITÉ** : Les formules mathématiques sont dans `formules.py`, côté serveur, inaccessible aux clients
2. **API** : Tout passe par des endpoints JSON, le client ne voit que les résultats
3. **LOCAL FIRST** : Développement et tests locaux avant déploiement
4. **DOCKER** : Déploiement containerisé pour la production
5. **PROTECTED** : Même avec accès HTTP, le code Python n'est jamais exposé

---

## 📝 Notes de Développement

### Fichiers Modifiés Récemment

- `hippie/formules.py` - 24Ko, 809 lignes de mathématiques pures
- `hippie/views.py` - 13Ko, API endpoints
- `hippie/urls.py` - Configuration des routes
- `hippie/templates/hippie/turf_filter.html` - Interface utilisateur complète

### Prochaines Étapes

1. ✅ Création de l'architecture de base
2. ✅ Implémentation des formules mathématiques
3. ✅ Création des API endpoints
4. ✅ Interface utilisateur fonctionnelle
5. ⏳ Tests locaux approfondis
6. ⏳ Déploiement Hostinger Dev
7. ⏳ Tests en production
8. ⏳ Documentation utilisateur

---

*Document généré par GLM 4.6 pour le projet TurfFilter Django*
*Dernière mise à jour : 23 janvier 2026*
