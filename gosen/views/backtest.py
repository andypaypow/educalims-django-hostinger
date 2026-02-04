from django.http import JsonResponse


def test_arrivee(request):
    """Teste une arrivée contre les combinaisons filtrées"""
    import json
    
    data = json.loads(request.body)
    arrivee = data.get('arrivee', [])
    combinations = data.get('combinations', [])
    
    arrivee_set = set(arrivee)
    
    # Trouver les combinaisons qui contiennent l'arrivée
    matching = []
    for combi in combinations:
        combi_set = set(combi)
        if arrivee_set.issubset(combi_set):
            matching.append(combi)
    
    return JsonResponse({
        'arrivee': arrivee,
        'found': len(matching) > 0,
        'matching_count': len(matching),
        'matching_combinations': matching
    })
