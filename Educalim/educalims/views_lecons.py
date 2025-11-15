from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import Discipline, Cycle, Niveau, Palier, Partie, Chapitre, Lecon


def lecon_detail(request, lecon_id):
    """
    Vue pour afficher le détail d'une leçon
    """
    lecon = get_object_or_404(Lecon.objects.select_related(
        'chapitre__palier__niveau',
        'chapitre__partie__niveau'
    ), id=lecon_id)

    # Récupérer le parent (palier ou partie) pour la navigation
    parent = lecon.chapitre.get_parent()
    niveau = lecon.chapitre.get_niveau()

    context = {
        'lecon': lecon,
        'parent': parent,
        'niveau': niveau,
    }
    return render(request, 'educalims/lecon_detail.html', context)


def chapitre_detail(request, chapitre_id):
    """
    Vue pour afficher les détails d'un chapitre avec ses leçons
    """
    chapitre = get_object_or_404(Chapitre.objects.prefetch_related(
        'lecons'
    ), id=chapitre_id)

    # Récupérer toutes les leçons du chapitre
    lecons = chapitre.lecons.all()

    # Récupérer le niveau associé via le parent
    niveau = chapitre.get_niveau()

    context = {
        'chapitre': chapitre,
        'lecons': lecons,
        'niveau': niveau,
    }
    return render(request, 'educalims/chapitre_detail.html', context)


@csrf_exempt
@require_http_methods(["GET"])
def get_lecons_by_chapitre(request):
    """
    Vue AJAX pour récupérer les leçons disponibles par chapitre
    """
    chapitre_id = request.GET.get('chapitre_id')
    if not chapitre_id:
        return JsonResponse({'error': 'chapitre_id requis'}, status=400)

    try:
        # Récupérer le chapitre
        chapitre = Chapitre.objects.get(id=chapitre_id)

        # Récupérer toutes les leçons de ce chapitre
        lecons = Lecon.objects.filter(chapitre=chapitre).order_by('numero')

        # Formatter les données pour le JSON
        lecons_data = []
        for lecon in lecons:
            lecons_data.append({
                'id': lecon.id,
                'titre': lecon.titre,
                'numero': lecon.numero,
                'description': lecon.description
            })

        return JsonResponse({'lecons': lecons_data})
    except Chapitre.DoesNotExist:
        return JsonResponse({'error': 'chapitre introuvable'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)