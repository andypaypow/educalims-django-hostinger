from django.http import JsonResponse
from itertools import combinations


def apply_filter(request):
    """
    Filtre Poids: Garder si le poids total est entre min et max
    """
    import json
    
    data = json.loads(request.body)
    n = data.get('n', 16)
    k = data.get('k', 6)
    weight_min = data.get('weight_min', 21)
    weight_max = data.get('weight_max', 81)
    source = data.get('source', 'default')
    manual_weights = data.get('manual_weights', {})
    
    # Construire la map des poids
    weight_map = {}
    
    if source == 'default':
        for i in range(1, n + 1):
            weight_map[i] = i
    elif source == 'manual':
        weight_map = manual_weights
    
    # Générer et filtrer les combinaisons
    partants = list(range(1, n + 1))
    all_combinations = list(combinations(partants, k))
    
    filtered = []
    for combi in all_combinations:
        total_weight = sum(weight_map.get(h, n + 1) for h in combi)
        if weight_min <= total_weight <= weight_max:
            filtered.append(list(combi))
    
    return JsonResponse({
        'filtered_count': len(filtered),
        'total_count': len(all_combinations),
        'combinations': filtered
    })
