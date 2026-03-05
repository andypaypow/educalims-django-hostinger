# Views pour la sauvegarde et chargement de configurations
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from gosen.models import SauvegardeConfiguration
import json
from django.db import models

@csrf_exempt
@require_http_methods(['POST'])
def sauvegarder_configuration(request):
    """Sauvegarde la configuration actuelle"""
    try:
        data = json.loads(request.body)
        nom = data.get('nom', 'Sauvegarde sans nom')
        num_partants = data.get('num_partants')
        taille_combinaison = data.get('taille_combinaison')
        pronostics = data.get('pronostics', {})
        criteres_filtres = data.get('criteres_filtres', {})
        arrivee = data.get('arrivee', [])
        combinaisons_filtrees = data.get('combinaisons_filtrees', [])

        sauvegarde = SauvegardeConfiguration.objects.create(
            nom=nom,
            num_partants=num_partants,
            taille_combinaison=taille_combinaison,
            pronostics=pronostics,
            criteres_filtres=criteres_filtres,
            arrivee=arrivee,
            combinaisons_filtrees=combinaisons_filtrees
        )

        return JsonResponse({
            'success': True,
            'sauvegarde_id': sauvegarde.id,
            'message': 'Configuration sauvegardée avec succès'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(['GET'])
def lister_sauvegardes(request):
    """Liste toutes les sauvegardes de l'utilisateur"""
    try:
        sauvegardes = SauvegardeConfiguration.objects.all().order_by('-date_modification')
        data = [{
            'id': s.id,
            'nom': s.nom,
            'date_creation': s.date_creation.isoformat(),
            'date_modification': s.date_modification.isoformat(),
            'num_partants': s.num_partants,
            'taille_combinaison': s.taille_combinaison,
            'a_arrivee': bool(s.arrivee),
            'arrivee': s.arrivee if s.arrivee else []
        } for s in sauvegardes]
        return JsonResponse({'success': True, 'sauvegardes': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(['GET'])
def charger_sauvegarde(request, sauvegarde_id):
    """Charge une sauvegarde spécifique"""
    try:
        sauvegarde = SauvegardeConfiguration.objects.get(id=sauvegarde_id)
        data = {
            'id': sauvegarde.id,
            'nom': sauvegarde.nom,
            'num_partants': sauvegarde.num_partants,
            'taille_combinaison': sauvegarde.taille_combinaison,
            'pronostics': sauvegarde.pronostics,
            'criteres_filtres': sauvegarde.criteres_filtres,
            'arrivee': sauvegarde.arrivee if sauvegarde.arrivee else [],
            'combinaisons_filtres': sauvegarde.combinaisons_filtrees if sauvegarde.combinaisons_filtrees else []
        }
        return JsonResponse({'success': True, 'sauvegarde': data})
    except SauvegardeConfiguration.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Sauvegarde non trouvée'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(['POST', 'PUT'])
def modifier_sauvegarde(request, sauvegarde_id):
    """Modifie une sauvegarde existante (ex: ajouter l'arrivée)"""
    try:
        sauvegarde = SauvegardeConfiguration.objects.get(id=sauvegarde_id)
        data = json.loads(request.body)

        if 'arrivee' in data:
            sauvegarde.arrivee = data['arrivee']
        if 'nom' in data:
            sauvegarde.nom = data['nom']

        sauvegarde.save()
        return JsonResponse({'success': True, 'message': 'Sauvegarde mise à jour'})
    except SauvegardeConfiguration.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Sauvegarde non trouvée'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(['DELETE'])
def supprimer_sauvegarde(request, sauvegarde_id):
    """Supprime une sauvegarde"""
    try:
        sauvegarde = SauvegardeConfiguration.objects.get(id=sauvegarde_id)
        sauvegarde.delete()
        return JsonResponse({'success': True, 'message': 'Sauvegarde supprimée'})
    except SauvegardeConfiguration.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Sauvegarde non trouvée'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
