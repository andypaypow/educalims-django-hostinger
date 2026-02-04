from django.http import JsonResponse
from itertools import combinations
from collections import defaultdict


def apply_filter(request):
    """
    Filtre Expert 2: Garder si au moins X chevaux communs existent dans au moins Y groupes
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
    
    # Pour chaque combinaison, compter les occurrences de chaque cheval dans les groupes
    filtered = []
    for combi in all_combinations:
        horse_group_count = defaultdict(int)
        
        for horse in combi:
            for group in groups:
                if horse in group.get('horses', []):
                    horse_group_count[horse] += 1
        
        # Compter combien de chevaux apparaissent dans au moins groupes_min groupes
        count = sum(1 for h in combi if horse_group_count[h] >= groupes_min)
        
        if count >= chevaux_min:
            filtered.append(list(combi))
    
    return JsonResponse({
        'filtered_count': len(filtered),
        'total_count': len(all_combinations),
        'combinations': filtered
    })
