"""
Views for Hippique TurfFilter application
"""
from django.shortcuts import render


def turf_filter(request):
    """
    Vue principale du filtre de combinaisons hippiques
    Utilise un template Django avec contexte
    """
    context = {
        'title': '🏇 Gosen TurfFilter',
        'heading': '🏇 Gosen TurfFilter',
        'subtitle': 'Filtrez vos combinaisons hippiques avec précision',
    }
    return render(request, 'hippique/turf_filter.html', context)


def api_filtrer(request):
    """
    API placeholder pour filtrer les combinaisons
    """
    from django.http import JsonResponse
    import json

    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        # Placeholder pour le traitement
        return JsonResponse({'success': True, 'message': 'API endpoint'})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
