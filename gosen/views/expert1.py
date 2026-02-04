from django.http import JsonResponse
from itertools import combinations


def apply_filter(request):
    """
    Filtre Expert 1: Garder si au moins X chevaux sont dans au moins Y groupes
    """
    import json
    
    data = json.loads(request.body)
    n = data.get('n', 16)
    k = data.get('k', 6)
    groups = data.get('groups', [])
    chevaux_min = data.get('chevaux_min', 1)
    groupes_min = data.get('groupes_min', 1)
    
    # Générer toutes les combinaisons
    partants = list(range(1, n + 1))
    all_combinations = list(combinations(partants, k))
    
    # Filtrer
    filtered = []
    for combi in all_combinations:
        # Compter combien de groupes ont au moins chevaux_min chevaux dans la combinaison
        count = 0
        for group in groups:
            horses_in_group = sum(1 for h in combi if h in group.get('horses', []))
            if horses_in_group >= chevaux_min:
                count += 1
        
        if count >= groupes_min:
            filtered.append(list(combi))
    
    return JsonResponse({
        'filtered_count': len(filtered),
        'total_count': len(all_combinations),
        'combinations': filtered
    })
