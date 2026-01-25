"""
🧮 FORMULES MATHÉMATIQUES - TURBOQUINTEPLUS
===========================================

Toutes les fonctions de calcul pour le filtrage de combinaisons hippiques.

Prêt à être copié dans Django : hippique/calculs.py
"""

from typing import List, Tuple, Dict, Set, Generator, Optional
import itertools


# =============================================================================
# 1. COMBINAISONS (Coefficient Binomial)
# =============================================================================

def combinations_count(n: int, k: int) -> int:
    """
    C(n, k) = n! / (k! * (n-k)!)

    Calcule le nombre de combinaisons de k éléments parmi n.

    Args:
        n: Nombre total d'éléments
        k: Taille des combinaisons

    Returns:
        Nombre de combinaisons possibles

    Examples:
        >>> combinations_count(16, 6)
        8008
        >>> combinations_count(15, 4)
        1365
        >>> combinations_count(14, 8)
        3003
    """
    if k < 0 or k > n:
        return 0
    if k == 0 or k == n:
        return 1
    if k > n / 2:
        k = n - k

    result = 1
    for i in range(1, k + 1):
        result = result * (n - i + 1) // i

    return result


def combination_generator(arr: List[int], k: int) -> Generator[List[int], None, None]:
    """
    Génère toutes les combinaisons de taille k depuis arr.

    Args:
        arr: Liste d'éléments [1, 2, 3, ..., n]
        k: Taille des combinaisons

    Yields:
        Combinaison [élément1, élément2, ...]

    Examples:
        >>> list(combination_generator([1, 2, 3], 2))
        [[1, 2], [1, 3], [2, 3]]
    """
    if k == 0:
        yield []
        return

    for i in range(len(arr) - k + 1):
        first = arr[i]
        rest = arr[i + 1:]

        for c in combination_generator(rest, k - 1):
            yield [first] + c


# =============================================================================
# 2. SYNTHÈSE PAR CITATION
# =============================================================================

def citation_synthesis(groups: List[Dict]) -> List[Tuple[int, int]]:
    """
    Compte le nombre d'apparitions de chaque cheval dans tous les groupes.

    Args:
        groups: List de dict {name: str, horses: List[int]}

    Returns:
        List triée [(cheval, count), ...] par ordre décroissant

    Examples:
        >>> groups = [
        ...     {'name': 'G1', 'horses': [1, 2, 3]},
        ...     {'name': 'G2', 'horses': [2, 4, 6]},
        ...     {'name': 'G3', 'horses': [1, 4, 8]}
        ... ]
        >>> citation_synthesis(groups)
        [(1, 2), (2, 2), (4, 2), (3, 1), (6, 1), (8, 1)]
    """
    citation_counts = {}

    for group in groups:
        for horse in group['horses']:
            citation_counts[horse] = citation_counts.get(horse, 0) + 1

    return sorted(citation_counts.items(), key=lambda x: x[1], reverse=True)


# =============================================================================
# 3. SYNTHÈSE PAR POSITION (Pondérée)
# =============================================================================

def position_synthesis(groups: List[Dict]) -> List[Tuple[int, int]]:
    """
    Attribue des points selon la position dans chaque groupe.

    Poids = (taille_groupe - position)

    Args:
        groups: List de dict {name: str, horses: List[int]}

    Returns:
        List triée [(cheval, score), ...] par ordre décroissant

    Examples:
        >>> groups = [
        ...     {'name': 'G1', 'horses': [1, 2, 3, 4]}
        ... ]
        >>> position_synthesis(groups)
        [(1, 4), (2, 3), (3, 2), (4, 1)]
    """
    position_scores = {}

    for group in groups:
        group_size = len(group['horses'])
        for index, horse in enumerate(group['horses']):
            score = group_size - index
            position_scores[horse] = position_scores.get(horse, 0) + score

    return sorted(position_scores.items(), key=lambda x: x[1], reverse=True)


# =============================================================================
# 4. SYNTHÈSE DE L'EXPERT (Classement Global)
# =============================================================================

def expert_synthesis(
    citation_data: List[Tuple[int, int]],
    position_data: List[Tuple[int, int]],
    results_data: List[Tuple[int, int]]
) -> List[Tuple[int, float]]:
    """
    Combine les 3 synthèses avec des pondérations.

    Score_Final = (P_Citation × 1.0) + (P_Position × 1.5) + (P_Results × 2.0)

    Args:
        citation_data: [(cheval, count), ...]
        position_data: [(cheval, score), ...]
        results_data: [(cheval, frequency), ...]

    Returns:
        List triée [(cheval, score_final), ...] par ordre décroissant
    """
    weights = {
        'citation': 1.0,
        'position': 1.5,
        'results': 2.0
    }

    # Points de rang pour chaque catégorie
    rank_points = {
        'citation': {horse: len(citation_data) - i for i, (horse, _) in enumerate(citation_data)},
        'position': {horse: len(position_data) - i for i, (horse, _) in enumerate(position_data)},
        'results': {horse: len(results_data) - i for i, (horse, _) in enumerate(results_data)}
    }

    # Tous les chevaux uniques
    all_horses = set()
    for data in [citation_data, position_data, results_data]:
        all_horses.update([h for h, _ in data])

    # Score final
    final_scores = {}
    for horse in all_horses:
        p_citation = rank_points['citation'].get(horse, 0)
        p_position = rank_points['position'].get(horse, 0)
        p_results = rank_points['results'].get(horse, 0)

        final_scores[horse] = (
            p_citation * weights['citation'] +
            p_position * weights['position'] +
            p_results * weights['results']
        )

    return sorted(final_scores.items(), key=lambda x: x[1], reverse=True)


# =============================================================================
# 5. FILTRAGE PAR GROUPE (Min/Max)
# =============================================================================

def filter_by_group_min_max(combination: List[int], groups: List[Dict]) -> bool:
    """
    Vérifie que chaque groupe respecte ses bornes min/max.

    Args:
        combination: [cheval1, cheval2, ...]
        groups: List de dict {horses: List[int], min: int, max: int}

    Returns:
        True si tous les groupes respectent leurs bornes

    Examples:
        >>> groups = [
        ...     {'horses': [1, 2, 3], 'min': 1, 'max': 2}
        ... ]
        >>> filter_by_group_min_max([1, 4, 6], groups)
        True  # 1 cheval du groupe, dans [1, 2]
        >>> filter_by_group_min_max([1, 2, 4, 6], groups)
        True  # 2 chevaux du groupe, dans [1, 2]
        >>> filter_by_group_min_max([1, 2, 3, 4], groups)
        False  # 3 chevaux du groupe, > max
    """
    for group in groups:
        horses_in_group = sum(1 for h in combination if h in group['horses'])

        if horses_in_group < group['min'] or horses_in_group > group['max']:
            return False

    return True


# =============================================================================
# 6. FILTRE EXPERT 1 (Standard) - OU Logique
# =============================================================================

def expert1_filter(
    combination: List[int],
    groups: List[Dict],
    chevaux_min: int,
    groupes_min: int
) -> bool:
    """
    "Garder si au moins X chevaux sont dans au moins Y groupes"

    Logique OU:
    Pour chaque groupe, compter les chevaux communs avec la combinaison.
    Si nombre de groupes avec ≥ chevaux_min communs ≥ groupes_min → Garder.

    Args:
        combination: [cheval1, cheval2, ...]
        groups: List de dict {horses: List[int]}
        chevaux_min: X (minimum de chevaux communs)
        groupes_min: Y (minimum de groupes satisfaisants)

    Returns:
        True si la combinaison satisfait le critère

    Examples:
        >>> groups = [
        ...     {'horses': [1, 2, 3]},
        ...     {'horses': [2, 4, 6]}
        ... ]
        >>> expert1_filter([1, 4, 6], groups, 1, 2)
        True  # G1: 1 cheval commun, G2: 2 chevaux communs → 2 groupes satisfaits
    """
    satisfying_groups = 0

    for group in groups:
        common_horses = sum(1 for h in combination if h in group['horses'])

        if common_horses >= chevaux_min:
            satisfying_groups += 1

    return satisfying_groups >= groupes_min


# =============================================================================
# 7. FILTRE EXPERT 2 (Avancé) - ET Logique
# =============================================================================

def expert2_filter(
    combination: List[int],
    groups: List[Dict],
    chevaux_min: int,
    groupes_min: int
) -> bool:
    """
    "Garder si au moins X chevaux COMMUNS existent dans au moins Y groupes"

    Logique ET:
    Pour chaque cheval de la combinaison, compter dans combien de groupes
    il apparaît. Compter les chevaux qui apparaissent dans ≥ groupes_min groupes.
    Si ce compte ≥ chevaux_min → Garder.

    Args:
        combination: [cheval1, cheval2, ...]
        groups: List de dict {horses: List[int]}
        chevaux_min: X (minimum de chevaux satisfaisants)
        groupes_min: Y (minimum d'apparitions dans les groupes)

    Returns:
        True si la combinaison satisfait le critère

    Examples:
        >>> groups = [
        ...     {'horses': [1, 2, 3]},
        ...     {'horses': [2, 4, 6]},
        ...     {'horses': [1, 4, 8]}
        ... ]
        >>> expert2_filter([1, 2, 4], groups, 2, 2)
        True  # 1 et 2 et 4 apparaissent dans ≥ 2 groupes
    """
    horse_group_counts = {horse: 0 for horse in combination}

    for horse in combination:
        for group in groups:
            if horse in group['horses']:
                horse_group_counts[horse] += 1

    satisfying_horses = sum(
        1 for count in horse_group_counts.values()
        if count >= groupes_min
    )

    return satisfying_horses >= chevaux_min


# =============================================================================
# 8. FILTRAGE PAIRS/IMPAIRS
# =============================================================================

def count_even_odd(combination: List[int]) -> Tuple[int, int]:
    """
    Compte les nombres pairs et impairs.

    Args:
        combination: [cheval1, cheval2, ...]

    Returns:
        (even_count, odd_count)

    Examples:
        >>> count_even_odd([1, 2, 3, 4, 5, 6])
        (3, 3)
    """
    even_count = sum(1 for num in combination if num % 2 == 0)
    odd_count = len(combination) - even_count

    return even_count, odd_count


# =============================================================================
# 9. FILTRAGE PETITS/GRANDS NUMÉROS
# =============================================================================

def count_small_large(combination: List[int], limit: int) -> Tuple[int, int]:
    """
    Compte les petits (≤ limit) et grands (> limit) numéros.

    Args:
        combination: [cheval1, cheval2, ...]
        limit: Seuil de séparation

    Returns:
        (small_count, large_count)

    Examples:
        >>> count_small_large([1, 5, 10, 15], 10)
        (3, 1)
    """
    small_count = sum(1 for num in combination if num <= limit)
    large_count = len(combination) - small_count

    return small_count, large_count


# =============================================================================
# 10. FILTRAGE SUITES CONSÉCUTIVES
# =============================================================================

def get_longest_consecutive(combination: List[int]) -> int:
    """
    Trouve la plus longue suite de nombres consécutifs.

    Args:
        combination: [cheval1, cheval2, ...]

    Returns:
        Longueur de la plus longue suite

    Examples:
        >>> get_longest_consecutive([1, 2, 3, 5, 7, 8, 9])
        3
        >>> get_longest_consecutive([1, 3, 5, 7])
        1
    """
    if len(combination) < 2:
        return len(combination)

    sorted_combination = sorted(combination)

    max_len = 1
    current_len = 1

    for i in range(1, len(sorted_combination)):
        if sorted_combination[i] == sorted_combination[i - 1] + 1:
            current_len += 1
        else:
            max_len = max(max_len, current_len)
            current_len = 1

    return max(max_len, current_len)


# =============================================================================
# 11. FILTRE POIDS
# =============================================================================

def calculate_combination_weight(combination: List[int], weight_map: Dict[int, int]) -> int:
    """
    Poids_Total = Σ(poids_cheval_i)

    Args:
        combination: [cheval1, cheval2, ...]
        weight_map: {cheval: poids}

    Returns:
        Poids total de la combinaison

    Examples:
        >>> weight_map = {1: 10, 2: 20, 3: 30}
        >>> calculate_combination_weight([1, 2], weight_map)
        30
    """
    total_weight = sum(weight_map.get(horse, 0) for horse in combination)

    return total_weight


def build_weight_map(
    source: str,
    n: int,
    synthesis_data: Optional[Dict] = None,
    manual_list: Optional[List[int]] = None
) -> Tuple[Dict[int, int], List[int]]:
    """
    Construit une map de poids selon la source.

    Args:
        source: 'default', 'manual', 'citation', 'position', 'results', 'expert'
        n: Nombre de partants
        synthesis_data: Dict avec les synthèses {'citation': [], 'position': ...}
        manual_list: Liste manuelle [cheval1, cheval2, ...]

    Returns:
        (weight_map, sorted_weights)

    Examples:
        >>> weight_map, sorted_weights = build_weight_map('default', 16, None, None)
        >>> weight_map[1]
        1
        >>> weight_map[16]
        16
    """
    weight_map = {}

    # Initialiser avec pénalité
    for i in range(1, n + 1):
        weight_map[i] = n + 1

    if source == 'default':
        for i in range(1, n + 1):
            weight_map[i] = i
        sorted_weights = list(range(1, n + 1))

    elif source == 'manual' and manual_list:
        for index, horse in enumerate(manual_list):
            weight_map[horse] = index + 1
        sorted_weights = list(range(1, len(manual_list) + 1))

    elif source in ['citation', 'position', 'results', 'expert'] and synthesis_data:
        synthesis_list = synthesis_data.get(source, [])
        if synthesis_list:
            for index, (horse, _) in enumerate(synthesis_list):
                weight_map[horse] = index + 1
            sorted_weights = list(range(1, len(synthesis_list) + 1))
        else:
            sorted_weights = []

    else:
        sorted_weights = []

    return weight_map, sorted_weights


def calculate_weight_bounds(sorted_weights: List[int], k: int) -> Tuple[int, int]:
    """
    Poids_Min_Théorique = somme des k plus petits poids
    Poids_Max_Théorique = somme des k plus grands poids

    Args:
        sorted_weights: [poids1, poids2, ...] triés
        k: Taille de la combinaison

    Returns:
        (min_weight, max_weight)
    """
    if len(sorted_weights) < k:
        return 0, 0

    min_weight = sum(sorted_weights[:k])
    max_weight = sum(sorted_weights[-k:])

    return min_weight, max_weight


# =============================================================================
# 12. FILTRE ALTERNANCE
# =============================================================================

def calculate_alternances(combination: List[int], source_array: List[str]) -> int:
    """
    Compte le nombre de changements S→N ou N→S en parcourant source_array.

    S = cheval sélectionné (dans la combinaison)
    N = cheval non sélectionné

    Args:
        combination: [cheval1, cheval2, ...]
        source_array: [chevalA, chevalB, ...] (ordonné, en string)

    Returns:
        Nombre d'alternances

    Examples:
        >>> calculate_alternances([1, 3, 5], ['1', '2', '3', '4', '5', '6'])
        5
    """
    if not source_array:
        return 0

    combination_set = set(str(h) for h in combination)

    alternances = 0
    for i in range(len(source_array) - 1):
        current_in = source_array[i] in combination_set
        next_in = source_array[i + 1] in combination_set

        if current_in != next_in:
            alternances += 1

    return alternances


def max_alternances(k: int) -> int:
    """
    Maximum théorique d'alternances pour une combinaison de taille k.
    Max = 2 × k

    Args:
        k: Taille de la combinaison

    Returns:
        Maximum théorique
    """
    return 2 * k


# =============================================================================
# 13. SYNTHÈSE DES RÉSULTATS
# =============================================================================

def results_synthesis(combinaisons: List[List[int]]) -> List[Tuple[int, int]]:
    """
    Compte la fréquence d'apparition de chaque cheval dans les combinaisons filtrées.

    Args:
        combinaisons: [[1,2,3], [1,2,4], ...]

    Returns:
        List triée [(cheval, frequency), ...] par ordre décroissant

    Examples:
        >>> results_synthesis([[1, 2, 3], [1, 2, 4], [1, 5, 6]])
        [(1, 3), (2, 2), (3, 1), (4, 1), (5, 1), (6, 1)]
    """
    horse_counts = {}

    for combi in combinaisons:
        for horse in combi:
            horse_counts[horse] = horse_counts.get(horse, 0) + 1

    return sorted(horse_counts.items(), key=lambda x: x[1], reverse=True)


# =============================================================================
# 14. TAUX DE FILTRAGE
# =============================================================================

def calculate_filtration_rate(total_combinations: int, filtered_combinations: int) -> float:
    """
    Taux = ((total - filtered) / total) × 100

    Args:
        total_combinations: Nombre initial
        filtered_combinations: Nombre après filtrage

    Returns:
        Pourcentage de réduction

    Examples:
        >>> calculate_filtration_rate(8008, 25)
        99.69
    """
    if total_combinations == 0:
        return 0.0

    return ((total_combinations - filtered_combinations) / total_combinations) * 100


# =============================================================================
# 15. BACKTEST - Trouver les Combinaisons
# =============================================================================

def find_matching_combinations(
    arrivee: List[int],
    combinaisons: List[List[int]]
) -> List[List[int]]:
    """
    Trouve les combinaisons qui contiennent tous les numéros de l'arrivée.

    Args:
        arrivee: [1, 2, 3, 4, 5]
        combinaisons: [[1,2,3], [1,2,6], ...]

    Returns:
        List des combinaisons qui contiennent l'arrivée

    Examples:
        >>> find_matching_combinations([1, 2], [[1, 2, 3], [1, 4, 5]])
        [[1, 2, 3]]
    """
    arrivee_set = set(arrivee)
    matching = []

    for combi in combinaisons:
        combi_set = set(combi)

        # Vérifier que tous les numéros de l'arrivée sont dans la combinaison
        if arrivee_set.issubset(combi_set):
            matching.append(combi)

    return matching


# =============================================================================
# 16. FONCTION PRINCIPALE DE FILTRAGE
# =============================================================================

def apply_all_filters(
    n: int,
    k: int,
    groups: List[Dict],
    or_filters: List[Dict],
    and_filters: List[Dict],
    even_odd_filters: List[Dict],
    small_large_filters: List[Dict],
    consecutive_filters: List[Dict],
    weight_filters: List[Dict],
    alternance_filters: List[Dict]
) -> List[List[int]]:
    """
    Applique tous les filtres pour générer les combinaisons filtrées.

    Args:
        n: Nombre de partants
        k: Taille des combinaisons
        groups: Groupes avec min/max
        or_filters: Filtres Expert 1
        and_filters: Filtres Expert 2
        even_odd_filters: Filtres pairs/impairs
        small_large_filters: Filtres petits/grands
        consecutive_filters: Filtres suites
        weight_filters: Filtres poids
        alternance_filters: Filtres alternance

    Returns:
        List des combinaisons filtrées
    """
    partants = list(range(1, n + 1))
    filtered_combinations = []

    for combi in combination_generator(partants, k):
        is_kept = True

        # 1. Filtre Groupe Min/Max
        if is_kept and groups:
            if not filter_by_group_min_max(combi, groups):
                is_kept = False

        # 2. Filtre Expert 1 (OU)
        if is_kept and or_filters:
            for f in or_filters:
                if not expert1_filter(combi, groups, f['chevaux_min'], f['groupes_min']):
                    is_kept = False
                    break

        # 3. Filtre Expert 2 (ET)
        if is_kept and and_filters:
            for f in and_filters:
                if not expert2_filter(combi, groups, f['chevaux_min'], f['groupes_min']):
                    is_kept = False
                    break

        # 4. Filtre Pairs/Impairs
        if is_kept and even_odd_filters:
            even_count, _ = count_even_odd(combi)
            for f in even_odd_filters:
                if not (f['min'] <= even_count <= f['max']):
                    is_kept = False
                    break

        # 5. Filtre Petits/Grands
        if is_kept and small_large_filters:
            for f in small_large_filters:
                small_count, _ = count_small_large(combi, f['limit'])
                if not (f['min'] <= small_count <= f['max']):
                    is_kept = False
                    break

        # 6. Filtre Suites Consécutives
        if is_kept and consecutive_filters:
            longest = get_longest_consecutive(combi)
            for f in consecutive_filters:
                if not (f['min'] <= longest <= f['max']):
                    is_kept = False
                    break

        # 7. Filtre Poids
        if is_kept and weight_filters:
            for f in weight_filters:
                total_weight = calculate_combination_weight(combi, f['map'])
                if not (f['min'] <= total_weight <= f['max']):
                    is_kept = False
                    break

        # 8. Filtre Alternance
        if is_kept and alternance_filters:
            for f in alternance_filters:
                if f['source']:
                    alt_count = calculate_alternances(combi, f['source'])
                    if not (f['min'] <= alt_count <= f['max']):
                        is_kept = False
                        break

        if is_kept:
            filtered_combinations.append(sorted(combi))

    return filtered_combinations


# =============================================================================
# TESTS
# =============================================================================

if __name__ == '__main__':
    print("=== TEST DES FORMULES ===\n")

    # Test 1: Combinaisons
    print("1. C(16, 6) =", combinations_count(16, 6))
    print("   Attendu: 8008\n")

    # Test 2: Citation
    groups = [
        {'name': 'G1', 'horses': [1, 2, 3]},
        {'name': 'G2', 'horses': [2, 4, 6]},
        {'name': 'G3', 'horses': [1, 4, 8]}
    ]
    print("2. Citation synthesis:", citation_synthesis(groups))
    print("   Attendu: [(1,2), (2,2), (4,2), (3,1), (6,1), (8,1)]\n")

    # Test 3: Position
    print("3. Position synthesis:", position_synthesis(groups))
    print()

    # Test 4: Pairs/Impairs
    combi = [1, 2, 3, 4, 5, 6]
    print(f"4. Pairs/Impairs {combi}:", count_even_odd(combi))
    print("   Attendu: (3, 3)\n")

    # Test 5: Suites
    combi = [1, 2, 3, 5, 7, 8, 9]
    print(f"5. Plus longue suite {combi}:", get_longest_consecutive(combi))
    print("   Attendu: 3\n")

    # Test 6: Alternance
    combi = [1, 3, 5]
    source = ['1', '2', '3', '4', '5', '6']
    print(f"6. Alternances {combi} with source {source}:")
    print("   ", calculate_alternances(combi, source))
    print("   Attendu: 5\n")

    print("=== Tous les tests sont terminés ===")
