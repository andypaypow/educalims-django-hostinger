# 🏇 Guide de Création - Gosen Filter Django

---

## 📋 Sommaire

1. **Architecture du Projet** - Structure Django
2. **Configuration Hostinger** - Port 8082
3. **Intégration du HTML** - Template base
4. **Vues Django** - Une vue par filtre
5. **API Endpoints** - Communication frontend/backend
6. **Déploiement** - Mise en production

---

## ÉTAPE 1 : ARCHITECTURE DU PROJET

### 📁 Structure Django

```
gosen-filter/
├── gosen_project/           # Configuration Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── gosen/                   # Application principale
│   ├── views/               # Vues séparées par filtre
│   │   ├── __init__.py
│   │   ├── base.py          # Vue principale
│   │   ├── expert1.py       # Filtre Expert 1
│   │   ├── expert2.py       # Filtre Expert 2
│   │   ├── poids.py         # Filtre Poids
│   │   ├── statistiques.py  # Filtre Statistiques
│   │   ├── alternance.py    # Filtre Alternance
│   │   ├── synthesis.py     # Vues de synthèse
│   │   └── backtest.py      # Vue Backtest
│   ├── templates/
│   │   └── gosen/
│   │       ├── base.html    # Template principal (tri1.html)
│   │       └── partials/    # Morceaux de template
│   ├── static/
│   │   └── gosen/
│   │       ├── css/
│   │       ├── js/
│   │       └── img/
│   └── models.py
├── docker-compose.dev.yml
├── Dockerfile
└── requirements.txt
```

---

## ÉTAPE 2 : CONFIGURATION HOSTINGER

### 🌐 SSH Connection

```bash
ssh -i ~/.ssh/id_ed25519 root@72.62.181.239
```

### 📁 Création du répertoire

```bash
cd /root
mkdir gosen-filter-dev
cd gosen-filter-dev
```

### 🔧 Fichiers de Configuration

**`.env.dev`**
```bash
SECRET_KEY=django-insecure-gosen-dev-change-in-production
DEBUG=True
ALLOWED_HOSTS=*
POSTGRES_DB=gosen_dev
POSTGRES_USER=gosen
POSTGRES_PASSWORD=password
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

**`docker-compose.dev.yml`**
```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    container_name: gosen-dev-db
    environment:
      POSTGRES_DB: gosen_dev
      POSTGRES_USER: gosen
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data_dev:/var/lib/postgresql/data

  web:
    build: .
    container_name: gosen-dev-web
    command: gunicorn gosen_project.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 120
    volumes:
      - .:/code
      - static_volume:/code/staticfiles
    ports:
      - "8082:8000"
    depends_on:
      - db
    environment:
      - DEBUG=True
      - POSTGRES_DB=gosen_dev
      - POSTGRES_USER=gosen
      - POSTGRES_PASSWORD=password
      - POSTGRES_HOST=db
      - POSTGRES_PORT=5432

volumes:
  postgres_data_dev:
  static_volume:
```

**`Dockerfile`**
```dockerfile
FROM python:3.11-slim

WORKDIR /code

RUN apt-get update && apt-get install -y gcc postgresql-client && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

COPY . /code

RUN python manage.py collectstatic --noinput || true

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

**`requirements.txt`**
```txt
Django>=4.2,<5.0
psycopg2-binary>=2.9.6
gunicorn>=21.2.0
django-cors-headers>=4.0.0
```

---

## ÉTAPE 3 : CRÉATION DU PROJET DJANGO

### 🚀 Initialisation

```bash
# Sur Hostinger
cd /root/gosen-filter-dev
docker run --rm -v $(pwd):/code -w /code python:3.11-slim sh -c "
    pip install django && \
    django-admin startproject gosen_project . && \
    python manage.py startapp gosen
"
```

### ⚙️ Configuration `gosen_project/settings.py`

```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-dev')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'gosen',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'gosen' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'gosen_dev'),
        'USER': os.environ.get('POSTGRES_USER', 'gosen'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'password'),
        'HOST': os.environ.get('POSTGRES_HOST', 'db'),
        'PORT': os.environ.get('POSTGRES_PORT', '5432'),
    }
}

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'gosen' / 'static']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOW_ALL_ORIGINS = True
CSRF_TRUSTED_ORIGINS = ['http://72.62.181.239:8082']
```

---

## ÉTAPE 4 : INTÉGRATION DU HTML

### 📄 Copie du Template Principal

```bash
# Copier tri1.html vers le template Django
cp /root/Gosen-Filter/tri1.html /root/gosen-filter-dev/gosen/templates/gosen/base.html
```

### 🔧 Adapter le Template pour Django

**`gosen/templates/gosen/base.html`** (modifications)

```html
{% load static %}
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏇 Gosen TurfFilter</title>
    <script src='https://cdn.jsdelivr.net/npm/tesseract.js@5/dist/tesseract.min.js' defer></script>
    <!-- CSS reste identique -->
    <style>
        /* ... CSS inchangé ... */
    </style>
</head>
<body>
    <div class="container">
        <!-- HTML inchangé -->
    </div>

    <!-- JavaScript avec API Django -->
    <script>
        // Ajouter l'URL de l'API Django
        const DJANGO_API_URL = '/api/';

        document.addEventListener('DOMContentLoaded', () => {
            // ... code JavaScript existant ...

            // Remplacer la fonction triggerFilter() pour appeler Django
            async function triggerFilter() {
                // Récupérer les données du formulaire
                const formData = {
                    num_partants: parseInt(document.getElementById('num-partants').value),
                    taille_combinaison: parseInt(document.getElementById('taille-combinaison').value),
                    pronostics: parsePronostics(),
                    filters: getActiveFilters()
                };

                // Appeler l'API Django
                const response = await fetch(`${DJANGO_API_URL}filter/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify(formData)
                });

                const result = await response.json();
                displayResults(result.filtered_combinations, result.total_combinations);
            }
        });

        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
    </script>
</body>
</html>
```

---

## ÉTAPE 5 : VUES DJANGO

### 📁 Structure des Vues

**`gosen/views/__init__.py`**
```python
from .base import *
from .expert1 import *
from .expert2 import *
from .poids import *
from .statistiques import *
from .alternance import *
from .synthesis import *
from .backtest import *
```

**`gosen/views/base.py`**
```python
from django.shortcuts import render
from django.http import JsonResponse
import json

def index(request):
    """Vue principale - affiche le template"""
    return render(request, 'gosen/base.html')

def api_filter(request):
    """
    API principale qui orchestre tous les filtres
    Endpoint: POST /api/filter/
    """
    if request.method == 'POST':
        data = json.loads(request.body)

        # Extraire les données
        n = data.get('num_partants')
        k = data.get('taille_combinaison')
        pronostics = data.get('pronostics', [])
        filters = data.get('filters', {})

        # Générer toutes les combinaisons
        all_combinations = generate_combinations(n, k)

        # Appliquer les filtres
        filtered = apply_all_filters(all_combinations, pronostics, filters)

        return JsonResponse({
            'filtered_combinations': filtered,
            'total_combinations': len(all_combinations),
            'filtered_count': len(filtered)
        })

def generate_combinations(n, k):
    """Génère toutes les combinaisons de k parmi n"""
    from itertools import combinations
    partants = list(range(1, n + 1))
    return [list(combo) for combo in combinations(partants, k)]

def apply_all_filters(combinations, pronostics, filters):
    """
    Orchestre l'application de tous les filtres
    Délègue à chaque vue de filtre spécialisée
    """
    from .expert1 import filter_expert1
    from .expert2 import filter_expert2
    from .poids import filter_poids
    from .statistiques import filter_statistiques
    from .alternance import filter_alternance

    result = combinations

    # Appliquer chaque filtre activé
    if filters.get('expert1', {}).get('enabled'):
        result = filter_expert1(result, pronostics, filters['expert1'])

    if filters.get('expert2', {}).get('enabled'):
        result = filter_expert2(result, pronostics, filters['expert2'])

    if filters.get('poids', {}).get('enabled'):
        result = filter_poids(result, filters['poids'])

    if filters.get('statistiques', {}).get('enabled'):
        result = filter_statistiques(result, filters['statistiques'])

    if filters.get('alternance', {}).get('enabled'):
        result = filter_alternance(result, filters['alternance'])

    return result
```

**`gosen/views/expert1.py`**
```python
"""
Filtre Expert 1: "Garder si au moins X chevaux sont dans au moins Y groupes"
"""
from typing import List

def filter_expert1(combinations: List[List[int]], pronostics: List[dict], params: dict) -> List[List[int]]:
    """
    Args:
        combinations: Liste des combinaisons à filtrer
        pronostics: Liste des groupes de pronostics [{name: str, horses: List[int]}, ...]
        params: Paramètres du filtre {chevaux_min: int, groupes_min: int}

    Returns:
        Combinaisons filtrées
    """
    chevaux_min = params.get('chevaux_min', 1)
    groupes_min = params.get('groupes_min', 1)

    filtered = []

    for combo in combinations:
        # Compter combien de groupes contiennent au moins chevaux_min de cette combinaison
        valid_groups = 0

        for group in pronostics:
            horses_in_group = sum(1 for h in combo if h in group['horses'])
            if horses_in_group >= chevaux_min:
                valid_groups += 1

        # Garder si assez de groupes valides
        if valid_groups >= groupes_min:
            filtered.append(combo)

    return filtered
```

**`gosen/views/expert2.py`**
```python
"""
Filtre Expert 2: "Garder si au moins X chevaux communs existent dans au moins Y groupes"
"""
from typing import List
from collections import Counter

def filter_expert2(combinations: List[List[int]], pronostics: List[dict], params: dict) -> List[List[int]]:
    """
    Args:
        combinations: Liste des combinaisons à filtrer
        pronostics: Liste des groupes de pronostics
        params: {chevaux_min: int, groupes_min: int}

    Returns:
        Combinaisons filtrées
    """
    chevaux_min = params.get('chevaux_min', 1)
    groupes_min = params.get('groupes_min', 1)

    filtered = []

    for combo in combinations:
        # Pour chaque cheval de la combinaison, compter dans combien de groupes il apparaît
        horse_group_count = {}

        for horse in combo:
            count = 0
            for group in pronostics:
                if horse in group['horses']:
                    count += 1
            horse_group_count[horse] = count

        # Compter les chevaux qui apparaissent dans au moins groupes_min groupes
        horses_with_enough_groups = sum(
            1 for count in horse_group_count.values()
            if count >= groupes_min
        )

        # Garder si au moins chevaux_min chevaux sont communs à assez de groupes
        if horses_with_enough_groups >= chevaux_min:
            filtered.append(combo)

    return filtered
```

**`gosen/views/poids.py`**
```python
"""
Filtre Poids: Filtrage par poids total des combinaisons
"""
from typing import List

def build_weight_map(source: str, n: int, pronostics: List[dict] = None, synthesis_data: dict = None) -> dict:
    """
    Construit une map de poids pour chaque cheval

    Args:
        source: 'default', 'manual', 'citation', 'position', 'results', 'expert'
        n: Nombre de partants
        pronostics: Groupes de pronostics
        synthesis_data: Données de synthèse

    Returns:
        Dictionnaire {numero_cheval: poids}
    """
    weight_map = {}

    if source == 'default':
        # Poids = numéro du cheval
        for i in range(1, n + 1):
            weight_map[i] = i

    elif source == 'citation' and synthesis_data:
        # Poids basé sur la synthèse par citation
        for idx, (horse, _) in enumerate(synthesis_data.get('citation', [])):
            weight_map[horse] = idx + 1

    elif source == 'position' and synthesis_data:
        # Poids basé sur la synthèse par position
        for idx, (horse, _) in enumerate(synthesis_data.get('position', [])):
            weight_map[horse] = idx + 1

    # Initialiser les chevaux non listés avec une pénalité
    for i in range(1, n + 1):
        if i not in weight_map:
            weight_map[i] = n + 1

    return weight_map

def filter_poids(combinations: List[List[int]], params: dict) -> List[List[int]]:
    """
    Args:
        combinations: Liste des combinaisons
        params: {
            weight_min: int,
            weight_max: int,
            source: str,
            n: int,
            pronostics: List[dict],
            synthesis_data: dict
        }

    Returns:
        Combinaisons filtrées
    """
    weight_min = params.get('weight_min', 21)
    weight_max = params.get('weight_max', 81)
    source = params.get('source', 'default')
    n = params.get('n', 16)
    pronostics = params.get('pronostics', [])
    synthesis_data = params.get('synthesis_data', {})

    # Construire la map de poids
    weight_map = build_weight_map(source, n, pronostics, synthesis_data)

    # Filtrer
    filtered = []
    for combo in combinations:
        total_weight = sum(weight_map.get(h, n + 1) for h in combo)
        if weight_min <= total_weight <= weight_max:
            filtered.append(combo)

    return filtered
```

**`gosen/views/statistiques.py`**
```python
"""
Filtre Statistiques: Pairs/Petits/Suites
"""
from typing import List

def filter_statistiques(combinations: List[List[int]], params: dict) -> List[List[int]]:
    """
    Args:
        combinations: Liste des combinaisons
        params: {
            even_odd: {enabled: bool, min: int, max: int},
            small_large: {enabled: bool, limit: int, min: int, max: int},
            consecutive: {enabled: bool, min: int, max: int}
        }

    Returns:
        Combinaisons filtrées
    """
    result = combinations

    # Filtre Pairs/Impairs
    if params.get('even_odd', {}).get('enabled'):
        result = _filter_even_odd(
            result,
            params['even_odd'].get('min', 0),
            params['even_odd'].get('max', 6)
        )

    # Filtre Petits/Grands
    if params.get('small_large', {}).get('enabled'):
        result = _filter_small_large(
            result,
            params['small_large'].get('limit', 10),
            params['small_large'].get('min', 0),
            params['small_large'].get('max', 6)
        )

    # Filtre Suites
    if params.get('consecutive', {}).get('enabled'):
        result = _filter_consecutive(
            result,
            params['consecutive'].get('min', 0),
            params['consecutive'].get('max', 7)
        )

    return result

def _filter_even_odd(combinations: List[List[int]], min_even: int, max_even: int) -> List[List[int]]:
    """Filtre par nombre de numéros pairs"""
    filtered = []
    for combo in combinations:
        even_count = sum(1 for n in combo if n % 2 == 0)
        if min_even <= even_count <= max_even:
            filtered.append(combo)
    return filtered

def _filter_small_large(combinations: List[List[int]], limit: int, min_small: int, max_small: int) -> List[List[int]]:
    """Filtre par nombre de petits numéros (<= limite)"""
    filtered = []
    for combo in combinations:
        small_count = sum(1 for n in combo if n <= limit)
        if min_small <= small_count <= max_small:
            filtered.append(combo)
    return filtered

def _filter_consecutive(combinations: List[List[int]], min_consec: int, max_consec: int) -> List[List[int]]:
    """Filtre par longueur de suite consécutive"""
    def get_longest_consecutive(arr):
        if len(arr) < 2:
            return len(arr)
        sorted_arr = sorted(arr)
        max_len = 1
        current_len = 1
        for i in range(1, len(sorted_arr)):
            if sorted_arr[i] == sorted_arr[i-1] + 1:
                current_len += 1
            else:
                max_len = max(max_len, current_len)
                current_len = 1
        return max(max_len, current_len)

    filtered = []
    for combo in combinations:
        longest = get_longest_consecutive(combo)
        if min_consec <= longest <= max_consec:
            filtered.append(combo)
    return filtered
```

**`gosen/views/alternance.py`**
```python
"""
Filtre Alternance: Compte les alternances sélectionné/non-sélectionné
"""
from typing import List

def calculate_alternances(combination: List[int], source_array: List[str]) -> int:
    """
    Compte le nombre d'alternances dans la combinaison

    Args:
        combination: Liste des numéros de la combinaison
        source_array: Liste ordonnée de tous les partants (en string)

    Returns:
        Nombre d'alternances
    """
    if len(source_array) == 0:
        return 0

    combo_set = set(str(h) for h in combination)
    alternances = 0

    for i in range(len(source_array) - 1):
        current_in = source_array[i] in combo_set
        next_in = source_array[i + 1] in combo_set
        if current_in != next_in:
            alternances += 1

    return alternances

def build_source_array(source: str, n: int, manual_input: str = None, synthesis_data: dict = None) -> List[str]:
    """
    Construit le tableau source pour le calcul d'alternance

    Returns:
        Liste de numéros en string (ordonnés)
    """
    if source == 'default':
        return [str(i) for i in range(1, n + 1)]

    elif source == 'manual' and manual_input:
        import re
        return re.findall(r'\d+', manual_input)

    elif source in ['citation', 'position', 'results', 'expert'] and synthesis_data:
        return [str(h) for h, _ in synthesis_data.get(source, [])]

    return []

def filter_alternance(combinations: List[List[int]], params: dict) -> List[List[int]]:
    """
    Args:
        combinations: Liste des combinaisons
        params: {
            min: int,
            max: int,
            source: str,
            n: int,
            manual_input: str,
            synthesis_data: dict
        }

    Returns:
        Combinaisons filtrées
    """
    min_alt = params.get('min', 0)
    max_alt = params.get('max', 5)
    source = params.get('source', 'default')
    n = params.get('n', 16)
    manual_input = params.get('manual_input', '')
    synthesis_data = params.get('synthesis_data', {})

    # Construire le tableau source
    source_array = build_source_array(source, n, manual_input, synthesis_data)

    if not source_array:
        return combinations  # Pas de filtrage si pas de source

    # Filtrer
    filtered = []
    for combo in combinations:
        alt_count = calculate_alternances(combo, source_array)
        if min_alt <= alt_count <= max_alt:
            filtered.append(combo)

    return filtered
```

**`gosen/views/synthesis.py`**
```python
"""
Vues de synthèse: Citation, Position, Résultats, Expert
"""
from django.http import JsonResponse
from typing import List, Dict
import json

def api_synthesis_citation(request):
    """
    API: Synthèse par citation
    Endpoint: POST /api/synthesis/citation/
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        pronostics = data.get('pronostics', [])

        # Compter les citations
        citation_counts = {}
        for group in pronostics:
            for horse in group.get('horses', []):
                citation_counts[horse] = citation_counts.get(horse, 0) + 1

        # Trier par ordre décroissant
        sorted_citation = sorted(citation_counts.items(), key=lambda x: x[1], reverse=True)

        return JsonResponse({
            'synthesis': sorted_citation,
            'compact': ' - '.join([str(h) for h, _ in sorted_citation])
        })

def api_synthesis_position(request):
    """
    API: Synthèse par position (pondérée)
    Endpoint: POST /api/synthesis/position/
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        pronostics = data.get('pronostics', [])

        # Calculer les scores de position
        position_scores = {}
        for group in pronostics:
            horses = group.get('horses', [])
            for idx, horse in enumerate(horses):
                # Plus de points si position = début de liste
                points = len(horses) - idx
                position_scores[horse] = position_scores.get(horse, 0) + points

        # Trier
        sorted_position = sorted(position_scores.items(), key=lambda x: x[1], reverse=True)

        return JsonResponse({
            'synthesis': sorted_position,
            'compact': ' - '.join([str(h) for h, _ in sorted_position])
        })

def api_synthesis_results(request):
    """
    API: Synthèse des chevaux filtrés
    Endpoint: POST /api/synthesis/results/
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        combinations = data.get('combinations', [])

        # Compter les apparitions
        horse_counts = {}
        for combo in combinations:
            for horse in combo:
                horse_counts[horse] = horse_counts.get(horse, 0) + 1

        # Trier
        sorted_results = sorted(horse_counts.items(), key=lambda x: x[1], reverse=True)

        return JsonResponse({
            'synthesis': sorted_results,
            'compact': ' - '.join([str(h) for h, _ in sorted_results])
        })

def api_synthesis_expert(request):
    """
    API: Synthèse de l'expert (classement global pondéré)
    Endpoint: POST /api/synthesis/expert/
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        citation = data.get('citation', [])
        position = data.get('position', [])
        results = data.get('results', [])

        # Poids pour chaque catégorie
        weights = {'citation': 1.0, 'position': 1.5, 'results': 2.0}

        # Extraire tous les chevaux uniques
        all_horses = set()
        for h, _ in citation: all_horses.add(h)
        for h, _ in position: all_horses.add(h)
        for h, _ in results: all_horses.add(h)

        # Calculer les points de rang pour chaque catégorie
        def get_rank_points(data_list, horse):
            for idx, (h, _) in enumerate(data_list):
                if h == horse:
                    return len(data_list) - idx
            return 0

        # Calculer le score final
        final_scores = {}
        for horse in all_horses:
            p_citation = get_rank_points(citation, horse)
            p_position = get_rank_points(position, horse)
            p_results = get_rank_points(results, horse)

            final_scores[horse] = (
                p_citation * weights['citation'] +
                p_position * weights['position'] +
                p_results * weights['results']
            )

        # Trier
        sorted_expert = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)

        return JsonResponse({
            'synthesis': [(h, round(s, 1)) for h, s in sorted_expert],
            'compact': ' - '.join([str(h) for h, _ in sorted_expert])
        })
```

**`gosen/views/backtest.py`**
```python
"""
Vue Backtest: Test d'une arrivée contre les combinaisons filtrées
"""
from django.http import JsonResponse
import json
from datetime import datetime

def api_backtest(request):
    """
    API: Backtest d'une arrivée
    Endpoint: POST /api/backtest/
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        arrivee = data.get('arrivee', [])
        combinations = data.get('combinations', [])
        filters = data.get('filters', {})
        config = data.get('config', {})

        # Convertir l'arrivée en set
        arrivee_set = set(arrivee)

        # Trouver les combinaisons qui contiennent l'arrivée
        matching_combinations = []
        for combo in combinations:
            combo_set = set(combo)
            if arrivee_set.issubset(combo_set):
                matching_combinations.append(combo)

        # Construire le rapport
        report = build_backtest_report(
            arrivee,
            matching_combinations,
            combinations,
            filters,
            config
        )

        return JsonResponse({
            'found': len(matching_combinations) > 0,
            'count': len(matching_combinations),
            'report': report
        })

def build_backtest_report(arrivee, matching_combinations, all_combinations, filters, config):
    """Construit le rapport de backtest"""
    report_lines = [
        "--- RAPPORT DE BACKTEST ---",
        f"Arrivée testée : {' - '.join(map(str, arrivee))}",
        f"Date du test : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
        "",
        "--- STATUT DE PRÉSENCE ---"
    ]

    if matching_combinations:
        report_lines.append(
            f"✅ TROUVÉE : L'arrivée [{', '.join(map(str, arrivee))}] est contenue dans {len(matching_combinations)} combinaison(s)"
        )
    else:
        report_lines.append(
            f"❌ ABSENTE : Aucune combinaison ne contient l'arrivée [{', '.join(map(str, arrivee))}]"
        )

    return '\n'.join(report_lines)

def api_save_backtest(request):
    """
    API: Sauvegarder un rapport de backtest
    Endpoint: POST /api/backtest/save/
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        report = data.get('report', '')

        # Créer un fichier avec la date
        filename = f"backtest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        # Sauvegarder (optionnel: en base de données ou fichier)
        # Pour l'instant, retourner le contenu

        return JsonResponse({
            'success': True,
            'filename': filename,
            'content': report
        })
```

---

## ÉTAPE 6 : URLS DJANGO

**`gosen_project/urls.py`**
```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('gosen.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
```

**`gosen/urls.py`** (créer ce fichier)
```python
from django.urls import path
from . import views

app_name = 'gosen'

urlpatterns = [
    # Page principale
    path('', views.index, name='index'),

    # API endpoints
    path('api/filter/', views.api_filter, name='api_filter'),

    # Synthèse APIs
    path('api/synthesis/citation/', views.api_synthesis_citation, name='api_synthesis_citation'),
    path('api/synthesis/position/', views.api_synthesis_position, name='api_synthesis_position'),
    path('api/synthesis/results/', views.api_synthesis_results, name='api_synthesis_results'),
    path('api/synthesis/expert/', views.api_synthesis_expert, name='api_synthesis_expert'),

    # Backtest API
    path('api/backtest/', views.api_backtest, name='api_backtest'),
    path('api/backtest/save/', views.api_save_backtest, name='api_save_backtest'),
]
```

---

## ÉTAPE 7 : DÉPLOIEMENT

### 🚀 Lancer les conteneurs

```bash
cd /root/gosen-filter-dev
docker compose -f docker-compose.dev.yml up -d --build
```

### ✅ Vérifier le déploiement

```bash
# Vérifier les conteneurs
docker ps --filter 'name=gosen'

# Vérifier les logs
docker compose -f docker-compose.dev.yml logs -f web

# Appliquer les migrations
docker compose -f docker-compose.dev.yml exec web python manage.py migrate

# Créer un super utilisateur
docker compose -f docker-compose.dev.yml exec web python manage.py createsuperuser
```

### 🌐 Accès

| Environnement | URL | Admin |
|---------------|-----|-------|
| Dev | http://72.62.181.239:8082/ | http://72.62.181.239:8082/admin/ |

---

## ÉTAPE 8 : FICHIERS À CRÉER

### 📝 Liste complète

```bash
cd /root/gosen-filter-dev

# Structure des dossiers
mkdir -p gosen/views
mkdir -p gosen/templates/gosen
mkdir -p gosen/static/gosen/{css,js,img}

# Créer les fichiers vides
touch gosen/views/__init__.py
touch gosen/views/base.py
touch gosen/views/expert1.py
touch gosen/views/expert2.py
touch gosen/views/poids.py
touch gosen/views/statistiques.py
touch gosen/views/alternance.py
touch gosen/views/synthesis.py
touch gosen/views/backtest.py

# Copier le HTML
cp /root/Gosen-Filter/tri1.html gosen/templates/gosen/base.html
```

---

## 🔄 FONCTIONNEMENT GLOBAL

```
┌─────────────────────────────────────────────────────────────┐
│                    BROWSER (Client)                         │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP Request
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              DJANGO VIEW (base.py)                          │
│  - Reçoit les données du formulaire                         │
│  - Orchestre les filtres                                    │
│  - Retourne les résultats                                   │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
    ┌─────────┐    ┌─────────┐    ┌─────────┐
    │Expert1  │    │Expert2  │    │ Poids   │
    │  View   │    │  View   │    │  View   │
    └─────────┘    └─────────┘    └─────────┘
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
    ┌─────────┐    ┌─────────┐    ┌─────────┐
    │Stats    │    │Alternate │    │Synthesis│
    │  View   │    │   View   │    │  Views  │
    └─────────┘    └─────────┘    └─────────┘
         └───────────────┬───────────────┘
                         ▼
                ┌────────────────┐
                │  FILTERED      │
                │  COMBINATIONS  │
                └────────────────┘
```

---

## 📊 API ENDPOINTS

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/` | GET | Page principale |
| `/api/filter/` | POST | Appliquer tous les filtres |
| `/api/synthesis/citation/` | POST | Synthèse par citation |
| `/api/synthesis/position/` | POST | Synthèse par position |
| `/api/synthesis/results/` | POST | Synthèse des résultats |
| `/api/synthesis/expert/` | POST | Synthèse expert pondérée |
| `/api/backtest/` | POST | Tester une arrivée |
| `/api/backtest/save/` | POST | Sauvegarder rapport |

---

**Document créé le :** 28 Janvier 2026
**Projet :** Gosen TurfFilter Django
**Port Dev :** 8082
**VPS :** Hostinger (72.62.181.239)
