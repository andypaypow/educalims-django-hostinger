from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import Discipline, Cycle, Niveau, Palier, Partie, Chapitre, Lecon


def palier_detail(request, palier_id):
    """
    Vue pour afficher le détail d'un palier avec ses chapitres
    """
    palier = get_object_or_404(Palier.objects.select_related(
        'niveau__cycle__discipline'
    ), id=palier_id)
    
    # Récupérer les chapitres associés à ce palier
    chapitres = Chapitre.objects.filter(palier=palier).order_by('numero')
    
    context = {
        'palier': palier,
        'chapitres': chapitres,
    }
    return render(request, 'educalims/palier_detail.html', context)


def partie_detail(request, partie_id):
    """
    Vue pour afficher le détail d'une partie avec ses chapitres
    """
    partie = get_object_or_404(Partie.objects.select_related(
        'niveau__cycle__discipline'
    ), id=partie_id)
    
    # Récupérer les chapitres associés à cette partie
    chapitres = Chapitre.objects.filter(partie=partie).order_by('numero')
    
    context = {
        'partie': partie,
        'chapitres': chapitres,
    }
    return render(request, 'educalims/partie_detail.html', context)


@csrf_exempt
@require_http_methods(["GET"])
def get_paliers_by_niveau(request):
    """
    Vue AJAX pour récupérer les paliers disponibles par niveau
    """
    niveau_id = request.GET.get('niveau_id')
    if not niveau_id:
        return JsonResponse({'error': 'niveau_id requis'}, status=400)
    
    try:
        # Récupérer le niveau
        niveau = Niveau.objects.get(id=niveau_id)
        
        # Récupérer tous les paliers disponibles pour ce niveau
        paliers = Palier.objects.filter(niveau=niveau).order_by('numero')
        
        # Formatter les données pour le JSON
        paliers_data = []
        for palier in paliers:
            paliers_data.append({
                'id': palier.id,
                'titre': palier.titre,
                'numero': palier.numero,
                'description': palier.description,
                'niveau': palier.niveau.nom
            })
        
        return JsonResponse({'paliers': paliers_data})
    except Niveau.DoesNotExist:
        return JsonResponse({'error': 'niveau introuvable'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_parties_by_niveau(request):
    """
    Vue AJAX pour récupérer les parties disponibles par niveau
    """
    niveau_id = request.GET.get('niveau_id')
    if not niveau_id:
        return JsonResponse({'error': 'niveau_id requis'}, status=400)
    
    try:
        # Récupérer le niveau
        niveau = Niveau.objects.get(id=niveau_id)
        
        # Récupérer toutes les parties disponibles pour ce niveau
        parties = Partie.objects.filter(niveau=niveau).order_by('titre')
        
        # Formatter les données pour le JSON
        parties_data = []
        for partie in parties:
            parties_data.append({
                'id': partie.id,
                'titre': partie.titre,
                'description': partie.description,
                'niveau': partie.niveau.nom
            })
        
        return JsonResponse({'parties': parties_data})
    except Niveau.DoesNotExist:
        return JsonResponse({'error': 'niveau introuvable'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)