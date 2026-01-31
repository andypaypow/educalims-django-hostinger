# Calculs Côté Serveur - Gosen TurfFilter

## 🎯 Objectif

Protéger les formules de filtrage en effectuant **tous les calculs côté serveur** plutôt que dans le navigateur client. Les utilisateurs peuvent utiliser l'application mais ne peuvent pas voir ni copier les formules.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Architecture serveur                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  👤 Utilisateur (navigateur)                                │
│  ─────────────────────────────                              │
│  • Remplit les formulaires                                   │
│  • Clique "Filtrer"                                          │
│  ⬇️ Envoie données via API POST                             │
│                                                              │
│  ┌──────────────────────────────────────────────────┐      │
│  │          🖥️ SERVEUR DJANGO (Hostinger)           │      │
│  │                                                   │      │
│  │   🔒 API: /api/filter/                            │      │
│  │                                                   │      │
│  │   • Reçoit les paramètres                          │      │
│  │   • Génère les combinaisons                        │      │
│  │   • Applique TOUS les filtres                     │      │
│  │   • Renvoie les résultats                          │      │
│  │                                                   │      │
│  │   ✅ Formules cachées (views/filters.py)          │      │
│  价比                                                   │      │
│  └──────────────────────────────────────────────────┘      │
│           ⬆️ Renvoie JSON {filtered, total}                 │
│                                                              │
│  👤 Navigateur affiche les résultats                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Fichiers impliqués

### 1. API de filtrage (Côté serveur)

**Fichier** : `gosen/views/filters.py`

```python
@require_http_methods(["POST"])
@csrf_exempt
def api_filter_combinations(request):
    """
    API principale de filtrage
    Accessible à tous les utilisateurs
    TOUT les calculs se font côté serveur
    """
    # Paramètres reçus du client
    n = data.get('n')  # nombre de partants
    k = data.get('k')  # taille de combinaison
    groups = data.get('groups')  # pronostics
    orFilters = data.get('orFilters')  # Expert 1
    andFilters = data.get('andFilters')  # Expert 2
    weightFilters = data.get('weightFilters')  # Poids
    alternanceFilters = data.get('alternanceFilters')  # Alternance
    # ... autres filtres

    # Génération et filtrage des combinaisons
    for combi in combination_generator(partants, k):
        # Appliquer tous les filtres
        # ...
        if kept:
            filtered_combinations.append(combi)

    return JsonResponse({
        'success': True,
        'filtered': filtered_combinations,
        'total': total_combinations
    })
```

### 2. JavaScript client (Envoi des données)

**Fichier** : `gosen/static/gosen/js/main.js`

```javascript
async function triggerFilter() {
    // Collecter les données depuis le DOM
    const n = parseInt(numPartantsInput.value);
    const k = parseInt(tailleCombinaisonInput.value);
    const groups = [...];  // depuis parsedGroupsDiv
    const orFilters = [...];  // depuis .standard-filter
    // ... autres filtres

    // ====== APPEL API CÔTÉ SERVEUR ======
    const response = await fetch('/api/filter/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({n, k, groups, orFilters, ...})
    });

    const data = await response.json();

    if (data.success) {
        displayResults(data.filtered, data.total);
    }
}
```

### 3. URLs

**Fichier** : `gosen/urls.py`

```python
urlpatterns = [
    # ...
    path('api/filter/', filters.api_filter_combinations, name='api_filter'),
]
```

---

## 🔄 Flux de données

### 1. Utilisateur remplit le formulaire

```
navigateur → DOM input values
```

### 2. JavaScript collecte les données

```javascript
const n = parseInt(numPartantsInput.value);  // ex: 16
const k = parseInt(tailleCombinaisonInput.value);  // ex: 6
const groups = [
    {name: "Groupe 1", horses: [1,2,3], min: 1, max: 2}
];
```

### 3. JavaScript envoie à l'API

```bash
POST /api/filter/
Content-Type: application/json

{
  "n": 16,
  "k": 6,
  "groups": [...],
  "orFilters": [...],
  "andFilters": [...]
}
```

### 4. Serveur calcule et renvoie

```python
# Côté serveur (Python)
for combi in combinations([1,2,3,...,16], 6):
    if passe_tous_les_filtres(combi):
        resultats.append(combi)

return JsonResponse({
    "filtered": [[1,2,3,4,5,6], [1,2,3,4,5,7], ...],
    "total": 8008
})
```

### 5. JavaScript affiche les résultats

```javascript
displayResults(data.filtered, data.total);
// → Affiche les combinaisons dans le DOM
```

---

## ✅ Avantages

| Avant (Client) | Après (Serveur) |
|----------------|-----------------|
| ❌ Formules visibles (F12) | ✅ Formules cachées |
| ❌ Calculs dans le navigateur | ✅ Calculs sur le serveur |
| ❌ Facile à copier | ✅ Protégé |
| ⚠️ Dépend du navigateur | ✅ Plus contrôle |

---

## 🔧 Implémentation sur DEV (8082)

### Structure des fichiers

```
gosen/
├── views/
│   └── filters.py          ← API de calculs côté serveur
├── static/
│   └── gosen/
│       ├── css/
│       │   └── styles.css  ← Styles séparés
│       └── js/
│           └── main.js     ← Appelle l'API (ne calcule pas)
└── templates/
    └── gosen/
        └── base.html       ← HTML simplifié
```

### URL de l'API

```
POST http://72.62.181.239:8082/api/filter/
```

### Corps de la requête

```json
{
  "n": 16,
  "k": 6,
  "groups": [
    {"name": "Favoris", "horses": [1,2,3], "min": 1, "max": 2}
  ],
  "orFilters": [
    {"chevauxMin": 1, "groupesMin": 1}
  ],
  "andFilters": [],
  "weightFilters": [],
  "evenOddFilters": [],
  "smallLargeFilters": [],
  "consecutiveFilters": [],
  "alternanceFilters": []
}
```

### Réponse de l'API

```json
{
  "success": true,
  "filtered": [
    [1, 2, 4, 5, 6, 7],
    [1, 2, 4, 5, 6, 8],
    ...
  ],
  "total": 8008,
  "count": 5000
}
```

---

## 🚨 Points importants

### 1. PLUS de calculs côté client

Avant :
```javascript
// Web Worker avec TOUTE la logique de filtrage
const workerCode = `
    function* combinationGenerator(arr, k) { ... }
    function getLongestConsecutive(arr) { ... }
    // ... toutes les formules visibles
`;
```

Après :
```javascript
// Simple appel API
const response = await fetch('/api/filter/', {...});
// Les formules sont sur le serveur, invisibles
```

### 2. Le serveur est OBLIGATOIRE

- ❌ **Sans serveur** = Pas de filtrage possible
- ✅ **Avec serveur** = Filtrage fonctionnel
- 🔒 **Formules protégées** sur le serveur

### 3. Pas besoin d'être admin

- ✅ Tout le monde peut utiliser l'application
- ✅ Aucune restriction d'accès
- 🔒 Les formules restent cachées

---

## 🧪 Test

### Tester l'API directement

```bash
curl -X POST http://72.62.181.239:8082/api/filter/ \
  -H "Content-Type: application/json" \
  -d '{
    "n": 16,
    "k": 6,
    "groups": [{"horses": [1,2,3], "min": 1, "max": 2}],
    "orFilters": [],
    "andFilters": []
  }'
```

Réponse attendue :
```json
{
  "success": true,
  "filtered": [[1, 2, 4, 5, 6, 7], ...],
  "total": 8008
}
```

---

## 📝 Résumé

1. **Client** : Envoie les paramètres via API
2. **Serveur** : Calcule avec les formules cachées
3. **Client** : Affiche les résultats reçus

**Les formules ne sont JAMAIS envoyées au client.** 🔒

---

**Dernière mise à jour** : 31 Janvier 2026
**Projet** : Gosen TurfFilter - Port 8082 (DEV)
