# CLAUDE_HIPPIQUE.md

Ce fichier fournit des instructions à Claude Code (claude.ai/code) lorsqu'il travaille avec le code de l'application Hippique.

---

# 🏇 Hippique TurbFilter - Guide Complet Hostinger

---

## 📋 Sommaire

1. **Architecture sur Hostinger** - Infrastructure
2. **Base de Données et Modèles** - Données et structure
3. **Filtrage de Combinaisons** - Algorithmes et formules
4. **Git et Déploiement** - Commit, Push, Migrations
5. **Workflow Dev ↔ Prod** - Processus complet

---

## ÉTAPE 1 : ARCHITECTURE SUR HOSTINGER

### 🌐 Architecture Globale

```
┌─────────────────────────────────────────────────────────────┐
│                   Hostinger VPS                              │
│  IP : 72.62.181.239                                         │
│  SSH : ssh -i ~/.ssh/id_ed25519 root@72.62.181.239          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ Educalims    │  │ Hippique     │  │ Hippique     │   │
│  │ Dev          │  │ Dev          │  │ Prod         │   │
│  │ Port: 8081   │  │ Port: 8082   │  │ Port: 8083   │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
│                                                              │
│  ┌──────────────┐                                           │
│  │ Educalims    │                                           │
│  │ Prod         │                                           │
│  │ Port: 80     │                                           │
│  └──────────────┘                                           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 📁 Structure des Répertoires

```
/root/
├── educalims-dev/         ← Application éducative (existant)
│   └── Port 8081
│
├── educalims-prod/        ← Application éducative (existant)
│   └── Port 80
│
├── hippique-dev/          ← NOUVEAU : Filtre hippique Dev
│   ├── docker-compose.dev.yml
│   ├── .env.dev
│   ├── git-push.sh
│   └── code/ (volume monté)
│
└── hippique-prod/         ← NOUVEAU : Filtre hippique Prod
    ├── docker-compose.yml
    ├── .env.prod
    └── code (image Docker)
```

### 🐳 Conteneurs par Environnement

| Conteneur | Rôle | Port Interne |
|-----------|------|---------------|
| **nginx** | Reverse Proxy + Static | - |
| **web** | Django + Gunicorn | 8000 |
| **db** | PostgreSQL | 5432 |

---

## ÉTAPE 2 : BASE DE DONNÉES ET MODÈLES

### 🗄️ Structure PostgreSQL

**Dev :** hippique_dev
**Prod :** hippique_prod
**User :** hippique

### 📊 Tables Principales

```sql
-- Tables principales
hippique_course               -- Courses hippiques
hippique_pronosticgroupe     -- Groupes de pronostics
hippique_filtreconfiguration  -- Configurations de filtres
hippique_resultatanalyse     -- Résultats d'analyses
hippique_backtest            -- Tests d'arrivée
hippique_utilisateurpreferences -- Préférences utilisateur
hippique_course_reelle       -- Arrivées officielles
hippique_cacheanalyse        -- Cache de performance
hippique_performancestats    -- Statistiques de performance
```

### 🔄 Relations entre Modèles

```
Course (1) ─────< (M) PronosticGroupe
  │
  │
 (1)
  │
  ▼
FiltreConfiguration (M) ──> Course (FK)

ResultatAnalyse (M) ──> Course (FK)
  │
  │
 (1)
  │
  ▼
Backtest (M) ─────────────> ResultatAnalyse (FK)

User (Django) (1) ─────> UtilisateurPreferences (1)
```

### 📦 Migrations

```bash
# Créer les migrations après modification des modèles
docker compose -f docker-compose.dev.yml exec web python manage.py makemigrations

# Appliquer les migrations
docker compose -f docker-compose.dev.yml exec web python manage.py migrate

# Voir les migrations appliquées
docker compose -f docker-compose.dev.yml exec web python manage.py showmigrations
```

### ✅ Vérifier l'État de la Base

```bash
docker compose -f docker-compose.dev.yml exec -T db psql -U hippique -d hippique_dev -c "
SELECT 'Courses', COUNT(*) FROM hippique_course
UNION ALL SELECT 'Pronostics', COUNT(*) FROM hippique_pronosticgroupe
UNION ALL SELECT 'Filtres', COUNT(*) FROM hippique_filtreconfiguration
UNION ALL SELECT 'Analyses', COUNT(*) FROM hippique_resultatanalyse
UNION ALL SELECT 'Backtests', COUNT(*) FROM hippique_backtest;"
```

---

## ÉTAPE 3 : FILTRAGE DE COMBINAISONS

### 🧮 Formules Mathématiques Principales

#### 1. Combinaisons (Coefficient Binomial)

```python
def combinations_count(n, k):
    """
    C(n,k) = n! / (k! * (n-k)!)

    Exemple: C(16, 6) = 8008 combinaisons
    """
```

#### 2. Synthèse par Citation

```python
def citation_synthesis(groups):
    """
    Compte le nombre d'apparitions de chaque cheval dans tous les groupes

    Exemple:
        Groupe 1: [1, 2, 3]
        Groupe 2: [2, 4, 6]
        → 1: 1 fois, 2: 2 fois, 3: 1 fois, 4: 1 fois, 6: 1 fois
    """
```

#### 3. Synthèse par Position (Pondérée)

```python
def position_synthesis(groups):
    """
    Attribue des points selon la position dans chaque groupe
    Score = (taille_groupe - position)

    Exemple:
        Groupe [1, 2, 3, 4]:
        Position 0 (cheval 1): 4 pts
        Position 1 (cheval 2): 3 pts
        Position 2 (cheval 3): 2 pts
        Position 3 (cheval 4): 1 pt
    """
```

#### 4. Synthèse de l'Expert (Global)

```python
def expert_synthesis(citation, position, results):
    """
    Combine les 3 synthèses avec pondérations

    Score = (P_Citation × 1.0) + (P_Position × 1.5) + (P_Results × 2.0)

    Les résultats filtrés ont un poids plus important (2.0)
    """
```

#### 5. Filtre Poids

```python
def calculate_combination_weight(combination, weight_map):
    """
    Poids_Total = Σ(poids_cheval_i)

    Sources de poids:
    - default: poids = numéro du cheval
    - manual: poids = position dans liste manuelle
    - citation: poids = rang dans synthèse citation
    - position: poids = rang dans synthèse position
    - results: poids = rang dans synthèse résultats
    - expert: poids = rang dans synthèse expert
    """
```

#### 6. Filtre Alternance

```python
def calculate_alternances(combination, source_array):
    """
    Compte les changements Sélectionné ↔ Non-Sélectionné
    en parcourant la liste ordonnée

    Maximum théorique = 2 × k (taille de combinaison)

    Exemple:
        Combination: [1, 3, 5]
        Source: [1, 2, 3, 4, 5, 6]
        Analyse: 1(S)→2(N)→3(S)→4(N)→5(S)→6(N)
        Alternances: 5
    """
```

### 🎯 Ordre d'Application des Filtres

```
1. Groupe Min/Max
2. Expert 1 (Standard - OU logique)
3. Expert 2 (Avancé - ET logique)
4. Pairs/Impairs
5. Petits/Grands numéros
6. Suites consécutives
7. Poids
8. Alternance
```

---

## ÉTAPE 4 : GIT ET DÉPLOIEMENT

### 📝 Workflow Git

```bash
# 1. Travailler en DEV
cd /root/hippique-dev
git checkout dev

# 2. Modifier le code
# ... modifications ...

# 3. Vérifier
git status
git diff

# 4. Ajouter et committer (PAS de secrets)
git add .
git commit -m "feat: description"
./git-push.sh
```

### 🚀 Déploiement vers Prod

```bash
# 1. Mergere dev → main
cd /root/hippique-dev
git checkout main
git merge dev
./git-push.sh

# 2. Aller en PROD et pull
cd /root/hippique-prod
git pull origin main

# 3. REBUILD le conteneur web (OBLIGATOIRE)
docker compose up -d --build web

# 4. Appliquer les migrations
docker compose exec web python manage.py migrate

# 5. Retourner sur dev
cd /root/hippique-dev
git checkout dev
```

### 📋 Format des Commits

```
feat: nouvelle fonctionnalité
fix: correction de bug
refactor: refactoring
docs: documentation
style: style/formatting
test: tests
chore: tâches diverses
```

---

## ÉTAPE 5 : WORKFLOW DEV ↔ PROD

### 🔄 Processus Complet

```
┌─────────────────────────────────────────────────────────────┐
│                     DÉVELOPPEMENT                         │
│                                                             │
│  1. cd /root/hippique-dev                                │
│  2. git checkout dev                                       │
│  3. ... coder et tester localement ...                     │
│  4. git add . && git commit -m "feat: ..."               │
│  5. ./git-push.sh                                          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                     MERGE                                 │
│                                                             │
│  1. git checkout main                                      │
│  2. git merge dev                                          │
│  3. ./git-push.sh                                          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  PRODUCTION                                │
│                                                             │
│  1. cd /root/hippique-prod                                │
│  2. git pull origin main                                   │
│  3. docker compose up -d --build web  ← OBLIGATOIRE       │
│  4. docker compose exec web python manage.py migrate      │
└─────────────────────────────────────────────────────────────┘
```

### 📊 Comparaison Dev vs Prod

| Action | Dev | Prod |
|--------|-----|------|
| **Port** | 8082 | 8083 |
| **Chemin** | /root/hippique-dev | /root/hippique-prod |
| **Compose** | docker-compose.dev.yml | docker-compose.yml |
| **Code** | Volume monté | Dans image Docker |
| **Déploiement** | `restart web` | `--build web` OBLIGATOIRE |
| **DB** | hippique_dev | hippique_prod |

---

## 🌐 ACCÈS RAPIDES

| Environnement | URL | Admin Django |
|---------------|-----|---------------|
| **Hippique Dev** | http://72.62.181.239:8082/ | http://72.62.181.239:8082/admin/ |
| **Hippique Prod** | http://72.62.181.239:8083/ | http://72.62.181.239:8083/admin/ |

**Identifiants Admin par défaut :**
- Username : `admin`
- Password : `admin`

---

## ⚠️ PIÈGES À ÉVITER

1. **NE JAMAIS modifier directement en prod** → Toujours passer par git
2. **TOUJOURS faire `--build web` en prod** après pull
3. **TOUJOURS migrer** après changement de modèles
4. **JAMAIS committer de secrets** → .env, tokens, clés API
5. **NE JAMAIS supprimer les volumes** sans sauvegarde → `docker compose down -v` ❌

### 🚨 Fichiers à NE JAMAIS COMMIT

```
.env / .env.dev / .env.prod
*.pyc
__pycache__
.github_token
*.bak
*.log
db.sqlite3
```

### ✅ Checklist Avant Commit

- [ ] Pas de fichiers .env dans le staging
- [ ] Pas de secrets dans les fichiers
- [ ] Message de commit clair (type: description)
- [ ] Fichiers .bak retirés du staging
- [ ] `git status` vérifié

---

## 🔧 COMMANDES UTILES

### Démarrer/Arrêter les conteneurs

```bash
# Dev
cd /root/hippique-dev
docker compose -f docker-compose.dev.yml up -d
docker compose -f docker-compose.dev.yml down

# Prod
cd /root/hippique-prod
docker compose up -d
docker compose down
```

### Voir les logs

```bash
# Dev
docker compose -f docker-compose.dev.yml logs -f web

# Prod
docker compose logs -f web
```

### Accéder au shell Django

```bash
# Dev
docker compose -f docker-compose.dev.yml exec web python manage.py shell

# Prod
docker compose exec web python manage.py shell
```

---

## 💾 SAUVEGARDE ET RESTAURATION

### ⚠️ RÈGLE D'OR

**NE JAMAIS supprimer les volumes Docker sans sauvegarde !**

### Sauvegarder

```bash
# Dev
cd /root/hippique-dev
mkdir -p backups
docker compose -f docker-compose.dev.yml exec -T db pg_dump -U hippique hippique_dev > backups/backup_$(date +%Y%m%d_%H%M%S).sql

# Prod
cd /root/hippique-prod
mkdir -p backups
docker compose exec -T db pg_dump -U hippique hippique_prod > backups/backup_$(date +%Y%m%d_%H%M%S).sql
```

### Restaurer

```bash
# Restaurer depuis une sauvegarde
cat backups/backup_XXX.sql | docker compose -f docker-compose.dev.yml exec -T db psql -U hippique hippique_dev
```

---

**Dernière mise à jour** : 22 Janvier 2026
**Application** : Hippique TurbFilter - Filtre de combinaisons hippiques
**Repository** : https://github.com/andypaypow/hippique-django-hostinger.git
