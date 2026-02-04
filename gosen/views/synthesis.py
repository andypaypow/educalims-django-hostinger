from django.http import JsonResponse


def citation_synthesis(request):
    """Synthèse par citation (nombre d'apparitions dans les groupes)"""
    import json
    
    data = json.loads(request.body)
    groups = data.get('groups', [])
    
    citation_counts = {}
    for group in groups:
        for horse in group.get('horses', []):
            citation_counts[horse] = citation_counts.get(horse, 0) + 1
    
    sorted_citation = sorted(citation_counts.items(), key=lambda x: x[1], reverse=True)
    
    return JsonResponse({
        'synthesis': [{'horse': h, 'count': c} for h, c in sorted_citation]
    })


def position_synthesis(request):
    """Synthèse par position (pondérée par la position dans chaque groupe)"""
    import json
    
    data = json.loads(request.body)
    groups = data.get('groups', [])
    
    position_scores = {}
    for group in groups:
        horses = group.get('horses', [])
        for idx, horse in enumerate(horses):
            position_scores[horse] = position_scores.get(horse, 0) + (len(horses) - idx)
    
    sorted_position = sorted(position_scores.items(), key=lambda x: x[1], reverse=True)
    
    return JsonResponse({
        'synthesis': [{'horse': h, 'score': s} for h, s in sorted_position]
    })
