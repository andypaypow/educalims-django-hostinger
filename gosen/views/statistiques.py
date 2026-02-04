from django.http import JsonResponse
from itertools import combinations


def apply_filter(request):
    """
    Filtre Statistiques: Filtres numériques (pairs/petits/suites)
    """
    import json
    
    data = json.loads(request.body)
    n = data.get('n', 16)
    k = data.get('k', 6)
    
    # Sous-filtres
    even_odd = data.get('even_odd', {})
    small_large = data.get('small_large', {})
    consecutive = data.get('consecutive', {})
    
    # Générer les combinaisons
    partants = list(range(1, n + 1))
    all_combinations = list(combinations(partants, k))
    
    filtered = []
    
    for combi in all_combinations:
        keep = True
        
        # Filtre pairs/impairs
        if even_odd.get('enabled', False):
            even_count = sum(1 for h in combi if h % 2 == 0)
            if not (even_odd.get('min', 0) <= even_count <= even_odd.get('max', k)):
                keep = False
        
        # Filtre petits/grands
        if keep and small_large.get('enabled', False):
            limit = small_large.get('limit', 10)
            small_count = sum(1 for h in combi if h <= limit)
            if not (small_large.get('min', 0) <= small_count <= small_large.get('max', k)):
                keep = False
        
        # Filtre suites consécutives
        if keep and consecutive.get('enabled', False):
            sorted_combi = sorted(combi)
            max_consecutive = 1
            current = 1
            for i in range(1, len(sorted_combi)):
                if sorted_combi[i] == sorted_combi[i-1] + 1:
                    current += 1
                    max_consecutive = max(max_consecutive, current)
                else:
                    current = 1
            if not (consecutive.get('min', 0) <= max_consecutive <= consecutive.get('max', k)):
                keep = False
        
        if keep:
            filtered.append(list(combi))
    
    return JsonResponse({
        'filtered_count': len(filtered),
        'total_count': len(all_combinations),
        'combinations': filtered
    })
