from django.http import JsonResponse
from itertools import combinations


def calculate_alternances(combination, source_array):
    """Calcule le nombre d'alternances"""
    if not source_array:
        return 0
    
    combi_set = set(str(h) for h in combination)
    alternances = 0
    
    for i in range(len(source_array) - 1):
        current_in = source_array[i] in combi_set
        next_in = source_array[i + 1] in combi_set
        if current_in != next_in:
            alternances += 1
    
    return alternances


def apply_filter(request):
    """
    Filtre Alternance: Garder si le nombre d'alternances est entre min et max
    """
    import json
    
    data = json.loads(request.body)
    n = data.get('n', 16)
    k = data.get('k', 6)
    alternance_min = data.get('alternance_min', 0)
    alternance_max = data.get('alternance_max', 5)
    source = data.get('source', 'default')
    manual_source = data.get('manual_source', [])
    
    # Construire la source ordonnée
    if source == 'default':
        source_array = [str(i) for i in range(1, n + 1)]
    elif source == 'manual':
        source_array = [str(h) for h in manual_source]
    else:
        source_array = [str(i) for i in range(1, n + 1)]
    
    # Générer et filtrer
    partants = list(range(1, n + 1))
    all_combinations = list(combinations(partants, k))
    
    filtered = []
    for combi in all_combinations:
        alt_count = calculate_alternances(combi, source_array)
        if alternance_min <= alt_count <= alternance_max:
            filtered.append(list(combi))
    
    return JsonResponse({
        'filtered_count': len(filtered),
        'total_count': len(all_combinations),
        'combinations': filtered
    })
