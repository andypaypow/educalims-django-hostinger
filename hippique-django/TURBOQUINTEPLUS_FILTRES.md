# 🏇 TurboQuintePlus - Filtres pour Edge Functions Supabase

Ce document liste tous les filtres de l'application **Gosen TurfFilter** à implémenter dans des Edge Functions Supabase.

---

## 📋 Table des Matières

1. [Filtres de Base](#filtres-de-base)
2. [Filtres de Groupes](#filtres-de-groupes)
3. [Filtres Standard (Expert 1)](#filtres-standard-expert-1)
4. [Filtres Avancés (Expert 2)](#filtres-avancés-expert-2)
5. [Filtres de Poids](#filtres-de-poids)
6. [Filtres Statistiques](#filtres-statistiques)
7. [Filtres d'Alternance](#filtres-dalternance)
8. [Synthèses](#synthèses)
9. [Structure des Données](#structure-des-données)
10. [Edge Functions Templates](#edge-functions-templates)

---

## 1. FILTRES DE BASE

### 1.1 Configuration Initiale

```typescript
interface BaseConfig {
  numPartants: number;      // 8-16
  tailleCombinaison: number; // 2-7
}
```

### 1.2 Génération des Combinaisons

```typescript
function* combinationGenerator(arr: number[], k: number): Generator<number[]> {
    if (k === 0) { yield []; return; }
    for (let i = 0; i <= arr.length - k; i++) {
        for (const c of combinationGenerator(arr.slice(i + 1), k - 1)) {
            yield [arr[i], ...c];
        }
    }
}
```

### 1.3 Calcul du Nombre de Combinaisons

```typescript
function combinationsCount(n: number, k: number): number {
    if (k < 0 || k > n) return 0;
    if (k === 0 || k === n) return 1;
    if (k > n / 2) k = n - k;
    let res = 1;
    for (let i = 1; i <= k; i++) {
        res = res * (n - i + 1) / i;
    }
    return Math.round(res);
}
```

---

## 2. FILTRES DE GROUPES

### 2.1 Structure d'un Groupe

```typescript
interface Group {
    name: string;        // Nom du groupe (ex: "Favoris", "Outsiders")
    horses: number[];   // Liste des numéros de chevaux
    min: number;        // Minimum de chevaux à conserver (0 par défaut)
    max: number;        // Maximum de chevaux à conserver (taille du groupe par défaut)
}
```

### 2.2 Filtre Min/Max par Groupe

**Description :** Garde uniquement les combinaisons qui contiennent entre min et max chevaux de chaque groupe.

```typescript
function filterByGroupMinMax(
    combination: number[],
    groups: Group[]
): boolean {
    for (const group of groups) {
        const horsesInGroup = combination.filter(horse =>
            group.horses.includes(horse)
        ).length;

        if (horsesInGroup < group.min || horsesInGroup > group.max) {
            return false;
        }
    }
    return true;
}
```

**Exemple d'utilisation :**
```typescript
// Groupe "Favoris": [4, 7, 10], min: 1, max: 2
// Combinaison [4, 1, 2, 3, 5, 6] → 1 cheval du groupe → CONSERVÉE
// Combinaison [4, 7, 1, 2, 3, 5] → 2 chevaux du groupe → CONSERVÉE
// Combinaison [4, 7, 10, 1, 2, 3] → 3 chevaux du groupe → ÉLIMINÉE
```

---

## 3. FILTRES STANDARD (EXPERT 1)

### 3.1 Structure

```typescript
interface StandardFilter {
    chevauxMin: number;   // X: Nombre minimum de chevaux
    groupesMin: number;   // Y: Nombre minimum de groupes
}
```

### 3.2 Logique OR (Au moins X chevaux dans au moins Y groupes)

**Description :** "Garder si au moins X chevaux sont dans au moins Y groupes"

```typescript
function filterStandardOR(
    combination: number[],
    groups: Group[],
    filter: StandardFilter
): boolean {
    const matchingGroups = groups.filter(group => {
        const horsesInGroup = combination.filter(horse =>
            group.horses.includes(horse)
        ).length;
        return horsesInGroup >= filter.chevauxMin;
    });

    return matchingGroups.length >= filter.groupesMin;
}
```

**Exemple :**
```typescript
// chevauxMin: 2, groupesMin: 1
// Combinaison [4, 7, 1, 2, 3, 5]
// → Si "Favoris" = [4, 7, 10] → 2 chevaux dans le groupe → VALIDE
```

---

## 4. FILTRES AVANCÉS (EXPERT 2)

### 4.1 Structure

```typescript
interface AdvancedFilter {
    chevauxMin: number;   // X: Nombre minimum de chevaux communs
    groupesMin: number;   // Y: Nombre minimum de groupes
}
```

### 4.2 Logique AND (Chevaux communs dans plusieurs groupes)

**Description :** "Garder si au moins X chevaux communs existent dans au moins Y groupes"

```typescript
function filterAdvancedAND(
    combination: number[],
    groups: Group[],
    filter: AdvancedFilter
): boolean {
    // Compter combien de groupes contiennent chaque cheval
    const horseGroupCount: Record<number, number> = {};

    combination.forEach(horse => {
        horseGroupCount[horse] = 0;
        groups.forEach(group => {
            if (group.horses.includes(horse)) {
                horseGroupCount[horse]++;
            }
        });
    });

    // Compter les chevaux présents dans au moins 'groupesMin' groupes
    const commonHorses = Object.keys(horseGroupCount).filter(
        horse => horseGroupCount[parseInt(horse)] >= filter.groupesMin
    );

    return commonHorses.length >= filter.chevauxMin;
}
```

**Exemple :**
```typescript
// groupesMin: 2, chevauxMin: 1
// Si le cheval 4 est dans "Favoris" ET "Outsiders"
// → Il est compté comme cheval commun
```

---

## 5. FILTRES DE POIDS

### 5.1 Structure

```typescript
type WeightSource = 'default' | 'manual' | 'citation' | 'position' | 'results' | 'expert';

interface WeightFilter {
    source: WeightSource;    // Source des poids
    min: number;             // Poids total minimum
    max: number;             // Poids total maximum
    manualWeights?: number[]; // Liste manuelle (si source = 'manual')
}
```

### 5.2 Construction de la Map de Poids

```typescript
function buildWeightMap(
    filter: WeightFilter,
    numPartants: number,
    synthesisData: SynthesisData
): Map<string, number> {
    const weightMap = new Map<string, number>();

    // Initialiser tous les chevaux avec une pénalité
    for (let i = 1; i <= numPartants; i++) {
        weightMap.set(i.toString(), numPartants + 1);
    }

    switch (filter.source) {
        case 'default':
            // Poids = numéro du cheval
            for (let i = 1; i <= numPartants; i++) {
                weightMap.set(i.toString(), i);
            }
            break;

        case 'manual':
            // Poids selon l'ordre manuel
            filter.manualWeights?.forEach((horse, index) => {
                weightMap.set(horse.toString(), index + 1);
            });
            break;

        case 'citation':
            synthesisData.citation.forEach(([horse, _], index) => {
                weightMap.set(horse.toString(), index + 1);
            });
            break;

        case 'position':
            synthesisData.position.forEach(([horse, _], index) => {
                weightMap.set(horse.toString(), index + 1);
            });
            break;

        case 'results':
            synthesisData.results.forEach(([horse, _], index) => {
                weightMap.set(horse.toString(), index + 1);
            });
            break;

        case 'expert':
            synthesisData.expert.forEach(([horse, _], index) => {
                weightMap.set(horse.toString(), index + 1);
            });
            break;
    }

    return weightMap;
}
```

### 5.3 Application du Filtre de Poids

```typescript
function filterByWeight(
    combination: number[],
    weightMap: Map<string, number>,
    filter: WeightFilter
): boolean {
    const totalWeight = combination.reduce((sum, horse) => {
        return sum + (weightMap.get(horse.toString()) || 0);
    }, 0);

    return totalWeight >= filter.min && totalWeight <= filter.max;
}
```

---

## 6. FILTRES STATISTIQUES

### 6.1 Structure

```typescript
interface StatisticFilter {
    evenOdd: {
        enabled: boolean;
        min: number;    // Nombre minimum de pairs
        max: number;    // Nombre maximum de pairs
    };
    smallLarge: {
        enabled: boolean;
        limit: number;  // Limite pour "petit" (ex: 10)
        min: number;
        max: number;
    };
    consecutive: {
        enabled: boolean;
        min: number;
        max: number;
    };
}
```

### 6.2 Filtre Pairs/Impairs

```typescript
function filterByEvenOdd(
    combination: number[],
    filter: StatisticFilter
): boolean {
    if (!filter.evenOdd.enabled) return true;

    const evenCount = combination.filter(num => num % 2 === 0).length;
    return evenCount >= filter.evenOdd.min && evenCount <= filter.evenOdd.max;
}
```

### 6.3 Filtre Petits/Grands

```typescript
function filterBySmallLarge(
    combination: number[],
    filter: StatisticFilter
): boolean {
    if (!filter.smallLarge.enabled) return true;

    const smallCount = combination.filter(num =>
        num <= filter.smallLarge.limit
    ).length;

    return smallCount >= filter.smallLarge.min &&
           smallCount <= filter.smallLarge.max;
}
```

### 6.4 Filtre Suites Consécutives

```typescript
function getLongestConsecutive(arr: number[]): number {
    if (arr.length < 2) return arr.length;

    const sorted = [...arr].sort((a, b) => a - b);
    let maxLen = 1;
    let currentLen = 1;

    for (let i = 1; i < sorted.length; i++) {
        if (sorted[i] === sorted[i - 1] + 1) {
            currentLen++;
        } else {
            maxLen = Math.max(maxLen, currentLen);
            currentLen = 1;
        }
    }

    return Math.max(maxLen, currentLen);
}

function filterByConsecutive(
    combination: number[],
    filter: StatisticFilter
): boolean {
    if (!filter.consecutive.enabled) return true;

    const longest = getLongestConsecutive(combination);
    return longest >= filter.consecutive.min &&
           longest <= filter.consecutive.max;
}
```

---

## 7. FILTRES D'ALTERNANCE

### 7.1 Structure

```typescript
type AlternanceSource = 'default' | 'manual' | 'citation' | 'position' | 'results' | 'expert';

interface AlternanceFilter {
    source: AlternanceSource;
    sourceArray?: number[];  // Liste manuelle ordonnée
    min: number;
    max: number;
}
```

### 7.2 Calcul des Alternances

```typescript
function calculateAlternances(
    combination: number[],
    sourceArray: number[]
): number {
    if (sourceArray.length === 0) return 0;

    const combinationSet = new Set(combination.map(String));
    let alternances = 0;

    for (let i = 0; i < sourceArray.length - 1; i++) {
        const currentIn = combinationSet.has(sourceArray[i].toString());
        const nextIn = combinationSet.has(sourceArray[i + 1].toString());

        if (currentIn !== nextIn) {
            alternances++;
        }
    }

    return alternances;
}
```

### 7.3 Application du Filtre d'Alternance

```typescript
function filterByAlternance(
    combination: number[],
    filter: AlternanceFilter,
    synthesisData: SynthesisData
): boolean {
    let sourceArray: number[] = [];

    switch (filter.source) {
        case 'default':
            sourceArray = Array.from({ length: 16 }, (_, i) => i + 1);
            break;
        case 'manual':
            sourceArray = filter.sourceArray || [];
            break;
        case 'citation':
            sourceArray = synthesisData.citation.map(([h]) => h);
            break;
        case 'position':
            sourceArray = synthesisData.position.map(([h]) => h);
            break;
        case 'results':
            sourceArray = synthesisData.results.map(([h]) => h);
            break;
        case 'expert':
            sourceArray = synthesisData.expert.map(([h]) => h);
            break;
    }

    const alternanceCount = calculateAlternances(combination, sourceArray);
    return alternanceCount >= filter.min && alternanceCount <= filter.max;
}
```

**Exemple :**
```typescript
// Combinaison: [1, 3, 5]
// Liste ordonnée: [1, 2, 3, 4, 5, 6, ...]
// 1(S) → 2(N) → 3(S) → 4(N) → 5(S)
// Alternances: 4
```

---

## 8. SYNTHÈSES

### 8.1 Structure des Données de Synthèse

```typescript
interface SynthesisData {
    citation: [number, number][];   // [cheval, nombre de citations]
    position: [number, number][];   // [cheval, score de position]
    results: [number, number][];    // [cheval, fréquence dans résultats]
    expert: [number, number][];     // [cheval, score expert]
}
```

### 8.2 Synthèse par Citation

```typescript
function calculateCitationSynthesis(groups: Group[]): [number, number][] {
    const citationCounts: Record<number, number> = {};

    groups.forEach(group => {
        group.horses.forEach(horse => {
            citationCounts[horse] = (citationCounts[horse] || 0) + 1;
        });
    });

    return Object.entries(citationCounts)
        .sort((a, b) => b[1] - a[1])
        .map(([horse, count]) => [parseInt(horse), count]);
}
```

### 8.3 Synthèse par Position

```typescript
function calculatePositionSynthesis(groups: Group[]): [number, number][] {
    const positionScores: Record<number, number> = {};

    groups.forEach(group => {
        group.horses.forEach((horse, index) => {
            positionScores[horse] = (positionScores[horse] || 0) +
                (group.horses.length - index);
        });
    });

    return Object.entries(positionScores)
        .sort((a, b) => b[1] - a[1])
        .map(([horse, score]) => [parseInt(horse), score]);
}
```

### 8.4 Synthèse des Résultats

```typescript
function calculateResultsSynthesis(combinations: number[][]): [number, number][] {
    const horseCounts: Record<number, number> = {};

    combinations.flat().forEach(horse => {
        horseCounts[horse] = (horseCounts[horse] || 0) + 1;
    });

    return Object.entries(horseCounts)
        .sort((a, b) => b[1] - a[1])
        .map(([horse, count]) => [parseInt(horse), count]);
}
```

### 8.5 Synthèse Expert (Pondérée)

```typescript
function calculateExpertSynthesis(synthesisData: SynthesisData): [number, number][] {
    const weights = {
        citation: 1.0,
        position: 1.5,
        results: 2.0
    };

    const allHorses = new Set([
        ...synthesisData.citation.map(h => h[0]),
        ...synthesisData.position.map(h => h[0]),
        ...synthesisData.results.map(h => h[0])
    ]);

    const rankPoints = {
        citation: new Map(synthesisData.citation.map(([h, _], i) =>
            [h, synthesisData.citation.length - i])),
        position: new Map(synthesisData.position.map(([h, _], i) =>
            [h, synthesisData.position.length - i])),
        results: new Map(synthesisData.results.map(([h, _], i) =>
            [h, synthesisData.results.length - i]))
    };

    const finalScores: Record<number, number> = {};

    allHorses.forEach(horse => {
        const pCitation = rankPoints.citation.get(horse) || 0;
        const pPosition = rankPoints.position.get(horse) || 0;
        const pResults = rankPoints.results.get(horse) || 0;

        finalScores[horse] =
            (pCitation * weights.citation) +
            (pPosition * weights.position) +
            (pResults * weights.results);
    });

    return Object.entries(finalScores)
        .sort((a, b) => b[1] - a[1])
        .map(([horse, score]) => [parseInt(horse), score]);
}
```

---

## 9. STRUCTURE DES DONNÉES

### 9.1 Requête Complète

```typescript
interface FilterRequest {
    config: BaseConfig;
    groups: Group[];
    standardFilters: StandardFilter[];
    advancedFilters: AdvancedFilter[];
    weightFilters: WeightFilter[];
    statisticFilter: StatisticFilter;
    alternanceFilters: AlternanceFilter[];
}

interface FilterResponse {
    filteredCombinations: number[][];
    totalCount: number;
    filteredCount: number;
    reductionRate: number;
    synthesis: SynthesisData;
}
```

### 9.2 Pronostics (Input Format)

```typescript
// Format texte des pronostics:
// "Favoris: 4, 7, 10"
// "Outsiders: 1, 5, 12, 16"
// "Bases: 2, 8"

interface PronosticsInput {
    raw: string;  // Texte brut
    parsed?: Group[];
}
```

---

## 10. EDGE FUNCTIONS TEMPLATES

### 10.1 Edge Function Principale

```typescript
// functions/turboquinte-filter/index.ts
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

serve(async (req) => {
    try {
        const request: FilterRequest = await req.json();

        // Générer toutes les combinaisons
        const partants = Array.from(
            { length: request.config.numPartants },
            (_, i) => i + 1
        );

        const allCombinations: number[][] = [];
        for (const combo of combinationGenerator(partants, request.config.tailleCombinaison)) {
            allCombinations.push(combo);
        }

        // Appliquer tous les filtres
        let filtered = allCombinations;

        // Filtres de groupes
        filtered = filtered.filter(combo =>
            filterByGroupMinMax(combo, request.groups)
        );

        // Filtres standard (Expert 1)
        for (const filter of request.standardFilters) {
            filtered = filtered.filter(combo =>
                filterStandardOR(combo, request.groups, filter)
            );
        }

        // Filtres avancés (Expert 2)
        for (const filter of request.advancedFilters) {
            filtered = filtered.filter(combo =>
                filterAdvancedAND(combo, request.groups, filter)
            );
        }

        // Filtres de poids
        for (const filter of request.weightFilters) {
            const weightMap = buildWeightMap(filter, request.config.numPartants, synthesisData);
            filtered = filtered.filter(combo =>
                filterByWeight(combo, weightMap, filter)
            );
        }

        // Filtres statistiques
        filtered = filtered.filter(combo =>
            filterByEvenOdd(combo, request.statisticFilter) &&
            filterBySmallLarge(combo, request.statisticFilter) &&
            filterByConsecutive(combo, request.statisticFilter)
        );

        // Filtres d'alternance
        const synthesisData = calculateSynthesisData(filtered);
        for (const filter of request.alternanceFilters) {
            filtered = filtered.filter(combo =>
                filterByAlternance(combo, filter, synthesisData)
            );
        }

        // Calculer les synthèses finales
        const finalSynthesis = calculateSynthesisData(filtered);

        const response: FilterResponse = {
            filteredCombinations: filtered.slice(0, 1000), // Limiter à 1000
            totalCount: allCombinations.length,
            filteredCount: filtered.length,
            reductionRate: ((allCombinations.length - filtered.length) / allCombinations.length * 100),
            synthesis: finalSynthesis
        };

        return new Response(JSON.stringify(response), {
            headers: { 'Content-Type': 'application/json' },
            status: 200
        });

    } catch (error) {
        return new Response(JSON.stringify({ error: error.message }), {
            headers: { 'Content-Type': 'application/json' },
            status: 400
        });
    }
});
```

### 10.2 Edge Function de Backtest

```typescript
// functions/turboquinte-backtest/index.ts
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

serve(async (req) => {
    try {
        const { arrivee, filteredCombinations, groups, filters } = await req.json();

        const arriveeSet = new Set(arrivee);
        const matchingCombinations = filteredCombinations.filter(combo => {
            const comboSet = new Set(combo);
            return [...arriveeSet].every(num => comboSet.has(num));
        });

        // Générer le rapport
        const report = generateBacktestReport(
            arrivee,
            matchingCombinations,
            groups,
            filters
        );

        return new Response(JSON.stringify({ report, matchingCount: matchingCombinations.length }), {
            headers: { 'Content-Type': 'application/json' },
            status: 200
        });

    } catch (error) {
        return new Response(JSON.stringify({ error: error.message }), {
            headers: { 'Content-Type': 'application/json' },
            status: 400
        });
    }
});
```

---

## 11. EXEMPLES D'UTILISATION

### 11.1 Appel depuis le Frontend

```typescript
const response = await fetch(
    'https://qfkyzljqykymahlpmdnu.supabase.co/functions/v1/turboquinte-filter',
    {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${SUPABASE_ANON_KEY}`
        },
        body: JSON.stringify({
            config: {
                numPartants: 16,
                tailleCombinaison: 6
            },
            groups: [
                { name: 'Favoris', horses: [4, 7, 10], min: 1, max: 2 },
                { name: 'Outsiders', horses: [1, 5, 12, 16], min: 0, max: 3 }
            ],
            standardFilters: [
                { chevauxMin: 2, groupesMin: 1 }
            ],
            advancedFilters: [],
            weightFilters: [],
            statisticFilter: {
                evenOdd: { enabled: true, min: 2, max: 4 },
                smallLarge: { enabled: true, limit: 10, min: 3, max: 6 },
                consecutive: { enabled: false, min: 0, max: 7 }
            },
            alternanceFilters: []
        })
    }
);

const result = await response.json();
console.log(`${result.filteredCount} combinaisons conservées`);
```

---

## 12. TABLES SUPABASE SUGGÉRÉES

### 12.1 Table des Configurations

```sql
CREATE TABLE turbo_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id),
    name VARCHAR(255),
    config JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 12.2 Table des Backtests

```sql
CREATE TABLE turbo_backtests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id),
    arrivee INT[] NOT NULL,
    matching_count INT,
    report TEXT,
    filters JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

**Dernière mise à jour** : 28 Janvier 2026
**Projet** : TurboQuintePlus - Filtres pour Edge Functions Supabase
**Repository** : https://github.com/andypaypow/turboquinteplus
