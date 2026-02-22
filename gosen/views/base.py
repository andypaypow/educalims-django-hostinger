from django.shortcuts import render
from django.http import JsonResponse


def index(request):
    """Vue principale de l'application Filtre Expert"""
    return render(request, 'gosen/base.html')


def api_combinations_count(request):
    """API pour calculer le nombre de combinaisons possibles"""
    from math import comb
    
    n = int(request.GET.get('n', 16))
    k = int(request.GET.get('k', 6))
    
    if k < 0 or k > n or n < 8 or k < 2:
        return JsonResponse({'count': 0, 'error': 'Paramètres invalides'})
    
    count = comb(n, k)
    return JsonResponse({'count': count})


def parse_pronostics(request):
    """API pour parser les pronostics saisis par l'utilisateur"""
    import re
    
    text = request.POST.get('pronostics', '')
    lines = text.strip().split('\n')
    
    groups = []
    for line in lines:
        if not line.strip():
            continue
        
        parts = line.split(':')
        if len(parts) > 1:
            name = parts[0].strip()
            horses = list(set([int(h) for h in re.findall(r'\d+', parts[1])]))
        else:
            horses = list(set([int(h) for h in re.findall(r'\d+', line)]))
            name = f'Groupe {len(groups) + 1}'
        
        if horses:
            groups.append({'name': name, 'horses': sorted(horses)})
    
    return JsonResponse({'groups': groups})
