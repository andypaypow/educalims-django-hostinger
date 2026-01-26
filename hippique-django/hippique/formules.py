"""
Filtres pour TurboQuinte+ - Gosen TurfFilter
Logique de filtrage des combinaisons hippiques
"""


def filtre_ou(combination, groupes):
    """
    Filtre OU: au moins un cheval d'un des groupes doit être présent

    Args:
        combination: Liste de 6 numéros [1, 2, 3, 4, 5, 6]
        groupes: Dictionnaire {"groupe1": [1,2,3], "groupe2": [4,5], ...}

    Returns:
        True si la combinaison passe le filtre, False sinon
    """
    if not groupes:
        return True  # Pas de filtre OU = toutes les combinaisons passent

    # Si au moins un groupe a un cheval dans la combinaison, on conserve
    for groupe in groupes.values():
        if isinstance(groupe, list) and any(num in groupe for num in combination):
            return True

    return False


def filtre_et(combination, groupes):
    """
    Filtre ET: tous les chevaux de chaque groupe doivent être présents

    Args:
        combination: Liste de 6 numéros [1, 2, 3, 4, 5, 6]
        groupes: Dictionnaire {"groupe1": [1,2], "groupe2": [3,4], ...}

    Returns:
        True si la combinaison passe le filtre, False sinon
    """
    if not groupes:
        return True  # Pas de filtre ET = toutes les combinaisons passent

    # Tous les groupes doivent avoir tous leurs chevaux dans la combinaison
    for groupe in groupes.values():
        if isinstance(groupe, list) and not all(num in combination for num in groupe):
            return False

    return True


def filtre_pairs_impairs(combination, params):
    """
    Filtre Pairs/Impairs: contrôle la répartition des numéros pairs et impairs

    Args:
        combination: Liste de 6 numéros [1, 2, 3, 4, 5, 6]
        params: Dictionnaire {"pairs_min": 2, "pairs_max": 4,
                              "impairs_min": 2, "impairs_max": 4}

    Returns:
        True si la combinaison passe le filtre, False sinon
    """
    if not params:
        return True

    pairs = sum(1 for num in combination if num % 2 == 0)
    impairs = len(combination) - pairs

    pairs_min = params.get('pairs_min', 0)
    pairs_max = params.get('pairs_max', 6)
    impairs_min = params.get('impairs_min', 0)
    impairs_max = params.get('impairs_max', 6)

    return (pairs_min <= pairs <= pairs_max) and (impairs_min <= impairs <= impairs_max)


def filtre_petits_suites(combination, params):
    """
    Filtre Petits/Suites: filtre sur les petits numéros et suites consécutives

    Args:
        combination: Liste de 6 numéros [1, 2, 3, 4, 5, 6]
        params: Dictionnaire {"petits_min": 2, "petits_max": 4,
                              "suites_min": 1, "suite_length": 2}

    Returns:
        True si la combinaison passe le filtre, False sinon
    """
    if not params:
        return True

    # Petits numéros (≤ 8)
    petits = sum(1 for num in combination if num <= 8)
    petits_min = params.get('petits_min', 0)
    petits_max = params.get('petits_max', 6)

    petits_ok = (petits_min <= petits <= petits_max)

    # Suites consécutives
    sorted_nums = sorted(combination)
    suites = 0
    i = 0
    suite_length_min = params.get('suite_length', 2)

    while i < len(sorted_nums) - 1:
        current_suite_length = 1
        while (i + current_suite_length < len(sorted_nums) and
               sorted_nums[i + current_suite_length] == sorted_nums[i] + current_suite_length):
            current_suite_length += 1

        if current_suite_length >= suite_length_min:
            suites += 1

        i += current_suite_length

    suites_min = params.get('suites_min', 0)
    suites_ok = (suites >= suites_min)

    return petits_ok and suites_ok


def filtre_limitation(combination, params):
    """
    Filtre Limitation: limite le nombre de chevaux par groupe

    Args:
        combination: Liste de 6 numéros [1, 2, 3, 4, 5, 6]
        params: Dictionnaire {"limit_per_group": 2,
                              "groupes": {"groupe1": [1,2,3,4], "groupe2": [5,6,7,8]}}

    Returns:
        True si la combinaison passe le filtre, False sinon
    """
    if not params:
        return True

    limit = params.get('limit_per_group', 6)
    groupes = params.get('groupes', {})

    if not groupes:
        return True

    # Vérifier que chaque groupe n'a pas plus de X chevaux dans la combinaison
    for groupe in groupes.values():
        if isinstance(groupe, list):
            count = sum(1 for num in combination if num in groupe)
            if count > limit:
                return False

    return True


def filtre_poids(combination, params):
    """
    Filtre Poids: filtrage basé sur le poids des chevaux

    Args:
        combination: Liste de 6 numéros [1, 2, 3, 4, 5, 6]
        params: Dictionnaire {"seuil": 15, "poids": {"1": 5, "2": 4, ...}}

    Returns:
        True si la combinaison passe le filtre, False sinon
    """
    if not params:
        return True

    seuil = params.get('seuil', 0)
    poids = params.get('poids', {})

    if seuil == 0:
        return True

    # Calculer le poids total de la combinaison
    poids_total = sum(poids.get(str(num), 0) for num in combination)

    return poids_total >= seuil


def filtre_alternance(combination, params):
    """
    Filtre Alternance: gestion des alternances successifs/non-successifs

    Args:
        combination: Liste de 6 numéros [1, 2, 3, 4, 5, 6]
        params: Dictionnaire {"alternance_succ_min": 1, "alternance_succ_max": 3,
                              "alternance_nonsucc_min": 1, "alternance_nonsucc_max": 4}

    Returns:
        True si la combinaison passe le filtre, False sinon
    """
    if not params:
        return True

    sorted_nums = sorted(combination)
    successifs = 0
    nonsuccessifs = 0

    for i in range(len(sorted_nums) - 1):
        if sorted_nums[i + 1] == sorted_nums[i] + 1:
            successifs += 1
        else:
            nonsuccessifs += 1

    succ_min = params.get('alternance_succ_min', 0)
    succ_max = params.get('alternance_succ_max', 6)
    nonsucc_min = params.get('alternance_nonsucc_min', 0)
    nonsucc_max = params.get('alternance_nonsucc_max', 6)

    return (succ_min <= successifs <= succ_max) and \
           (nonsucc_min <= nonsuccessifs <= nonsucc_max)


def filtrer_combinaisons(combinaisons, filtres):
    """
    Applique tous les filtres aux combinaisons

    Args:
        combinaisons: Liste de combinaisons [[1,2,3,4,5,6], [1,2,3,4,5,7], ...]
        filtres: Dictionnaire avec tous les paramètres de filtres

    Returns:
        Liste des combinaisons qui passent tous les filtres
    """
    resultats = []

    for comb in combinaisons:
        # Appliquer chaque filtre
        if not filtre_ou(comb, filtres.get('ou', {})):
            continue
        if not filtre_et(comb, filtres.get('et', {})):
            continue
        if not filtre_pairs_impairs(comb, filtres.get('pairs_impairs', {})):
            continue
        if not filtre_petits_suites(comb, filtres.get('petits_suites', {})):
            continue
        if not filtre_limitation(comb, filtres.get('limitation', {})):
            continue
        if not filtre_poids(comb, filtres.get('poids', {})):
            continue
        if not filtre_alternance(comb, filtres.get('alternance', {})):
            continue

        resultats.append(comb)

    return resultats


def generer_toutes_combinaisons(n=16, k=6):
    """
    Génère toutes les combinaisons possibles de k parmi n

    Args:
        n: Nombre total de chevaux (défaut: 16)
        k: Taille de la combinaison (défaut: 6)

    Returns:
        Liste de toutes les combinaisons possibles
    """
    combinaisons = []

    def generate(startIndex, current, depth):
        if depth == k:
            combinaisons.append(current[:])
            return

        for i in range(startIndex, n - (k - depth) + 1):
            current.append(i + 1)
            generate(i + 1, current, depth + 1)
            current.pop()

    generate(0, [], 0)
    return combinaisons


def formater_combinaison(combinaison):
    """
    Formate une combinaison pour l'affichage

    Args:
        combinaison: Liste de numéros [1, 2, 3, 4, 5, 6]

    Returns:
        Chaîne formatée "1 - 2 - 3 - 4 - 5 - 6"
    """
    return ' - '.join(str(num) for num in combinaison)


def calculer_frequence_chevaux(combinaisons):
    """
    Calcule la fréquence d'apparition de chaque cheval dans les combinaisons

    Args:
        combinaisons: Liste de combinaisons

    Returns:
        Dictionnaire {cheval: frequence}
    """
    frequence = {}

    for comb in combinaisons:
        for num in comb:
            frequence[num] = frequence.get(num, 0) + 1

    return dict(sorted(frequence.items()))


def calculer_taux_filtrage(total, conservees):
    """
    Calcule le taux de filtrage en pourcentage

    Args:
        total: Nombre total de combinaisons
        conservees: Nombre de combinaisons conservées

    Returns:
        Taux de filtrage en pourcentage
    """
    if total == 0:
        return 0.0

    return round(((total - conservees) / total) * 100, 2)
